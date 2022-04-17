import os
from dotenv import load_dotenv
import boto3
import json


glue_trust_policy = """
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "glue.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
"""

s3_access_policy = """
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject"
                ],
                "Resource": []
            }
        ]
    }
"""


def create_basic_glue_role(client, role_name):
    res = client.create_role(AssumeRolePolicyDocument=json.dumps(json.loads(glue_trust_policy)),
                             Path='/',
                             RoleName=role_name)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200
    return res


def attach_policy(client, role_name, policy_arn):
    res = client.attach_role_policy(PolicyArn=policy_arn,
                                    RoleName=role_name)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200
    return res


def create_policy(client, policy_name, policy):
    res = client.create_policy(PolicyName=policy_name,
                               PolicyDocument=json.dumps(policy))
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200
    return res['Policy']['Arn']


if __name__ == '__main__':
    load_dotenv()

    project_id = os.getenv('PROJECT_ID')
    assert project_id

    iam_client = boto3.client('iam')

    role_name = '{}_BasicETLRole'.format(project_id)
    policy_arn = False

    try:
        res = create_basic_glue_role(iam_client, role_name)
        print(res)
    except iam_client.exceptions.EntityAlreadyExistsException as ex:
        print(ex)

    try:
        policy = json.loads(s3_access_policy)
        # enter s3 bucket arns here
        policy['Statement'][0]['Resource'] = ['arn']
        policy_arn = create_policy(iam_client, '{}_S3ACCESS'.format(project_id), policy)
        print(policy_arn)
    except iam_client.exceptions.EntityAlreadyExistsException as ex:
        print(ex)

    assert role_name and policy_arn
    res = attach_policy(iam_client, role_name, policy_arn)
    print(res)
