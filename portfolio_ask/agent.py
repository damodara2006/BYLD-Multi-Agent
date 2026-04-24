from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, TypedDict, cast

from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph
from rich.console import Console
from rich.text import Text

from portfolio_ask.llm import get_fallback_response, get_llm
from portfolio_ask.schemas import GeneralQA, NewsImpact
from portfolio_ask.vector_store import CHROMA_PATH, build_vector_store, get_vector_store

console = Console()

# Global pointer for CLI progress updates
_NODE_PROGRESS_CALLBACK: Callable[[str], None] | None = None

class AgentState(TypedDict):
    query: str
    query_type: str
    retrieved_docs: list[Document]
    portfolio_data: list[dict[str, Any]]
    ranked_items: list[dict[str, Any]]
    final_response: GeneralQA | NewsImpact | None
    trace_log: list[str]

def _emit_node_heartbeat(node_name: str, message: str) -> None:
    """Emit a visible node heartbeat and update optional CLI status."""
    style_map = {
        "retrieving context": "bold green",
        "cross-referencing": "bold cyan",
        "ranking assets": "bold yellow",
        "finalizing output": "bold magenta",
    }
    label_style = style_map.get(node_name, "bold blue")
    console.print(Text("Node: ", style=label_style) + Text(message))
    if _NODE_PROGRESS_CALLBACK is not None:
        _NODE_PROGRESS_CALLBACK(node_name)

def detect_query_type(query: str) -> str:
    """Detect if the user asks for news impact or general Q&A."""
    lowered_query = query.lower()
    tax_keywords = ["tax", "ltcg", "xirr", "glossary"]
    if any(kw in lowered_query for kw in tax_keywords):
        return "general_qa"
    full_portfolio_keywords = ["all holdings", "entire portfolio", "list everything", "all my stocks", "list all my holdings", "list my holdings"]
    if any(kw in lowered_query for kw in full_portfolio_keywords):
        return "full_portfolio"
    risk_keywords = ["low risk", "safe", "defensive", "risk level"]
    if any(kw in lowered_query for kw in risk_keywords):
        return "risk_query"
    impact_keywords = ["impact", "news", "affected", "affect", "rank", "exposure", "holdings", "stocks", "sector", "positioned", "portfolio", "performance"]
    if any(kw in lowered_query for kw in impact_keywords):
        return "news_impact"
    return "general_qa"

def retrieve_node(state: AgentState) -> AgentState:
    """Step 1: Retrieve relevant chunks from Chroma vector store."""
    _emit_node_heartbeat("retrieving context", "Fetching relevant news and glossary chunks...")
    
    trace_log = list(state["trace_log"])
    trace_log.append("retrieve: entered retrieval node")

    if not os.path.exists(CHROMA_PATH):
        trace_log.append("retrieve: vector store not found, building index")
        build_vector_store()

    vector_store = get_vector_store()
    # We fetch k=6 to provide enough context for complex Indian tech/wealth queries
    docs = vector_store.similarity_search(state["query"], k=6)
    trace_log.append(f"retrieve: fetched {len(docs)} chunks")

    return {**state, "retrieved_docs": docs, "trace_log": trace_log}

def cross_reference_node(state: AgentState) -> AgentState:
    """Step 2: Map retrieved text to actual portfolio holdings."""
    _emit_node_heartbeat("cross-referencing", "Mapping news to your portfolio holdings...")
    
    trace_log = list(state["trace_log"])
    trace_log.append("cross_reference: loading portfolio data")

    portfolio_path = Path("data/portfolio.json")
    portfolio_data: list[dict[str, Any]] = []
    if portfolio_path.exists():
        with portfolio_path.open("r", encoding="utf-8") as file:
            portfolio_data = cast(list[dict[str, Any]], json.load(file))
    
    query_type = state["query_type"]
    mapped_holdings: list[dict[str, Any]] = []

    # Global bypass: for full_portfolio and risk_query requests, skip text-based filtering
    if query_type in {"full_portfolio", "risk_query"}:
        mapped_holdings = portfolio_data
    else:
        retrieved_text = "\n".join(doc.page_content for doc in state["retrieved_docs"])
        # Identify which of our holdings are mentioned in the retrieved news
        for item in portfolio_data:
            ticker = str(item.get("ticker", ""))
            if ticker and ticker in retrieved_text:
                mapped_holdings.append({
                    "ticker": ticker,
                    "holding_name": str(item.get("holding_name", "")),
                    "quantity": int(item.get("quantity", 0)),
                    "current_price": float(item.get("current_price", 0.0)),
                    "instrument_type": str(item.get("instrument_type", "")),
                    "sector": str(item.get("sector", "")),
                })

    trace_log.append(f"cross_reference: mapped {len(mapped_holdings)} holdings to context")

    return {**state, "portfolio_data": portfolio_data, "ranked_items": mapped_holdings, "trace_log": trace_log}

def rank_node(state: AgentState) -> AgentState:
    """Step 3: Calculate exposure weights for the identified holdings."""
    _emit_node_heartbeat("ranking assets", "Calculating portfolio exposure and impact weights...")
    
    trace_log = list(state["trace_log"])
    trace_log.append("rank: started ranking by weight")

    mapped_items = list(state["ranked_items"])
    total_value = sum(float(i["quantity"]) * float(i["current_price"]) for i in mapped_items)

    ranked_final: list[dict[str, Any]] = []
    for item in mapped_items:
        item_value = float(item["quantity"]) * float(item["current_price"])
        weight = round(item_value / total_value, 4) if total_value > 0 else 0.0

        ranked_final.append({
            "ticker": item["ticker"],
            "rationale": f"Market context suggests impact on {item['sector']} ({item['instrument_type']}).",
            "exposure_weight": weight,
        })

    ranked_final.sort(key=lambda x: x["exposure_weight"], reverse=True)
    trace_log.append(f"rank: ranked {len(ranked_final)} items")

    return {**state, "ranked_items": ranked_final, "trace_log": trace_log}

def format_node(state: AgentState) -> AgentState:
    """Step 4: Generate final structured response via LLM or Fallback."""
    _emit_node_heartbeat("finalizing output", "Generating structured JSON (Inference phase)...")
    
    trace_log = list(state["trace_log"])
    trace_log.append("format: preparing final output")

    # Deduplicate sources
    sources = sorted({str(doc.metadata.get("source", "unknown")) for doc in state["retrieved_docs"]})
    schema_cls = NewsImpact if state["query_type"] in {"news_impact", "full_portfolio"} else GeneralQA

    context_block = "\n\n".join(doc.page_content for doc in state["retrieved_docs"])
    ranked_block = json.dumps(state["ranked_items"], indent=2)

    prompt = (
        "You are a specialized Wealth-Tech Analyst for BYLD Wealth.\n"
        "Generate a strictly structured response based on the following data:\n\n"
        f"USER QUERY: {state['query']}\n"
        f"CONTEXT: {context_block}\n"
        f"PORTFOLIO MATCHES: {ranked_block}\n\n"
        "Ensure the response matches the schema exactly. No conversational filler.\n"
        "CRITICAL: You must provide a clear, narrative explanation of the answer in the 'summary' field, especially for tax or glossary-related queries. If the user asks for an explanation (like LTCG), synthesize the retrieved glossary definitions into the summary.\n"
        "CRITICAL: Do not provide a 'meta' summary. Instead of saying 'I will analyze...', provide the actual analysis immediately based on the data. Be direct and insightful.\n"
        "NEGATIVE CONSTRAINT: If a ticker mentioned in the query is NOT present in the 'Cross referenced ranked items' block, you MUST explicitly state that the user does not hold that specific ticker. DO NOT attribute weights or data from other holdings to tickers the user does not own.\n"
        "GLOBAL BYPASS: If the query type is 'full_portfolio', you are receiving the complete list of assets. Categorize every single one of them into Low, Medium, or High risk based on their sector and instrument type (e.g., Bonds are Low, Growth Tech is High).\n"
        "For every item in the 'ranked_items' list, you MUST determine the 'risk_level' (Low, Medium, or High) based on the asset type and sector. Ensure this is populated for every ticker."
    )

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(schema_cls)
        response = structured_llm.invoke(prompt)
        
        # Inject our internal trace and sources into the LLM's response
        final_response = response.model_copy(update={"sources": sources, "trace": trace_log})
        trace_log.append("format: successfully generated via local LLM")
        
    except Exception as exc:
        trace_log.append(f"format: LLM unavailable, using deterministic fallback ({type(exc).__name__})")
        fallback = get_fallback_response(state["query"], schema_cls)
        ranked_items = list(state.get("ranked_items", []))
        tickers = [str(item.get("ticker", "")) for item in ranked_items if str(item.get("ticker", ""))]
        fallback_summary = (
            "LLM Inference failed, but your portfolio identifies potential impacts on: "
            f"{', '.join(tickers) if tickers else 'no specific tickers were identified'}. "
            "Please check current news for these specific holdings."
        )
        # Ensure fallbacks also have the correct metadata
        final_response = fallback.model_copy(
            update={
                "summary": fallback_summary,
                "ranked_items": ranked_items,
                "sources": sources or ["data/portfolio.json"],
                "trace": trace_log,
            }
        )

    return {**state, "final_response": final_response, "trace_log": trace_log}

def build_graph() -> Any:
    """Assemble the nodes into a compiled StateGraph."""
    graph = StateGraph(AgentState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("cross_reference", cross_reference_node)
    graph.add_node("rank", rank_node)
    graph.add_node("format", format_node)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "cross_reference")
    graph.add_edge("cross_reference", "rank")
    graph.add_edge("rank", "format")
    graph.add_edge("format", END)

    return graph.compile()

def run_agent(
    query: str, 
    print_trace: bool = False, 
    progress_callback: Callable[[str], None] | None = None
) -> GeneralQA | NewsImpact:
    """Orchestrate the agent run with clean cleanup of global callbacks."""
    global _NODE_PROGRESS_CALLBACK
    _NODE_PROGRESS_CALLBACK = progress_callback

    try:
        app = build_graph()
        initial_state: AgentState = {
            "query": query,
            "query_type": detect_query_type(query),
            "retrieved_docs": [],
            "portfolio_data": [],
            "ranked_items": [],
            "final_response": None,
            "trace_log": ["agent: system initialized"],
        }

        result = app.invoke(initial_state)
        final = cast(GeneralQA | NewsImpact, result.get("final_response"))

        if print_trace:
            console.print("\n[bold yellow]Full Execution Trace:[/bold yellow]")
            for entry in result.get("trace_log", []):
                console.print(f"  > {entry}")

        return final
    finally:
        # Prevent memory leaks or callback pollution
        _NODE_PROGRESS_CALLBACK = None