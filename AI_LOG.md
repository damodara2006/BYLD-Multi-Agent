# AI_LOG.md

## Tools used

- I used Python 3.11+, uv packaging, Makefile, LangGraph, LangChain, Chroma, sentence-transformers, and Ollama.
- I added `langchain-community` and `langchain-text-splitters` to avoid import issues in the indexer.

## Significant prompts

- Prompt: Build project infrastructure and deterministic mock data for BYLD Wealth.
  - What the AI produced: `pyproject.toml`, `.env.example`, `.gitignore`, `Makefile`, and `scripts/generate_mock_data.py` with portfolio/news/glossary generation.
  - What I kept/rejected: I kept the full data generation flow, but later rejected Groq-based setup because I needed a local Ollama path.
- Prompt: Replace Groq with Ollama and keep structured fallback behavior.
  - What the AI produced: `portfolio_ask/schemas.py`, `indexer.py`, `vector_store.py`, and `llm.py` using `langchain_ollama` plus deterministic fallback.
  - What I kept/rejected: I kept Ollama integration and fallback logic; I rejected Groq API usage completely.
- Prompt: Build Step 3 multi-step LangGraph agent with retrieval, cross-reference, ranking, and formatting.
  - What the AI produced: `portfolio_ask/agent.py` with a typed state and 4 nodes (`retrieve`, `cross_reference`, `rank`, `format`), plus `portfolio_ask/__main__.py` CLI that prints formatted JSON.
  - What I kept/rejected: I kept the full graph flow and JSON-only CLI output. I rejected any chatbot-style response behavior.

## A bug your AI introduced

- The AI originally wrote my log in the wrong format using step-based headers. I caught this because it did not match the reviewer template. I fixed it by rewriting the full file to this exact 5-section format.
- The AI used `langchain_community` and `langchain_text_splitters` in code but did not include both dependencies at first. I fixed it by adding both packages to `pyproject.toml`.

## A design choice you made against AI suggestion

- I chose local Ollama inference over hosted Groq even though hosted inference can be easier to start. I did this because this assignment needs deterministic behavior without external API dependency risk.
- I chose a strict JSON CLI contract (no conversational wrapper text) so test harnesses can parse output reliably.

## Time split

- 30% infrastructure and data setup
- 35% retrieval/indexing plus schema work
- 25% multi-step agent state flow and CLI integration
- 10% debugging and log/template corrections
