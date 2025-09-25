#!/usr/bin/env python3
"""
Inter-Agent Communication Demo using OpenHands Agent SDK.
This example demonstrates two agents communicating with each other through custom messaging tools.
"""

import os
import threading
import time
from typing import Dict, Any, Optional, Sequence
from queue import Queue, Empty
from pydantic import SecretStr, Field
from openhands.sdk import LLM, Conversation, get_logger
from openhands.sdk.preset.default import get_default_agent
from openhands.sdk.tool import ActionBase, ObservationBase, Tool, ToolExecutor, ToolAnnotations, register_tool
from openhands.sdk.llm import TextContent

# Set up logging
logger = get_logger(__name__)

# Global message queues for inter-agent communication
agent_queues: Dict[str, Queue] = {}

class SendMessageAction(ActionBase):
    """Action for sending a message to another agent."""
    recipient_id: str = Field(description="The ID of the recipient agent")
    message: str = Field(description="The message to send")

class SendMessageObservation(ObservationBase):
    """Observation from sending a message."""
    success: bool = Field(description="Whether the message was sent successfully")
    message: str = Field(description="Status message")
    recipient: str = Field(description="The recipient agent ID")
    sender: str = Field(description="The sender agent ID")
    
    @property
    def agent_observation(self) -> Sequence[TextContent]:
        return [TextContent(text=self.message)]

class ReceiveMessagesAction(ActionBase):
    """Action for receiving messages from other agents."""
    timeout: int = Field(default=5, description="Timeout in seconds to wait for messages")

class ReceiveMessagesObservation(ObservationBase):
    """Observation from receiving messages."""
    success: bool = Field(description="Whether the operation was successful")
    messages: list[str] = Field(description="List of received messages")
    count: int = Field(description="Number of messages received")
    recipient: str = Field(description="The recipient agent ID")
    
    @property
    def agent_observation(self) -> Sequence[TextContent]:
        if self.messages:
            message_text = f"Received {self.count} message(s):\n" + "\n".join(f"• {msg}" for msg in self.messages)
        else:
            message_text = "No messages received"
        return [TextContent(text=message_text)]

class InterAgentMessenger(ToolExecutor):
    """Custom tool executor that allows agents to send messages to each other."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        # Ensure this agent has a message queue
        if agent_id not in agent_queues:
            agent_queues[agent_id] = Queue()
    
    def execute(self, action: SendMessageAction) -> SendMessageObservation:
        """Send a message to another agent."""
        try:
            if action.recipient_id not in agent_queues:
                agent_queues[action.recipient_id] = Queue()
            
            # Add sender information to the message
            full_message = f"[From {self.agent_id}]: {action.message}"
            agent_queues[action.recipient_id].put(full_message)
            
            return SendMessageObservation(
                success=True,
                message=f"Message sent to {action.recipient_id}: {action.message}",
                recipient=action.recipient_id,
                sender=self.agent_id
            )
        except Exception as e:
            return SendMessageObservation(
                success=False,
                message=f"Failed to send message to {action.recipient_id}: {str(e)}",
                recipient=action.recipient_id,
                sender=self.agent_id
            )

class MessageReceiver(ToolExecutor):
    """Custom tool executor that allows agents to receive messages from other agents."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        # Ensure this agent has a message queue
        if agent_id not in agent_queues:
            agent_queues[agent_id] = Queue()
    
    def execute(self, action: ReceiveMessagesAction) -> ReceiveMessagesObservation:
        """Check for incoming messages from other agents."""
        try:
            messages = []
            start_time = time.time()
            
            # Collect all available messages within the timeout period
            while time.time() - start_time < action.timeout:
                try:
                    message = agent_queues[self.agent_id].get_nowait()
                    messages.append(message)
                except Empty:
                    if messages:  # If we have some messages, return them
                        break
                    time.sleep(0.1)  # Brief pause before checking again
            
            return ReceiveMessagesObservation(
                success=True,
                messages=messages,
                count=len(messages),
                recipient=self.agent_id
            )
        except Exception as e:
            return ReceiveMessagesObservation(
                success=False,
                messages=[],
                count=0,
                recipient=self.agent_id
            )

def create_messaging_tools(agent_id: str) -> Sequence[Tool]:
    """Create messaging tools for an agent."""
    
    # Create send message tool
    send_tool = Tool(
        name=f"send_message_{agent_id}",
        description=f"Send a message to another agent. Use this to communicate with other agents in the system.",
        action_type=SendMessageAction,
        observation_type=SendMessageObservation,
        annotations=ToolAnnotations(
            title=f"Send Message ({agent_id})",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        ),
        executor=InterAgentMessenger(agent_id)
    )
    
    # Create receive messages tool
    receive_tool = Tool(
        name=f"receive_messages_{agent_id}",
        description=f"Check for incoming messages from other agents. Use this to see if other agents have sent you any messages.",
        action_type=ReceiveMessagesAction,
        observation_type=ReceiveMessagesObservation,
        annotations=ToolAnnotations(
            title=f"Receive Messages ({agent_id})",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        ),
        executor=MessageReceiver(agent_id)
    )
    
    return [send_tool, receive_tool]

def create_agent_with_messaging(agent_id: str, llm: LLM, working_dir: str):
    """Create an agent with messaging capabilities."""
    
    # Register the messaging tools for this agent
    messenger_tool_name = f"send_message_{agent_id}"
    receiver_tool_name = f"receive_messages_{agent_id}"
    
    register_tool(messenger_tool_name, lambda: create_messaging_tools(agent_id)[:1])  # Send tool only
    register_tool(receiver_tool_name, lambda: create_messaging_tools(agent_id)[1:])   # Receive tool only
    
    # Get default agent
    agent = get_default_agent(
        llm=llm,
        working_dir=working_dir,
        cli_mode=True,
    )
    
    # Add messaging tools to the agent
    from openhands.sdk.tool import ToolSpec
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
        model="claude-3-5-sonnet-20241022",
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
    - Use 'send_message_Alice' to send messages to Bob (set recipient_id to "Bob")
    - Use 'receive_messages_Alice' to check for messages from Bob
    
    Your task is to start a collaborative conversation with Bob about planning a simple Python project. 
    Begin by introducing yourself and asking Bob what kind of project he'd like to work on together.
    """
    
    bob_initial = """
    Hello! You are Agent Bob. You have been given special tools to communicate with Agent Alice:
    - Use 'send_message_Bob' to send messages to Alice (set recipient_id to "Alice")
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