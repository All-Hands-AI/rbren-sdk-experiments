# OpenHands Agent SDK Experiments

This repository contains experiments and demos with the OpenHands Agent SDK, showcasing various capabilities and use cases.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Anthropic API key

### Installation

#### Option 1: Using pip (Recommended)
```bash
# Clone this repository
git clone https://github.com/All-Hands-AI/rbren-sdk-experiments.git
cd rbren-sdk-experiments

# Install dependencies (includes agent-sdk from GitHub)
pip install -e .
# or
pip install -r requirements.txt
```

#### Option 2: Manual Setup
```bash
# Clone both repositories
git clone https://github.com/All-Hands-AI/rbren-sdk-experiments.git
git clone https://github.com/All-Hands-AI/agent-sdk.git

# Build agent-sdk
cd agent-sdk
make build
cd ../rbren-sdk-experiments
```

### Setup Environment
```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Run Demos
```bash
# Using the demo runner (automatically detects agent-sdk)
python run_demo.py simple_hello_world.py
python run_demo.py inter_agent_communication_demo_v2.py

# Or run directly if you have agent-sdk in your Python path
python simple_hello_world.py
```

### Demo Runner

The `run_demo.py` script automatically:
- Finds the agent-sdk installation
- Sets up the proper Python environment
- Validates that your API key is configured
- Runs the demo from the correct directory

Usage: `python run_demo.py <demo_file.py>`

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

#### `inter_agent_communication_demo_v2.py` ✅ (Fully Functional)
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

### 3. Utilities

#### `run_demo.py`
- **Description**: Demo runner script that handles environment setup
- **Features**:
  - Auto-detects agent-sdk installation
  - Sets up proper Python paths
  - Validates API key configuration
  - Provides helpful error messages
- **Usage**: `python run_demo.py <demo_file.py>`

### 4. Documentation

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

## ✅ Current Status

All demos are **fully functional** and tested:

- ✅ **Hello World Examples**: All working perfectly
- ✅ **Inter-Agent Communication**: Fixed and tested successfully
- ✅ **Demo Runner**: Automated setup and execution
- ✅ **Documentation**: Comprehensive and up-to-date

## 🎯 Key Learnings

1. **Tool Registration**: Tools must return `Sequence[Tool]`, not individual tool instances
2. **Action/Observation Pattern**: Proper tool implementation requires both Action and Observation classes
3. **Tool Executor Interface**: Custom executors must implement `__call__()` method, not `execute()`
4. **Thread Safety**: Inter-agent communication requires careful handling of shared state
5. **LLM Integration**: Claude 3.5 Sonnet works excellently with the OpenHands SDK
6. **Cost Efficiency**: High cache hit rates (99.91-99.95%) make repeated operations very cost-effective

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
- **Token Usage**: ~70K-1.4M input tokens, ~1.14K-1.69K output tokens
- **Cache Efficiency**: 99.91-99.95% cache hit rate (excellent caching performance)
- **Cost**: ~$0.046-$0.092 per demo run
- **Success Rate**: 100% for properly implemented demos
- **Inter-Agent Communication**: Successfully tested with message passing between agents

## 🤝 Contributing

Feel free to add more experiments and demos to this repository. Follow the existing patterns:
- Clear documentation in README
- Proper error handling
- Thread safety for multi-agent scenarios
- Cost-conscious LLM usage
