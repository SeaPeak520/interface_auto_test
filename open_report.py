import subprocess

local_allure_path = 'D:\\allure-2.22.0\\bin\\allure'
cmd = f"{local_allure_path} open ./report/allure-report"
subprocess.run(cmd, shell=True, capture_output=True, encoding='utf-8')
