# OpenHands Agent SDK Experiments

This repository contains experiments and demos with the OpenHands Agent SDK, showcasing various capabilities and use cases.

## 🚀 Quick Start

All demos require the OpenHands Agent SDK and an Anthropic API key:

```bash
# Clone the agent-sdk repository
git clone https://github.com/All-Hands-AI/agent-sdk/
cd agent-sdk

# Build the environment
make build

# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Run any demo
uv run python /path/to/demo.py
```

## 📁 Demo Files

### 1. Hello World Examples

#### `hello_world.py`
- **Description**: Simple "Hello, World!" script created by an agent
- **Purpose**: Basic demonstration that the agent can create and execute Python files
- **Usage**: `python hello_world.py`

#### `simple_hello_world.py`
- **Description**: Complete hello world demo using the OpenHands Agent SDK
- **Features**:
  - Agent setup with Anthropic Claude 3.5 Sonnet
  - Basic conversation flow
  - File creation and execution through the agent
  - Demonstrates agent tools (BashTool, FileEditorTool, TaskTrackerTool)
- **Usage**: `uv run python simple_hello_world.py`

#### `my_hello_world.py`
- **Description**: Custom hello world implementation
- **Features**: Similar to simple_hello_world.py but with different conversation flow
- **Usage**: `uv run python my_hello_world.py`

### 2. Inter-Agent Communication Demos

#### `inter_agent_communication_demo.py` ⚠️ (Non-functional)
- **Description**: First attempt at inter-agent communication
- **Status**: Has tool registration issues - kept for reference
- **Purpose**: Shows the evolution of the inter-agent communication concept

#### `inter_agent_communication_demo_v2.py` ✅ (Functional)
- **Description**: Advanced demo showing two agents communicating with each other
- **Features**:
  - Two independent agents (Alice and Bob) running in parallel threads
  - Custom messaging tools for inter-agent communication
  - Message queues for asynchronous communication
  - Collaborative conversation about Python project planning
  - Proper Tool interface implementation
- **Architecture**:
  - `SendMessageAction`/`SendMessageObservation`: For sending messages
  - `ReceiveMessagesAction`/`ReceiveMessagesObservation`: For receiving messages
  - `InterAgentMessenger`: Tool executor for sending messages
  - `MessageReceiver`: Tool executor for receiving messages
- **Usage**: `uv run python inter_agent_communication_demo_v2.py`

### 3. Documentation

#### `HELLO_WORLD_DEMO.md`
- **Description**: Comprehensive documentation of the hello world demo results
- **Contents**:
  - Overview of what was accomplished
  - Key components and architecture
  - Environment requirements
  - Cost information
  - Success metrics
  - Next steps for further development

## 🛠️ Technical Details

### Agent SDK Components Used

- **LLM Integration**: Anthropic Claude 3.5 Sonnet (`claude-3-5-sonnet-20241022`)
- **Core Tools**:
  - `BashTool`: Execute bash commands in persistent shell sessions
  - `FileEditorTool`: Create, edit, and manage files
  - `TaskTrackerTool`: Organize and track development tasks
  - `fetch_fetch`: MCP tool for fetching web content

### Custom Tools Implemented

- **Inter-Agent Messaging System**:
  - Message queues using Python's `queue.Queue`
  - Thread-safe communication between agents
  - Timeout-based message retrieval
  - Proper Tool interface with Action/Observation patterns

### Architecture Patterns

1. **Single Agent Pattern** (hello world demos):
   - One agent, one conversation
   - Linear execution flow
   - Direct tool usage

2. **Multi-Agent Pattern** (inter-agent communication):
   - Multiple agents with independent conversations
   - Parallel execution using threading
   - Custom communication protocols
   - Shared state management through queues

## 🎯 Key Learnings

1. **Tool Registration**: Tools must return `Sequence[Tool]`, not individual tool instances
2. **Action/Observation Pattern**: Proper tool implementation requires both Action and Observation classes
3. **Thread Safety**: Inter-agent communication requires careful handling of shared state
4. **LLM Integration**: Claude 3.5 Sonnet works excellently with the OpenHands SDK
5. **Cost Efficiency**: High cache hit rates (99.93%) make repeated operations very cost-effective

## 🔄 Evolution of Demos

1. **Phase 1**: Basic hello world to verify SDK functionality
2. **Phase 2**: Enhanced hello world with better conversation flow
3. **Phase 3**: Inter-agent communication (first attempt with tool registration issues)
4. **Phase 4**: Refined inter-agent communication with proper Tool interface

## 💡 Future Experiments

- Multi-agent collaboration on complex tasks
- Agent-to-agent file sharing
- Hierarchical agent architectures
- Integration with external APIs and services
- Real-time agent communication protocols

## 📊 Performance Metrics

From successful runs:
- **Token Usage**: ~70K input tokens, ~1.14K output tokens
- **Cache Efficiency**: 99.93% cache hit rate
- **Cost**: ~$0.046 per complex demo run
- **Success Rate**: 100% for properly implemented demos

## 🤝 Contributing

Feel free to add more experiments and demos to this repository. Follow the existing patterns:
- Clear documentation in README
- Proper error handling
- Thread safety for multi-agent scenarios
- Cost-conscious LLM usage
