.PHONY: dev test eval seed demo lint docker-up clean

PYTHON := python
PYTEST := pytest

dev:
	uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload

test:
	$(PYTHON) -m pytest gigbid/tests gigbid/mcp_servers -v

eval:
	$(PYTHON) gigbid/evals/runners/rag_eval.py
	$(PYTHON) gigbid/evals/runners/decision_eval.py
	$(PYTHON) gigbid/evals/runners/gigsim_outcomes.py
	$(PYTHON) gigbid/evals/runners/judge_calibration.py
	$(PYTHON) gigbid/evals/runners/ablation.py

seed:
	$(PYTHON) gigbid/scripts/seed_data.py

demo:
	$(PYTHON) -m apps.api.main

lint:
	$(PYTHON) -m py_compile gigbid/apps/api/main.py

docker-up:
	docker compose -f infra/docker-compose.yml up --build

clean:
	rm -rf .pytest_cache gigbid/**/__pycache__
