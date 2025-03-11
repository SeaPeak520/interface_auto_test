#!/bin/bash

username=$1
if id -u ${username} >/dev/null 2>&1; then
  echo '用户${username}存在'
else
  useradd -d /home/${username} ${username}
  expect <<EOF
  set timeout 10
  spawn passwd ${username}
  expect {
      "New password" {send "123456\r";exp_continue;}
      "Retype new password" {set timeout 500;send "123456\r";}
  }
  expect eof
  EOF
  chmod 755 /home/${username}
fi

