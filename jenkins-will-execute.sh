#!/bin/bash
#jenkins里要执行的命令

project_name="interface_auto_test"
project_path="/root/${project_name}"
contains_name="auto"
image_name="auto_test"
#启动容器并执行命令
#构建执行shell代码，生成python容器
#通过--volumes-from将jenkins工作空间的代码映射到python容器，会生成匿名容器卷，--rm 容器停止时，容器被自动删除，匿名卷也删除
#启动  /home/jenkins/workspace/auto_test为jenkins挂载目录
docker run -itd --name ${contains_name} --rm -w=$WORKSPACE --volumes-from=jenkins -v ${project_path}:/${project_name} --privileged=true ${image_name}
#查看用例执行情况
docker logs -f --tail=100 ${contains_name}
#结束命令
exit 0
