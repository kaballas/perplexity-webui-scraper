"""Debate agent classes that participate in the discussion."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .prompts import DebateTurn, format_history, HUGGING_DEBATER_PROMPT, PERPLEXITY_DEBATER_PROMPT, WRITER_DEBATER_PROMPT, ASK_QUESTIONS_DEBATER_PROMPT, ANSWER_QUESTIONS_DEBATER_PROMPT, INTEGRATION_EXPERT_DEBATER_PROMPT, FUNCTIONAL_SPEC_DEBATER_PROMPT, TECHNICAL_SPEC_DEBATER_PROMPT, CONFIGURATION_AGENT_PROMPT, DATA_MIGRATION_AGENT_PROMPT, REPORTING_AGENT_PROMPT, SECURITY_AGENT_PROMPT, TESTING_AGENT_PROMPT, CHANGE_MGMT_AGENT_PROMPT, MONITORING_AGENT_PROMPT, LEARNING_AGENT_PROMPT, METADATA_EXTRACT_AGENT_PROMPT, INTERNET_RESEARCH_AGENT_PROMPT, CRITIQUE_AGENT_PROMPT, COMPRESSION_AGENT_PROMPT, TODO_AGENT_PROMPT, MR_PROMPT_BUILDER_AGENT_PROMPT
from .clients import HuggingFaceClient, PerplexityClient


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
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("Hugging", "defend the proposition", "a pragmatic solution architect")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = HUGGING_DEBATER_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: SOLUTION_ARCHITECT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] HuggingDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] HuggingDebater.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class PerplexityDebater(DebateAgent):
    def __init__(self, client: PerplexityClient) -> None:
        super().__init__("Perplexity", "challenge the proposition", "an investigative strategist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = PERPLEXITY_DEBATER_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: FACT_CHECK prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] PerplexityDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        return self._client.call_api(prompt)


class WriterDebater(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("Writer", "synthesize and summarize", "a technical writer")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = WRITER_DEBATER_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: TECHNICAL_WRITER prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] WriterDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] WriterDebater.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class AskQuestionsDebater(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("AskQuestions", "ask clarifying questions", "a curious inquirer")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = ASK_QUESTIONS_DEBATER_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: ASK_QUESTIONS prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] AskQuestionsDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] AskQuestionsDebater.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class AnswerQuestionsDebater(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("AnswerQuestions", "answer questions", "a knowledgeable responder")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = ANSWER_QUESTIONS_DEBATER_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: ANSWER_QUESTIONS prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] AnswerQuestionsDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] AnswerQuestionsDebater.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class IntegrationExpertDebater(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("IntegrationExpert", "provide integration architecture expertise", "a senior SAP Integration Architect")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = INTEGRATION_EXPERT_DEBATER_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: INTEGRATION_EXPERT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] IntegrationExpertDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] IntegrationExpertDebater.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class FunctionalSpecDebater(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("FunctionalSpec", "provide functional specifications", "a senior SAP Functional Analyst")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = FUNCTIONAL_SPEC_DEBATER_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: FUNCTIONAL_SPEC prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] FunctionalSpecDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] FunctionalSpecDebater.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class TechnicalSpecDebater(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("TechnicalSpec", "provide technical specifications", "a senior SAP Technical Architect")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = TECHNICAL_SPEC_DEBATER_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: TECHNICAL_SPEC prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] TechnicalSpecDebater.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] TechnicalSpecDebater.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class ConfigurationAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("Configuration", "handle module configuration", "a senior SAP SuccessFactors Configuration Specialist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = CONFIGURATION_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: CONFIGURATION_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] ConfigurationAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] ConfigurationAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class DataMigrationAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("DataMigration", "handle data migration processes", "a senior SAP SuccessFactors Data Migration Specialist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = DATA_MIGRATION_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: DATA_MIGRATION_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] DataMigrationAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] DataMigrationAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class ReportingAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("Reporting", "build and optimize reports", "a senior SAP SuccessFactors Reporting Analyst")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = REPORTING_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: REPORTING_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] ReportingAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] ReportingAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class SecurityAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("Security", "manage security and access", "a senior SAP SuccessFactors Security Architect")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = SECURITY_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: SECURITY_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] SecurityAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] SecurityAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class TestingAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("Testing", "automate and manage testing processes", "a senior SAP SuccessFactors Quality Assurance Engineer")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = TESTING_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: TESTING_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] TestingAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] TestingAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class ChangeMgmtAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("ChangeMgmt", "manage release and change processes", "a senior SAP SuccessFactors Change Management Specialist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = CHANGE_MGMT_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: CHANGE_MGMT_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] ChangeMgmtAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] ChangeMgmtAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class MonitoringAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("Monitoring", "monitor system health and performance", "a senior SAP SuccessFactors System Monitoring Specialist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = MONITORING_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: MONITORING_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] MonitoringAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] MonitoringAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class LearningAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("Learning", "manage Learning Management System", "a senior SAP SuccessFactors Learning Management Specialist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = LEARNING_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: LEARNING_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] LearningAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] LearningAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class MetadataExtractAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("MetadataExtract", "extract and analyze system metadata", "a senior SAP SuccessFactors Metadata Extraction Specialist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = METADATA_EXTRACT_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: METADATA_EXTRACT_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] MetadataExtractAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] MetadataExtractAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        response = self._client.call_api(prompt)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        meta_dir = Path("meta")
        try:
            meta_dir.mkdir(parents=True, exist_ok=True)
            file_path = meta_dir / f"metadataextract_{timestamp}.txt"
            with file_path.open("w", encoding="utf-8") as fh:
                fh.write(response)
        except Exception as exc:
            print(f"[DEBUG] MetadataExtractAgent.respond: failed to save response: {exc!r}", file=sys.stderr)

        return response


class InternetResearchAgent(DebateAgent):
    def __init__(self, client) -> None:  # Using generic client type as this can use either Perplexity or HuggingFace
        super().__init__("InternetResearch", "conduct internet research", "an internet research specialist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = INTERNET_RESEARCH_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: INTERNET_RESEARCH_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] InternetResearchAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        return self._client.call_api(prompt)


class CritiqueAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("Critique", "perform quality assurance review", "a senior SAP Quality Assurance Specialist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = CRITIQUE_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: CRITIQUE_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] CritiqueAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] CritiqueAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)


class CompressionAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("Compression", "summarize conversation history", "a conversation compression specialist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = COMPRESSION_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: COMPRESSION_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] CompressionAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] CompressionAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        response = self._client.call_api(prompt)

        # Check if this is a request to compress and reset the conversation
        if "RESET_CONVERSATION" in response.upper():
            print(f"[DEBUG] CompressionAgent.respond: detected RESET_CONVERSATION request", file=sys.stderr)
            # Extract the compressed summary and indicate reset is needed
            # For now, we'll just return the response as-is and let the core logic handle the reset
            pass

        return response


class TodoAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("Todo", "generate todo lists from discussions", "a task management specialist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = TODO_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: TODO_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] TodoAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] TodoAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)

        response = self._client.call_api(prompt)
        print(f"[DEBUG] TodoAgent.respond: response received, length={len(response)}", file=sys.stderr)

        return response


class MrPromptBuilderAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("MrPromptBuilder", "craft and optimize prompts for various use cases", "a senior prompt engineering specialist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = MR_PROMPT_BUILDER_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: MR_PROMPT_BUILDER_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] MrPromptBuilderAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] MrPromptBuilderAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)
