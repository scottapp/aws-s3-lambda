import os
from dotenv import load_dotenv
import boto3
import json


if __name__ == '__main__':
    load_dotenv()

    project_id = os.getenv('PROJECT_ID')
    role_name = os.getenv('LAMBDA_ROLE_NAME')
    assert role_name
    role_name = '{}_{}'.format(project_id, role_name)

    iam_client = boto3.client('iam')

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

    glue_start_crawler_policy = """
    {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "glue:StartCrawler",
            "Resource": "*"
        }
    ]
    }
    """

    # create basic lambda execution role
    res = iam_client.create_role(AssumeRolePolicyDocument=json.dumps(json.loads(lambda_trust_policy)),
                                 Path='/',
                                 RoleName='{}_LambdaBasicExecutionRole'.format(project_id))
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200

    # attatch basic role policy
    res = iam_client.attach_role_policy(PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
                                        RoleName='{}_LambdaBasicExecutionRole'.format(project_id))
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200

    # create role to start Glue Crawler
    res = iam_client.create_role(AssumeRolePolicyDocument=json.dumps(json.loads(lambda_trust_policy)),
                                 Path='/',
                                 RoleName=role_name)
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200

    # attatch basic role policy
    res = iam_client.attach_role_policy(PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
                                        RoleName=role_name)
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200

    # create policy
    res = iam_client.create_policy(PolicyName='{}_Policy'.format(role_name),
                                   PolicyDocument=json.dumps(json.loads(glue_start_crawler_policy)))
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200
    glue_start_crawler_policy_arn = res['Policy']['Arn']

    # attach policy
    res = iam_client.attach_role_policy(PolicyArn=glue_start_crawler_policy_arn,
                                        RoleName=role_name)
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200
