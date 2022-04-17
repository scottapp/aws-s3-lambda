import boto3
import json


iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda')
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
rule_arn = response['RuleArn']

response = client.put_targets(
    Rule=rule_name,
    EventBusName='default',
    Targets=[{'Id': 'Target', 'Arn': 'arn:aws:lambda:ap-northeast-1:922656660811:function:HelloWorld'}]
)
print(response)

res = lambda_client.add_permission(
    Action='lambda:InvokeFunction',
    StatementId='EVT_TRIGGER_ID',
    FunctionName='HelloWorld',
    Principal='events.amazonaws.com',
    SourceArn=rule_arn
)
print(res)
