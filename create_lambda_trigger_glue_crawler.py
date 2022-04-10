import boto3
import json
from zipfile import ZipFile

iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda')

function_name = 'TriggerGlueCrawler'
role_name = 'GlueLambdaRole'

with ZipFile('tmp.zip', 'w') as zip_fp:
    zip_fp.write(f'src/{function_name}/handler.py')

zipped_code = None
with open('tmp.zip', 'rb') as f:
    zipped_code = f.read()

role = iam_client.get_role(RoleName=role_name)
response = lambda_client.create_function(
    FunctionName=function_name,
    Runtime='python3.9',
    Role=role['Role']['Arn'],
    Handler=f'src/{function_name}/handler.lambda_handler',
    Code=dict(ZipFile=zipped_code),
    Timeout=300,
    )
print(response)

"""
zipped_code = None
with open('tmp.zip', 'rb') as f:
    zipped_code = f.read()

response = lambda_client.update_function_code(FunctionName=function_name, ZipFile=zipped_code)
print(response)
"""
