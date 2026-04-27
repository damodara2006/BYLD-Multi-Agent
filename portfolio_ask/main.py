from __future__ import annotations

import sys
from typing import Any

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from portfolio_ask.agent import run_agent

console = Console()

_BANNER = r"""
██████╗ ██╗   ██╗██╗     ██████╗     ██╗    ██╗███████╗ █████╗ ██╗  ████████╗██╗  ██╗
██╔══██╗╚██╗ ██╔╝██║     ██╔══██╗    ██║    ██║██╔════╝██╔══██╗██║  ╚══██╔══╝██║  ██║
██████╔╝ ╚████╔╝ ██║     ██║  ██║    ██║ █╗ ██║█████╗  ███████║██║     ██║   ███████║
██╔══██╗  ╚██╔╝  ██║     ██║  ██║    ██║███╗██║██╔══╝  ██╔══██║██║     ██║   ██╔══██║
██████╔╝   ██║   ███████╗██████╔╝    ╚███╔███╔╝███████╗██║  ██║███████╗██║   ██║  ██║
╚═════╝    ╚═╝   ╚══════╝╚═════╝      ╚══▀══╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝
"""


def _render_banner() -> None:
    banner_text = Text(_BANNER, style="bold blue")
    subtitle = Text("Portfolio Intelligence Engine", style="italic dim blue")
    console.print(Panel.fit(
        Text.assemble(banner_text, "\n", subtitle),
        title="BYLD QUEST",
        title_align="center",
        border_style="blue",
        padding=(1, 3),
        box=box.ROUNDED
    ))


def _risk_style(risk_level: str) -> str:
    lowered = risk_level.lower()
    if lowered == "high":
        return "bold red"
    if lowered == "medium":
        return "bold yellow"
    if lowered == "low":
        return "bold green"
    return "white"


def _render_ranked_table(ranked_items: list[dict[str, Any]]) -> None:
    table = Table(
        title="Ranked Holdings by Impact",
        box=box.ROUNDED,
        header_style="bold white on blue",
        title_style="bold blue",
        border_style="blue"
    )
    table.add_column("Ticker", style="bold blue")
    table.add_column("Rationale", overflow="fold", style="black")
    table.add_column("Weight (%)", justify="right", style="bold blue")
    table.add_column("Risk Level", justify="center")

    if not ranked_items:
        table.add_row("-", "No ranked items were returned.", "-", "-")
        console.print(table)
        return

    for item in ranked_items:
        ticker = str(item.get("ticker", "-"))
        rationale = str(item.get("rationale", "-"))
        weight_value = item.get("exposure_weight", 0)
        try:
            weight_percent = f"{float(weight_value) * 100:.1f}%"
        except (TypeError, ValueError):
            weight_percent = "-"
        risk_level = str(item.get("risk_level", "-")).title()
        risk_style = _risk_style(risk_level)
        risk_text = Text(risk_level, style=risk_style)
        table.add_row(ticker, rationale, weight_percent, risk_text)

    console.print(table)


def _render_summary(summary: str) -> None:
    console.print(
        Panel(
            Markdown(summary),
            title="Summary",
            title_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )


def _render_sources(sources: list[str]) -> None:
    source_text = "\n".join(f"  {source}" for source in sources) if sources else "  No sources were returned."
    console.print(
        Panel(
            Text(source_text, style="black"),
            title="Sources",
            title_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )


def _render_trace(trace: list[str]) -> None:
    if not trace:
        return
    trace_text = "\n".join(f"  > {entry}" for entry in trace)
    console.print(
        Panel(
            Text(trace_text, style="black"),
            title="Execution Trace",
            title_align="left",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )


def main() -> None:
    """CLI entry point for BYLD Multi-Agent."""
    argv = sys.argv[1:]

    if not argv:
        console.print(
            Panel(
                "[bold blue]Example:[/bold blue] [blue]python -m portfolio_ask 'What is my tech exposure?'[/blue]",
                title="Missing Query",
                border_style="red",
                box=box.ROUNDED,
                padding=(1, 2),
                )
        )
        raise SystemExit(1)

    print_trace = False
    filtered_args: list[str] = []
    for arg in argv:
        if arg == "--trace":
            print_trace = True
        else:
            filtered_args.append(arg)

    query = " ".join(filtered_args).strip()

    _render_banner()
    console.print(Panel.fit(
        f"[bold blue]Question:[/bold blue] [black]{query}[/black]",
        border_style="blue",
        box=box.ROUNDED,
        padding=(0, 1),
        style="on black"
    ))

    with console.status("[bold blue]Analyzing query...[/bold blue]", spinner="dots") as status:
        def update_status(node_name: str) -> None:
            friendly_map = {
                "retrieving context": "Fetching News",
                "cross-referencing": "Mapping Holdings",
                "ranking assets": "Ranking Assets",
                "finalizing output": "Generating Output",
            }
            friendly_name = friendly_map.get(node_name, node_name.replace("_", " ").title())
            status.update(f"[bold blue]{friendly_name}...[/bold blue]")

        result = run_agent(
            query=query,
            print_trace=print_trace,
            progress_callback=update_status,
        )

    payload = result.model_dump()
    _render_summary(str(payload.get("summary", "")))
    _render_ranked_table(list(payload.get("ranked_items", [])))
    _render_sources(list(payload.get("sources", [])))
    _render_trace(list(payload.get("trace", [])))
    console.print()
    console.print(Panel(
        "[dim black]Machine-readable JSON response[/dim black]",
        title="Raw Data",
        title_align="center",
        border_style="blue",
        box=box.ROUNDED,
        padding=(0, 1)
    ))
    console.print_json(result.model_dump_json(indent=2))
    console.print(Panel("[bold blue]Query Complete[/bold blue]", border_style="blue", box=box.ROUNDED))


if __name__ == "__main__":
    main()
