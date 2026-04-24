import json
from pathlib import Path
from pydantic import BaseModel
from portfolio_ask.schemas import GeneralQA, NewsImpact
from langchain_ollama import ChatOllama
import os

def get_llm() -> ChatOllama:
    """Returns the standard configured Ollama LLM."""
    if os.getenv("BYLD_FORCE_FALLBACK", "0") == "1":
        raise RuntimeError("Forced fallback enabled for deterministic evaluation.")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return ChatOllama(model="llama3.1:8b", temperature=0.0, base_url=base_url)

def get_fallback_response(query: str, schema_cls: type[BaseModel]) -> BaseModel:
    """
    Deterministic heuristic fallback execution in case of LLM failure.
    If the query contains 'risk', we statically filter for FMCG or Bonds.
    """
    trace_log = ["Entered get_fallback_response due to failure or trigger."]
    portfolio_file = Path("data/portfolio.json")
    
    portfolio_data = []
    if portfolio_file.exists():
        with open(portfolio_file, "r") as f:
            portfolio_data = json.load(f)
            
    filtered_items = []
    answer = "I could not definitively process your query."
    
    if "risk" in query.lower():
        trace_log.append("Heuristic trigger: 'risk' detected. Filtering for FMCG and Bonds.")
        filtered_items = [
            item for item in portfolio_data
            if item.get("sector") == "FMCG" or item.get("instrument_type") == "Bond"
        ]
        tickers = [item["ticker"] for item in filtered_items]
        answer = f"As a deterministic fallback for risk mitigation, consider evaluating defensive assets like FMCG or Bonds. Found: {', '.join(tickers)}."
        
    if schema_cls == GeneralQA:
        return GeneralQA(
            query_type="heuristic_fallback",
            summary=answer,
            sources=["data/portfolio.json"],
            trace=trace_log
        )
    elif schema_cls == NewsImpact:
        ranked = []
        for i, item in enumerate(filtered_items):
            risk_level = "Low" if item.get("instrument_type") == "Bond" or item.get("sector") == "FMCG" else "Medium"
            ranked.append({
                "ticker": item["ticker"],
                "rationale": "Static defensive fallback inclusion.",
                "exposure_weight": 1.0 / (i + 1),
                "risk_level": risk_level,
            })
        return NewsImpact(
            query_type="heuristic_fallback",
            summary=answer,
            ranked_items=ranked,
            sources=["data/portfolio.json"],
            trace=trace_log
        )
    raise ValueError("Unsupported schema class for fallback.")
