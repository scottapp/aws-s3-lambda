import os
from dotenv import load_dotenv
import boto3


if __name__ == '__main__':
    load_dotenv()

    project_id = os.getenv('PROJECT_ID')
    role_name = os.getenv('GLUE_CRAWLER_NAME')
    rule_name = os.getenv('EVENT_RULE_NAME')
    target_arn = os.getenv('EVENT_RULE_TARGET_ARN')

    assert project_id
    assert role_name
    assert rule_name
    assert target_arn

    full_crawler_name = '{}_{}'.format(project_id, role_name)

    pattern = """
    {
  "source": [
    "aws.glue"
  ],
  "detail-type": [
    "Glue Crawler State Change"
  ],
  "detail": {
    "crawlerName": "%s",
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

    response = client.put_targets(
        Rule=rule_name,
        EventBusName='default',
        Targets=[{'Id': 'Target', 'Arn': target_arn}]
    )
    print(response)

