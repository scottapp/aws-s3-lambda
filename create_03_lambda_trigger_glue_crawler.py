import os
from dotenv import load_dotenv
import time
import boto3
import json
from zipfile import ZipFile


if __name__ == '__main__':
    load_dotenv()

    project_id = os.getenv('PROJECT_ID')
    assert project_id
    role_name = os.getenv('LAMBDA_ROLE_NAME')
    assert role_name
    role_name = '{}_{}'.format(project_id, role_name)
    source_account = os.getenv('SOURCE_ACCOUNT')
    bucket_name = os.getenv('BUCKET_NAME')
    function_name = os.getenv('LAMBDA_FUNCTION_NAME')
    assert function_name
    function_name = '{}_{}'.format(project_id, function_name)

    iam_client = boto3.client('iam')
    lambda_client = boto3.client('lambda')
    s3_client = boto3.resource('s3')

    with ZipFile('tmp.zip', 'w') as zip_fp:
        zip_fp.write(f'src/{function_name}/handler.py')

    zipped_code = None
    with open('tmp.zip', 'rb') as f:
        zipped_code = f.read()

    role = iam_client.get_role(RoleName=role_name)
    res = lambda_client.create_function(
        FunctionName=function_name,
        Runtime='python3.9',
        Role=role['Role']['Arn'],
        Handler=f'src/{function_name}/handler.lambda_handler',
        Code=dict(ZipFile=zipped_code),
        Timeout=300,
    )
    print(res)

    assert res['ResponseMetadata']['HTTPStatusCode'] == 201
    lambda_arn = res['FunctionArn']
    print(lambda_arn)

    # add permission for s3 to invoke lambda function
    res = lambda_client.add_permission(
        Action='lambda:InvokeFunction',
        FunctionName=function_name,
        Principal='s3.amazonaws.com',
        SourceAccount=source_account,
        SourceArn=f'arn:aws:s3:::{bucket_name}',
        StatementId='s3',
    )
    print(res)
    assert res['ResponseMetadata']['HTTPStatusCode'] == 201

    """
    zipped_code = None
    with open('tmp.zip', 'rb') as f:
        zipped_code = f.read()

    response = lambda_client.update_function_code(FunctionName=function_name, ZipFile=zipped_code)
    print(response)    
    """

    # setup event notification
    bucket_notification = s3_client.BucketNotification(bucket_name)
    bucket_notification.load()
    res = bucket_notification.put(
        NotificationConfiguration={'LambdaFunctionConfigurations':
            [
                {'LambdaFunctionArn': lambda_arn,
                 'Events': ['s3:ObjectCreated:*']}
            ]
        })
    print(res)
