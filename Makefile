.PHONY: setup data run eval

setup:
	rm -f uv.lock
	uv sync

data:
	uv run python scripts/generate_mock_data.py

run:
	uv run python -m portfolio_ask "$(QUERY)"

eval:
	uv run python evals/run_eval.py
