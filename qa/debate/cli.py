"""CLI interface for the debate orchestrator."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv

from .core import run_debate
from .agents import HuggingDebater, PerplexityDebater, WriterDebater, AskQuestionsDebater, AnswerQuestionsDebater, IntegrationExpertDebater, FunctionalSpecDebater, TechnicalSpecDebater, ConfigurationAgent, DataMigrationAgent, ReportingAgent, SecurityAgent, TestingAgent, ChangeMgmtAgent, MonitoringAgent, LearningAgent, MetadataExtractAgent, InternetResearchAgent, CritiqueAgent, CompressionAgent, TodoAgent, MrPromptBuilderAgent
from .clients import HuggingFaceClient, PerplexityClient, ApiConfig


def build_hugging_config(args: argparse.Namespace) -> ApiConfig:
    print("[DEBUG] build_hugging_config: checking token", file=sys.stderr)
    from generate_wricef_prompts import ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
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
    client = PerplexityClient(session_token=session_token)
    return PerplexityDebater(client)


def build_writer_agent(args: argparse.Namespace) -> WriterDebater:
    print("[DEBUG] build_writer_agent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
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
    client = HuggingFaceClient(config=config)
    return WriterDebater(client)


def build_askquestions_agent(args: argparse.Namespace) -> AskQuestionsDebater:
    print("[DEBUG] build_askquestions_agent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
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
    client = HuggingFaceClient(config=config)
    return AskQuestionsDebater(client)


def build_answerquestions_agent(args: argparse.Namespace) -> AnswerQuestionsDebater:
    print("[DEBUG] build_answerquestions_agent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
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
    client = HuggingFaceClient(config=config)
    return AnswerQuestionsDebater(client)


def build_integrationexpert_agent(args: argparse.Namespace) -> IntegrationExpertDebater:
    print("[DEBUG] build_integrationexpert_agent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.integrationexpert_token or os.getenv("INTEGRATIONEXPERT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"IntegrationExpert API token required. Provide --integrationexpert-token or set INTEGRATIONEXPERT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for integrationexpert-specific URL in environment
    url = args.integrationexpert_url or os.getenv("INTEGRATIONEXPERT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for integrationexpert-specific model in environment
    model = args.integrationexpert_model or os.getenv("INTEGRATIONEXPERT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_integrationexpert_agent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.integrationexpert_temperature,
        timeout=args.integrationexpert_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_integrationexpert_agent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return IntegrationExpertDebater(client)


def build_functionalspec_agent(args: argparse.Namespace) -> FunctionalSpecDebater:
    print("[DEBUG] build_functionalspec_agent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.functionalspec_token or os.getenv("FUNCTIONALSPEC_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"FunctionalSpec API token required. Provide --functionalspec-token or set FUNCTIONALSPEC_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for functionalspec-specific URL in environment
    url = args.functionalspec_url or os.getenv("FUNCTIONALSPEC_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for functionalspec-specific model in environment
    model = args.functionalspec_model or os.getenv("FUNCTIONALSPEC_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_functionalspec_agent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.functionalspec_temperature,
        timeout=args.functionalspec_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_functionalspec_agent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return FunctionalSpecDebater(client)


def build_technicalspec_agent(args: argparse.Namespace) -> TechnicalSpecDebater:
    print("[DEBUG] build_technicalspec_agent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.technicalspec_token or os.getenv("TECHNICALSPEC_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"TechnicalSpec API token required. Provide --technicalspec-token or set TECHNICALSPEC_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for technicalspec-specific URL in environment
    url = args.technicalspec_url or os.getenv("TECHNICALSPEC_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for technicalspec-specific model in environment
    model = args.technicalspec_model or os.getenv("TECHNICALSPEC_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_technicalspec_agent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.technicalspec_temperature,
        timeout=args.technicalspec_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_technicalspec_agent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return TechnicalSpecDebater(client)


def build_configagent(args: argparse.Namespace) -> ConfigurationAgent:
    print("[DEBUG] build_configagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.configagent_token or os.getenv("CONFIGAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"Configuration API token required. Provide --configagent-token or set CONFIGAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for configagent-specific URL in environment
    url = args.configagent_url or os.getenv("CONFIGAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for configagent-specific model in environment
    model = args.configagent_model or os.getenv("CONFIGAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_configagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.configagent_temperature,
        timeout=args.configagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_configagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return ConfigurationAgent(client)


def build_datamigrationagent(args: argparse.Namespace) -> DataMigrationAgent:
    print("[DEBUG] build_datamigrationagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.datamigrationagent_token or os.getenv("DATAMIGRATIONAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"DataMigration API token required. Provide --datamigrationagent-token or set DATAMIGRATIONAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for datamigrationagent-specific URL in environment
    url = args.datamigrationagent_url or os.getenv("DATAMIGRATIONAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for datamigrationagent-specific model in environment
    model = args.datamigrationagent_model or os.getenv("DATAMIGRATIONAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_datamigrationagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.datamigrationagent_temperature,
        timeout=args.datamigrationagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_datamigrationagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return DataMigrationAgent(client)


def build_reportingagent(args: argparse.Namespace) -> ReportingAgent:
    print("[DEBUG] build_reportingagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.reportingagent_token or os.getenv("REPORTINGAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"Reporting API token required. Provide --reportingagent-token or set REPORTINGAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for reportingagent-specific URL in environment
    url = args.reportingagent_url or os.getenv("REPORTINGAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for reportingagent-specific model in environment
    model = args.reportingagent_model or os.getenv("REPORTINGAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_reportingagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.reportingagent_temperature,
        timeout=args.reportingagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_reportingagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return ReportingAgent(client)


def build_securityagent(args: argparse.Namespace) -> SecurityAgent:
    print("[DEBUG] build_securityagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.securityagent_token or os.getenv("SECURITYAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"Security API token required. Provide --securityagent-token or set SECURITYAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for securityagent-specific URL in environment
    url = args.securityagent_url or os.getenv("SECURITYAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for securityagent-specific model in environment
    model = args.securityagent_model or os.getenv("SECURITYAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_securityagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.securityagent_temperature,
        timeout=args.securityagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_securityagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return SecurityAgent(client)


def build_testingagent(args: argparse.Namespace) -> TestingAgent:
    print("[DEBUG] build_testingagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.testingagent_token or os.getenv("TESTINGAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"Testing API token required. Provide --testingagent-token or set TESTINGAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for testingagent-specific URL in environment
    url = args.testingagent_url or os.getenv("TESTINGAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for testingagent-specific model in environment
    model = args.testingagent_model or os.getenv("TESTINGAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_testingagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.testingagent_temperature,
        timeout=args.testingagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_testingagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return TestingAgent(client)


def build_changemgmtagent(args: argparse.Namespace) -> ChangeMgmtAgent:
    print("[DEBUG] build_changemgmtagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.changemgmtagent_token or os.getenv("CHANGEMGMTAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"ChangeMgmt API token required. Provide --changemgmtagent-token or set CHANGEMGMTAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for changemgmtagent-specific URL in environment
    url = args.changemgmtagent_url or os.getenv("CHANGEMGMTAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for changemgmtagent-specific model in environment
    model = args.changemgmtagent_model or os.getenv("CHANGEMGMTAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_changemgmtagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.changemgmtagent_temperature,
        timeout=args.changemgmtagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_changemgmtagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return ChangeMgmtAgent(client)


def build_monitoringagent(args: argparse.Namespace) -> MonitoringAgent:
    print("[DEBUG] build_monitoringagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.monitoringagent_token or os.getenv("MONITORINGAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"Monitoring API token required. Provide --monitoringagent-token or set MONITORINGAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for monitoringagent-specific URL in environment
    url = args.monitoringagent_url or os.getenv("MONITORINGAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for monitoringagent-specific model in environment
    model = args.monitoringagent_model or os.getenv("MONITORINGAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_monitoringagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.monitoringagent_temperature,
        timeout=args.monitoringagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_monitoringagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return MonitoringAgent(client)


def build_learningagent(args: argparse.Namespace) -> LearningAgent:
    print("[DEBUG] build_learningagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.learningagent_token or os.getenv("LEARNINGAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"Learning API token required. Provide --learningagent-token or set LEARNINGAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for learningagent-specific URL in environment
    url = args.learningagent_url or os.getenv("LEARNINGAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for learningagent-specific model in environment
    model = args.learningagent_model or os.getenv("LEARNINGAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_learningagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.learningagent_temperature,
        timeout=args.learningagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_learningagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return LearningAgent(client)


def build_metadataextractagent(args: argparse.Namespace) -> MetadataExtractAgent:
    print("[DEBUG] build_metadataextractagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.metadataextractagent_token or os.getenv("METADATAEXTRACTAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"MetadataExtract API token required. Provide --metadataextractagent-token or set METADATAEXTRACTAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for metadataextractagent-specific URL in environment
    url = args.metadataextractagent_url or os.getenv("METADATAEXTRACTAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for metadataextractagent-specific model in environment
    model = args.metadataextractagent_model or os.getenv("METADATAEXTRACTAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_metadataextractagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.metadataextractagent_temperature,
        timeout=args.metadataextractagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_metadataextractagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return MetadataExtractAgent(client)


def build_internetresearch_agent(args: argparse.Namespace) -> InternetResearchAgent:
    print("[DEBUG] build_internetresearch_agent: checking token", file=sys.stderr)
    # Check in order: command line argument, INTERNET_RESEARCH_TOKEN env, PERPLEXITY_SESSION_TOKEN env
    session_token = (
        args.internetresearch_token or
        os.getenv("INTERNET_RESEARCH_TOKEN", "") or
        os.getenv("PERPLEXITY_SESSION_TOKEN", "")
    ).strip()
    if not session_token:
        raise ValueError("InternetResearch Perplexity session token required. Provide --internetresearch-token or set INTERNET_RESEARCH_TOKEN or PERPLEXITY_SESSION_TOKEN.")
    print(f"[DEBUG] build_internetresearch_agent: token found, length={len(session_token)}", file=sys.stderr)
    client = PerplexityClient(session_token=session_token)
    return InternetResearchAgent(client)


def build_critiqueagent(args: argparse.Namespace) -> CritiqueAgent:
    print("[DEBUG] build_critiqueagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.critiqueagent_token or os.getenv("CRITIQUEAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"Critique API token required. Provide --critiqueagent-token or set CRITIQUEAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for critiqueagent-specific URL in environment
    url = args.critiqueagent_url or os.getenv("CRITIQUEAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for critiqueagent-specific model in environment
    model = args.critiqueagent_model or os.getenv("CRITIQUEAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_critiqueagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.critiqueagent_temperature,
        timeout=args.critiqueagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_critiqueagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return CritiqueAgent(client)


def build_compressionagent(args: argparse.Namespace) -> CompressionAgent:
    print("[DEBUG] build_compressionagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.compressionagent_token or os.getenv("COMPRESSIONAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"Compression API token required. Provide --compressionagent-token or set COMPRESSIONAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for compressionagent-specific URL in environment
    url = args.compressionagent_url or os.getenv("COMPRESSIONAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for compressionagent-specific model in environment
    model = args.compressionagent_model or os.getenv("COMPRESSIONAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_compressionagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.compressionagent_temperature,
        timeout=args.compressionagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_compressionagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return CompressionAgent(client)


def build_todoagent(args: argparse.Namespace) -> TodoAgent:
    print("[DEBUG] build_todoagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.todoagent_token or os.getenv("TODOAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"Todo API token required. Provide --todoagent-token or set TODOAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for todoagent-specific URL in environment
    url = args.todoagent_url or os.getenv("TODOAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for todoagent-specific model in environment
    model = args.todoagent_model or os.getenv("TODOAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_todoagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.todoagent_temperature,
        timeout=args.todoagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_todoagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return TodoAgent(client)


def build_mrpromptbuilderagent(args: argparse.Namespace) -> MrPromptBuilderAgent:
    print("[DEBUG] build_mrpromptbuilderagent: checking token", file=sys.stderr)
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        ENV_TOKEN_KEY as HUGGING_TOKEN_ENV
    )
    token = args.mrpromptbuilderagent_token or os.getenv("MRPROMPTBUILDERAGENT_TOKEN", "").strip() or os.getenv(HUGGING_TOKEN_ENV, "").strip()
    if not token:
        raise ValueError(
            f"MrPromptBuilder API token required. Provide --mrpromptbuilderagent-token or set MRPROMPTBUILDERAGENT_TOKEN or {HUGGING_TOKEN_ENV}."
        )

    # Check for mrpromptbuilderagent-specific URL in environment
    url = args.mrpromptbuilderagent_url or os.getenv("MRPROMPTBUILDERAGENT_API_URL", "").strip()
    if not url:
        # If no URL provided via argument or environment, fall back to default
        url = DEFAULT_HUGGING_URL

    # Check for mrpromptbuilderagent-specific model in environment
    model = args.mrpromptbuilderagent_model or os.getenv("MRPROMPTBUILDERAGENT_MODEL", "").strip() or DEFAULT_HUGGING_MODEL

    print(f"[DEBUG] build_mrpromptbuilderagent: token found, length={len(token)}", file=sys.stderr)
    config = ApiConfig(
        url=url,
        token=token,
        model=model,
        temperature=args.mrpromptbuilderagent_temperature,
        timeout=args.mrpromptbuilderagent_timeout,
        include_raw=False,
    )
    print(f"[DEBUG] build_mrpromptbuilderagent: created config (url={config.url}, model={config.model}, temp={config.temperature})", file=sys.stderr)
    client = HuggingFaceClient(config=config)
    return MrPromptBuilderAgent(client)


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
        default=80,
        help="Maximum number of turns (default: 80).",
    )
    parser.add_argument(
        "--first-speaker",
        choices=("hugging", "perplexity", "writer", "askquestions", "answerquestions", "integrationexpert", "functionalspec", "technicalspec", "config", "datamigration", "reporting", "security", "testing", "changemgmt", "monitoring", "learning", "metadataextract", "internetresearch", "critique", "compression", "todo"),
        default="hugging",
        help="Agent that speaks first (default: hugging).",
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        help="Path to save conversation transcript (.txt file). Default: transcripts/debate_TIMESTAMP.txt",
    )
    from generate_wricef_prompts import (
        DEFAULT_API_URL as DEFAULT_HUGGING_URL,
        DEFAULT_MODEL as DEFAULT_HUGGING_MODEL,
        DEFAULT_TEMPERATURE as DEFAULT_HUGGING_TEMPERATURE,
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
        default=300.0,
        help="Hugging API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--hugging-token",
        help=f"Hugging API token (overrides WRICEF_API_TOKEN).",
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
        help=f"Writer API model identifier (default: value from WRITER_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
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
        default=300.0,
        help="Writer API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--writer-token",
        help=f"Writer API token (overrides WRICEF_API_TOKEN).",
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
        default=300.0,
        help="AskQuestions API timeout in seconds (default: 300).",
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
        default=300.0,
        help="AnswerQuestions API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--answerquestions-token",
        help=f"AnswerQuestions API token (overrides ANSWERQUESTIONS_TOKEN).",
    )
    # IntegrationExpert agent configuration
    parser.add_argument(
        "--integrationexpert-url",
        default="",
        help=f"IntegrationExpert API endpoint (default: value from INTEGRATIONEXPERT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--integrationexpert-model",
        default="",
        help=f"IntegrationExpert API model identifier (default: value from INTEGRATIONEXPERT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--integrationexpert-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"IntegrationExpert API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--integrationexpert-timeout",
        type=float,
        default=300.0,
        help="IntegrationExpert API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--integrationexpert-token",
        help=f"IntegrationExpert API token (overrides INTEGRATIONEXPERT_TOKEN).",
    )
    # FunctionalSpec agent configuration
    parser.add_argument(
        "--functionalspec-url",
        default="",
        help=f"FunctionalSpec API endpoint (default: value from FUNCTIONALSPEC_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--functionalspec-model",
        default="",
        help=f"FunctionalSpec API model identifier (default: value from FUNCTIONALSPEC_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--functionalspec-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"FunctionalSpec API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--functionalspec-timeout",
        type=float,
        default=300.0,
        help="FunctionalSpec API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--functionalspec-token",
        help=f"FunctionalSpec API token (overrides FUNCTIONALSPEC_TOKEN).",
    )
    # TechnicalSpec agent configuration
    parser.add_argument(
        "--technicalspec-url",
        default="",
        help=f"TechnicalSpec API endpoint (default: value from TECHNICALSPEC_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--technicalspec-model",
        default="",
        help=f"TechnicalSpec API model identifier (default: value from TECHNICALSPEC_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--technicalspec-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"TechnicalSpec API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--technicalspec-timeout",
        type=float,
        default=300.0,
        help="TechnicalSpec API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--technicalspec-token",
        help=f"TechnicalSpec API token (overrides TECHNICALSPEC_TOKEN).",
    )
    # ConfigurationAgent configuration
    parser.add_argument(
        "--configagent-url",
        default="",
        help=f"Configuration API endpoint (default: value from CONFIGAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--configagent-model",
        default="",
        help=f"Configuration API model identifier (default: value from CONFIGAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--configagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"Configuration API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--configagent-timeout",
        type=float,
        default=300.0,
        help="Configuration API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--configagent-token",
        help=f"Configuration API token (overrides CONFIGAGENT_TOKEN).",
    )
    # DataMigrationAgent configuration
    parser.add_argument(
        "--datamigrationagent-url",
        default="",
        help=f"DataMigration API endpoint (default: value from DATAMIGRATIONAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--datamigrationagent-model",
        default="",
        help=f"DataMigration API model identifier (default: value from DATAMIGRATIONAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--datamigrationagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"DataMigration API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--datamigrationagent-timeout",
        type=float,
        default=300.0,
        help="DataMigration API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--datamigrationagent-token",
        help=f"DataMigration API token (overrides DATAMIGRATIONAGENT_TOKEN).",
    )
    # ReportingAgent configuration
    parser.add_argument(
        "--reportingagent-url",
        default="",
        help=f"Reporting API endpoint (default: value from REPORTINGAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--reportingagent-model",
        default="",
        help=f"Reporting API model identifier (default: value from REPORTINGAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--reportingagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"Reporting API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--reportingagent-timeout",
        type=float,
        default=300.0,
        help="Reporting API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--reportingagent-token",
        help=f"Reporting API token (overrides REPORTINGAGENT_TOKEN).",
    )
    # SecurityAgent configuration
    parser.add_argument(
        "--securityagent-url",
        default="",
        help=f"Security API endpoint (default: value from SECURITYAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--securityagent-model",
        default="",
        help=f"Security API model identifier (default: value from SECURITYAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--securityagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"Security API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--securityagent-timeout",
        type=float,
        default=300.0,
        help="Security API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--securityagent-token",
        help=f"Security API token (overrides SECURITYAGENT_TOKEN).",
    )
    # TestingAgent configuration
    parser.add_argument(
        "--testingagent-url",
        default="",
        help=f"Testing API endpoint (default: value from TESTINGAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--testingagent-model",
        default="",
        help=f"Testing API model identifier (default: value from TESTINGAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--testingagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"Testing API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--testingagent-timeout",
        type=float,
        default=300.0,
        help="Testing API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--testingagent-token",
        help=f"Testing API token (overrides TESTINGAGENT_TOKEN).",
    )
    # ChangeMgmtAgent configuration
    parser.add_argument(
        "--changemgmtagent-url",
        default="",
        help=f"ChangeMgmt API endpoint (default: value from CHANGEMGMTAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--changemgmtagent-model",
        default="",
        help=f"ChangeMgmt API model identifier (default: value from CHANGEMGMTAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--changemgmtagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"ChangeMgmt API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--changemgmtagent-timeout",
        type=float,
        default=300.0,
        help="ChangeMgmt API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--changemgmtagent-token",
        help=f"ChangeMgmt API token (overrides CHANGEMGMTAGENT_TOKEN).",
    )
    # MonitoringAgent configuration
    parser.add_argument(
        "--monitoringagent-url",
        default="",
        help=f"Monitoring API endpoint (default: value from MONITORINGAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--monitoringagent-model",
        default="",
        help=f"Monitoring API model identifier (default: value from MONITORINGAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--monitoringagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"Monitoring API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--monitoringagent-timeout",
        type=float,
        default=300.0,
        help="Monitoring API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--monitoringagent-token",
        help=f"Monitoring API token (overrides MONITORINGAGENT_TOKEN).",
    )
    # LearningAgent configuration
    parser.add_argument(
        "--learningagent-url",
        default="",
        help=f"Learning API endpoint (default: value from LEARNINGAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--learningagent-model",
        default="",
        help=f"Learning API model identifier (default: value from LEARNINGAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--learningagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"Learning API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--learningagent-timeout",
        type=float,
        default=300.0,
        help="Learning API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--learningagent-token",
        help=f"Learning API token (overrides LEARNINGAGENT_TOKEN).",
    )
    # MetadataExtractAgent configuration
    parser.add_argument(
        "--metadataextractagent-url",
        default="",
        help=f"MetadataExtract API endpoint (default: value from METADATAEXTRACTAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--metadataextractagent-model",
        default="",
        help=f"MetadataExtract API model identifier (default: value from METADATAEXTRACTAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--metadataextractagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"MetadataExtract API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--metadataextractagent-timeout",
        type=float,
        default=300.0,
        help="MetadataExtract API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--metadataextractagent-token",
        help=f"MetadataExtract API token (overrides METADATAEXTRACTAGENT_TOKEN).",
    )
    # InternetResearchAgent configuration
    parser.add_argument(
        "--internetresearch-token",
        help="InternetResearch Perplexity session token (overrides INTERNET_RESEARCH_TOKEN or PERPLEXITY_SESSION_TOKEN).",
    )
    # CritiqueAgent configuration
    parser.add_argument(
        "--critiqueagent-url",
        default="",
        help=f"Critique API endpoint (default: value from CRITIQUEAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--critiqueagent-model",
        default="",
        help=f"Critique API model identifier (default: value from CRITIQUEAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--critiqueagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"Critique API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--critiqueagent-timeout",
        type=float,
        default=300.0,
        help="Critique API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--critiqueagent-token",
        help=f"Critique API token (overrides CRITIQUEAGENT_TOKEN).",
    )
    # CompressionAgent configuration
    parser.add_argument(
        "--compressionagent-url",
        default="",
        help=f"Compression API endpoint (default: value from COMPRESSIONAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--compressionagent-model",
        default="",
        help=f"Compression API model identifier (default: value from COMPRESSIONAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--compressionagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"Compression API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--compressionagent-timeout",
        type=float,
        default=300.0,
        help="Compression API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--compressionagent-token",
        help=f"Compression API token (overrides COMPRESSIONAGENT_TOKEN).",
    )
    # TodoAgent configuration
    parser.add_argument(
        "--todoagent-url",
        default="",
        help=f"Todo API endpoint (default: value from TODOAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--todoagent-model",
        default="",
        help=f"Todo API model identifier (default: value from TODOAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--todoagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"Todo API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--todoagent-timeout",
        type=float,
        default=300.0,
        help="Todo API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--todoagent-token",
        help=f"Todo API token (overrides TODOAGENT_TOKEN).",
    )
    # MrPromptBuilderAgent configuration
    parser.add_argument(
        "--mrpromptbuilderagent-url",
        default="",
        help=f"MrPromptBuilder API endpoint (default: value from MRPROMPTBUILDERAGENT_API_URL environment variable, or {DEFAULT_HUGGING_URL} if not set).",
    )
    parser.add_argument(
        "--mrpromptbuilderagent-model",
        default="",
        help=f"MrPromptBuilder API model identifier (default: value from MRPROMPTBUILDERAGENT_MODEL environment variable, or {DEFAULT_HUGGING_MODEL} if not set).",
    )
    parser.add_argument(
        "--mrpromptbuilderagent-temperature",
        type=float,
        default=DEFAULT_HUGGING_TEMPERATURE,
        help=f"MrPromptBuilder API sampling temperature (default: {DEFAULT_HUGGING_TEMPERATURE}).",
    )
    parser.add_argument(
        "--mrpromptbuilderagent-timeout",
        type=float,
        default=300.0,
        help="MrPromptBuilder API timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--mrpromptbuilderagent-token",
        help=f"MrPromptBuilder API token (overrides MRPROMPTBUILDERAGENT_TOKEN).",
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
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        transcript_file = Path("transcripts") / f"debate_{timestamp}.txt"

    print(f"[DEBUG] main: transcript_file={transcript_file}", file=sys.stderr)

    print("[DEBUG] main: building Hugging config", file=sys.stderr)
    hugging_config = build_hugging_config(args)
    print("[DEBUG] main: building Perplexity agent", file=sys.stderr)
    perplexity_agent = build_perplexity_agent(args)
    print("[DEBUG] main: creating HuggingDebater", file=sys.stderr)
    hugging_agent = HuggingDebater(HuggingFaceClient(hugging_config))
    print("[DEBUG] main: creating WriterDebater", file=sys.stderr)
    writer_agent = build_writer_agent(args)
    print("[DEBUG] main: creating AskQuestionsDebater", file=sys.stderr)
    askquestions_agent = build_askquestions_agent(args)
    print("[DEBUG] main: creating AnswerQuestionsDebater", file=sys.stderr)
    answerquestions_agent = build_answerquestions_agent(args)
    print("[DEBUG] main: creating IntegrationExpertDebater", file=sys.stderr)
    integrationexpert_agent = build_integrationexpert_agent(args)
    print("[DEBUG] main: creating FunctionalSpecDebater", file=sys.stderr)
    functionalspec_agent = build_functionalspec_agent(args)
    print("[DEBUG] main: creating TechnicalSpecDebater", file=sys.stderr)
    technicalspec_agent = build_technicalspec_agent(args)
    print("[DEBUG] main: creating ConfigurationAgent", file=sys.stderr)
    configagent_agent = build_configagent(args)
    print("[DEBUG] main: creating DataMigrationAgent", file=sys.stderr)
    datamigrationagent_agent = build_datamigrationagent(args)
    print("[DEBUG] main: creating ReportingAgent", file=sys.stderr)
    reportingagent_agent = build_reportingagent(args)
    print("[DEBUG] main: creating SecurityAgent", file=sys.stderr)
    securityagent_agent = build_securityagent(args)
    print("[DEBUG] main: creating TestingAgent", file=sys.stderr)
    testingagent_agent = build_testingagent(args)
    print("[DEBUG] main: creating ChangeMgmtAgent", file=sys.stderr)
    changemgmtagent_agent = build_changemgmtagent(args)
    print("[DEBUG] main: creating MonitoringAgent", file=sys.stderr)
    monitoringagent_agent = build_monitoringagent(args)
    print("[DEBUG] main: creating LearningAgent", file=sys.stderr)
    learningagent_agent = build_learningagent(args)
    print("[DEBUG] main: creating MetadataExtractAgent", file=sys.stderr)
    metadataextractagent_agent = build_metadataextractagent(args)
    print("[DEBUG] main: creating InternetResearchAgent", file=sys.stderr)
    internetresearch_agent = build_internetresearch_agent(args)
    print("[DEBUG] main: creating CritiqueAgent", file=sys.stderr)
    critiqueagent_agent = build_critiqueagent(args)
    print("[DEBUG] main: creating CompressionAgent", file=sys.stderr)
    compressionagent_agent = build_compressionagent(args)
    print("[DEBUG] main: creating TodoAgent", file=sys.stderr)
    todoagent_agent = build_todoagent(args)
    print("[DEBUG] main: creating MrPromptBuilderAgent", file=sys.stderr)
    mrpromptbuilderagent_agent = build_mrpromptbuilderagent(args)

    print("[DEBUG] main: starting debate", file=sys.stderr)
    return run_debate(
        topic,
        hugging_agent,
        perplexity_agent,
        writer_agent,
        askquestions_agent,
        answerquestions_agent,
        integrationexpert_agent,
        functionalspec_agent,
        technicalspec_agent,
        configagent_agent,
        datamigrationagent_agent,
        reportingagent_agent,
        securityagent_agent,
        testingagent_agent,
        changemgmtagent_agent,
        monitoringagent_agent,
        learningagent_agent,
        metadataextractagent_agent,
        internetresearch_agent,
        critiqueagent_agent,
        compressionagent_agent,
        todoagent_agent,
        mrpromptbuilderagent_agent,
        max_rounds=max(1, args.max_rounds),
        first_speaker=args.first_speaker,
        transcript_file=transcript_file,
    )
