#!/usr/bin/env python3
"""
Inter-Agent Communication Demo using OpenHands Agent SDK.
This example demonstrates two agents communicating with each other through custom messaging tools.
"""

import os
import threading
import time
from typing import Dict, Any, Optional
from queue import Queue, Empty
from pydantic import SecretStr
from openhands.sdk import LLM, Conversation, get_logger
from openhands.sdk.preset.default import get_default_agent
from openhands.sdk.tool import ToolExecutor, ToolSpec, register_tool

# Set up logging
logger = get_logger(__name__)

# Global message queues for inter-agent communication
agent_queues: Dict[str, Queue] = {}

class InterAgentMessenger(ToolExecutor):
    """Custom tool that allows agents to send messages to each other."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        # Ensure this agent has a message queue
        if agent_id not in agent_queues:
            agent_queues[agent_id] = Queue()
    
    def execute(self, recipient_id: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send a message to another agent."""
        try:
            if recipient_id not in agent_queues:
                agent_queues[recipient_id] = Queue()
            
            # Add sender information to the message
            full_message = f"[From {self.agent_id}]: {message}"
            agent_queues[recipient_id].put(full_message)
            
            return {
                "success": True,
                "message": f"Message sent to {recipient_id}: {message}",
                "recipient": recipient_id,
                "sender": self.agent_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to send message to {recipient_id}"
            }

class MessageReceiver(ToolExecutor):
    """Custom tool that allows agents to receive messages from other agents."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        # Ensure this agent has a message queue
        if agent_id not in agent_queues:
            agent_queues[agent_id] = Queue()
    
    def execute(self, timeout: int = 5, **kwargs) -> Dict[str, Any]:
        """Check for incoming messages from other agents."""
        try:
            messages = []
            start_time = time.time()
            
            # Collect all available messages within the timeout period
            while time.time() - start_time < timeout:
                try:
                    message = agent_queues[self.agent_id].get_nowait()
                    messages.append(message)
                except Empty:
                    if messages:  # If we have some messages, return them
                        break
                    time.sleep(0.1)  # Brief pause before checking again
            
            if messages:
                return {
                    "success": True,
                    "messages": messages,
                    "count": len(messages),
                    "recipient": self.agent_id
                }
            else:
                return {
                    "success": True,
                    "messages": [],
                    "count": 0,
                    "message": "No messages received",
                    "recipient": self.agent_id
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to check for messages"
            }

def create_agent_with_messaging(agent_id: str, llm: LLM, working_dir: str):
    """Create an agent with messaging capabilities."""
    
    # Register the messaging tools for this agent
    messenger_tool_name = f"send_message_{agent_id}"
    receiver_tool_name = f"receive_messages_{agent_id}"
    
    register_tool(messenger_tool_name, lambda: [InterAgentMessenger(agent_id)])
    register_tool(receiver_tool_name, lambda: [MessageReceiver(agent_id)])
    
    # Get default agent with additional messaging tools
    agent = get_default_agent(
        llm=llm,
        working_dir=working_dir,
        cli_mode=True,
    )
    
    # Add messaging tools to the agent
    messaging_tools = [
        ToolSpec(name=messenger_tool_name, params={}),
        ToolSpec(name=receiver_tool_name, params={})
    ]
    
    # Add the messaging tools to the existing tools
    agent.tools.extend(messaging_tools)
    
    return agent

def run_agent_conversation(agent_id: str, agent, initial_message: str, conversation_steps: int = 3):
    """Run a conversation for a specific agent."""
    print(f"\n🤖 Starting conversation for Agent {agent_id}")
    print("=" * 50)
    
    conversation = Conversation(agent=agent)
    
    # Send initial message
    conversation.send_message(initial_message)
    conversation.run()
    
    # Continue conversation for specified steps
    for step in range(conversation_steps):
        print(f"\n📨 Agent {agent_id} - Step {step + 1}: Checking for messages and responding...")
        
        # Check for messages and respond
        if agent_id == "Alice":
            other_agent = "Bob"
        else:
            other_agent = "Alice"
            
        check_message = f"Please check for any messages from {other_agent} using your receive_messages tool, and if you receive any, respond appropriately using your send_message tool."
        
        conversation.send_message(check_message)
        conversation.run()
        
        # Brief pause between steps
        time.sleep(2)
    
    print(f"✅ Agent {agent_id} conversation completed")

def main():
    """Main function to demonstrate inter-agent communication."""
    
    # Configure LLM with Anthropic Claude
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
    
    print("🚀 Setting up Inter-Agent Communication Demo")
    print("=" * 60)
    
    llm = LLM(
        model="claude-sonnet-4-20250514",
        api_key=SecretStr(api_key),
        service_id="inter-agent-demo",
    )
    
    cwd = os.getcwd()
    
    # Create two agents with messaging capabilities
    print("👥 Creating Agent Alice and Agent Bob...")
    
    agent_alice = create_agent_with_messaging("Alice", llm, cwd)
    agent_bob = create_agent_with_messaging("Bob", llm, cwd)
    
    print("✅ Both agents created successfully!")
    
    # Define initial messages for each agent
    alice_initial = """
    Hello! You are Agent Alice. You have been given special tools to communicate with Agent Bob:
    - Use 'send_message_Alice' to send messages to Bob
    - Use 'receive_messages_Alice' to check for messages from Bob
    
    Your task is to start a collaborative conversation with Bob about planning a simple Python project. 
    Begin by introducing yourself and asking Bob what kind of project he'd like to work on together.
    """
    
    bob_initial = """
    Hello! You are Agent Bob. You have been given special tools to communicate with Agent Alice:
    - Use 'send_message_Bob' to send messages to Alice  
    - Use 'receive_messages_Bob' to check for messages from Alice
    
    Your task is to collaborate with Alice on planning a Python project. Wait for Alice to contact you first, 
    then engage in a friendly conversation about what kind of project you could build together. 
    You're particularly interested in data analysis and visualization projects.
    """
    
    print("\n🎭 Starting parallel conversations...")
    
    # Create threads for each agent conversation
    alice_thread = threading.Thread(
        target=run_agent_conversation,
        args=("Alice", agent_alice, alice_initial, 4),
        name="Alice-Thread"
    )
    
    bob_thread = threading.Thread(
        target=run_agent_conversation, 
        args=("Bob", agent_bob, bob_initial, 4),
        name="Bob-Thread"
    )
    
    # Start both conversations
    alice_thread.start()
    time.sleep(3)  # Give Alice a head start to send the first message
    bob_thread.start()
    
    # Wait for both conversations to complete
    alice_thread.join()
    bob_thread.join()
    
    print("\n" + "=" * 60)
    print("🎉 Inter-Agent Communication Demo Completed!")
    print("\n📊 Final Message Queue Status:")
    
    for agent_id, queue in agent_queues.items():
        remaining_messages = []
        while not queue.empty():
            try:
                remaining_messages.append(queue.get_nowait())
            except Empty:
                break
        
        if remaining_messages:
            print(f"📬 {agent_id} has {len(remaining_messages)} unread messages:")
            for msg in remaining_messages:
                print(f"   • {msg}")
        else:
            print(f"📭 {agent_id} has no unread messages")

if __name__ == "__main__":
    main()