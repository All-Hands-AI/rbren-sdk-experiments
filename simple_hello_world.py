#!/usr/bin/env python3
"""
Simple Hello World example using OpenHands Agent SDK with Anthropic Claude.
This example demonstrates basic agent setup and conversation flow.
"""

import os
from pydantic import SecretStr
from openhands.sdk import LLM, Conversation, get_logger
from openhands.sdk.preset.default import get_default_agent

# Set up logging
logger = get_logger(__name__)

def main():
    # Configure LLM with Anthropic Claude
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")
    
    print("🤖 Setting up OpenHands Agent with Anthropic Claude...")
    
    llm = LLM(
        model="claude-3-5-sonnet-20241022",  # Using Claude 3.5 Sonnet
        api_key=SecretStr(api_key),
        service_id="hello-world-anthropic",
    )
    
    # Create agent with default tools and configuration
    cwd = os.getcwd()
    agent = get_default_agent(
        llm=llm,
        working_dir=cwd,
        cli_mode=True,  # Disable browser tools for CLI environments
    )
    
    print("✅ Agent created successfully!")
    
    # Create conversation
    conversation = Conversation(agent=agent)
    
    print("\n🚀 Starting conversation...")
    print("=" * 60)
    
    # Send a simple message that doesn't require file creation
    conversation.send_message(
        "Hello! Please tell me what the current date and time is, and also show me what files are in the current directory."
    )
    
    # Run the conversation
    conversation.run()
    
    print("=" * 60)
    print("✨ First conversation completed!")
    
    # Send another message to demonstrate continued conversation
    print("\n🔄 Continuing conversation...")
    print("=" * 60)
    
    conversation.send_message(
        "Great! Now please create a simple Python file called 'hello_world.py' that prints 'Hello, World from OpenHands!' and then run it to show me the output."
    )
    
    conversation.run()
    
    print("=" * 60)
    print("🎉 All done! The OpenHands Agent SDK is working with Anthropic Claude!")

if __name__ == "__main__":
    main()