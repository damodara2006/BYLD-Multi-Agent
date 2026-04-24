.PHONY: setup data run eval

setup:
	uv venv
	uv pip install -e .

data:
	python scripts/generate_mock_data.py

run:
	python -m portfolio_ask

eval:
	python evals/run_eval.py
