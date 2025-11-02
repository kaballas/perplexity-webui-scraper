"""Debate orchestrator that alternates between the HuggingFace WRICEF API and Perplexity."""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Sequence

from dotenv import load_dotenv
from generate_wricef_prompts import (
    DEFAULT_API_URL as DEFAULT_HUGGING_URL,
    DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
    DEFAULT_TEMPERATURE as DEFAULT_HUGGING_TEMPERATURE,
    ENV_TOKEN_KEY as HUGGING_TOKEN_ENV,
    ApiConfig,
    call_wricef_api,
)
from pplx_harness.net.pplx import PplxAdapter, collect_stream_text


@dataclass(slots=True)
class DebateTurn:
    speaker: str
    text: str
    feedback: str | None = None


def format_history(history: Sequence[DebateTurn]) -> str:
    if not history:
        return "No dialogue yet."
    parts = []
    for turn in history:
        parts.append(f"{turn.speaker}: {turn.text}")
        if turn.feedback:
            parts.append(f"[User Feedback]: {turn.feedback}")
    return "\n".join(parts)


def should_stop(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        print("[DEBUG] should_stop: empty text, returning False", file=sys.stderr)
        return False
    upper = stripped.upper()
    result = upper == "STOP" or upper.endswith(" STOP")
    print(f"[DEBUG] should_stop: checking '{stripped[:50]}...' -> {result}", file=sys.stderr)
    return result


def prompt_user_continue(agent_name: str, agent_requested_stop: bool) -> tuple[bool, str | None]:
    """
    Prompt user to continue and optionally provide feedback.
    Returns (should_continue, feedback_text).
    """
    print(f"[DEBUG] prompt_user_continue: agent={agent_name}, agent_requested_stop={agent_requested_stop}", file=sys.stderr)
    default_yes = not agent_requested_stop
    yes_label = "Y" if default_yes else "y"
    no_label = "n" if default_yes else "N"

    if agent_requested_stop:
        message = f"{agent_name} suggested ending the debate with STOP. Continue anyway? [{yes_label}/{no_label}]: "
    else:
        message = f"Continue to the next round? [{yes_label}/{no_label}]: "

    while True:
        try:
            response = input(message).strip().lower()
            print(f"[DEBUG] User input: '{response}'", file=sys.stderr)
        except (EOFError, KeyboardInterrupt):
            print("\n[DEBUG] EOFError/KeyboardInterrupt during input", file=sys.stderr)
            print("\nNo input detected; stopping debate.")
            return False, None

        if not response:
            should_continue = default_yes
            print(f"[DEBUG] Empty input, using default: {should_continue}", file=sys.stderr)
            if not should_continue:
                return False, None
            break

        if response in {"y", "yes", "c", "continue"}:
            print("[DEBUG] User chose to continue", file=sys.stderr)
            break
        if response in {"n", "no", "stop", "s", "q", "quit"}:
            print("[DEBUG] User chose to stop", file=sys.stderr)
            return False, None

        print("Please respond with 'y' or 'n'.")

    # Continuing - ask for optional feedback
    try:
        feedback_prompt = "Optional feedback to inject into the conversation (press Enter to skip): "
        feedback = input(feedback_prompt).strip()
        print(f"[DEBUG] User feedback: '{feedback[:100]}...' ({len(feedback)} chars)", file=sys.stderr)
        return True, feedback if feedback else None
    except (EOFError, KeyboardInterrupt):
        print("\n[DEBUG] Skipping feedback due to interrupt", file=sys.stderr)
        return True, None


class DebateAgent:
    def __init__(self, name: str, stance: str, persona: str) -> None:
        self.name = name
        self.stance = stance
        self.persona = persona

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        raise NotImplementedError

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        raise NotImplementedError


class HuggingDebater(DebateAgent):
    def __init__(self, config: ApiConfig) -> None:
        super().__init__("Hugging", "defend the proposition", "a pragmatic solution architect")
        self._config = config

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = (
            f"""You are a senior SAP SuccessFactors Solution Architect working for Deloitte on the Queensland Department of Education's Human Capital Management System (HCMS) implementation. Your role involves:

- Designing and implementing SAP SuccessFactors solutions aligned with the Queensland DoE's requirements
- Working within the Explore phase of the implementation lifecycle
- Collaborating with the Department's security architects to ensure compliance with cybersecurity standards
- Addressing integration considerations, configuration requirements, and system design elements
- Focusing on modules including Employee Central, Offer Management, Payroll integration, and Organisational Design Management
- Ensuring adherence to disaster recovery, business continuity, and backup requirements (noting that these are vendor responsibilities with SAP as the cloud-based solution provider)
- Working with configurable admin alerts, custom fields, and master data synchronization requirements
- Supporting integration with e-signature tools and offer negotiation processes
- Providing expertise on Fiori design language and user experience consistency
- Coordinating with managed services support models including AI chatbots and change management processes

Your responses should reflect deep knowledge of SAP SuccessFactors HCM Suite, cloud-based solution architecture, integration suite capabilities, and the specific needs of educational sector human capital management. You must prioritize security compliance, system reliability, and alignment with the Department's operational requirements while leveraging Deloitte's implementation methodologies.

{topic}

Discussion so far:
{conversation}

###Important: Deloitte uses PeopleForms for custom developments instead of SAP Fiori Elements.###
Provide your next statement now."""
        )
        print(f"[DEBUG] {self.name}._build_prompt: SOLUTION_ARCHITECT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] HuggingDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        start_time = time.time()
        print(f"[DEBUG] HuggingDebater.respond: calling API (url={self._config.url}, model={self._config.model})", file=sys.stderr)
        text, _ = call_wricef_api(prompt, config=self._config)
        elapsed = time.time() - start_time
        print(f"[DEBUG] HuggingDebater.respond: API returned {len(text)} chars in {elapsed:.2f}s", file=sys.stderr)
        return text.strip()


class PerplexityDebater(DebateAgent):
    def __init__(self, session_token: str) -> None:
        super().__init__("Perplexity", "challenge the proposition", "an investigative strategist")
        self._client = PplxAdapter(session_token=session_token)

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = f"""You are a senior SAP functional consultant and fact-checking analyst operating under strict research-journalist standards.

Objective:
Fact-check the provided WRICEF documentation and SAP SuccessFactors analysis line by line. For each statement, use verified web sources to confirm accuracy, identify discrepancies, and cite your findings. Focus on technical validity, current SAP best practices, and official documentation consistency.

Research Standards:
1. TEMPERATURE_SIM=0.4 (deterministic, logical reasoning)
2. THINK_DEEP and THINK_STEP_BY_STEP (internal reasoning; output remains concise/logical)
3. Maintain research-journalist persona; technical tone; no emojis or decorative symbols
4. Statements must follow a logical chain

Source Requirements (Mandatory Targets):
- Peer-reviewed repositories: arXiv, PubMed, Google Scholar (PDFs only), JSTOR, ScienceDirect, Scopus
- Technical libraries: IEEE Xplore, ACM Digital Library
- Preprint servers: BioRxiv, MedRxiv, SSRN
- Official sources: .edu/.gov domains, national labs (MIT, CERN, NIST, NASA)
- EXCLUSIONS: No news/blogs/forums/social media/video transcripts/commercial pages/AI overviews

Citation Rules:
- MINIMUM: ≥2 sources per core statement
- PREFERRED: Peer-reviewed papers or listed repositories
- FORMAT: Immediate in-text citations (Author, Year)
- REFERENCES: APA style at end

Output Format:
Present findings in tabular format:
| Statement | Status | Evidence Summary | Source/Citation | Notes |

Where:
- Statement: Original claim from analysis
- Status: Factual / Partially True / False / Unverified
- Evidence Summary: 2-3 sentences from qualifying sources
- Source/Citation: (Author, Year) with URL
- Notes: Context, version info, deprecation warnings

Context:
WRICEF (Workflows, Reports, Interfaces, Conversions, Enhancements, and Forms) items are key SAP project deliverables. Accuracy is critical for system integrity and audit compliance.

Topic:
{topic}

Analysis to Fact-Check:
{conversation}

Provide your fact-check results now following the tabular format and citation requirements."""

        print(f"[DEBUG] {self.name}._build_prompt: FACT_CHECK prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] PerplexityDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        start_time = time.time()
        print(f"[DEBUG] PerplexityDebater.respond: calling PplxAdapter.ask", file=sys.stderr)
        text = collect_stream_text(self._client, prompt)
        elapsed = time.time() - start_time
        print(f"[DEBUG] PerplexityDebater.respond: stream returned {len(text)} chars in {elapsed:.2f}s", file=sys.stderr)
        return text.strip()


class WriterDebater(DebateAgent):
    def __init__(self, config: ApiConfig) -> None:
        super().__init__("Writer", "synthesize and summarize", "a technical writer")
        self._config = config

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = f"""You are a senior technical writer specializing in SAP SuccessFactors documentation and system analysis. Your role is to synthesize information from the debate between the solution architect and fact-checker to create clear, well-structured documentation.

Your responsibilities include:
- Summarizing key points from both perspectives (solution architect and fact-checker)
- Identifying agreements and disagreements between the parties
- Creating clear, actionable documentation that addresses both technical implementation and verification concerns
- Maintaining professional, precise language appropriate for technical documentation
- Providing recommendations based on the combined insights

Context:
{topic}

Debate Transcript:
{conversation}

Synthesize the information and provide a comprehensive summary with clear recommendations."""

        print(f"[DEBUG] {self.name}._build_prompt: TECHNICAL_WRITER prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        print(f"[DEBUG] WriterDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        start_time = time.time()
        print(f"[DEBUG] WriterDebater.respond: calling API (url={self._config.url}, model={self._config.model})", file=sys.stderr)
        text, _ = call_wricef_api(prompt, config=self._config)
        elapsed = time.time() - start_time
        print(f"[DEBUG] WriterDebater.respond: API returned {len(text)} chars in {elapsed:.2f}s", file=sys.stderr)
        return text.strip()


class AskQuestionsDebater(DebateAgent):
    def __init__(self, config: ApiConfig) -> None:
        super().__init__("AskQuestions", "ask clarifying questions", "a curious inquirer")
        self._config = config

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = f"""You are a curious inquirer whose role is to ask clarifying questions about the topic and the ongoing debate. Your goal is to help deepen understanding by identifying gaps in knowledge, requesting additional details, and challenging assumptions through thoughtful questions.

Your responsibilities include:
- Asking specific, relevant questions based on the topic and current discussion
- Identifying areas where more clarity is needed
- Requesting examples or use cases to better understand concepts
- Challenging assumptions in a constructive way
- Helping the other agents think more deeply about the subject

Context:
{topic}

Debate Transcript:
{conversation}

Formulate relevant questions that would help clarify and expand the discussion."""
        
        print(f"[DEBUG] {self.name}._build_prompt: ASK_QUESTIONS prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        print(f"[DEBUG] AskQuestionsDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        start_time = time.time()
        print(f"[DEBUG] AskQuestionsDebater.respond: calling API (url={self._config.url}, model={self._config.model})", file=sys.stderr)
        text, _ = call_wricef_api(prompt, config=self._config)
        elapsed = time.time() - start_time
        print(f"[DEBUG] AskQuestionsDebater.respond: API returned {len(text)} chars in {elapsed:.2f}s", file=sys.stderr)
        return text.strip()


class AnswerQuestionsDebater(DebateAgent):
    def __init__(self, config: ApiConfig) -> None:
        super().__init__("AnswerQuestions", "answer questions", "a knowledgeable responder")
        self._config = config

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = f"""You are a knowledgeable responder whose role is to provide clear, accurate answers to questions raised in the debate. Your goal is to address specific questions posed by other agents and provide comprehensive, well-researched responses.

Your responsibilities include:
- Providing accurate and detailed answers to questions asked in the discussion
- Drawing from the provided context and any relevant background knowledge
- Clarifying technical concepts with specific examples when possible
- Addressing concerns raised by other agents with substantive responses
- Supporting your answers with logical reasoning and evidence where applicable

Context:
{topic}

Debate Transcript:
{conversation}

Provide clear, comprehensive answers to any questions raised in the conversation."""
        
        print(f"[DEBUG] {self.name}._build_prompt: ANSWER_QUESTIONS prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        print(f"[DEBUG] AnswerQuestionsDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        start_time = time.time()
        print(f"[DEBUG] AnswerQuestionsDebater.respond: calling API (url={self._config.url}, model={self._config.model})", file=sys.stderr)
        text, _ = call_wricef_api(prompt, config=self._config)
        elapsed = time.time() - start_time
        print(f"[DEBUG] AnswerQuestionsDebater.respond: API returned {len(text)} chars in {elapsed:.2f}s", file=sys.stderr)
        return text.strip()


def build_hugging_config(args: argparse.Namespace) -> ApiConfig:
    print("[DEBUG] build_hugging_config: checking token", file=sys.stderr)
    token = args.hugging_token or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"Hugging API token required. Provide --hugging-token or set {HUGGING_TOKEN_ENV}."
        )
    print(f"[DEBUG] build_hugging_config: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=args.hugging_url,
        token=token,
        model=args.hugging_model,
        temperature=args.hugging_temperature,
        timeout=args.hugging_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_hugging_config: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    return config


def build_perplexity_agent(args: argparse.Namespace) -> PerplexityDebater:
    print("[DEBUG] build_perplexity_agent: checking session token", file=sys.stderr)
    session_token = (args.perplexity_token or os.getenv("PERPLEXITY_SESSION_TOKEN", "")).strip()
    if not session_token:
        raise ValueError("Perplexity session token required. Provide --perplexity-token or set PERPLEXITY_SESSION_TOKEN.")
    print(f"[DEBUG] build_perplexity_agent: token found, length={len(session_token)}", file=sys.stderr)
    return PerplexityDebater(session_token=session_token)


def build_writer_agent(args: argparse.Namespace) -> WriterDebater:
    print("[DEBUG] build_writer_agent: checking token", file=sys.stderr)
    token = args.writer_token or os.getenv("WRITER_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"Writer API token required. Provide --writer-token or set WRITER_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for writer-specific URL in environment
    url = args.writer_url or os.getenv("WRITER_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for writer-specific model in environment
    model = args.writer_model or os.getenv("WRITER_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_writer_agent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.writer_temperature,
        timeout=args.writer_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_writer_agent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    return WriterDebater(config=config)


def build_askquestions_agent(args: argparse.Namespace) -> AskQuestionsDebater:
    print("[DEBUG] build_askquestions_agent: checking token", file=sys.stderr)
    token = args.askquestions_token or os.getenv("ASKQUESTIONS_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"AskQuestions API token required. Provide --askquestions-token or set ASKQUESTIONS_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for askquestions-specific URL in environment
    url = args.askquestions_url or os.getenv("ASKQUESTIONS_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for askquestions-specific model in environment
    model = args.askquestions_model or os.getenv("ASKQUESTIONS_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_askquestions_agent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.askquestions_temperature,
        timeout=args.askquestions_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_askquestions_agent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    return AskQuestionsDebater(config=config)


def build_answerquestions_agent(args: argparse.Namespace) -> AnswerQuestionsDebater:
    print("[DEBUG] build_answerquestions_agent: checking token", file=sys.stderr)
    token = args.answerquestions_token or os.getenv("ANSWERQUESTIONS_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"AnswerQuestions API token required. Provide --answerquestions-token or set ANSWERQUESTIONS_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for answerquestions-specific URL in environment
    url = args.answerquestions_url or os.getenv("ANSWERQUESTIONS_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for answerquestions-specific model in environment
    model = args.answerquestions_model or os.getenv("ANSWERQUESTIONS_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_answerquestions_agent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.answerquestions_temperature,
        timeout=args.answerquestions_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_answerquestions_agent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    return AnswerQuestionsDebater(config=config)


def append_turn_to_file(filepath: Path, turn: DebateTurn, round_idx: int) -> None:
    """Append a debate turn to the transcript file."""
    try:
        with filepath.open("a", encoding="utf-8") as f:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"Round {round_idx} - {turn.speaker}\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"{turn.text}\n")
            if turn.feedback:
                f.write(f"\n[User Feedback]\n{turn.feedback}\n")
        print(f"[DEBUG] append_turn_to_file: wrote round {round_idx} to {filepath}", file=sys.stderr)
    except Exception as exc:
        print(f"[DEBUG] append_turn_to_file: failed to write to {filepath}: {exc!r}", file=sys.stderr)


def initialize_transcript_file(filepath: Path, topic: str, max_rounds: int, first_speaker: str) -> None:
    """Initialize transcript file with metadata header."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("w", encoding="utf-8") as f:
            f.write(f"Debate Transcript\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Topic: {topic}\n")
            f.write(f"Max Rounds: {max_rounds}\n")
            f.write(f"First Speaker: {first_speaker}\n")
            f.write(f"{'=' * 80}\n")
        print(f"[DEBUG] initialize_transcript_file: created {filepath}", file=sys.stderr)
    except Exception as exc:
        print(f"[DEBUG] initialize_transcript_file: failed to create {filepath}: {exc!r}", file=sys.stderr)


def run_debate(
    topic: str,
    hugging: HuggingDebater,
    perplexity: PerplexityDebater,
    writer: "WriterDebater",
    askquestions: "AskQuestionsDebater",
    answerquestions: "AnswerQuestionsDebater",
    *,
    max_rounds: int,
    first_speaker: str,
    transcript_file: Path | None = None,
) -> int:
    print(f"[DEBUG] run_debate: topic='{topic}', max_rounds={max_rounds}, first_speaker={first_speaker}", file=sys.stderr)

    # Initialize transcript file
    if transcript_file:
        initialize_transcript_file(transcript_file, topic, max_rounds, first_speaker)
        print(f"[INFO] Transcript will be saved to: {transcript_file}")

    debaters = {
        "hugging": hugging,
        "perplexity": perplexity,
        "writer": writer,
        "askquestions": askquestions,
        "answerquestions": answerquestions,
    }
    print(f"[DEBUG] run_debate: available agents={list(debaters.keys())}", file=sys.stderr)
    history: List[DebateTurn] = []

    print(f"Debate topic: {topic}\n")
    stop_reason = "max_rounds"

    # --- AGENT SELECTION: Ask user to select agent for round 1 ---
    print(f"\nRound 1 - Available agents:")
    for i, (agent_key, agent) in enumerate(debaters.items(), 1):
        print(f"  {i}. {agent.name}")
    selected_agent_key = None
    while selected_agent_key is None:
        try:
            user_input = input(f"Select agent for round 1 (1-{len(debaters)} or agent name): ").strip().lower()
            if user_input.isdigit():
                index = int(user_input) - 1
                if 0 <= index < len(debaters):
                    selected_agent_key = list(debaters.keys())[index]
            else:
                for agent_key in debaters.keys():
                    if user_input in [agent_key, debaters[agent_key].name.lower()]:
                        selected_agent_key = agent_key
                        break
            if selected_agent_key is None:
                print(f"Invalid selection. Please enter a number between 1 and {len(debaters)}, or an agent name.")
        except (EOFError, KeyboardInterrupt):
            print("\n[DEBUG] EOFError/KeyboardInterrupt during agent selection", file=sys.stderr)
            print("\nNo input detected; stopping debate.")
            return 0

    for round_idx in range(1, max_rounds + 1):
        # For round 1, use the selected agent; for subsequent rounds, prompt user
        if round_idx == 1:
            responder = debaters[selected_agent_key]
        else:
            print(f"\nRound {round_idx} - Available agents:")
            for i, (agent_key, agent) in enumerate(debaters.items(), 1):
                print(f"  {i}. {agent.name}")
            selected_agent_key = None
            while selected_agent_key is None:
                try:
                    user_input = input(f"Select agent for round {round_idx} (1-{len(debaters)} or agent name): ").strip().lower()
                    if user_input.isdigit():
                        index = int(user_input) - 1
                        if 0 <= index < len(debaters):
                            selected_agent_key = list(debaters.keys())[index]
                    else:
                        for agent_key in debaters.keys():
                            if user_input in [agent_key, debaters[agent_key].name.lower()]:
                                selected_agent_key = agent_key
                                break
                    if selected_agent_key is None:
                        print(f"Invalid selection. Please enter a number between 1 and {len(debaters)}, or an agent name.")
                except (EOFError, KeyboardInterrupt):
                    print("\n[DEBUG] EOFError/KeyboardInterrupt during agent selection", file=sys.stderr)
                    print("\nNo input detected; stopping debate.")
                    return 0
            responder = debaters[selected_agent_key]

        # Select opponent - use the most recent speaker that is not the current one
        opponent = None
        for turn in reversed(history):
            if turn.speaker != responder.name:
                opponent_agent = debaters[turn.speaker.lower()]
                if opponent_agent.name == turn.speaker:
                    opponent = opponent_agent
                    break
        if opponent is None:
            for agent_key, agent in debaters.items():
                if agent_key != selected_agent_key:
                    opponent = agent
                    break

        print(f"[DEBUG] Round {round_idx}: speaker={responder.name}, opponent={opponent.name if opponent else 'None'}", file=sys.stderr)

        try:
            response = responder.respond(topic, history, opponent)
        except Exception as exc:
            print(f"[DEBUG] Exception during {responder.name}.respond: {exc!r}", file=sys.stderr)
            print(f"{responder.name} failed to respond: {exc}", file=sys.stderr)
            return 1

        cleaned = response.strip() or "[No response]"
        print(f"[DEBUG] Round {round_idx} response: length={len(cleaned)}, first_50_chars='{cleaned[:50]}'", file=sys.stderr)
        turn = DebateTurn(speaker=responder.name, text=cleaned)
        history.append(turn)

        print(f"Round {round_idx} - {responder.name}:\n{cleaned}\n")

        if transcript_file:
            append_turn_to_file(transcript_file, turn, round_idx)

        agent_requested_stop = should_stop(cleaned)

        if round_idx >= max_rounds:
            print(f"[DEBUG] Reached max_rounds ({max_rounds})", file=sys.stderr)
            stop_reason = "max_rounds"
            break

        should_continue, user_feedback = prompt_user_continue(responder.name, agent_requested_stop)

        if not should_continue:
            print("[DEBUG] User requested stop", file=sys.stderr)
            stop_reason = "user_stop"
            break

        if user_feedback:
            turn.feedback = user_feedback
            print(f"[DEBUG] Attached feedback to round {round_idx}: {len(user_feedback)} chars", file=sys.stderr)
            if transcript_file:
                try:
                    with transcript_file.open("a", encoding="utf-8") as f:
                        f.write(f"\n[User Feedback]\n{user_feedback}\n")
                    print(f"[DEBUG] Appended feedback to transcript", file=sys.stderr)
                except Exception as exc:
                    print(f"[DEBUG] Failed to append feedback: {exc!r}", file=sys.stderr)

    print(f"[DEBUG] Debate ended: stop_reason={stop_reason}, total_turns={len(history)}", file=sys.stderr)
    if stop_reason == "max_rounds" and len(history) == max_rounds:
        print("Maximum rounds reached; debate ended.")
    elif stop_reason == "user_stop":
        print("Debate stopped by user.")

    print("\nFinal transcript:\n")
    for transcript_turn in history:
        print(f"{transcript_turn.speaker}: {transcript_turn.text}")

    print(f"\n[DEBUG] Final statistics: total_turns={len(history)}, total_chars={sum(len(t.text) for t in history)}", file=sys.stderr)
    if transcript_file:
        try:
            with transcript_file.open("a", encoding="utf-8") as f:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"Debate Summary\n")
                f.write(f"{'=' * 80}\n")
                f.write(f"Stop Reason: {stop_reason}\n")
                f.write(f"Total Rounds: {len(history)}\n")
                f.write(f"Total Characters: {sum(len(t.text) for t in history)}\n")
                f.write(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            print(f"[DEBUG] Appended summary to {transcript_file}", file=sys.stderr)
        except Exception as exc:
            print(f"[DEBUG] Failed to append summary: {exc!r}", file=sys.stderr)
    return 0


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a debate between the HuggingFace WRICEF API and Perplexity until one responds with STOP."
    )

    # Topic input: either direct string or from file
    topic_group = parser.add_mutually_exclusive_group(required=True)
    topic_group.add_argument(
        "topic",
        nargs="?",
        help="Topic or question to debate (provide as string)."
    )
    topic_group.add_argument(
        "--topic-file",
        type=Path,
        help="Path to .txt file containing the topic/question to debate."
    )

    parser.add_argument(
        "--max-rounds",
        type=int,
        default=8,
        help="Maximum number of turns (default: 8).",
    )
    parser.add_argument(
        "--first-speaker",
        choices=("hugging", "perplexity", "writer", "askquestions", "answerquestions"),
        default="hugging",
        help="Agent that speaks first (default: hugging).",
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        help="Path to save conversation transcript (.txt file). Default: transcripts/debate_TIMESTAMP.txt",
    )
    parser.add_argument(
        "--hugging-url",
        default=DEFAULT_HUGGING_URL,
        help=f"Hugging API endpoint (default: {DEFAULT_HUGGING_URL}).",
    )
    parser.add_argument(
        "--hugging-model",
        default=DEFAULT_HUGGING_MODEL,
        help=f"Hugging API model identifier (default: {DEFAULT_HUGGING_MODEL}).",
    )
    parser.add_argument(
        "--hugging-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"Hugging API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--hugging-timeout",
        type=float,
        default=60.0,
        help="Hugging API timeout in seconds (default: 60).",
    )
    parser.add_argument(
        "--hugging-token",
        help=f"Hugging API token (overrides {HUGGING_TOKEN_ENV}).",
    )
    parser.add_argument(
        "--perplexity-token",
        help="Perplexity session token (overrides PERPLEXITY_SESSION_TOKEN).",
    )
    # Writer agent configuration
    parser.add_argument(
        "--writer-url",
        default="",
        help=f"Writer API endpoint (default: value from WRITER_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--writer-model",
        default="",
        help="Writer API model identifier (default: value from WRITER_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--writer-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"Writer API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--writer-timeout",
        type=float,
        default=60.0,
        help="Writer API timeout in seconds (default: 60).",
    )
    parser.add_argument(
        "--writer-token",
        help=f"Writer API token (overrides {HUGGING_TOKEN_ENV}).",
    )
    # AskQuestions agent configuration
    parser.add_argument(
        "--askquestions-url",
        default="",
        help=f"AskQuestions API endpoint (default: value from ASKQUESTIONS_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--askquestions-model",
        default="",
        help=f"AskQuestions API model identifier (default: value from ASKQUESTIONS_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--askquestions-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"AskQuestions API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--askquestions-timeout",
        type=float,
        default=60.0,
        help="AskQuestions API timeout in seconds (default: 60).",
    )
    parser.add_argument(
        "--askquestions-token",
        help=f"AskQuestions API token (overrides ASKQUESTIONS_TOKEN).",
    )
    # AnswerQuestions agent configuration
    parser.add_argument(
        "--answerquestions-url",
        default="",
        help=f"AnswerQuestions API endpoint (default: value from ANSWERQUESTIONS_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--answerquestions-model",
        default="",
        help=f"AnswerQuestions API model identifier (default: value from ANSWERQUESTIONS_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--answerquestions-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"AnswerQuestions API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--answerquestions-timeout",
        type=float,
        default=60.0,
        help="AnswerQuestions API timeout in seconds (default: 60).",
    )
    parser.add_argument(
        "--answerquestions-token",
        help=f"AnswerQuestions API token (overrides ANSWERQUESTIONS_TOKEN).",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    print("[DEBUG] main: loading .env", file=sys.stderr)
    load_dotenv()
    print("[DEBUG] main: parsing arguments", file=sys.stderr)
    args = parse_args(argv)

    # Load topic from file or use direct argument
    if args.topic_file:
        print(f"[DEBUG] main: loading topic from file {args.topic_file}", file=sys.stderr)
        try:
            topic = args.topic_file.read_text(encoding="utf-8").strip()
            if not topic:
                print(f"[ERROR] Topic file {args.topic_file} is empty", file=sys.stderr)
                return 1
            print(f"[DEBUG] main: loaded topic from file ({len(topic)} chars)", file=sys.stderr)
        except FileNotFoundError:
            print(f"[ERROR] Topic file not found: {args.topic_file}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"[ERROR] Failed to read topic file {args.topic_file}: {exc}", file=sys.stderr)
            return 1
    else:
        topic = args.topic
        print(f"[DEBUG] main: using topic from argument", file=sys.stderr)

    print(f"[DEBUG] main: parsed args: topic_length={len(topic)}, max_rounds={args.max_rounds}, first_speaker={args.first_speaker}", file=sys.stderr)

    # Determine transcript file path
    if args.transcript:
        transcript_file = args.transcript
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        transcript_file = Path("transcripts") / f"debate_{timestamp}.txt"

    print(f"[DEBUG] main: transcript_file={transcript_file}", file=sys.stderr)

    print("[DEBUG] main: building Hugging config", file=sys.stderr)
    hugging_config = build_hugging_config(args)
    print("[DEBUG] main: building Perplexity agent", file=sys.stderr)
    perplexity_agent = build_perplexity_agent(args)
    print("[DEBUG] main: creating HuggingDebater", file=sys.stderr)
    hugging_agent = HuggingDebater(hugging_config)
    print("[DEBUG] main: creating WriterDebater", file=sys.stderr)
    writer_agent = build_writer_agent(args)
    print("[DEBUG] main: creating AskQuestionsDebater", file=sys.stderr)
    askquestions_agent = build_askquestions_agent(args)
    print("[DEBUG] main: creating AnswerQuestionsDebater", file=sys.stderr)
    answerquestions_agent = build_answerquestions_agent(args)

    print("[DEBUG] main: starting debate", file=sys.stderr)
    return run_debate(
        topic,
        hugging_agent,
        perplexity_agent,
        writer_agent,
        askquestions_agent,
        answerquestions_agent,
        max_rounds=max(1, args.max_rounds),
        first_speaker=args.first_speaker,
        transcript_file=transcript_file,
    )


if __name__ == "__main__":
    raise SystemExit(main())
