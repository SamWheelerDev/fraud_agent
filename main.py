import asyncio
import os
import time

from mcp_agent.app import MCPApp
from mcp_agent.config import (
    Settings,
    LoggerSettings,
    MCPSettings,
    MCPServerSettings,
    OpenAISettings,
    AnthropicSettings,
)
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm import RequestParams
from mcp_agent.workflows.llm.llm_selector import ModelPreferences
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM


# Create the MCP app
app = MCPApp(name="fraud_agent")


async def fraud_agent_workflow():
    """Main workflow for the fraud agent that can access transaction services"""
    async with app.run() as agent_app:
        logger = agent_app.logger
        context = agent_app.context

        logger.info("Starting fraud agent workflow")
        
        # Add the current directory to the filesystem server's args if needed
        if "filesystem" in context.config.mcp.servers:
            context.config.mcp.servers["filesystem"].args.extend([os.getcwd()])

        # Create a fraud_agent that can access the transaction services
        fraud_agent = Agent(
            name="fraud_agent",
            instruction="""You are a fraud investigation assistant with access to transaction 
            lookup and dispute submission services. You can help users search for transactions, 
            view transaction details, and submit dispute claims when appropriate.
            
            The transaction lookup service is available at http://localhost:5001
            The dispute submission service is available at http://localhost:5002
            
            Both services require login with username 'demo' and password 'password'.
            
            Follow these guidelines:
            1. When searching for transactions, use the search functionality at http://localhost:5001/search
            2. To view transaction details, use the URL format http://localhost:5001/transaction/{transaction_id}
            3. To submit a dispute, access the form at http://localhost:5002/dispute
            4. To view existing disputes, check http://localhost:5002/disputes
            """,
            server_names=["http", "fetch"],
        )

        async with fraud_agent:
            logger.info("Fraud agent: Connected to server, initializing...")
            tools = await fraud_agent.list_tools()
            logger.info("Tools available:", data=tools.model_dump())

            llm = await fraud_agent.attach_llm(OpenAIAugmentedLLM)
            
            # Initialize by logging into both services
            login_result = await llm.generate_str(
                message="""Login to both the transaction lookup service (http://localhost:5001/login) 
                and the dispute submission service (http://localhost:5002/login) with 
                username 'demo' and password 'password'."""
            )
            logger.info("Login completed")
            
            # Interactive user session
            logger.info("Fraud agent ready for interactions")
            print("\nFraud Investigation Assistant initialized and ready for queries.")
            print("You can ask about transactions, view transaction details, or submit disputes.")
            
            while True:
                user_query = input("\nWhat would you like to do? (Type 'exit' to quit): ")
                
                if user_query.lower() == 'exit':
                    print("Exiting fraud agent workflow...")
                    break
                
                print("Processing your request...")
                response = await llm.generate_str(message=user_query)
                print(f"\nResponse: {response}")


def main():
    """Main entry point for the fraud agent"""
    print("Starting Fraud Investigation Assistant...")
    
    start = time.time()
    asyncio.run(fraud_agent_workflow())
    end = time.time()
    
    print(f"\nTotal session time: {end - start:.2f}s")


if __name__ == "__main__":
    main()
