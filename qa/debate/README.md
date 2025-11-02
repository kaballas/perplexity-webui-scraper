# SAP SuccessFactors Debate Orchestrator

A sophisticated multi-agent conversation platform designed for SAP SuccessFactors implementation discussions, quality assurance, research, and documentation. This tool enables structured debates between specialized AI agents, each with distinct expertise in different aspects of SAP SuccessFactors.

## Overview

The Debate Orchestrator facilitates intelligent discussions among 22 specialized agents, allowing for comprehensive analysis, design, implementation, and validation of SAP SuccessFactors solutions. Each agent brings unique capabilities to address different aspects of enterprise HR system implementation.

## Available Agents

### Core Architecture Agents
1. **Hugging** - Solution Architect: Designs comprehensive SuccessFactors solutions
2. **Perplexity** - Fact Checker: Validates information accuracy using web research
3. **Writer** - Technical Writer: Documents solutions and creates formal specifications
4. **IntegrationExpert** - Integration Architect: Designs system integrations and data flows

### Specification & Design Agents
5. **FunctionalSpec** - Functional Analyst: Creates detailed functional specifications
6. **TechnicalSpec** - Technical Architect: Develops technical architecture and design
7. **Configuration** - Configuration Specialist: Handles system configuration and setup
8. **DataMigration** - Data Migration Specialist: Plans and executes data migration strategies

### Specialized Domain Agents
9. **Reporting** - Reporting Analyst: Designs reports and analytics solutions
10. **Security** - Security Architect: Implements security frameworks and access controls
11. **Testing** - QA Engineer: Develops test strategies and validates implementations
12. **ChangeMgmt** - Change Management Specialist: Manages system updates and releases
13. **Monitoring** - System Monitor: Implements monitoring and alerting solutions
14. **Learning** - Learning Management Specialist: Designs learning solutions
15. **MetadataExtract** - Metadata Specialist: Extracts and analyzes system metadata
16. **InternetResearch** - Research Specialist: Conducts web research using Perplexity

### Quality Assurance Agents

17. **AskQuestions** - Curious Inquirer: Asks clarifying questions about requirements
18. **AnswerQuestions** - Knowledgeable Responder: Provides detailed answers to technical questions
19. **Critique** - Quality Assurance Specialist: Reviews deliverables for compliance and quality
20. **Compression** - Conversation Manager: Summarizes long conversations and manages context
21. **Todo** - Task Management Specialist: Generates todo lists from discussion content

### Prompt Engineering Agent

22. **MrPromptBuilder** - Prompt Engineering Specialist: Crafts and optimizes prompts for various AI systems and use cases

### Agent Descriptions

#### Todo Agent (New!)
The TodoAgent is a specialized task management agent that analyzes conversation transcripts to generate structured todo lists. Its key responsibilities include:

- **Action Item Extraction**: Identifying all actionable items, tasks, and follow-ups from conversation transcripts
- **Task Categorization**: Organizing tasks by priority, complexity, and domain expertise
- **SMART Task Creation**: Creating Specific, Measurable, Achievable, Relevant, and Time-bound task descriptions
- **Dependency Mapping**: Identifying and documenting task dependencies and sequences
- **Resource Allocation**: Assigning appropriate ownership and resource requirements to tasks
- **Effort Estimation**: Estimating effort levels (small, medium, large) for each task
- **Missing Information Identification**: Highlighting any missing information needed to complete tasks

The TodoAgent outputs structured JSON todo lists with:
- Unique task identifiers
- Clear task titles and detailed descriptions
- Priority levels (high, medium, low)
- Assigned owners or roles
- Effort estimates
- Current status (pending, in_progress, completed)
- Dependencies on other tasks
- Due dates or time references
- Additional notes and context

This agent is particularly useful for converting brainstorming sessions, design discussions, and implementation planning meetings into actionable work items.

## Key Features

### Multi-Agent Conversations
- Interactive selection of agents for each conversation round
- Configurable conversation flow and participant order
- Support for extended discussions with automatic continuation prompts
- User feedback injection at any conversation point

### Specialized Expertise
- Each agent has domain-specific knowledge and responsibilities
- Agents maintain consistent personas and response styles
- Context-aware responses based on conversation history
- Cross-agent collaboration for comprehensive solution development

### Advanced Configuration
- Per-agent API endpoints, models, and parameters
- Environment variable support for secure credential management
- Customizable temperature, timeout, and token settings
- Flexible output formatting and transcript generation

### Quality Assurance
- Built-in critique and review capabilities
- Compliance checking against SAP best practices
- Automated validation of technical specifications
- Consistency checks across conversation rounds

### Conversation Management
- Automatic transcript generation with timestamps
- Conversation compression for efficient context management
- Smart reset functionality for long discussions
- Resume support for interrupted conversations

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd perplexity-webui-scraper/qa

# Ensure dependencies are installed
pip install -r requirements.txt
```

## Quick Start

```bash
# Basic usage - start a debate with default settings
python -m debate "Discuss the implementation of SuccessFactors Employee Central for a mid-sized organization"

# Specify a topic file
python -m debate --topic-file my_topic.txt
python -m debate --topic-file "C:\DTT\work\perplexity-webui-scraper\qa\pplx_harness\test.txt"
# Choose the first speaker
python -m debate --first-speaker integrationexpert "Design an integration between SuccessFactors and SAP S/4HANA"
```

## Configuration

### Environment Variables

Set these environment variables for default configuration:

```bash
# API Tokens (required for respective services)
WRICEF_API_TOKEN=your_huggingface_token
PERPLEXITY_SESSION_TOKEN=your_perplexity_token

# Optional API Endpoints (override defaults)
HUGGING_API_URL=https://your-custom-endpoint.com/api/v1/chat/completions
PERPLEXITY_API_URL=https://your-perplexity-endpoint.com/api/v1/chat/completions
```

### Command Line Options

```bash
# View all available options
python -m debate --help

# Set maximum conversation rounds
python -m debate --max-rounds 10 "Your topic here"

# Configure specific agent parameters
python -m debate \
  --hugging-model gpt-4 \
  --hugging-temperature 0.7 \
  --hugging-timeout 300 \
  "Configure Employee Central for healthcare industry"
```

## Advanced Usage

### Extended Conversations

The orchestrator supports multi-round conversations with user interaction:

1. Each round presents available agents for selection
2. Users can provide feedback that gets injected into the conversation
3. Conversations automatically continue until an agent responds with "STOP"
4. Transcripts are saved for future reference

### Agent Selection Strategies

Agents can be selected manually or programmatically:

```bash
# Manual selection (default)
python -m debate "Your topic"

# Pre-select first speaker
python -m debate --first-speaker technicalspec "Design a compensation model"

# Use specific agents for different aspects
python -m debate --first-speaker functionalspec \
  "Create functional specs for performance management"
```

### Conversation Management

Long conversations can be managed using the Compression agent:

1. **Automatic Summarization**: Compression agent periodically summarizes conversation history
2. **Smart Reset**: Trigger conversation reset when discussions become too complex
3. **Context Preservation**: Maintain key points while reducing token usage
4. **New Session Creation**: Start fresh conversations with compressed context

### Quality Assurance Workflow

Use the Critique agent for peer review and quality assurance:

1. **Specification Review**: Validate functional and technical specifications
2. **Compliance Checking**: Ensure SAP best practices adherence
3. **Risk Assessment**: Identify potential implementation risks
4. **Improvement Suggestions**: Provide actionable recommendations

## Agent-Specific Capabilities

### IntegrationExpert
Specializes in designing integrations between SuccessFactors and other systems:
- SAP S/4HANA, Oracle, Workday integrations
- REST/SOAP API design and governance
- Data mapping and transformation strategies
- Error handling and retry mechanisms

### FunctionalSpec
Creates detailed functional specifications:
- Business requirement analysis
- Process flow documentation
- User story development
- Acceptance criteria definition

### TechnicalSpec
Develops technical architecture:
- System design patterns
- Database schema design
- API specification development
- Performance optimization strategies

### Configuration
Handles system setup and customization:
- Field configuration and validation
- Workflow design and implementation
- Picklist management
- Role-based permission setup

### DataMigration
Plans and executes data strategies:
- Legacy system data extraction
- Data cleansing and transformation
- Migration sequence planning
- Validation and reconciliation

### Critique
Provides quality assurance and review:
- Specification validation
- Best practice compliance
- Risk assessment
- Improvement recommendations

### Compression
Manages conversation context:
- Intelligent summarization
- Conversation reset triggers
- Context preservation
- Efficient token usage
- Automatic reset functionality for long discussions

The Compression agent can automatically detect when a conversation has become too long or complex and trigger a reset. When this happens:
- A new conversation file is created with a timestamp-based name
- The compressed summary becomes the first message in the new conversation
- The original conversation is preserved with reset information
- The debate continues seamlessly with the reset context

### MetadataExtract
Specializes in extracting and analyzing system metadata from SAP SuccessFactors:
- OData API metadata extraction
- Employee Central data model analysis
- MDF (Master Data Framework) object definitions
- Foundation object relationships
- Picklist metadata and values
- Field definitions and properties
- Workforce Schema API extraction
- Configuration and security metadata
- Integration mapping information
- Report and dashboard metadata

The MetadataExtract agent helps with system documentation, migration planning, and integration design by providing detailed metadata analysis.

### InternetResearch
Conducts comprehensive web research using Perplexity to gather current, accurate information:
- Researches current trends and developments in SAP SuccessFactors
- Fact-checks technical information with credible sources
- Synthesizes information from multiple web sources
- Identifies authoritative references and documentation
- Validates claims with evidence from reliable sources
- Evaluates source reliability and identifies bias
- Extracts key insights from research findings
- Provides comprehensive analysis with citations

The InternetResearch agent enhances the debate with up-to-date information and verified facts from the web.

### AskQuestions
Asks clarifying questions to deepen understanding of topics and requirements:
- Asks specific, relevant questions based on the topic and current discussion
- Identifies gaps in knowledge and areas needing clarification
- Requests additional details and examples to better understand concepts
- Challenges assumptions in a constructive way
- Helps other agents think more deeply about the subject
- Facilitates comprehensive exploration of complex topics
- Encourages detailed elaboration on technical aspects
- Promotes collaborative problem-solving

The AskQuestions agent ensures thorough exploration of topics by identifying knowledge gaps.

### AnswerQuestions
Provides clear, accurate answers to questions raised in the debate:
- Answers specific questions asked in the discussion with detailed responses
- Draws from provided context and relevant background knowledge
- Clarifies technical concepts with specific examples when possible
- Addresses concerns raised by other agents with substantive responses
- Supports answers with logical reasoning and evidence where applicable
- Ensures responses are comprehensive and actionable
- Maintains technical accuracy and relevance
- Provides clear explanations for complex concepts

The AnswerQuestions agent ensures that specific queries receive detailed, accurate responses.

### Reporting
Designs reports and analytics solutions for SAP SuccessFactors implementations:
- Builds Ad Hoc, Canvas, and People Analytics reports
- Optimizes data models for operational and strategic HR reporting
- Designs report layouts and visualization approaches
- Structures data for meaningful analytics presentation
- Ensures reports meet business requirements and KPIs
- Aligns reporting solutions with organizational needs
- Validates data accuracy and completeness in reports
- Recommends appropriate reporting tools and techniques

The Reporting agent specializes in creating effective reporting and analytics solutions.

### Security
Manages Role-Based Permissions (RBP), group hierarchies, and data privacy compliance:
- Designs and implements security architectures for SAP SuccessFactors
- Manages Role-Based Permissions (RBP) and permission groups
- Creates and maintains group hierarchies and security structures
- Ensures data privacy compliance with regulations (GDPR, etc.)
- Detects and corrects conflicting roles and permissions
- Implements access control mechanisms and segregation of duties
- Validates security configurations and identifies vulnerabilities
- Recommends security best practices and improvements

The Security agent ensures robust security implementation and compliance.

### Testing
Automates regression, UAT, and integration testing across modules:
- Designs comprehensive test scenarios for all SuccessFactors modules
- Automates regression, UAT, and integration testing processes
- Validates workflow logic, data mappings, and UI changes
- Creates test scripts and execution frameworks
- Ensures test coverage for all functional areas
- Identifies and documents defects and issues
- Recommends testing improvements and best practices
- Validates fixes and verifies test results

The Testing agent ensures quality through comprehensive testing strategies.

### ChangeMgmt
Oversees release management, change control, and communication planning:
- Manages quarterly SAP SuccessFactors release implementations
- Coordinates change control processes and approvals
- Plans and executes communication strategies for changes
- Ensures stakeholder readiness for system updates
- Manages risk assessment and mitigation strategies
- Oversees go-live activities and post-release support
- Coordinates environment promotion and deployment
- Ensures business continuity during transitions

The ChangeMgmt agent ensures smooth transitions and effective change management.

### Monitoring
Continuously checks integration logs, API calls, and event center queues:
- Monitors integration logs and API call performance
- Tracks event center queues for failures or performance issues
- Implements system health and performance monitoring
- Sets up alerting mechanisms for critical issues
- Analyzes system metrics and identifies anomalies
- Recommends monitoring improvements and optimizations
- Ensures system reliability and uptime
- Provides troubleshooting guidance for issues

The Monitoring agent ensures system stability and performance through continuous monitoring.

### Learning
Focuses on SuccessFactors Learning (LMS) administration and course management:
- Manages SuccessFactors Learning (LMS) administration
- Designs course structures and learning catalogs
- Synchronizes content and manages catalog updates
- Configures learning programs and enrollment rules
- Ensures learning content effectiveness and quality
- Monitors learning metrics and completion rates
- Integrates learning with other SuccessFactors modules
- Recommends learning management improvements

The Learning agent specializes in effective learning management system implementation.

## Transcript Management

All conversations are automatically saved to transcript files:

```
transcripts/
├── debate_20251018_142646.txt     # Original conversation
├── debate_reset_20251018_153045.txt # Reset conversation
└── debate_reset_20251018_164522.txt # Additional resets
```

Features:
- Timestamp-based naming for easy identification
- Structured formatting with clear round indicators
- Speaker attribution for each contribution
- User feedback preservation
- Automatic saving with minimal performance impact

## Best Practices

### For Effective Conversations
1. **Clear Objectives**: Define specific goals for each conversation
2. **Right Agent Selection**: Match agents to conversation phases
3. **Progressive Detailing**: Start broad, then dive into specifics
4. **Regular Reviews**: Use Critique agent for quality checkpoints
5. **Context Management**: Leverage Compression for long discussions

### For Technical Documentation
1. **Collaborative Authoring**: Use Writer agent with specification agents
2. **Version Control**: Maintain transcript history for audit trails
3. **Cross-Referencing**: Link related conversations and documents
4. **Standard Compliance**: Ensure all outputs follow SAP guidelines
5. **Peer Review**: Incorporate critique feedback cycles

## Troubleshooting

### Common Issues

1. **API Timeout Errors**
   - Increase timeout values: `--hugging-timeout 600`
   - Check network connectivity
   - Verify API endpoint availability

2. **Authentication Failures**
   - Confirm API tokens are set in environment variables
   - Check token validity and permissions
   - Verify endpoint URLs are correct

3. **Agent Response Issues**
   - Adjust temperature settings for creativity vs. precision
   - Try different models for varied response styles
   - Provide more specific prompts or context

### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Enable debug logging
export DEBUG=1
python -m debate "Your topic"
```

This will show:
- API request/response details
- Prompt construction information
- Agent selection process
- Configuration resolution
- Error diagnostics

## Development

### Package Structure

```
debate/
├── __init__.py          # Package initialization
├── __main__.py          # Main entry point
├── agents.py           # Agent implementations
├── cli.py              # Command-line interface
├── clients.py          # API client implementations
├── core.py             # Core debate orchestration
├── prompts.py         # Agent prompt templates
└── README.md           # This documentation
```

### Extending Functionality

#### Adding New Agents to the Framework

Follow these steps to add a new agent to the debate framework:

##### Step 1: Define the Agent Prompt in `prompts.py`

Add a new prompt constant at the end of `prompts.py`:

```python
YOUR_AGENT_NAME_PROMPT = """You are [role description], a senior [expertise area] with expertise in [domain]. Your expertise covers:

**Core Competencies:**
- [Competency 1]
- [Competency 2]
- [Competency 3]

**Responsibilities:**
1. [Responsibility 1]
2. [Responsibility 2]

**Output Format:**
[Describe expected output format]

Conversation Context:
{{topic}}

Discussion Transcript:
{{conversation}}

[Specific instruction for the agent's response]"""
```

**Tips:**

- Use descriptive constant names in UPPER_SNAKE_CASE ending with `_PROMPT`
- Include `{{topic}}` and `{{conversation}}` placeholders for dynamic content
- Structure the prompt with clear sections (competencies, responsibilities, output format)
- Be specific about the agent's role and expertise boundaries
- Define clear output expectations and formats

##### Step 2: Import the Prompt in `agents.py`

Add your new prompt to the import statement at the top of `agents.py`:

```python
from .prompts import (
    DebateTurn, 
    format_history, 
    HUGGING_DEBATER_PROMPT,
    # ... other prompts ...
    YOUR_AGENT_NAME_PROMPT  # Add your prompt here
)
```

##### Step 3: Create the Agent Class in `agents.py`

Add a new agent class at the end of `agents.py`:

```python
class YourAgentName(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__(
            "YourAgentName",  # Short identifier (used in logs and output)
            "brief stance description",  # Agent's approach/stance
            "a senior [role description]"  # Persona description
        )
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = YOUR_AGENT_NAME_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: YOUR_AGENT_NAME prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] YourAgentName.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] YourAgentName.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)
```

**Important Notes:**

- Inherit from `DebateAgent` base class
- Accept appropriate client type (usually `HuggingFaceClient` or `PerplexityClient`)
- Use consistent naming: class name should match the prompt name
- Include debug print statements for troubleshooting
- Follow the established pattern for `_build_prompt()` and `respond()` methods

##### Step 4: Register the Agent in CLI (Optional)

If you want the agent to be directly accessible via command-line options, add it to `cli.py`:

1. Add a CLI argument in the argument parser:

```python
parser.add_argument('--your-agent', action='store_true',
                   help='Use YourAgentName agent')
```

2. Add agent instantiation logic in the agent selection code

3. Update the agent selection menu to include the new agent

##### Step 5: Verify the Agent

Test your new agent to ensure it works correctly:

```bash
# Test import
python -c "from debate.prompts import YOUR_AGENT_NAME_PROMPT; print('Prompt imported successfully')"

# Test agent class
python -c "from debate.agents import YourAgentName; print('Agent class imported successfully')"

# Test in conversation (if registered in CLI)
python -m debate "Test topic for new agent" --your-agent
```

##### Step 6: Update Documentation

1. **Add to Agent List**: Update the "Available Agents" section in this README
2. **Add Description**: Include a detailed description of the agent's capabilities
3. **Update Count**: Increment the total agent count in the Overview section

##### Complete Example: Adding a "Code Review Agent"

**In `prompts.py`:**

```python
CODE_REVIEW_AGENT_PROMPT = """You are a senior code review specialist with expertise in identifying code quality issues, security vulnerabilities, and best practice violations. Your expertise covers:

**Core Competencies:**
- Static code analysis and quality assessment
- Security vulnerability identification
- Performance optimization recommendations
- Code maintainability and readability analysis

**Responsibilities:**
1. Review code for bugs, security issues, and anti-patterns
2. Suggest improvements for code quality and maintainability
3. Ensure adherence to coding standards and best practices
4. Identify performance bottlenecks and optimization opportunities

**Output Format:**
Provide structured feedback with:
- Issue severity (critical, high, medium, low)
- Line numbers or code sections affected
- Clear explanation of the issue
- Recommended fix or improvement
- Best practice references

Conversation Context:
{{topic}}

Discussion Transcript:
{{conversation}}

Perform a thorough code review and provide actionable feedback."""
```

**In `agents.py`:**

```python
# Add to imports
from .prompts import CODE_REVIEW_AGENT_PROMPT

# Add agent class
class CodeReviewAgent(DebateAgent):
    def __init__(self, client: HuggingFaceClient) -> None:
        super().__init__("CodeReview", "review code quality and security", "a senior code review specialist")
        self._client = client

    def _build_prompt(self, topic: str, history: Sequence[DebateTurn], opponent: "DebateAgent") -> str:
        conversation = format_history(history)
        prompt = CODE_REVIEW_AGENT_PROMPT.format(topic=topic, conversation=conversation)
        print(f"[DEBUG] {self.name}._build_prompt: CODE_REVIEW_AGENT prompt, length={len(prompt)}, history_turns={len(history)}", file=sys.stderr)
        return prompt

    def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
        print(f"[DEBUG] CodeReviewAgent.respond: building prompt", file=sys.stderr)
        prompt = self._build_prompt(topic, history, opponent)
        print(f"[DEBUG] CodeReviewAgent.respond: calling API with client config (URL: {self._client.config.url}, Model: {self._client.config.model})", file=sys.stderr)
        return self._client.call_api(prompt)
```

##### Best Practices for Agent Design

1. **Single Responsibility**: Each agent should have a clear, focused purpose
2. **Domain Expertise**: Define specific knowledge areas and competencies
3. **Clear Output Format**: Specify how the agent should structure responses
4. **Context Awareness**: Ensure prompts leverage conversation history effectively
5. **Consistent Naming**: Use descriptive names that reflect the agent's role
6. **Comprehensive Prompts**: Include enough detail for consistent, high-quality responses
7. **Error Handling**: Consider edge cases and unusual inputs
8. **Token Efficiency**: Balance detail with conciseness to manage token usage

##### Advanced Customization

**Using Different API Clients:**

```python
# For agents that need web search (Perplexity)
class YourResearchAgent(DebateAgent):
    def __init__(self, client: PerplexityClient) -> None:
        # ... implementation
```

**Multi-Client Support:**

```python
# For flexible client selection
class YourFlexibleAgent(DebateAgent):
    def __init__(self, client) -> None:  # Generic client type
        # ... implementation
```

**Custom Response Processing:**

```python
def respond(self, topic: str, history: Sequence[DebateTurn], opponent: DebateAgent) -> str:
    prompt = self._build_prompt(topic, history, opponent)
    response = self._client.call_api(prompt)
    
    # Add custom processing
    if "SPECIAL_MARKER" in response:
        # Handle special cases
        pass
    
    return response
```

#### Other Extension Points

1. **Custom Prompts**: Extend `prompts.py` with specialized templates
2. **API Clients**: Implement new client types in `clients.py`
3. **CLI Options**: Add new arguments in `cli.py`
4. **Core Logic**: Modify debate flow in `core.py`

### Verification and Testing

Run tests to ensure functionality:

```bash
# Test basic import
python -c "import debate; print('Import successful')"

# Test agent creation
python -c "import debate.agents; print('All agents loaded')"

# Test CLI functionality
python -m debate --help
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the terms specified in the main repository license.

## Support

For issues, questions, or contributions, please:

1. Check existing documentation and issues
2. File a new issue with detailed information
3. Include error messages and reproduction steps
4. Specify your environment and configuration

---

**Designed for SAP SuccessFactors professionals, architects, and implementation teams**
