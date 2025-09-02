#!/usr/bin/env python3
"""Deploy ADK Agent to Vertex AI Agent Engine."""

import os
import sys
from pathlib import Path

import vertexai
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.root_agent import root_agent

load_dotenv()


def setup_environment():
    vertexai.init(
        project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION"),
        staging_bucket=os.environ.get("STAGING_BUCKET")
    )


def deploy():
    from vertexai.preview import reasoning_engines
    from vertexai import agent_engines

    adk_app = reasoning_engines.AdkApp(
        agent=root_agent,
        enable_tracing=True
    )

    # These packages will be installed in the Agent Engine container
    requirements = [
        "google-cloud-aiplatform[adk,agent_engines]",
        "python-dotenv",
        "protobuf",
        "google-adk",
        "google-cloud-logging",
        "litellm"
    ]

    env_vars = {
        "GOOGLE_GENAI_USE_VERTEXAI": os.environ.get("GOOGLE_GENAI_USE_VERTEXAI"),
        "MODEL": os.environ.get("MODEL"),
        "USE_LOCAL_MODEL": os.environ.get("USE_LOCAL_MODEL"),
        "MISTRAL_API_KEY": os.environ.get("MISTRAL_API_KEY"),
        "MISTRAL_MODEL": os.environ.get("MISTRAL_MODEL"),
        "LOCAL_MODEL": os.environ.get("LOCAL_MODEL"),
        "LOCAL_API_BASE": os.environ.get("LOCAL_API_BASE")
    }

    # Remove None values
    env_vars = {k: v for k, v in env_vars.items() if v is not None}

    print("Deploying to Agent Engine...")
    print(f"Environment variables being passed: {list(env_vars.keys())}")

    remote_app = agent_engines.create(
        agent_engine=adk_app,
        requirements=requirements,
        extra_packages=["agents"],
        display_name="Multi LLM Agents",
        description="Agents used to test the Multi LLM Agents in GCP.",
        env_vars=env_vars
    )

    print(f"Deployment successful!")
    print(f"Resource Name: {remote_app.resource_name}")
    return remote_app


def main():
    setup_environment()
    deploy()


if __name__ == "__main__":
    main()