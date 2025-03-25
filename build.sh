#!/bin/bash
image_name="auto_test"
# shellcheck disable=SC1083
image_exist=$(docker images --filter=reference='${image_name}' --format {{.Repository}})
if [ -n "${image_exist}" ];then
  docker rmi ${image_name}
  docker build -t ${image_name} .
else
  docker build -t ${image_name} .
fi
