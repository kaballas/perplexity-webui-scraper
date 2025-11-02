"""Core debate orchestration logic."""

from __future__ import annotations

import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Sequence

from .prompts import DebateTurn


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


def append_turn_to_file(filepath: Path, turn: DebateTurn, round_idx: int) -> None:
    """Append a debate turn to the transcript file."""
    try:
        with filepath.open("a", encoding="utf-8") as f:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"Task {round_idx}\n")
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
            f.write(f"{'=' * 80}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"TASK: {topic}\n")
            f.write(f"{'=' * 80}\n")
        print(f"[DEBUG] initialize_transcript_file: created {filepath}", file=sys.stderr)
    except Exception as exc:
        print(f"[DEBUG] initialize_transcript_file: failed to create {filepath}: {exc!r}", file=sys.stderr)


def run_debate(
    topic: str,
    hugging: "HuggingDebater",
    perplexity: "PerplexityDebater",
    writer: "WriterDebater",
    askquestions: "AskQuestionsDebater",
    answerquestions: "AnswerQuestionsDebater",
    integrationexpert: "IntegrationExpertDebater",
    functionalspec: "FunctionalSpecDebater",
    technicalspec: "TechnicalSpecDebater",
    configagent: "ConfigurationAgent",
    datamigrationagent: "DataMigrationAgent",
    reportingagent: "ReportingAgent",
    securityagent: "SecurityAgent",
    testingagent: "TestingAgent",
    changemgmtagent: "ChangeMgmtAgent",
    monitoringagent: "MonitoringAgent",
    learningagent: "LearningAgent",
    metadataextractagent: "MetadataExtractAgent",
    internetresearch_agent: "InternetResearchAgent",
    critiqueagent: "CritiqueAgent",
    compressionagent: "CompressionAgent",
    todoagent: "TodoAgent",
    mrpromptbuilderagent: "MrPromptBuilderAgent",
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
        "integrationexpert": integrationexpert,
        "functionalspec": functionalspec,
        "technicalspec": technicalspec,
        "config": configagent,
        "datamigration": datamigrationagent,
        "reporting": reportingagent,
        "security": securityagent,
        "testing": testingagent,
        "changemgmt": changemgmtagent,
        "monitoring": monitoringagent,
        "learning": learningagent,
        "metadataextract": metadataextractagent,
        "internetresearch": internetresearch_agent,
        "critique": critiqueagent,
        "compression": compressionagent,
        "todo": todoagent,
        "mrpromptbuilder": mrpromptbuilderagent,
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

        # Check if this is the CompressionAgent requesting a conversation reset
        if responder.name == "Compression" and "RESET_CONVERSATION" in response.upper():
            print(f"[DEBUG] CompressionAgent requested conversation reset", file=sys.stderr)
            # Extract the compressed summary (everything after RESET_CONVERSATION marker)
            reset_marker_pos = response.upper().find("RESET_CONVERSATION")
            if reset_marker_pos >= 0:
                compressed_summary = response[reset_marker_pos + len("RESET_CONVERSATION"):].strip()
                if compressed_summary:
                    # Create a new conversation with the compressed summary as the first message
                    print(f"[DEBUG] Creating new conversation with compressed summary", file=sys.stderr)

                    # Save the current transcript if it exists
                    if transcript_file:
                        try:
                            with transcript_file.open("a", encoding="utf-8") as f:
                                f.write(f"\n{'=' * 80}\n")
                                f.write(f"CONVERSATION COMPRESSED AND RESET\n")
                                f.write(f"{'=' * 80}\n")
                                f.write(f"Compressed Summary: {compressed_summary}\n")
                                f.write(f"Reset triggered by: {responder.name}\n")
                                f.write(f"Round: {round_idx}\n")
                        except Exception as exc:
                            print(f"[DEBUG] Failed to append compression info to transcript: {exc!r}", file=sys.stderr)

                    # Create a new transcript file for the reset conversation
                    if transcript_file:
                        from datetime import datetime
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        reset_transcript_file = transcript_file.parent / f"debate_reset_{timestamp}.txt"
                        print(f"[INFO] New conversation will be saved to: {reset_transcript_file}")

                        # Initialize the new transcript with the compressed summary
                        try:
                            reset_transcript_file.parent.mkdir(parents=True, exist_ok=True)
                            with reset_transcript_file.open("w", encoding="utf-8") as f:
                                f.write(f"{'=' * 80}\n")
                                f.write(f"Compressed Summary: {compressed_summary}\n")
                                f.write(f"Reset Round: {round_idx}\n")
                                f.write(f"{'=' * 80}\n")
                                f.write(f"\nTask 1 - {responder.name} (Compressed Summary):\n{compressed_summary}\n")
                            print(f"[DEBUG] Created new transcript with compressed summary", file=sys.stderr)

                            # Update the transcript file reference to the new file
                            transcript_file = reset_transcript_file
                        except Exception as exc:
                            print(f"[DEBUG] Failed to create new transcript: {exc!r}", file=sys.stderr)

                    # Reset the history with just the compressed summary
                    history = [DebateTurn(speaker=responder.name, text=compressed_summary)]
                    print(f"[DEBUG] History reset with compressed summary", file=sys.stderr)

                    # Continue with the next round using the reset history
                    continue

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
