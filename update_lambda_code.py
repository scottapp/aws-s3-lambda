import os
from dotenv import load_dotenv
import boto3
from zipfile import ZipFile


if __name__ == '__main__':
    load_dotenv()

    function_name = 'temp_StartSimpleETLJob'
    lambda_client = boto3.client('lambda')
    zip_file_name = '{}.zip'.format(function_name)

    assert os.path.isdir('src/%s' % function_name), 'error dir, src/{}'.format(function_name)

    with ZipFile(zip_file_name, 'w') as zip_fp:
        zip_fp.write(f'src/{function_name}/handler.py')

    zipped_code = None
    with open(zip_file_name, 'rb') as f:
        zipped_code = f.read()

    response = lambda_client.update_function_code(FunctionName=function_name, ZipFile=zipped_code)
    print(response)

    assert response['ResponseMetadata']['HTTPStatusCode'] == 200
