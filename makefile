.PHONY: run-console test-console

run-console:
	export PYTHONPATH="gen/py/src:." && \
	uvicorn --reload --host 0.0.0.0 --port 8010 openapi_server.main:app

test-console:
	export PYTHONPATH="gen/py/src:." && \
	pytest backend/console/tests
