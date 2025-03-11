#!/bin/bash
image_name="jenkins:2.426.3-jdk17"
jenkins_exist=`docker images --filter=reference='${image_name}' --format {{.Repository}}`
if [ -n "${jenkins_exist}" ];then
  docker rmi ${image_name}
  docker build -t ${image_name} .
else
  docker build -t ${image_name} .
fi
