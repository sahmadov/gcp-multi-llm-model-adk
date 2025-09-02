import os
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

load_dotenv()


def test_deployed_agent():
    """Test your deployed agent on Agent Engine"""

    # Initialize Vertex AI
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
    LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    STAGING_BUCKET = os.environ.get("STAGING_BUCKET")

    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )

    # Get your deployed agent - you'll need to replace this with your actual resource name
    # You can get this from the deployment output or Agent Engine UI
    AGENT_RESOURCE_NAME = input("Enter your agent resource name (from deployment output): ").strip()

    if not AGENT_RESOURCE_NAME:
        print("❌ Agent resource name is required")
        return

    try:
        # Connect to your deployed agent
        remote_agent = agent_engines.get(AGENT_RESOURCE_NAME)
        print(f"✅ Connected to agent: {AGENT_RESOURCE_NAME}")

        # Create a session
        session = remote_agent.create_session(user_id="test_user")
        session_id = session["id"]
        print(f"✅ Created session: {session_id}")

        # Interactive chat loop
        print("\n🤖 Chat with your deployed agent (type 'quit' to exit):")
        print("=" * 50)

        while True:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                break

            if not user_input:
                continue

            print("Agent: ", end="", flush=True)

            # Stream the agent's response
            full_response = ""
            for event in remote_agent.stream_query(
                    user_id="test_user",
                    session_id=session_id,
                    message=user_input,
            ):
                if event.get('parts'):
                    for part in event['parts']:
                        if part.get('text'):
                            print(part['text'], end="", flush=True)
                            full_response += part['text']
                        elif part.get('function_call'):
                            func_name = part['function_call']['name']
                            print(f"[Calling {func_name}...]", end="", flush=True)

            if not full_response.strip():
                print("(No text response)")

        print("\n👋 Goodbye!")

    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        print("Make sure you've deployed your agent first using deploy_to_agent_engine.py")


def list_deployed_agents():
    """List all your deployed agents"""

    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
    LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    STAGING_BUCKET = os.environ.get("STAGING_BUCKET")

    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )

    try:
        # Note: This functionality may vary based on the current Agent Engine API
        print("📋 Your deployed agents:")
        print("Visit https://console.cloud.google.com/vertex-ai/agents/agent-engines to see all your agents")

    except Exception as e:
        print(f"❌ Error listing agents: {e}")


if __name__ == "__main__":
    print("🤖 Agent Engine Testing Script")
    print("=" * 40)
    print("1. Test deployed agent")
    print("2. List deployed agents")

    choice = input("\nChoose an option (1 or 2): ").strip()

    if choice == "1":
        test_deployed_agent()
    elif choice == "2":
        list_deployed_agents()
    else:
        print("Invalid choice")