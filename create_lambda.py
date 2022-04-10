import boto3
import json

iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda')

"""
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
"""

"""
zipped_code = None
with open('lambda_hello_world.zip', 'rb') as f:
    zipped_code = f.read()


role = iam_client.get_role(RoleName='LambdaBasicExecution')
response = lambda_client.create_function(
    FunctionName='helloWorldLambda',
    Runtime='python3.9',
    Role=role['Role']['Arn'],
    Handler='handler.lambda_handler',
    Code=dict(ZipFile=zipped_code),
    Timeout=300,  # Maximum allowable timeout
    )
print(response)
"""


zipped_code = None
with open('handler.zip', 'rb') as f:
    zipped_code = f.read()

response = lambda_client.update_function_code(FunctionName='helloWorldLambda', ZipFile=zipped_code)
print(response)
