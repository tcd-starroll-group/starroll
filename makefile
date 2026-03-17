.PHONY: run-console test-console

run-console:
	export PYTHONPATH="gen/py/src:." && \
	uvicorn --reload --host 0.0.0.0 --port 8000 backend.console.app:app

test-console:
	export PYTHONPATH="gen/py/src:." && \
	pytest backend/console/tests
