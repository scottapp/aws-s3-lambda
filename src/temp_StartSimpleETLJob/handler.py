import boto3

glue = boto3.client(service_name='glue',
                    region_name='ap-northeast-1',
                    endpoint_url='https://glue.ap-northeast-1.amazonaws.com')


def lambda_handler(event, context):
    try:
        glue.start_job_run(Name='SimpleETLJob')
    except Exception as e:
        print(e)
        print('Error start job run')
        raise e
