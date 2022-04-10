import os
import boto3
import json



def create_lambda_trigger_role():
    tmp = {"Version": "2012-10-17",
                         "Statement": [
                             {"Sid": "VisualEditor0",
                              "Effect": "Allow",
                              "Action": "glue:StartCrawler",
                              "Resource": "*"
                              }]
        }
    policy = json.dumps(tmp, indent=2)
    try:
        client = boto3.client('iam')
        response = client.create_role(
            Path='string',
            RoleName='string',
            AssumeRolePolicyDocument='string',
            Description='string',
            MaxSessionDuration=123,
            PermissionsBoundary='string',
            Tags=[
                {
                    'Key': 'string',
                    'Value': 'string'
                },
            ]
        )
        create_role_res = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_relationship_policy_another_iam_user),
            Description='This is a test role',
            Tags=[
                {
                    'Key': 'Owner',
                    'Value': 'msb'
                }
            ]
        )
    except ClientError as error:
        print(erro)


def main():
    """
    # Let's use Amazon S3
    s3 = boto3.resource('s3')

    # Print out bucket names
    for bucket in s3.buckets.all():
        print(bucket.name)
    """
    try:
        iam_client = boto3.client('iam')
        create_role_res = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_relationship_policy_another_iam_user),
            Description='This is a test role',
            Tags=[
                {
                    'Key': 'Owner',
                    'Value': 'msb'
                }
            ]
        )
    except ClientError as error:
        if error.response['Error']['Code'] == 'EntityAlreadyExists':
            return 'Role already exists... hence exiting from here'
        else:
            return 'Unexpected error occurred... Role could not be created', error


if __name__ == '__main__':
    create_lambda_trigger_role()
