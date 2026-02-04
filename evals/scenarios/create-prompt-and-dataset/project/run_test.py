#!/usr/bin/env python3
"""
Test run script for the create-prompt-and-dataset eval.

This script:
1. Creates a test run in Freeplay
2. Executes the prompt template against the dataset
3. Records each completion with TestRunInfo
"""

import os
import sys
import time
from freeplay import CallInfo, Freeplay, RecordPayload, TestRunInfo
from openai import OpenAI


def main():
    # Initialize clients
    freeplay = Freeplay(
        freeplay_api_key=os.environ.get("FREEPLAY_API_KEY"),
        api_base=os.environ.get("FREEPLAY_BASE_URL", "https://dev.freeplay.ai") + "/api",
    )

    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    project_id = os.environ.get("FREEPLAY_PROJECT_ID")
    if not project_id:
        print("Error: FREEPLAY_PROJECT_ID not set", file=sys.stderr)
        sys.exit(1)

    # Create test run
    print("Creating test run...")
    test_run = freeplay.test_runs.create(
        project_id=project_id,
        name="eval-test-run",
        description="Test run for eval scenario verification",
        testlist="qa-assistant-test-dataset",
        include_outputs=True,
    )

    print(f"Test run created: {test_run.test_run_id}")
    print(f"Test cases to run: {len(test_run.test_cases)}")

    # Get prompt template
    print("\nFetching prompt template...")
    template_prompt = freeplay.prompts.get(
        project_id=project_id,
        template_name="qa-assistant",
        environment="latest",
    )

    # Run each test case
    print("\nRunning test cases...")
    for i, test_case in enumerate(test_run.test_cases, 1):
        print(f"  Running test case {i}/{len(test_run.test_cases)}...")

        # Bind variables and format the prompt
        formatted_prompt = template_prompt.bind(test_case.variables).format(
            flavor_name="openai_chat"
        )

        # Call the LLM
        start_time = time.time()
        response = openai_client.chat.completions.create(
            model=formatted_prompt.prompt_info.model,
            messages=formatted_prompt.llm_prompt,
        )
        end_time = time.time()

        # Record the completion to Freeplay with TestRunInfo
        freeplay.recordings.create(
            RecordPayload(
                project_id=project_id,
                all_messages=formatted_prompt.all_messages(
                    response.choices[0].message
                ),
                inputs=test_case.variables,
                session_info=freeplay.sessions.create(),
                prompt_version_info=formatted_prompt.prompt_info,
                call_info=CallInfo.from_prompt_info(
                    formatted_prompt.prompt_info, start_time, end_time
                ),
                test_run_info=TestRunInfo(
                    test_run_id=test_run.test_run_id, test_case_id=test_case.id
                ),
            )
        )

        print(f"    ✓ Recorded completion for test case {test_case.id}")

    print(f"\n✅ Test run completed successfully!")
    print(f"Test run ID: {test_run.test_run_id}")
    print(f"Test cases executed: {len(test_run.test_cases)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
