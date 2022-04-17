import os
from dotenv import load_dotenv
import time
import boto3
import json
from zipfile import ZipFile


lambda_trust_policy = """
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
"""


StartJobRun_policy = """
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "glue:StartJobRun",
            "Resource": "arn:aws:glue:*:922656660811:job/*"
        }
    ]
}
"""


def create_role(client, role_name):
    # create basic role
    res = client.create_role(AssumeRolePolicyDocument=json.dumps(json.loads(lambda_trust_policy)),
                             Path='/',
                             RoleName=role_name)
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200

    # attatch basic role policy
    res = client.attach_role_policy(PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
                                    RoleName=role_name)
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200


def attach_policy(client, role_name, policy_arn):
    res = client.attach_role_policy(PolicyArn=policy_arn,
                                    RoleName=role_name)
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200


def create_StartJobRun_policy(client, policy_name, policy_content):
    res = client.create_policy(PolicyName=policy_name,
                               PolicyDocument=json.dumps(json.loads(policy_content)))
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200
    return res['Policy']['Arn']


if __name__ == '__main__':
    load_dotenv()

    project_id = os.getenv('PROJECT_ID')
    function_name = os.getenv('LAMBDA_FUNCTION_NAME_START_JOB')
    crawler_name = os.getenv('GLUE_CRAWLER_NAME')

    assert project_id
    assert function_name
    assert crawler_name

    function_name = '{}_{}'.format(project_id, function_name)

    iam_client = boto3.client('iam')
    lambda_client = boto3.client('lambda')

    role_name = '{}_StartJobRunRole'.format(project_id)

    """
    create_role(iam_client, role_name)
    time.sleep(1)
    policy_arn = create_StartJobRun_policy(iam_client, '{}_StartJobRunPolicy'.format(project_id), StartJobRun_policy)
    time.sleep(1)
    attach_policy(iam_client, role_name, policy_arn)
    time.sleep(1)
    """

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

    full_crawler_name = '{}_{}'.format(project_id, crawler_name)
    rule_name = 'EVT_CRAWLER_SUCCEED'

    pattern = """
        {
      "source": [
        "aws.glue"
      ],
      "detail-type": [
        "Glue Crawler State Change"
      ],
      "detail": {
        "crawlerName": ["%s"],
        "state": ["Succeeded"]
      }
        }
        """ % full_crawler_name

    client = boto3.client('events')

    response = client.put_rule(
        Name=rule_name,
        EventPattern=pattern,
        State='ENABLED',
        EventBusName='default'
    )
    print(response)
    rule_arn = response['RuleArn']

    response = client.put_targets(
        Rule=rule_name,
        EventBusName='default',
        Targets=[{'Id': 'Target', 'Arn': lambda_arn}]
    )
    print(response)

    # modify lambda's trigger configuration
    res = lambda_client.add_permission(
        Action='lambda:InvokeFunction',
        StatementId='EVT_TRIGGER_{}'.format(function_name),
        FunctionName=function_name,
        Principal='events.amazonaws.com',
        SourceArn=rule_arn
    )
    print(res)

    """
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

    """
    zipped_code = None
    with open('tmp.zip', 'rb') as f:
        zipped_code = f.read()

    response = lambda_client.update_function_code(FunctionName=function_name, ZipFile=zipped_code)
    print(response)    
    """

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
    """
