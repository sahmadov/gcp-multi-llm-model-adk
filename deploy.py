import os
import logging
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

# Load environment variables
load_dotenv()


def get_model_config():
    """
    Get model configuration based on environment variables.
    Priority: Vertex AI Gemini > Hosted Mistral > Local Model
    """

    # Check if we should use Vertex AI Gemini (recommended for Agent Engine)
    if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true":
        print("🧠 Using Vertex AI Gemini model")
        model_name = os.environ.get("MODEL", "gemini-2.0-flash")
        return model_name  # Return model name directly for Vertex AI

    # Check if we should use local model
    elif os.environ.get("USE_LOCAL_MODEL", "").lower() == "true":
        print("🔧 Using LOCAL Mistral model")
        return LiteLlm(
            model=os.environ.get("LOCAL_MODEL", "mistral/mistralai/mistral-7b-instruct-v0.3"),
            api_base=os.environ.get("LOCAL_API_BASE", "http://localhost:1234/v1"),
            api_key="not-needed"
        )

    # Default to hosted Mistral AI
    else:
        print("☁️ Using HOSTED Mistral AI")
        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY is required for hosted mode")

        return LiteLlm(
            model=os.environ.get("MISTRAL_MODEL", "mistral/mistral-small-latest"),
            api_key=api_key
        )


def google_search(query: str) -> dict:
    """
    Perform a Google search for the given query.

    Args:
        query (str): The search query

    Returns:
        dict: Search results with status and results
    """
    # TODO: Implement actual Google search functionality
    # For now, return a placeholder
    return {
        "status": "success",
        "query": query,
        "results": [
            {
                "title": f"Search result for: {query}",
                "url": "https://example.com",
                "description": "This is a placeholder search result."
            }
        ]
    }


def create_agent():
    """Create the search agent with all dependencies defined locally."""
    return Agent(
        name="google_search_agent",
        description="Answer questions using Google Search.",
        model=get_model_config(),
        instruction="""You are an expert researcher with access to Google Search tools. 
        You stick to facts and provide accurate, well-researched answers. 
        Always cite your sources when providing information from searches.
        If you cannot find reliable information, clearly state that.""",
        tools=[google_search]
    )


def main():
    # Initialize Vertex AI - these values should be set in your .env file
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
    LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    STAGING_BUCKET = os.environ.get("STAGING_BUCKET")  # Format: gs://your-bucket-name

    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
    if not STAGING_BUCKET:
        raise ValueError("STAGING_BUCKET environment variable is required")

    print(f"🚀 Deploying agent to Agent Engine")
    print(f"   Project: {PROJECT_ID}")
    print(f"   Location: {LOCATION}")
    print(f"   Staging Bucket: {STAGING_BUCKET}")

    # Initialize Vertex AI
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )

    # Create the agent locally (no external module dependency)
    root_agent = create_agent()

    # Wrap your agent in an AdkApp object for Agent Engine compatibility
    app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True,  # Enable tracing for monitoring
    )

    # Test locally first (optional)
    print("\n🧪 Testing agent locally...")
    try:
        session = app.create_session(user_id="test_user")
        print(f"   ✅ Local test session created: {session.id}")

        # Quick test query
        test_query = "Hello, are you working?"
        response_found = False
        for event in app.stream_query(
                user_id="test_user",
                session_id=session.id,
                message=test_query,
        ):
            if event.get('parts') and event['parts'][0].get('text'):
                print(f"   ✅ Local test response: {event['parts'][0]['text'][:100]}...")
                response_found = True
                break

        if not response_found:
            print("   ⚠️ No text response received in local test")

    except Exception as e:
        print(f"   ⚠️ Local test failed: {e}")
        print("   Continuing with deployment...")

    # Deploy to Agent Engine
    print("\n☁️ Deploying to Agent Engine...")
    try:
        remote_agent = agent_engines.create(
            display_name="Google Search Agent",
            agent_engine=app,
            requirements=[
                "google-cloud-aiplatform[adk,agent_engines]",
                "python-dotenv",
                "protobuf",
                "google-adk",
                "google-cloud-logging",
                "litellm"
            ]
        )

        print(f"   ✅ Agent deployed successfully!")
        print(f"   Resource name: {remote_agent.resource_name}")

        # Test the deployed agent
        print("\n🧪 Testing deployed agent...")
        try:
            remote_session = remote_agent.create_session(user_id="test_user_remote")
            print(f"   ✅ Remote session created: {remote_session['id']}")

            test_response = list(remote_agent.stream_query(
                user_id="test_user_remote",
                session_id=remote_session["id"],
                message="Hello, are you working?",
            ))

            if test_response:
                print("   ✅ Remote agent is responding successfully!")
            else:
                print("   ⚠️ No response from remote agent")
        except Exception as e:
            print(f"   ⚠️ Remote test failed: {e}")

        print(f"\n🎉 Deployment complete!")
        print(f"   You can monitor your agent at: https://console.cloud.google.com/vertex-ai/agents/agent-engines")
        print(f"   Resource name: {remote_agent.resource_name}")

        return remote_agent

    except Exception as e:
        print(f"   ❌ Deployment failed: {e}")
        print(f"   Error details: {str(e)}")
        raise


if __name__ == "__main__":
    main()