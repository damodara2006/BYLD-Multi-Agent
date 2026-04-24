.PHONY: setup data run eval

setup:
	uv venv
	uv pip install -e .

data:
	python3 scripts/generate_mock_data.py

run:
	python3 -m portfolio_ask "$(QUERY)"

eval:
	python3 evals/run_eval.py
