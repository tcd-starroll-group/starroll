.PHONY: run-console
run-console:
	export PYTHONPATH="gen/py/src:." && \
	fastapi dev gen/py/src/openapi_server/main.py