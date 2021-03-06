import boto3
import json
from zipfile import ZipFile

iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda')


role_policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
response = iam_client.create_role(RoleName='LambdaBasicExecution',
                                  AssumeRolePolicyDocument=json.dumps(role_policy))
print(response)


function_name = 'HelloWorld'

with ZipFile('tmp.zip', 'w') as zip_fp:
    zip_fp.write(f'src/{function_name}/handler.py')

zipped_code = None
with open('tmp.zip', 'rb') as f:
    zipped_code = f.read()

role = iam_client.get_role(RoleName='LambdaBasicExecution')
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

rule_name = 'EV_CRAWLER_SUCCEED'
pattern = """
        {
      "source": [
        "aws.glue"
      ],
      "detail-type": [
        "Glue Crawler State Change"
      ],
      "detail": {
        "state": ["Succeeded"]
      }
        }
"""

client = boto3.client('events')

response = client.put_rule(
        Name=rule_name,
        EventPattern=pattern,
        State='ENABLED',
        EventBusName='default'
)
print(response)

response = client.put_targets(
    Rule=rule_name,
    EventBusName='default',
    Targets=[{'Id': 'Target', 'Arn': 'arn:aws:lambda:ap-northeast-1:922656660811:function:HelloWorld'}]
)
print(response)
