#!/usr/bin/env python3
"""
Comparison script for Freeplay plugin evaluation results.

Compares baseline vs with-plugin results and generates a report.
"""

import json
import sys
from pathlib import Path


def load_results(file_path: str) -> dict:
    """Load results from JSON file."""
    with open(file_path) as f:
        return json.load(f)


def compare_results(baseline: dict, with_plugin: dict) -> dict:
    """Compare two evaluation results."""
    comparison = {
        "scenario": baseline.get("scenario"),
        "baseline": {
            "mode": baseline.get("mode"),
            "timestamp": baseline.get("timestamp"),
            "score": baseline.get("score", {}),
        },
        "with_plugin": {
            "mode": with_plugin.get("mode"),
            "timestamp": with_plugin.get("timestamp"),
            "score": with_plugin.get("score", {}),
        },
        "improvements": [],
        "regressions": [],
        "unchanged": [],
    }

    # Compare individual categories
    baseline_cats = baseline.get("score", {}).get("categories", {})
    plugin_cats = with_plugin.get("score", {}).get("categories", {})

    all_categories = set(baseline_cats.keys()) | set(plugin_cats.keys())

    for category in all_categories:
        base_data = baseline_cats.get(category, {"passed": False, "points": 0})
        plugin_data = plugin_cats.get(category, {"passed": False, "points": 0})

        # Handle skipped checks
        if base_data.get("skipped") and plugin_data.get("skipped"):
            comparison["unchanged"].append({
                "category": category,
                "status": "skipped",
                "reason": plugin_data.get("reason"),
            })
        elif not base_data.get("passed") and plugin_data.get("passed"):
            comparison["improvements"].append({
                "category": category,
                "baseline": base_data.get("points", 0),
                "with_plugin": plugin_data.get("points", 0),
                "delta": plugin_data.get("points", 0) - base_data.get("points", 0),
            })
        elif base_data.get("passed") and not plugin_data.get("passed"):
            comparison["regressions"].append({
                "category": category,
                "baseline": base_data.get("points", 0),
                "with_plugin": plugin_data.get("points", 0),
                "delta": plugin_data.get("points", 0) - base_data.get("points", 0),
            })
        else:
            comparison["unchanged"].append({
                "category": category,
                "status": "passed" if base_data.get("passed") else "failed",
                "points": base_data.get("points", 0),
            })

    # Overall score comparison
    base_score = baseline.get("score", {})
    plugin_score = with_plugin.get("score", {})

    comparison["summary"] = {
        "baseline_total": base_score.get("total", 0),
        "plugin_total": plugin_score.get("total", 0),
        "delta": plugin_score.get("total", 0) - base_score.get("total", 0),
        "baseline_percentage": base_score.get("percentage", 0),
        "plugin_percentage": plugin_score.get("percentage", 0),
        "percentage_delta": plugin_score.get("percentage", 0) - base_score.get("percentage", 0),
    }

    return comparison


def print_comparison(comparison: dict):
    """Print a formatted comparison report."""
    print("=" * 60)
    print(f"EVALUATION COMPARISON: {comparison['scenario']}")
    print("=" * 60)
    print()

    # Score summary
    summary = comparison["summary"]
    print("OVERALL SCORES")
    print("-" * 40)
    print(f"{'Metric':<25} {'Baseline':>10} {'Plugin':>10} {'Delta':>10}")
    print("-" * 40)
    print(f"{'Total Points':<25} {summary['baseline_total']:>10} {summary['plugin_total']:>10} {summary['delta']:>+10}")
    print(f"{'Percentage':<25} {summary['baseline_percentage']:>9}% {summary['plugin_percentage']:>9}% {summary['percentage_delta']:>+9}%")
    print()

    # Improvements
    if comparison["improvements"]:
        print("✓ IMPROVEMENTS (Plugin passed where baseline failed)")
        print("-" * 40)
        for item in comparison["improvements"]:
            print(f"  • {item['category']}: {item['baseline']} → {item['with_plugin']} (+{item['delta']})")
        print()

    # Regressions
    if comparison["regressions"]:
        print("✗ REGRESSIONS (Baseline passed where plugin failed)")
        print("-" * 40)
        for item in comparison["regressions"]:
            print(f"  • {item['category']}: {item['baseline']} → {item['with_plugin']} ({item['delta']})")
        print()

    # Unchanged
    if comparison["unchanged"]:
        print("= UNCHANGED")
        print("-" * 40)
        for item in comparison["unchanged"]:
            status = item.get("status", "unknown")
            if status == "skipped":
                print(f"  ⊘ {item['category']}: skipped ({item.get('reason', 'unknown reason')})")
            else:
                print(f"  {'✓' if status == 'passed' else '✗'} {item['category']}: {status}")
        print()

    # Verdict
    print("=" * 60)
    delta = summary["delta"]
    if delta > 0:
        print(f"VERDICT: Plugin IMPROVED score by {delta} points ({summary['percentage_delta']:+.1f}%)")
    elif delta < 0:
        print(f"VERDICT: Plugin REDUCED score by {abs(delta)} points ({summary['percentage_delta']:.1f}%)")
    else:
        print("VERDICT: No change in score")
    print("=" * 60)


def main():
    if len(sys.argv) < 3:
        print("Usage: compare.py <baseline_results.json> <with_plugin_results.json>")
        print()
        print("Example:")
        print("  python compare.py results/integration-simple-baseline.json results/integration-simple-with-plugin.json")
        sys.exit(1)

    baseline_file = sys.argv[1]
    plugin_file = sys.argv[2]

    if not Path(baseline_file).exists():
        print(f"Error: Baseline file not found: {baseline_file}")
        sys.exit(1)

    if not Path(plugin_file).exists():
        print(f"Error: Plugin file not found: {plugin_file}")
        sys.exit(1)

    baseline = load_results(baseline_file)
    with_plugin = load_results(plugin_file)

    comparison = compare_results(baseline, with_plugin)
    print_comparison(comparison)

    # Optionally save comparison to file
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
        with open(output_file, "w") as f:
            json.dump(comparison, f, indent=2)
        print(f"\nComparison saved to: {output_file}")


if __name__ == "__main__":
    main()
