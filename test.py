import os
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_deployed_agent():
    """Test the deployed Google Search Agent

    Note: The google_search function in root_agent.py is currently a placeholder.
    To get real search results, you'll need to implement actual search functionality
    using Google Custom Search API or another search service.
    """

    # Initialize Vertex AI
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
    LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")

    print(f"🔍 Connecting to Agent Engine")
    print(f"   Project: {PROJECT_ID}")
    print(f"   Location: {LOCATION}")

    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
    )

    # You'll need to replace this with your actual agent resource name
    # Format: projects/{project}/locations/{location}/agents/{agent_id}
    # You can find this in the Google Cloud Console or from the deploy.py output
    AGENT_RESOURCE_NAME = "projects/773561763236/locations/us-central1/reasoningEngines/9014592370926157824"

    if not AGENT_RESOURCE_NAME:
        print("❌ Agent resource name is required!")
        print("   Example format: projects/your-project/locations/us-central1/agents/agent-id")
        return

    try:
        # Get the deployed agent
        print(f"\n📡 Connecting to agent: {AGENT_RESOURCE_NAME}")
        remote_agent = agent_engines.get(resource_name=AGENT_RESOURCE_NAME)

        # Create a session
        print("📝 Creating test session...")
        session = remote_agent.create_session(user_id="test_user")
        session_id = session["id"]
        print(f"   ✅ Session created: {session_id}")

        # Test queries
        test_queries = [
            "What is the weather like today?",
            "Tell me about artificial intelligence",
            "Search for recent technology news"
        ]

        print("\n🧪 Running test queries...")
        for query in test_queries:
            print(f"\n💬 Query: {query}")
            print("   Response: ", end="")

            # Stream the response
            response_text = ""

            for event in remote_agent.stream_query(
                    user_id="test_user",
                    session_id=session_id,
                    message=query,
            ):
                # Extract text from content.parts structure (Agent Engine format)
                if event.get('content') and event['content'].get('parts'):
                    parts = event['content']['parts']
                    if parts and len(parts) > 0 and parts[0].get('text'):
                        text = parts[0]['text']
                        response_text += text

                        # Print first 200 chars for brevity
                        if len(response_text) <= 200:
                            print(text, end="", flush=True)
                        elif len(response_text) - len(text) < 200:
                            print("...", end="", flush=True)

            if response_text:
                if len(response_text) > 200:
                    print(f" (total: {len(response_text)} chars)")
                else:
                    print()
            else:
                print("No response received")

        print("\n✅ All tests completed successfully!")

        # Interactive mode
        print("\n🎮 Entering interactive mode (type 'quit' to exit)")
        while True:
            user_query = input("\n💬 Your query: ").strip()
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            print("   Response: ", end="")
            response_text = ""

            for event in remote_agent.stream_query(
                    user_id="test_user",
                    session_id=session_id,
                    message=user_query,
            ):
                if event.get('content') and event['content'].get('parts'):
                    parts = event['content']['parts']
                    if parts and len(parts) > 0 and parts[0].get('text'):
                        text = parts[0]['text']
                        response_text += text
                        print(text, end="", flush=True)

            if not response_text:
                print("No response received")
            else:
                print()  # New line after response

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   Make sure the agent is deployed and the resource name is correct")


if __name__ == "__main__":
    test_deployed_agent()