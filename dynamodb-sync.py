from __future__ import print_function
import json
import boto3
import traceback
from boto3.session import Session
import zipfile
import tempfile
import botocore
import decimal

objmapping = None
code_pipeline = boto3.client('codepipeline')
dynamodb_client = boto3.client('dynamodb')
tablename = 'custom-lookup'
hashkey = 'teamname-environment'
rangekey = 'appname'

def handler(event,context):
    try:
        job_id = event['CodePipeline.job']['id']
        job_data = event['CodePipeline.job']['data']
        artifact_data = job_data['inputArtifacts'][0]

        params = get_user_params(job_id, job_data)
        artifact = params['file_to_sync']

        s3 = setup_s3_client(job_data)
        objartifact = get_file_from_artifact(s3, artifact_data, artifact)
        sampledata = load_data(objartifact)
        for item in sampledata:
            insert_update_data(item)

        put_job_success(job_id, "Success")
    except Exception as e:
        print('Function failed due to exception.')
        print(e)
        traceback.print_exc()
        put_job_failure(job_id, 'Function exception: ' + str(e))

def load_data(objfile):
    mappings = json.loads(objfile, parse_float=decimal.Decimal)
    return mappings
def insert_update_data(response):
    createtable()
    dynamodb_client.put_item(
        TableName=tablename,
        Item={
            hashkey: {'S': response[hashkey]},
            rangekey: {'S': response[rangekey]},
            'mappings': {'S': str(response['mappings'])}
        }
    )
def createtable():
    try:
        dynamodb_client.describe_table(TableName=tablename)
    except Exception:
        dynamodb_client.create_table(
            TableName=tablename,
            KeySchema=[
                {'AttributeName': hashkey, 'KeyType': 'HASH'},
                {'AttributeName': rangekey, 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': hashkey, 'AttributeType': 'S'},
                {'AttributeName': rangekey, 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        dynamodb_client.get_waiter('table_exists').wait(TableName=tablename)


def get_file_from_artifact(s3, artifact, file_in_zip):
    bucket = artifact['location']['s3Location']['bucketName']
    key = artifact['location']['s3Location']['objectKey']

    with tempfile.NamedTemporaryFile() as tmp_file:
        s3.download_file(bucket, key, tmp_file.name)
        with zipfile.ZipFile(tmp_file.name, 'r') as zip:
            print(zip.read(file_in_zip))
            return zip.read(file_in_zip)

def setup_s3_client(job_data):
    key_id = job_data['artifactCredentials']['accessKeyId']
    key_secret = job_data['artifactCredentials']['secretAccessKey']
    session_token = job_data['artifactCredentials']['sessionToken']

    session = Session(aws_access_key_id=key_id,
                      aws_secret_access_key=key_secret,
                      aws_session_token=session_token)
    return session.client('s3', config=botocore.client.Config(signature_version='s3v4'))

def put_job_success(job, message):
    """Notify CodePipeline of a successful job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status

    Raises:
        Exception: Any exception thrown by .put_job_success_result()

    """
    print('Putting job success')
    print(message)
    code_pipeline.put_job_success_result(jobId=job)

def put_job_failure(job, message):
    """Notify CodePipeline of a failed job

    Args:
        job: The CodePipeline job ID
        message: A message to be logged relating to the job status

    Raises:
        Exception: Any exception thrown by .put_job_failure_result()

    """
    print('Putting job failure')
    print(message)
    code_pipeline.put_job_failure_result(jobId=job, failureDetails={'message': message, 'type': 'JobFailed'})

def continue_job_later(job, message):
    """Notify CodePipeline of a continuing job

    This will cause CodePipeline to invoke the function again with the
    supplied continuation token.

    Args:
        job: The JobID
        message: A message to be logged relating to the job status
        continuation_token: The continuation token

    Raises:
        Exception: Any exception thrown by .put_job_success_result()

    """

    # Use the continuation token to keep track of any job execution state
    # This data will be available when a new job is scheduled to continue the current execution
    continuation_token = json.dumps({'previous_job_id': job})

    print('Putting job continuation')
    print(message)
    code_pipeline.put_job_success_result(jobId=job, continuationToken=continuation_token)

def get_user_params(job_id,job_data):
    try:
        user_parameters = job_data['actionConfiguration']['configuration']['UserParameters']
        decoded_parameters = json.loads(user_parameters)
        print(decoded_parameters)
    except Exception as e:
        put_job_failure(job_id,e)
        raise Exception('UserParameters could not be decoded as JSON')

    return decoded_parameters

if __name__ == "__main__":
    handler(None, None)

