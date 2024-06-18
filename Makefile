IMAGE_TAG ?= quicksight
DEPLOY_ENV ?= stage

build:
	docker build . -f Dockerfile --target qsight --tag ${IMAGE_TAG}

# Usage Trends Dashboard
sync-sandbox-ut-local:
	docker run --env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} --env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
	--env AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} --env ASSET_NAME='usage_trends' \
	--env DEPLOY_ENV=${DEPLOY_ENV} --env LOCAL=True \
	--rm ${IMAGE_PATH}:${IMAGE_TAG} sync-assets-local

fetch-sandbox-ut-local:
	docker run --env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} --env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
	--env AWS_SESSION_TOKEN=${AWS_SESSION_TOKEN} --env ASSET_NAME='usage_trends' --env DEPLOY_ENV=${DEPLOY_ENV} \
	--env LOCAL=True --volume ${PWD}/asset_bundles/analysis_bundles:/app/asset_bundles/analysis_bundles \
	--volume ${PWD}/asset_bundles/dashboard_bundles:/app/asset_bundles/dashboard_bundles \
	--rm ${IMAGE_PATH}:${IMAGE_TAG} fetch-assets-local

.PHONY: build push deploy-assets sync-sandbox-ut-local \
	 fetch-sandbox-ut-local 

