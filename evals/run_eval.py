from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import argparse

import yaml
from pydantic import ValidationError

from portfolio_ask.agent import run_agent
from portfolio_ask.schemas import GeneralQA, NewsImpact


def load_cases(cases_path: Path) -> list[dict[str, Any]]:
    """Load evaluation cases from YAML file."""
    with cases_path.open("r", encoding="utf-8") as file:
        payload = yaml.safe_load(file)

    if not isinstance(payload, dict) or "cases" not in payload:
        raise ValueError("cases.yaml must contain a top-level 'cases' key.")

    cases = payload["cases"]
    if not isinstance(cases, list):
        raise ValueError("'cases' must be a list.")

    if len(cases) != 5:
        raise ValueError("cases.yaml must define exactly 5 test cases.")

    return cases


def validate_output(expected_schema: str, result: Any) -> None:
    """Validate result against expected schema using strict Pydantic checks."""
    raw = result.model_dump()

    if expected_schema == "GeneralQA":
        GeneralQA.model_validate(raw)
    elif expected_schema == "NewsImpact":
        NewsImpact.model_validate(raw)
    else:
        raise AssertionError(f"Unknown schema requested: {expected_schema}")


def print_trace_lines(trace: list[str]) -> None:
    """Print execution trace lines in a neat format."""
    print("  trace:")
    for item in trace:
        print(f"    - {item}")


def main() -> None:
    """Run evaluation suite and print PASS/FAIL summary."""
    parser = argparse.ArgumentParser(description="Run BYLD-Multi-Agent evaluation suite")
    parser.add_argument('--case', help='Run only the specified case by id')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    cases_path = root / "evals" / "cases.yaml"

    all_cases = load_cases(cases_path)

    if args.case:
        cases = [c for c in all_cases if c.get('id') == args.case]
        if not cases:
            print(f"Case '{args.case}' not found in cases.yaml")
            return
    else:
        cases = all_cases

    passed = 0
    failed = 0

    print("Running BYLD-Multi-Agent evaluation suite")
    print("=" * 50)

    for index, case in enumerate(cases, start=1):
        case_id = str(case.get("id", f"case_{index}"))
        query = str(case["query"])
        expected_schema = str(case["expected_schema"])
        print_trace = bool(case.get("print_trace", False))
        force_fallback = bool(case.get("force_fallback", False))

        print(f"[{index}/{len(cases)}] {case_id}")
        print(f"  query: {query}")
        print(f"  expected: {expected_schema}")

        previous_force = os.environ.get("BYLD_FORCE_FALLBACK")

        try:
            if force_fallback:
                os.environ["BYLD_FORCE_FALLBACK"] = "1"

            result = run_agent(query=query, print_trace=False)

            validate_output(expected_schema=expected_schema, result=result)

            if force_fallback:
                assert result.query_type == "heuristic_fallback", (
                    "Expected heuristic fallback response when force_fallback is true."
                )
                if isinstance(result, GeneralQA):
                    assert "FMCG" in result.summary or "Bond" in result.summary, (
                        "Fallback risk answer should mention FMCG or Bond defensive signals."
                    )

            if print_trace:
                print_trace_lines(result.trace)

            print("  status: PASS")
            passed += 1
        except (AssertionError, ValidationError, Exception) as exc:  # noqa: BLE001
            print(f"  status: FAIL ({type(exc).__name__}: {exc})")
            failed += 1
        finally:
            if previous_force is None:
                os.environ.pop("BYLD_FORCE_FALLBACK", None)
            else:
                os.environ["BYLD_FORCE_FALLBACK"] = previous_force

    print("=" * 50)
    print(f"PASS: {passed}")
    print(f"FAIL: {failed}")

    if not args.case:
        assert failed == 0, "One or more eval cases failed."


if __name__ == "__main__":
    main()
