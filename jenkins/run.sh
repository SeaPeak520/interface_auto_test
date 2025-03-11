#!/bin/bash

allure_version="allure-2.24.0"
jdk_version="jdk-17.0.14"
current_dir=$(pwd)
jenkins_contains_name="jenkins"
jenkins_exist=`docker ps -a  --filter 'name=${jenkins_contains_name}' --format {{.Names}}`

tar -xf ${current_dir}/${allure_version}.tgz
tar -xf ${current_dir}/${jdk_version}_linux-x64_bin.tar.gz

if [ -n "${jenkins_exist}" ]; then
  #容器存在
  docker rm -f ${jenkins_contains_name}
  docker run -itd --name=${jenkins_contains_name} -p 8081:8080 -u=root --restart=always --privileged=true -v /usr/share/zoneinfo/Asia/Shanghai:/etc/localtime -v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker -v /home/jenkins:/var/jenkins_home -v ${current_dir}/${allure_version}:/${allure_version} -v ${current_dir}/${jdk_version}:/${jdk_version} jenkins:2.426.3-jdk17
else
  docker run -itd --name=${jenkins_contains_name} -p 8081:8080 -u=root --restart=always --privileged=true -v /usr/share/zoneinfo/Asia/Shanghai:/etc/localtime -v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker -v /home/jenkins:/var/jenkins_home -v ${current_dir}/${allure_version}:/${allure_version} -v ${current_dir}/${jdk_version}:/${jdk_version} jenkins:2.426.3-jdk17
fi


