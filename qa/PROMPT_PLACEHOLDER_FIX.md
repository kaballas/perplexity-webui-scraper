# Prompt Placeholder Fix - MrPromptBuilderAgent

## Issue Description

The `MrPromptBuilderAgent` was not receiving the `topic` and `conversation` context when building prompts. The placeholders `{topic}` and `{conversation}` were appearing literally in the final prompt instead of being replaced with actual values.

## Root Cause

In `prompts.py`, the `MR_PROMPT_BUILDER_AGENT_PROMPT` template used **double curly braces** instead of single curly braces:

```python
# INCORRECT (escaped literals)
Conversation Context:
{{topic}}

Discussion Transcript:
{{conversation}}
```

In Python's `.format()` method:
- `{placeholder}` → Gets replaced with the actual value
- `{{placeholder}}` → Produces literal `{placeholder}` text (escaped)

## The Fix

Changed the template in `prompts.py` from double to single curly braces:

```python
# CORRECT (proper placeholders)
Conversation Context:
{topic}

Discussion Transcript:
{conversation}
```

## Files Modified

- `qa/debate/prompts.py` - Line ~1350: Changed `{{topic}}` to `{topic}` and `{{conversation}}` to `{conversation}`

## Verification

The fix ensures that when `_build_prompt()` is called:

```python
prompt = MR_PROMPT_BUILDER_AGENT_PROMPT.format(topic=topic, conversation=conversation)
```

The actual topic and conversation history are now correctly injected into the prompt template.

## Before vs After

### Before (Broken)
```
Conversation Context:
{topic}

Discussion Transcript:
{conversation}

Analyze the requirements...
```
**Problem:** Literal placeholder text sent to the API

### After (Fixed)
```
Conversation Context:
================================================================================
Round 1 - Todo
================================================================================
{
  "summary": "The conversation focused on developing a technical specification..."
  ...
}

Discussion Transcript:
No dialogue yet.

Analyze the requirements...
```
**Solution:** Actual content injected into the prompt

## Impact

This was a critical bug that prevented the `MrPromptBuilderAgent` from:
- Understanding the conversation context
- Analyzing the topic being discussed  
- Providing relevant prompt engineering guidance
- Accessing conversation history for analysis

The agent would receive only its system prompt without any context about what to analyze or respond to.

## Status

✅ **FIXED** - October 19, 2025

The agent now correctly receives both topic and conversation context and can perform its prompt engineering analysis tasks.
