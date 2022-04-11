import os
import time
from dotenv import load_dotenv
import boto3
import json


if __name__ == '__main__':
    load_dotenv()

    project_id = os.getenv('PROJECT_ID')
    role_name = os.getenv('GLUE_CRAWLER_NAME')
    db_name = os.getenv('GLUE_DB_NAME')

    assert project_id
    assert role_name
    assert db_name

    crawler_name = '{}_{}'.format(project_id, role_name)
    role_name = 'AWSGlueServiceRole_{}_{}'.format(project_id, role_name)
    db_name = '{}_{}'.format(project_id, db_name)
    bucket_name = os.getenv('BUCKET_NAME')

    trust_policy = """
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
                "Resource": [
                    "arn:aws:s3:::%s*"
                ]
            }
        ]
    }""" % bucket_name

    glue_client = boto3.client('glue')
    iam_client = boto3.client('iam')

    # create glue service role
    res = iam_client.create_role(AssumeRolePolicyDocument=json.dumps(json.loads(trust_policy)),
                                 Path='/',
                                 RoleName=role_name)

    # attach basic service policy
    res = iam_client.attach_role_policy(PolicyArn='arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole',
                                        RoleName=role_name)
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200

    # create policy
    res = iam_client.create_policy(PolicyName='{}_Policy'.format(role_name),
                                   PolicyDocument=json.dumps(json.loads(s3_access_policy)))
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200
    policy_arn = res['Policy']['Arn']

    # attach policy
    res = iam_client.attach_role_policy(PolicyArn=policy_arn,
                                        RoleName=role_name)
    print(res)
    assert res and res['ResponseMetadata']['HTTPStatusCode'] == 200    

    res = glue_client.create_database(DatabaseInput={'Name':db_name})
    print(res)

    time.sleep(5)

    response = glue_client.create_crawler(
        Name=crawler_name,
        Role=role_name,
        DatabaseName=db_name,
        Description='Crawler Description',
        Targets={
            'S3Targets': [
                {
                    'Path': 's3://{}'.format(bucket_name),
                    'Exclusions': [
                    ]
                },
            ]
        },
        SchemaChangePolicy={
            'UpdateBehavior': 'UPDATE_IN_DATABASE',
            'DeleteBehavior': 'DELETE_FROM_DATABASE'
        }
    )
    print(response)
