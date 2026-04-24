# AI_LOG.md

## Tools used

- I used Python 3.11+, uv packaging, Makefile, LangGraph, LangChain, Chroma, sentence-transformers, and Ollama.
- I added `langchain-community` and `langchain-text-splitters` to avoid import issues in the indexer.
- I added YAML-driven evaluation with `PyYAML` and strict schema validation using Pydantic in `evals/run_eval.py`.

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
- Prompt: Generate a final eval harness with exactly 5 YAML cases, strict `assert` checks, trace printing, and pass/fail summary.
  - What the AI produced: `evals/cases.yaml`, `evals/run_eval.py`, README rewrite, and Makefile updates for `python3` compatibility.
  - What I kept/rejected: I kept the 5-case structure and strict schema checks. I rejected adding random or non-deterministic test data because I wanted reproducible reviewer runs.

## A bug your AI introduced

- The AI originally wrote my log in the wrong format using step-based headers. I caught this because it did not match the reviewer template. I fixed it by rewriting the full file to this exact 5-section format.
- The AI used `langchain_community` and `langchain_text_splitters` in code but did not include both dependencies at first. I fixed it by adding both packages to `pyproject.toml`.
- The AI initially used `python` in Makefile commands, but this Linux environment only had `python3`. I caught this from command failures and fixed the Makefile to use `python3` for `data`, `run`, and `eval`.
- The AI's default dependency configuration caused a massive 4GB CUDA/NVIDIA bloat via sentence-transformers. I caught this by interrupting the build.
- The AI claimed the PyTorch CPU fix worked, but uv pip install was still reading a cached lockfile and downloading CUDA binaries. I caught this hallucination by watching the terminal output. I fixed it by changing the Makefile to delete uv.lock and strictly use uv sync instead.
- The AI routed "What is my tech exposure?" to the NewsImpact schema because it used "exposure" as a news keyword. I caught this when eval case 1 failed schema validation. I fixed it by removing "exposure" from the news intent keyword list.
- When we pivoted from Groq to Ollama, the AI used an incorrect model string in `llm.py`. This caused Ollama to reject the connection and continuously trigger the fallback. I caught this by running `ollama list` and updating the code to request exactly `llama3.1:8b`.
- I caught a logic error where queries mentioning 'impact' triggered a news-only focus, leaving the 'summary' field empty for tax questions. I fixed this by updating the prompt to mandate a narrative synthesis in the summary field.
- I caught a naming mismatch where the evaluation script looked for '.answer' while the schema used '.summary'. I fixed this and also implemented a `--case` filter in the eval harness to allow for surgical testing of failed cases without re-running the entire suite.
- I caught a hallucination where the LLM attributed TCS.NS's exposure weight to Samsung. I fixed this by adding a strict 'Negative Constraint' to the prompt, forcing the LLM to admit when a ticker is missing from the portfolio.
- I identified a 'Category Drift' bug where portfolio-specific queries were being treated as general Q&A. I fixed this by expanding the keyword detection logic and hardening the system prompt to prevent 'meta' summaries.

## A design choice you made against AI suggestion

- I chose local Ollama inference over hosted Groq even though hosted inference can be easier to start. I did this because this assignment needs deterministic behavior without external API dependency risk.
- I chose a strict JSON CLI contract (no conversational wrapper text) so test harnesses can parse output reliably.
- I structured YAML test cases to cover one behavior per case (general, fallback, news-impact, glossary, edge). I did this so failures are easy to debug and reviewers can map each case to a clear requirement.
- Instead of passing messy --extra-index-url flags in the Makefile, I explicitly configured [[tool.uv.index]] and [tool.uv.sources] in the pyproject.toml. This forces uv to strictly resolve torch to the CPU-only index, ensuring the project always stays lightweight and installs in under 2 minutes for the reviewer.
- I changed Makefile runtime commands to `uv run` so I do not depend on manual shell activation. This keeps reviewer commands predictable and avoids missing-module errors.
- I forced the addition of a visual progress indicator using `rich`. While the AI suggested a simple CLI, a 3-minute wait on a CPU-bound local model requires a 'heartbeat' to prevent the user from thinking the process has hung.

## Time split

- 24% infrastructure and data setup
- 31% retrieval/indexing plus schema work
- 24% multi-step agent state flow and CLI integration
- 21% testing and documentation
