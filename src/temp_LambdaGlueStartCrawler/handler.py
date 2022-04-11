import boto3

print('Loading function')

# s3 = boto3.client('s3')

glue = boto3.client(service_name='glue',
                    region_name='ap-northeast-1',
                    endpoint_url='https://glue.ap-northeast-1.amazonaws.com')


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    # bucket = event['Records'][0]['s3']['bucket']['name']
    # key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        glue.start_crawler(Name='temp_DefaultGlueCrawler')

    except Exception as e:
        # print(e)
        # print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        # raise e
        print(e)
        print('Error starting crawler')
        raise e
