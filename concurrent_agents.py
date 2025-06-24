import asyncio
from semantic_kernel.agents import ChatCompletionAgent, AzureAIAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.agents import ConcurrentOrchestration
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel import Kernel
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
import os

load_dotenv()

# Helper to create a kernel with Azure OpenAI
def create_kernel():
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    kernel = Kernel()
    kernel.add_service(
        AzureChatCompletion(
            deployment_name=deployment_name,
            endpoint=endpoint,
            api_key=api_key
        )
    )
    return kernel

async def main():
    # Define agents
    agent_id = os.getenv("AZURE_AI_AGENT_ID")
    agent_endpoint = os.getenv("AZURE_AI_AGENT_ENDPOINT")
    client = AzureAIAgent.create_client(credential=DefaultAzureCredential(), endpoint=agent_endpoint)
    
    # Agent 1 - Contoso Pizzeria Customers Welcome Agent
    customers_welcome_agent = ChatCompletionAgent(
        name="CustomersWelcomeAgent",
        description="Greets customers and provides information about the restaurant.",
        instructions="Welcome the customer and provide a brief overview of the Contoso Pizzeria services offerings, based in Milan, close to the Central Station. Be friendly and engaging.",
        kernel=create_kernel()
    )

    # Agent 2 - Contoso Pizzeria Orders Manager Agent
    agent_definition = await client.agents.get_agent(agent_id=agent_id)
    orders_manager_agent = AzureAIAgent(client=client, definition=agent_definition, name="OrdersManagerAgent")

    # Agent 3 - Contoso Pizzeria Allergen Checker Agent
    allergen_checker_agent = ChatCompletionAgent(
        name="AllergenCheckerAgent",
        description="Checks order request and identifies potential allergens.",
        instructions="Analyze the order details and provide information about potential allergens present in the items.",
        kernel=create_kernel()
    )

    # Orchestrate agents concurrently
    orchestrator = ConcurrentOrchestration(members=[customers_welcome_agent, orders_manager_agent, allergen_checker_agent])

    runtime = InProcessRuntime()
    runtime.start()

    prompt = input("Please specify your order for Contoso Pizzeria: ")
    orchestration_result = await orchestrator.invoke(task=prompt, runtime=runtime)

    value = await orchestration_result.get(timeout=20)
    # For the concurrent orchestration, the result is a list of chat messages
    for item in value:
        print(f"# {item.name}:\n {item.content}\n")
        
    await runtime.stop_when_idle()

if __name__ == "__main__":
    asyncio.run(main())