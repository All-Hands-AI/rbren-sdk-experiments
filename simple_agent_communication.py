#!/usr/bin/env python3
"""
Simple Agent Communication Demo using OpenHands Agent SDK.
This example demonstrates two agents communicating with each other through direct messaging.
"""

import os
import threading
import time
from typing import Dict, Any, Optional, Sequence
from queue import Queue, Empty
from pydantic import SecretStr, Field
from openhands.sdk import LLM, Conversation, get_logger
from openhands.sdk.agent import Agent
from openhands.sdk.tool import ActionBase, ObservationBase, Tool, ToolExecutor, ToolAnnotations, ToolSpec, register_tool
from openhands.sdk.llm import TextContent

# Set up logging
logger = get_logger(__name__)

# Global message queues for inter-agent communication
agent_queues: Dict[str, Queue] = {}

# Global registry of active conversations
active_conversations: Dict[str, Conversation] = {}

# Lock for thread safety
conversation_lock = threading.Lock()

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

class InterAgentMessenger(ToolExecutor):
    """Custom tool executor that allows agents to send messages to each other."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        # Ensure this agent has a message queue
        if agent_id not in agent_queues:
            agent_queues[agent_id] = Queue()
    
    def __call__(self, action: SendMessageAction) -> SendMessageObservation:
        """Send a message to another agent."""
        try:
            if action.recipient_id not in agent_queues:
                agent_queues[action.recipient_id] = Queue()
            
            # Add sender information to the message
            full_message = f"[From {self.agent_id}]: {action.message}"
            agent_queues[action.recipient_id].put(full_message)
            
            # Trigger the recipient's conversation if it exists and isn't already running
            self._trigger_recipient_conversation(action.recipient_id)
            
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
    
    def _trigger_recipient_conversation(self, recipient_id: str):
        """Trigger the recipient's conversation to process the new message."""
        with conversation_lock:
            if recipient_id in active_conversations:
                conversation = active_conversations[recipient_id]
                
                # Check if the conversation is already running to avoid conflicts
                if hasattr(conversation, '_running') and not conversation._running:
                    # Deliver pending messages and trigger run in a separate thread
                    threading.Thread(
                        target=self._deliver_and_run,
                        args=(recipient_id, conversation),
                        daemon=True
                    ).start()
                elif not hasattr(conversation, '_running'):
                    # If _running attribute doesn't exist, assume it's safe to run
                    threading.Thread(
                        target=self._deliver_and_run,
                        args=(recipient_id, conversation),
                        daemon=True
                    ).start()
    
    def _deliver_and_run(self, agent_id: str, conversation: Conversation):
        """Deliver pending messages and run the conversation."""
        try:
            # Mark conversation as running
            conversation._running = True
            
            # Deliver pending messages
            messages = []
            if agent_id in agent_queues:
                while not agent_queues[agent_id].empty():
                    try:
                        message = agent_queues[agent_id].get_nowait()
                        messages.append(message)
                    except Empty:
                        break
            
            # If there are messages, deliver them and run
            if messages:
                message_text = f"You have received {len(messages)} message(s):\n" + "\n".join(f"• {msg}" for msg in messages)
                conversation.send_message(message_text)
                conversation.run()
        except Exception as e:
            logger.error(f"Error in _deliver_and_run for {agent_id}: {e}")
        finally:
            # Mark conversation as not running
            conversation._running = False

def create_messaging_tool(agent_id: str) -> Tool:
    """Create messaging tool for an agent."""
    
    # Create send message tool
    send_tool = Tool(
        name="send_message",
        description="Send a message to another agent. Use this to communicate with other agents in the system.",
        action_type=SendMessageAction,
        observation_type=SendMessageObservation,
        annotations=ToolAnnotations(
            title="Send Message",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=True,
        ),
        executor=InterAgentMessenger(agent_id)
    )
    
    return send_tool

def create_simple_agent(agent_id: str, llm: LLM, working_dir: str) -> Agent:
    """Create a simple agent with only messaging capabilities."""
    
    # Create messaging tool
    messaging_tool = create_messaging_tool(agent_id)
    
    # Create agent with only the messaging tool
    agent = Agent(
        llm=llm,
        tools=[ToolSpec(name="send_message", params={})],
        working_dir=working_dir,
        cli_mode=True,
    )
    
    register_tool("send_message", lambda: [messaging_tool])
    
    return agent

def register_conversation(agent_id: str, conversation: Conversation):
    """Register a conversation in the global registry."""
    with conversation_lock:
        active_conversations[agent_id] = conversation
        # Initialize running state
        conversation._running = False

def unregister_conversation(agent_id: str):
    """Unregister a conversation from the global registry."""
    with conversation_lock:
        if agent_id in active_conversations:
            del active_conversations[agent_id]

def run_agent_conversation(agent_id: str, agent: Agent, initial_message: str, max_duration: int = 60):
    """Run a conversation for a specific agent using event-driven messaging."""
    print(f"\n🤖 Starting conversation for Agent {agent_id}")
    print("=" * 50)
    
    conversation = Conversation(agent=agent)
    
    # Register the conversation so it can receive messages
    register_conversation(agent_id, conversation)
    
    try:
        # Send initial message and run
        conversation.send_message(initial_message)
        conversation._running = True
        conversation.run()
        conversation._running = False
        
        # Keep the conversation alive for the specified duration
        # The conversation will be triggered automatically when messages arrive
        start_time = time.time()
        while time.time() - start_time < max_duration:
            time.sleep(1)  # Check every second if we should continue
            
            # If this is Alice and no messages have been sent yet, give a gentle nudge
            if agent_id == "Alice" and time.time() - start_time > 5:
                with conversation_lock:
                    if not conversation._running:
                        other_agent = "Bob"
                        nudge_message = f"Please start the conversation with {other_agent} by sending them a message using the send_message tool with recipient_id set to '{other_agent}'."
                        conversation.send_message(nudge_message)
                        conversation._running = True
                        conversation.run()
                        conversation._running = False
                        break  # Only nudge once
        
    finally:
        # Unregister the conversation
        unregister_conversation(agent_id)
    
    print(f"✅ Agent {agent_id} conversation completed")

def main():
    """Main function to demonstrate simple inter-agent communication."""
    
    # Configure LLM with Anthropic Claude
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
    
    print("🚀 Setting up Simple Agent Communication Demo")
    print("=" * 60)
    
    llm = LLM(
        model="claude-3-5-sonnet-20241022",
        api_key=SecretStr(api_key),
        service_id="simple-agent-demo",
    )
    
    cwd = os.getcwd()
    
    # Create two simple agents with messaging capabilities
    print("👥 Creating Agent Alice and Agent Bob...")
    
    agent_alice = create_simple_agent("Alice", llm, cwd)
    agent_bob = create_simple_agent("Bob", llm, cwd)
    
    print("✅ Both agents created successfully!")
    
    # Define initial messages for each agent
    alice_initial = """
    Hello! You are Agent Alice. You have been given a special tool to communicate with Agent Bob:
    - Use 'send_message' to send messages to Bob (set recipient_id to "Bob")
    
    When you send a message to Bob, he will automatically receive it and respond. The conversation is event-driven,
    so you don't need to check for messages - they will be delivered to you automatically when Bob sends them.
    
    Your task is to start a collaborative conversation with Bob about planning a simple Python project. 
    Begin by introducing yourself and asking Bob what kind of project he'd like to work on together.
    """
    
    bob_initial = """
    Hello! You are Agent Bob. You have been given a special tool to communicate with Agent Alice:
    - Use 'send_message' to send messages to Alice (set recipient_id to "Alice")
    
    When you send a message to Alice, she will automatically receive it and respond. The conversation is event-driven,
    so you don't need to check for messages - they will be delivered to you automatically when Alice sends them.
    
    Your task is to collaborate with Alice on planning a Python project. Wait for Alice to contact you first, 
    then engage in a friendly conversation about what kind of project you could build together. 
    You're particularly interested in data analysis and visualization projects.
    """
    
    print("\n🎭 Starting parallel conversations...")
    
    # Create threads for each agent conversation
    alice_thread = threading.Thread(
        target=run_agent_conversation,
        args=("Alice", agent_alice, alice_initial, 60),  # 60 seconds max duration
        name="Alice-Thread"
    )
    
    bob_thread = threading.Thread(
        target=run_agent_conversation, 
        args=("Bob", agent_bob, bob_initial, 60),  # 60 seconds max duration
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
    print("🎉 Simple Agent Communication Demo Completed!")
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
