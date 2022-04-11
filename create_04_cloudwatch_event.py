import os
from dotenv import load_dotenv
import boto3


if __name__ == '__main__':
    load_dotenv()

    rule_name = os.getenv('EVENT_RULE_NAME')
    assert rule_name

    target_arn = os.getenv('EVENT_RULE_TARGET_ARN')

    pattern = """
    {
  "source": [
    "aws.glue"
  ],
  "detail-type": [
    "Glue Crawler State Change"
  ],
  "detail": {
    "state": [
      "Succeeded"
    ]
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
        Targets=[{'Id': 'Target', 'Arn': target_arn}]
    )
    print(response)

