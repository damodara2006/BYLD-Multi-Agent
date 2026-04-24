from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, TypedDict, cast

from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph

from portfolio_ask.llm import get_fallback_response, get_llm
from portfolio_ask.schemas import GeneralQA, NewsImpact
from portfolio_ask.vector_store import CHROMA_PATH, build_vector_store, get_vector_store


class AgentState(TypedDict):
    query: str
    query_type: str
    retrieved_docs: list[Document]
    portfolio_data: list[dict[str, Any]]
    ranked_items: list[dict[str, Any]]
    final_response: GeneralQA | NewsImpact | None
    trace_log: list[str]


def detect_query_type(query: str) -> str:
    """Detect if the user asks for news impact or general Q&A."""
    lowered_query = query.lower()
    impact_keywords = ["impact", "news", "affected", "affect", "rank"]
    for keyword in impact_keywords:
        if keyword in lowered_query:
            return "news_impact"
    return "general_qa"


def retrieve_node(state: AgentState) -> AgentState:
    """Retrieve relevant chunks from Chroma vector store."""
    trace_log = list(state["trace_log"])
    trace_log.append("retrieve: entered retrieval node")

    if not os.path.exists(CHROMA_PATH):
        trace_log.append("retrieve: vector store not found, building index")
        build_vector_store()

    vector_store = get_vector_store()
    docs = vector_store.similarity_search(state["query"], k=6)
    trace_log.append(f"retrieve: fetched {len(docs)} chunks")

    return {
        **state,
        "retrieved_docs": docs,
        "trace_log": trace_log,
    }


def cross_reference_node(state: AgentState) -> AgentState:
    """Load portfolio and map retrieved text to holdings by ticker mention."""
    trace_log = list(state["trace_log"])
    trace_log.append("cross_reference: loading portfolio data")

    portfolio_path = Path("data/portfolio.json")
    portfolio_data: list[dict[str, Any]] = []
    if portfolio_path.exists():
        with portfolio_path.open("r", encoding="utf-8") as file:
            portfolio_data = cast(list[dict[str, Any]], json.load(file))
    trace_log.append(f"cross_reference: loaded {len(portfolio_data)} holdings")

    retrieved_text = "\n".join(doc.page_content for doc in state["retrieved_docs"])
    ranked_seed: list[dict[str, Any]] = []

    for item in portfolio_data:
        ticker = str(item.get("ticker", ""))
        if ticker and ticker in retrieved_text:
            ranked_seed.append(
                {
                    "ticker": ticker,
                    "holding_name": str(item.get("holding_name", "")),
                    "quantity": int(item.get("quantity", 0)),
                    "current_price": float(item.get("current_price", 0.0)),
                    "instrument_type": str(item.get("instrument_type", "")),
                    "sector": str(item.get("sector", "")),
                }
            )

    trace_log.append(f"cross_reference: mapped {len(ranked_seed)} holdings to retrieved text")

    return {
        **state,
        "portfolio_data": portfolio_data,
        "ranked_items": ranked_seed,
        "trace_log": trace_log,
    }


def rank_node(state: AgentState) -> AgentState:
    """Rank mapped holdings by simple exposure weight."""
    trace_log = list(state["trace_log"])
    trace_log.append("rank: started ranking")

    ranked_seed = list(state["ranked_items"])
    total_value = 0.0
    for item in ranked_seed:
        total_value += float(item["quantity"]) * float(item["current_price"])

    ranked_final: list[dict[str, Any]] = []
    for item in ranked_seed:
        item_value = float(item["quantity"]) * float(item["current_price"])
        if total_value > 0:
            weight = round(item_value / total_value, 4)
        else:
            weight = 0.0

        ranked_final.append(
            {
                "ticker": item["ticker"],
                "rationale": (
                    f"Matched in retrieved context. Sector: {item['sector']}, "
                    f"Type: {item['instrument_type']}."
                ),
                "exposure_weight": weight,
            }
        )

    ranked_final.sort(key=lambda x: x["exposure_weight"], reverse=True)
    trace_log.append(f"rank: ranked {len(ranked_final)} items")

    return {
        **state,
        "ranked_items": ranked_final,
        "trace_log": trace_log,
    }


def format_node(state: AgentState) -> AgentState:
    """Generate final structured response with LLM or deterministic fallback."""
    trace_log = list(state["trace_log"])
    trace_log.append("format: preparing structured output")

    sources = sorted(
        {
            str(doc.metadata.get("source", "unknown"))
            for doc in state["retrieved_docs"]
        }
    )

    if state["query_type"] == "news_impact":
        schema_cls = NewsImpact
    else:
        schema_cls = GeneralQA

    context_block = "\n\n".join(doc.page_content for doc in state["retrieved_docs"])
    ranked_block = json.dumps(state["ranked_items"], indent=2)

    prompt = (
        "You are a strict JSON assistant for BYLD Wealth. "
        "Use the provided context only. Do not hallucinate.\n\n"
        f"User query:\n{state['query']}\n\n"
        f"Retrieved context:\n{context_block}\n\n"
        f"Cross referenced ranked items:\n{ranked_block}\n\n"
        "Return the response matching the schema exactly."
    )

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(schema_cls)
        response = structured_llm.invoke(prompt)

        if isinstance(response, GeneralQA):
            final_response: GeneralQA | NewsImpact = response.model_copy(
                update={"sources": sources, "trace": trace_log}
            )
        elif isinstance(response, NewsImpact):
            final_response = response.model_copy(
                update={"sources": sources, "trace": trace_log}
            )
        else:
            raise RuntimeError("Structured output did not return expected schema.")

        trace_log.append("format: structured response generated using Ollama")
    except Exception as exc:  # noqa: BLE001
        trace_log.append(f"format: LLM failed, switching to fallback ({type(exc).__name__})")
        fallback_response = get_fallback_response(state["query"], schema_cls)
        if isinstance(fallback_response, GeneralQA):
            final_response = fallback_response.model_copy(
                update={"sources": sources or ["data/portfolio.json"], "trace": trace_log}
            )
        else:
            final_response = fallback_response.model_copy(
                update={"sources": sources or ["data/portfolio.json"], "trace": trace_log}
            )

    return {
        **state,
        "final_response": final_response,
        "trace_log": trace_log,
    }


def build_graph() -> Any:
    """Compile and return the LangGraph state graph."""
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


def run_agent(query: str, print_trace: bool = False) -> GeneralQA | NewsImpact:
    """Run the full multi-step agent pipeline for a user query."""
    app = build_graph()
    initial_state: AgentState = {
        "query": query,
        "query_type": detect_query_type(query),
        "retrieved_docs": [],
        "portfolio_data": [],
        "ranked_items": [],
        "final_response": None,
        "trace_log": ["agent: initialized state"],
    }

    result = app.invoke(initial_state)
    final_response = cast(GeneralQA | NewsImpact | None, result.get("final_response"))

    if final_response is None:
        final_response = get_fallback_response(query, GeneralQA)

    if print_trace:
        for entry in cast(list[str], result.get("trace_log", [])):
            print(entry)

    return final_response
