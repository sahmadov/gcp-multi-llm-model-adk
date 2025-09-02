#!/usr/bin/env python3
"""Deploy Search Agent to Vertex AI Agent Engine."""
import sys
from pathlib import Path
from dotenv import load_dotenv
import os
import vertexai

# Add the project root to Python path
project_root = Path(__file__).parent.parent  # Goes up from search_agent/ to project root
sys.path.insert(0, str(project_root))

# Now we can import from search_agent module
from search_agent.agent import create_search_agent

load_dotenv()


def setup_environment():
    """Initialize Vertex AI environment."""
    PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
    LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    STAGING_BUCKET = os.environ.get("STAGING_BUCKET")

    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
    if not STAGING_BUCKET:
        raise ValueError("STAGING_BUCKET environment variable is required")

    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET
    )

    print(f"🚀 Deploying Search Agent")
    print(f"   Project: {PROJECT_ID}")
    print(f"   Location: {LOCATION}")
    print(f"   Staging Bucket: {STAGING_BUCKET}")


def deploy():
    """Deploy the search agent to Agent Engine."""
    from vertexai.preview import reasoning_engines
    from vertexai import agent_engines

    # Create the agent
    search_agent = create_search_agent()

    # Wrap in AdkApp
    adk_app = reasoning_engines.AdkApp(
        agent=search_agent,
        enable_tracing=True
    )

    # These packages will be installed in the Agent Engine container
    requirements = [
        "google-cloud-aiplatform[adk,agent_engines]>=1.106.0",
        "google-adk>=1.9.0",
        "python-dotenv>=1.0.0",
        "litellm>=1.50.0",
        "protobuf>=4.0.0"
    ]

    print("📦 Deploying to Agent Engine...")

    remote_app = agent_engines.create(
        agent_engine=adk_app,
        requirements=requirements,
        extra_packages=["search_agent"],  # This includes your search_agent module
        display_name="Google Search Agent",
        description="An AI agent that can perform Google searches to answer questions"
    )

    print(f"✅ Deployment successful!")
    print(f"   Resource Name: {remote_app.resource_name}")
    print(f"   Monitor at: https://console.cloud.google.com/vertex-ai/agents/agent-engines")

    return remote_app


def main():
    """Main deployment function."""
    setup_environment()
    deploy()


if __name__ == "__main__":
    main()