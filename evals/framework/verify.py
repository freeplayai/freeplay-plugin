#!/usr/bin/env python3
"""
Verification script for Freeplay plugin evaluations.

Checks success criteria and generates scores for eval runs.
"""

import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path


# =============================================================================
# Freeplay API Helper
# =============================================================================

class FreeplayAPI:
    """Helper for making Freeplay API requests."""

    def __init__(self):
        self.base_url = os.environ.get("FREEPLAY_BASE_URL", "https://api.freeplay.ai")
        self.api_key = os.environ.get("FREEPLAY_API_KEY", "")
        self.project_id = os.environ.get("FREEPLAY_PROJECT_ID", "")
        self.ssl_context = self._create_ssl_context()

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context, optionally disabling verification for local dev."""
        verify_ssl = os.environ.get("FREEPLAY_VERIFY_SSL", "true").lower() != "false"
        ctx = ssl.create_default_context()
        if not verify_ssl:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        return ctx

    def _request(self, method: str, path: str, data: dict = None) -> dict:
        """Make an API request and return parsed JSON response."""
        url = f"{self.base_url}{path}"

        if data is not None:
            payload = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(url, data=payload, method=method)
        else:
            req = urllib.request.Request(url, method=method)

        req.add_header("Authorization", f"Bearer {self.api_key}")
        req.add_header("Content-Type", "application/json")

        with urllib.request.urlopen(req, context=self.ssl_context, timeout=10) as response:
            body = response.read().decode("utf-8")
            return {
                "status_code": response.status,
                "data": json.loads(body) if body else {},
            }

    def search_completions(self, filters: dict = None) -> dict:
        """Search for completions."""
        path = f"/api/v2/projects/{self.project_id}/search/completions"
        return self._request("POST", path, {"filters": filters or {}})

    def list_prompt_templates(self) -> dict:
        """List all prompt templates."""
        path = f"/api/v2/projects/{self.project_id}/prompt-templates"
        return self._request("GET", path)

    def list_projects(self) -> dict:
        """List all projects."""
        path = f"/api/v2/projects/all"
        return self._request("GET", path)

    def get_prompt_template_version(self, template_id: str, version_id: str) -> dict:
        """Get a specific prompt template version."""
        path = f"/api/v2/projects/{self.project_id}/prompt-templates/id/{template_id}/versions/{version_id}"
        return self._request("GET", path)

    def list_prompt_datasets(self) -> dict:
        """List all prompt datasets."""
        path = f"/api/v2/projects/{self.project_id}/prompt-datasets"
        return self._request("GET", path)

    def get_dataset_test_cases(self, dataset_id: str) -> dict:
        """Get test cases for a dataset."""
        path = f"/api/v2/projects/{self.project_id}/prompt-datasets/{dataset_id}/test-cases"
        return self._request("GET", path)

    def list_test_runs(self) -> dict:
        """List all test runs in the project."""
        path = f"/api/v2/projects/{self.project_id}/test-runs"
        return self._request("GET", path)

    def get_test_run(self, test_run_id: str) -> dict:
        """Get a specific test run by ID."""
        path = f"/api/v2/projects/{self.project_id}/test-runs/id/{test_run_id}"
        return self._request("GET", path)


def get_eval_start_timestamp() -> str:
    """Get timestamp filter - either from EVAL_START_TIME or 5 mins ago."""
    eval_start = os.environ.get("EVAL_START_TIME")
    if eval_start:
        return eval_start
    # Use local time (Freeplay stores timestamps in local time)
    return (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")


def parse_completion_timestamp(completion: dict) -> datetime | None:
    """Parse timestamp from a completion record."""
    # Check both top-level and nested in completion_metadata
    sources = [completion, completion.get("completion_metadata", {})]

    for source in sources:
        for field in ["start_time", "created_at", "timestamp", "end_time"]:
            ts = source.get(field)
            if not ts or not isinstance(ts, str):
                continue
            try:
                # Normalize: remove timezone suffix, microseconds
                ts_clean = ts.replace("Z", "").replace("T", " ")
                if "+" in ts_clean:
                    ts_clean = ts_clean.split("+")[0]
                if "." in ts_clean:
                    ts_clean = ts_clean.split(".")[0]
                return datetime.strptime(ts_clean.strip(), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
    return None


# =============================================================================
# File and Code Checks
# =============================================================================

def load_scenario(scenario_name: str) -> dict:
    """Load scenario definition from JSON file."""
    evals_dir = Path(__file__).parent.parent
    scenario_path = evals_dir / "scenarios" / scenario_name / "scenario.json"
    with open(scenario_path) as f:
        return json.load(f)


def check_file_contains(project_dir: str, file_name: str, patterns: list[str]) -> dict:
    """Check if a file contains expected patterns."""
    file_path = Path(project_dir) / file_name
    result = {
        "check": "file_contains",
        "file": file_name,
        "patterns": patterns,
        "passed": False,
        "found": [],
        "missing": [],
    }

    if not file_path.exists():
        result["error"] = f"File not found: {file_name}"
        return result

    with open(file_path) as f:
        content = f.read().lower()

    for pattern in patterns:
        if pattern.lower() in content:
            result["found"].append(pattern)
        else:
            result["missing"].append(pattern)

    result["passed"] = len(result["missing"]) == 0
    return result


def check_code_runs(project_dir: str, command: str, timeout: int = 60) -> dict:
    """Check if code runs without errors."""
    result = {
        "check": "code_runs",
        "command": command,
        "passed": False,
        "stdout": "",
        "stderr": "",
    }

    try:
        # Install requirements first if they exist
        req_path = Path(project_dir) / "requirements.txt"
        if req_path.exists():
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", "-r", str(req_path)],
                cwd=project_dir,
                capture_output=True,
                timeout=120,
            )

        # Run the command
        proc = subprocess.run(
            command.split(),
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONPATH": project_dir},
        )

        result["stdout"] = proc.stdout[:2000] if proc.stdout else ""
        result["stderr"] = proc.stderr[:2000] if proc.stderr else ""
        result["return_code"] = proc.returncode

        # Check for errors even if exit code is 0 (some code catches and suppresses errors)
        stderr_lower = (proc.stderr or "").lower()
        has_suppressed_error = any(err in stderr_lower for err in ["error", "exception", "traceback", "failed"])

        result["passed"] = proc.returncode == 0 and not has_suppressed_error
        if has_suppressed_error and proc.returncode == 0:
            result["warning"] = "Exit code 0 but stderr contains error indicators"

    except subprocess.TimeoutExpired:
        result["error"] = f"Command timed out after {timeout}s"
    except Exception as e:
        result["error"] = str(e)

    return result


# =============================================================================
# API Verification Checks
# =============================================================================

def check_api_verify(project_dir: str, method: str, **kwargs) -> dict:
    """Verify data was logged to Freeplay via API."""
    result = {
        "check": "api_verify",
        "method": method,
        "passed": False,
    }

    api_key = os.environ.get("FREEPLAY_API_KEY")
    project_id = os.environ.get("FREEPLAY_PROJECT_ID")

    if not api_key or not project_id:
        result["skipped"] = True
        result["reason"] = "FREEPLAY_API_KEY or FREEPLAY_PROJECT_ID not set"
        return result

    try:
        api = FreeplayAPI()

        if method == "search_completions":
            result.update(verify_completion_logged(api))
        elif method == "check_prompt_exists":
            result.update(verify_prompt_exists(api, kwargs.get("prompt_name", "")))
        elif method == "check_completion_has_prompt":
            result.update(verify_completion_has_prompt(api))
        elif method == "check_prompt_has_variable":
            result.update(verify_prompt_has_variable(
                api,
                kwargs.get("prompt_name", ""),
                kwargs.get("variable_name", "")
            ))
        elif method == "check_dataset_exists":
            result.update(verify_dataset_exists(
                api,
                kwargs.get("prompt_name", ""),
                kwargs.get("dataset_name", "")
            ))
        elif method == "check_dataset_has_test_cases":
            result.update(verify_dataset_has_test_cases(
                api,
                kwargs.get("min_count", 1),
                kwargs.get("prompt_name", None),
                kwargs.get("dataset_name", None)
            ))
        elif method == "check_test_run_exists":
            result.update(verify_test_run_exists(
                api,
                kwargs.get("dataset_name", None)
            ))
        elif method == "check_test_run_has_sessions":
            result.update(verify_test_run_has_sessions(
                api,
                kwargs.get("min_count", 1)
            ))

    except urllib.error.HTTPError as e:
        result["api_reachable"] = True
        result["status_code"] = e.code
        result["error"] = str(e)
    except urllib.error.URLError as e:
        result["api_reachable"] = False
        result["error"] = str(e)
    except Exception as e:
        result["error"] = str(e)

    return result


def verify_completion_logged(api: FreeplayAPI) -> dict:
    """Check if a completion was logged since eval started."""
    timestamp_str = get_eval_start_timestamp()
    # Parse our filter timestamp for client-side comparison
    filter_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

    # Send filter to API (though it may not work server-side)
    filters = {"field": "start_time", "operator": "gte", "value": timestamp_str}

    resp = api.search_completions(filters)
    all_completions = resp["data"].get("data", [])

    # Client-side filter as fallback (API filter may not work reliably)
    recent_completions = []
    for c in all_completions:
        c_time = parse_completion_timestamp(c)
        if c_time and c_time >= filter_time:
            recent_completions.append(c)

    # If no completions pass client-side filter but we got results,
    # the API filter didn't work - use client-side count
    completion_count = len(recent_completions) if recent_completions or not all_completions else 0

    return {
        "api_reachable": True,
        "status_code": resp["status_code"],
        "completion_count": completion_count,
        "total_returned": len(all_completions),
        "since": timestamp_str,
        "passed": completion_count > 0,
    }


def verify_prompt_exists(api: FreeplayAPI, prompt_name: str) -> dict:
    """Check if a prompt template exists in Freeplay."""
    resp = api.list_prompt_templates()
    templates = resp["data"].get("data", [])
    found = any(t.get("name") == prompt_name for t in templates)

    return {
        "api_reachable": True,
        "status_code": resp["status_code"],
        "prompt_name": prompt_name,
        "template_count": len(templates),
        "found": found,
        "passed": found,
    }


def verify_completion_has_prompt(api: FreeplayAPI) -> dict:
    """Check if a recent completion has prompt info attached."""
    timestamp_str = get_eval_start_timestamp()
    filter_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

    # Send filter to API (though it may not work server-side)
    filters = {"field": "start_time", "operator": "gte", "value": timestamp_str}

    resp = api.search_completions(filters)
    all_completions = resp["data"].get("data", [])

    # Client-side filter for recent completions
    recent_completions = []
    for c in all_completions:
        c_time = parse_completion_timestamp(c)
        if c_time and c_time >= filter_time:
            recent_completions.append(c)

    has_prompt = False
    prompt_template = None
    for c in recent_completions:
        metadata = c.get("completion_metadata", {})
        if metadata.get("prompt_template"):
            has_prompt = True
            prompt_template = metadata.get("prompt_template")
            break

    return {
        "api_reachable": True,
        "status_code": resp["status_code"],
        "completion_count": len(recent_completions),
        "total_returned": len(all_completions),
        "since": timestamp_str,
        "has_prompt": has_prompt,
        "prompt_template": prompt_template,
        "passed": has_prompt,
    }


def verify_prompt_has_variable(api: FreeplayAPI, prompt_name: str, variable_name: str) -> dict:
    """Check if a prompt template contains a specific variable."""
    # First get the prompt template
    resp = api.list_prompt_templates()
    templates = resp["data"].get("data", [])
    template = None
    for t in templates:
        if t.get("name") == prompt_name:
            template = t
            break

    if not template:
        return {
            "api_reachable": True,
            "status_code": resp["status_code"],
            "prompt_name": prompt_name,
            "variable_name": variable_name,
            "found": False,
            "error": f"Prompt template '{prompt_name}' not found",
            "passed": False,
        }

    # Get the latest version to check for the variable
    latest_version_id = template.get("latest_template_version_id")
    template_id = template.get("id")

    if not latest_version_id or not template_id:
        return {
            "api_reachable": True,
            "status_code": resp["status_code"],
            "prompt_name": prompt_name,
            "variable_name": variable_name,
            "error": "Could not find latest version",
            "passed": False,
        }

    # Get the version details
    version_resp = api.get_prompt_template_version(template_id, latest_version_id)
    version_data = version_resp["data"]

    # Check if variable exists in content (messages)
    messages = version_data.get("content", [])
    variable_pattern = f"{{{{{variable_name}}}}}"
    has_variable = False

    for msg in messages:
        content = msg.get("content", "")
        if variable_pattern in content:
            has_variable = True
            break

    return {
        "api_reachable": True,
        "status_code": resp["status_code"],
        "prompt_name": prompt_name,
        "variable_name": variable_name,
        "template_id": template_id,
        "version_id": latest_version_id,
        "has_variable": has_variable,
        "passed": has_variable,
    }


def verify_dataset_exists(api: FreeplayAPI, prompt_name: str, dataset_name: str) -> dict:
    """Check if a specific dataset exists by name."""
    # Get datasets
    resp = api.list_prompt_datasets()
    datasets = resp["data"].get("data", [])

    # Look for exact dataset name match
    found = False
    dataset_id = None
    found_dataset_name = None

    for d in datasets:
        if d.get("name") == dataset_name:
            found = True
            dataset_id = d.get("id")
            found_dataset_name = d.get("name")
            break

    return {
        "api_reachable": True,
        "status_code": resp["status_code"],
        "prompt_name": prompt_name,
        "expected_dataset_name": dataset_name,
        "dataset_id": dataset_id,
        "dataset_name": found_dataset_name,
        "total_datasets": len(datasets),
        "found": found,
        "passed": found,
    }


def verify_dataset_has_test_cases(api: FreeplayAPI, min_count: int, prompt_name: str = None, dataset_name: str = None) -> dict:
    """Check if a specific dataset has at least min_count test cases."""
    # Get all datasets
    resp = api.list_prompt_datasets()
    datasets = resp["data"].get("data", [])

    if not datasets:
        return {
            "api_reachable": True,
            "status_code": resp["status_code"],
            "min_count": min_count,
            "error": "No datasets found",
            "passed": False,
        }

    # Find the specific dataset by name
    dataset = None
    if dataset_name:
        for d in datasets:
            if d.get("name") == dataset_name:
                dataset = d
                break

    # If not found by name, use first dataset
    if not dataset:
        dataset = datasets[0]

    dataset_id = dataset.get("id")
    found_dataset_name = dataset.get("name")

    # Get test cases
    test_cases_resp = api.get_dataset_test_cases(dataset_id)
    test_cases = test_cases_resp["data"].get("data", [])
    test_case_count = len(test_cases)

    return {
        "api_reachable": True,
        "status_code": resp["status_code"],
        "dataset_id": dataset_id,
        "dataset_name": found_dataset_name,
        "min_count": min_count,
        "test_case_count": test_case_count,
        "passed": test_case_count >= min_count,
    }


def verify_test_run_exists(api: FreeplayAPI, dataset_name: str = None) -> dict:
    """Check if a test run exists for the eval."""
    timestamp_str = get_eval_start_timestamp()
    filter_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    filter_timestamp = filter_time.timestamp()

    # Get all test runs
    resp = api.list_test_runs()
    test_runs = resp["data"].get("test_runs", [])

    # Filter for recent test runs created during this eval
    recent_test_runs = []
    for tr in test_runs:
        created_at = tr.get("created_at")
        if not created_at:
            continue

        # created_at is a Unix timestamp (integer)
        try:
            if isinstance(created_at, (int, float)):
                if created_at >= filter_timestamp:
                    recent_test_runs.append(tr)
        except (ValueError, TypeError):
            continue

    return {
        "api_reachable": True,
        "status_code": resp["status_code"],
        "test_run_count": len(recent_test_runs),
        "total_test_runs": len(test_runs),
        "since": timestamp_str,
        "test_run_ids": [tr.get("id") for tr in recent_test_runs],
        "passed": len(recent_test_runs) > 0,
    }


def verify_test_run_has_sessions(api: FreeplayAPI, min_count: int) -> dict:
    """Check if recent test runs have sessions (executions)."""
    timestamp_str = get_eval_start_timestamp()
    filter_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    filter_timestamp = filter_time.timestamp()

    # Get all test runs
    resp = api.list_test_runs()
    test_runs = resp["data"].get("test_runs", [])

    # Filter for recent test runs
    recent_test_runs = []
    for tr in test_runs:
        created_at = tr.get("created_at")
        if not created_at:
            continue

        try:
            if isinstance(created_at, (int, float)):
                if created_at >= filter_timestamp:
                    recent_test_runs.append(tr)
        except (ValueError, TypeError):
            continue

    if not recent_test_runs:
        return {
            "api_reachable": True,
            "status_code": resp["status_code"],
            "error": "No recent test runs found",
            "passed": False,
        }

    # Get the most recent test run and check its session count
    most_recent = recent_test_runs[0]
    test_run_id = most_recent.get("id")

    # Get detailed test run info
    try:
        tr_resp = api.get_test_run(test_run_id)
        tr_data = tr_resp["data"]
        sessions_count = tr_data.get("sessions_count", 0)

        return {
            "api_reachable": True,
            "status_code": resp["status_code"],
            "test_run_id": test_run_id,
            "test_run_name": most_recent.get("name"),
            "sessions_count": sessions_count,
            "min_count": min_count,
            "passed": sessions_count >= min_count,
        }
    except Exception as e:
        return {
            "api_reachable": True,
            "status_code": resp["status_code"],
            "test_run_id": test_run_id,
            "error": f"Failed to get test run details: {str(e)}",
            "passed": False,
        }


# =============================================================================
# Scoring
# =============================================================================

def calculate_score(scenario: dict, check_results: list[dict]) -> dict:
    """Calculate total score based on check results and scoring rubric."""
    scoring = scenario.get("scoring", {})
    scores = {}

    # Map check types/methods to scoring categories
    check_to_category = {
        ("file_contains", ""): "code_modified",
        ("code_runs", ""): "code_runs",
        ("api_verify", "search_completions"): "completion_logged",
        ("api_verify", "check_prompt_exists"): "prompt_created",
        ("api_verify", "check_completion_has_prompt"): "completion_has_prompt",
        ("api_verify", "check_prompt_has_variable"): "prompt_has_variable",
        ("api_verify", "check_dataset_exists"): "dataset_created",
        ("api_verify", "check_dataset_has_test_cases"): "test_cases_added",
        ("api_verify", "check_test_run_exists"): "test_run_created",
        ("api_verify", "check_test_run_has_sessions"): "test_run_executed",
    }

    for check in check_results:
        check_type = check.get("check", "")
        method = check.get("method", "")
        key = (check_type, method if check_type == "api_verify" else "")
        category = check_to_category.get(key)

        if not category or category not in scoring:
            continue

        max_points = scoring[category]["points"]

        if check.get("skipped"):
            scores[category] = {
                "passed": None,
                "skipped": True,
                "reason": check.get("reason"),
                "points": 0,
                "max_points": max_points,
            }
        else:
            passed = check.get("passed", False)
            scores[category] = {
                "passed": passed,
                "points": max_points if passed else 0,
                "max_points": max_points,
            }

    total = sum(d.get("points", 0) for d in scores.values())
    max_total = sum(d.get("max_points", 0) for d in scores.values())

    return {
        "categories": scores,
        "total": total,
        "max_total": max_total,
        "percentage": round(total / max_total * 100, 1) if max_total > 0 else 0,
    }


# =============================================================================
# Main
# =============================================================================

def verify_scenario(scenario_name: str, project_dir: str) -> dict:
    """Run all verification checks for a scenario."""
    scenario = load_scenario(scenario_name)
    results = []

    for criterion in scenario.get("success_criteria", []):
        check_type = criterion.get("type")

        if check_type == "file_contains":
            result = check_file_contains(
                project_dir,
                criterion.get("file", ""),
                criterion.get("patterns", []),
            )
        elif check_type == "code_runs":
            result = check_code_runs(
                project_dir,
                criterion.get("command", "python main.py"),
                criterion.get("timeout", 60),
            )
        elif check_type == "api_verify":
            result = check_api_verify(
                project_dir,
                criterion.get("method", ""),
                prompt_name=criterion.get("prompt_name", ""),
                variable_name=criterion.get("variable_name", ""),
                dataset_name=criterion.get("dataset_name", ""),
                min_count=criterion.get("min_count", 1),
            )
        else:
            result = {
                "check": check_type,
                "error": f"Unknown check type: {check_type}",
                "passed": False,
            }

        result["description"] = criterion.get("description", "")
        results.append(result)

    return {
        "scenario": scenario_name,
        "checks": results,
        "score": calculate_score(scenario, results),
    }


def main():
    if len(sys.argv) < 4:
        print("Usage: verify.py <scenario> <project_dir> <mode> [output_file]")
        sys.exit(1)

    scenario_name = sys.argv[1]
    project_dir = sys.argv[2]
    mode = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) > 4 else None

    print(f"Verifying scenario: {scenario_name}")
    print(f"Project directory: {project_dir}")
    print(f"Mode: {mode}")
    print()

    results = verify_scenario(scenario_name, project_dir)
    results["mode"] = mode
    results["timestamp"] = datetime.utcnow().isoformat() + "Z"
    results["project_dir"] = project_dir

    # Add timing info from runner
    results["timing"] = {
        "start_time": os.environ.get("EVAL_START_TIME"),
        "end_time": os.environ.get("EVAL_END_TIME"),
        "duration_seconds": int(os.environ.get("EVAL_DURATION_SECS", 0)),
    }

    # Print check results
    print("=== Check Results ===")
    for check in results["checks"]:
        status = "✓" if check.get("passed") else ("⊘" if check.get("skipped") else "✗")
        print(f"{status} {check.get('description', check.get('check'))}")
        if check.get("error"):
            print(f"  Error: {check['error']}")
        if check.get("missing"):
            print(f"  Missing patterns: {check['missing']}")
        if check.get("skipped"):
            print(f"  Skipped: {check.get('reason')}")

    print()
    print("=== Score ===")
    score = results["score"]
    for category, data in score["categories"].items():
        status = "✓" if data.get("passed") else ("⊘" if data.get("skipped") else "✗")
        print(f"{status} {category}: {data['points']}/{data['max_points']}")

    print(f"\nTotal: {score['total']}/{score['max_total']} ({score['percentage']}%)")

    # Print timing
    timing = results.get("timing", {})
    if timing.get("duration_seconds"):
        duration = timing["duration_seconds"]
        minutes, seconds = divmod(duration, 60)
        if minutes:
            print(f"Duration: {minutes}m {seconds}s")
        else:
            print(f"Duration: {seconds}s")

    # Save results to file
    if output_file:
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {output_file}")

    # Return exit code based on whether all non-skipped checks passed
    all_passed = all(
        check.get("passed") or check.get("skipped")
        for check in results["checks"]
    )
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
