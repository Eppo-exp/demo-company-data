build-dbt:
	dbt run --project-dir=dbt_project

sync-models:
	export EPPO_API_KEY=$(cat test_api_key.txt)
	export EPPO_SYNC_TAG=demo-company-dev
	. venv/bin/activate && \
	pip3 install --force-reinstall ~/git/eppo-metrics-sync/dist/eppo_metrics_sync-0.0.0-py3-none-any.whl && \
	python3 -m eppo_metrics_sync dbt_project/models --schema=dbt-model --dbt-model-prefix="test_db.test_schema" && \
	deactivate