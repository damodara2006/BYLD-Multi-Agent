from __future__ import annotations

import json
import sys

from portfolio_ask.agent import run_agent
from rich.console import Console


console = Console()


def main() -> None:
    """CLI entry point for BYLD Multi-Agent."""
    argv = sys.argv[1:]

    if not argv:
        error_payload = {
            "error": "missing_query",
            "message": "Provide a query. Example: python -m portfolio_ask 'What is my risk exposure?'",
        }
        print(json.dumps(error_payload, indent=2))
        raise SystemExit(1)

    print_trace = False
    filtered_args: list[str] = []
    for arg in argv:
        if arg == "--trace":
            print_trace = True
        else:
            filtered_args.append(arg)

    query = " ".join(filtered_args).strip()

    with console.status("[bold cyan]Agent: initializing...[/bold cyan]", spinner="dots") as status:
        def update_status(node_name: str) -> None:
            status.update(f"[bold cyan]Agent: {node_name}...[/bold cyan]")

        result = run_agent(
            query=query,
            print_trace=print_trace,
            progress_callback=update_status,
        )

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
