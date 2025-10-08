# OpenHands Agent SDK Hello World Demo

## Overview

This document demonstrates a successful setup and execution of the OpenHands Agent SDK using Anthropic's Claude 3.5 Sonnet model.

## What We Accomplished

✅ **Successfully cloned** the OpenHands Agent SDK repository from https://github.com/OpenHands/agent-sdk/

✅ **Built the development environment** using `make build` with uv package manager

✅ **Created a working hello world example** that demonstrates:
- LLM integration with Anthropic Claude 3.5 Sonnet
- Agent creation with default tools (BashTool, FileEditorTool, TaskTrackerTool)
- Conversation management and execution
- File creation and execution through the agent

✅ **Verified the agent can**:
- Execute bash commands
- Create Python files
- Run Python scripts
- Provide interactive responses

## Files Created

1. **`simple_hello_world.py`** - Our custom hello world example
2. **`hello_world.py`** - Created by the agent, prints "Hello, World from OpenHands!"
3. **`HELLO_WORLD_DEMO.md`** - This documentation file

## Key Components Used

### LLM Configuration
```python
llm = LLM(
    model="claude-3-5-sonnet-20241022",  # Using Claude 3.5 Sonnet
    api_key=SecretStr(api_key),
    service_id="hello-world-anthropic",
)
```

### Agent Setup
```python
agent = get_default_agent(
    llm=llm,
    working_dir=cwd,
    cli_mode=True,  # Disable browser tools for CLI environments
)
```

### Conversation Flow
```python
conversation = Conversation(agent=agent)
conversation.send_message("Your message here")
conversation.run()
```

## Tools Available

The agent has access to these tools:
- **BashTool**: Execute bash commands in a persistent shell session
- **FileEditorTool**: Create, edit, and manage files
- **TaskTrackerTool**: Organize and track development tasks
- **fetch_fetch**: MCP tool for fetching web content

## Environment Requirements

- Python 3.12+
- uv package manager (version 0.8.13+)
- ANTHROPIC_API_KEY environment variable

## Cost Information

The demo consumed approximately:
- Input tokens: ~70K (with 99.93% cache hit rate)
- Output tokens: ~1.14K
- Cost: ~$0.046

## Success Metrics

✅ Agent successfully created and executed Python code
✅ Conversation flow worked as expected
✅ File operations completed successfully
✅ Integration with Anthropic Claude API working
✅ All SDK components loaded properly

## Next Steps

This hello world example demonstrates that the OpenHands Agent SDK is properly configured and working with Anthropic Claude. You can now:

1. Explore more complex examples in the `examples/` directory
2. Build custom agents with specific tool configurations
3. Integrate with other LLM providers
4. Develop more sophisticated AI-powered applications

## Repository Structure

The OpenHands Agent SDK includes:
- **openhands-sdk**: Core SDK functionality
- **openhands-tools**: Runtime tool implementations
- **openhands-agent-server**: REST API and WebSocket server
- **examples/**: 23+ usage examples covering various features