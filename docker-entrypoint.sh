#!/bin/bash

set -e

function main() {
  if [ -z ${1+x} ]; then
    echo "Please pass an argument."
  fi

  cmd=$1; shift

  case "$cmd" in
    pass)
      echo "Container starts."
      ;;
    shell)
      exec "/bin/bash"
      ;;
    cmd)
      echo "$@"
      exec /bin/bash -c "$*"
      ;;
    deploy-assets)
      exec /app/bin/deploy_assets.py --asset_name ${ASSET_NAME} --deploy_env ${DEPLOY_ENV}
      ;;
    sync-assets-local)
      exec /app/bin/deploy_assets.py --asset_name ${ASSET_NAME} --deploy_env ${DEPLOY_ENV} --local ${LOCAL}
      ;;
    fetch-assets-local)
      exec /app/bin/fetch_assets.py --asset_name ${ASSET_NAME} --deploy_env ${DEPLOY_ENV} --local ${LOCAL}
      ;;
    *)
      echo "Unknown command \"${cmd}\"."
      ;;
  esac
}

main $@