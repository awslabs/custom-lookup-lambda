# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with
# the License. A copy of the License is located at
#     http://aws.amazon.com/apache2.0/
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import os
import json
import boto3
import decimal
import ast
from boto3.dynamodb.conditions import Key
import requests

dynamodb_client = boto3.client('dynamodb')
tablename = 'custom-lookup'
hashkey = 'teamname-environment'
rangekey = 'appname'


def initialize():
    if os.getenv('method') is None:
        os.environ["method"] = "query"
        print("Running the function in Query Mode")
    if os.getenv('method') == 'insert':
        print("Running the function in Insert Mode")


def handler(event, context):
    print(event)
    if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
        initialize()
        if os.getenv('method') != "query":
            sampledata = load_data()
            for item in sampledata:
                insert_data(item)
        else:
            data = get_data(event['ResourceProperties'])
            respond_cloudformation(event, "SUCCESS", data)
            return get_data(event['ResourceProperties'])
    else:
        respond_cloudformation(event, "SUCCESS")
        return


def insert_data(response):
    createtable()
    dynamodb_client.put_item(
        TableName=tablename,
        Item={
            hashkey: {'S': response[hashkey]},
            rangekey: {'S': response[rangekey]},
            'info': {'S': str(response['info'])}
        }
    )


def load_data(file="sampledata/sampledata.json"):
    with open(file) as configuration_file:
        mappings = json.load(configuration_file, parse_float=decimal.Decimal)
    return mappings


def get_data(event):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tablename)
    response = table.query(
        KeyConditionExpression=Key(hashkey).eq(event[hashkey]) \
                               & Key(rangekey).eq(event[rangekey])
    )
    for item in response['Items']:
        objkeypair = ast.literal_eval(item['info'])
        if 'lookup' in event:
            return objkeypair[event['lookup']]
        else:
            return objkeypair


def respond_cloudformation(event, status, data=None):
    responseBody = {
        'Status': status,
        'Reason': 'See the details in CloudWatch Log Stream',
        'PhysicalResourceId': 'Custom Lambda Function',
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': data
    }

    print('Response = ' + json.dumps(responseBody))
    requests.put(event['ResponseURL'], data=json.dumps(responseBody))


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


# This is the test harness
if __name__ == '__main__':
    request1 = {
        'StackId': 'arn:aws:cloudformation:us-west-2:accountgoeshere:stack/sample-stack/stackidgoeshere',
        'ResponseURL': 'https://test.com',
        'ResourceProperties': {
            'teamname-environment': 'team1-dev',
            'ServiceToken': 'lambdaarn',
            'appname': 'app1',
            'lookup': 'vpc'
        },
        'RequestType': 'Create',
        'ServiceToken': 'lambdaarn',
        'ResourceType': 'Custom::Lookup',
        'RequestId': 'sampleid',
        'LogicalResourceId': 'CUSTOMLOOKUP'
    }
    request2 = {
        'StackId': 'arn:aws:cloudformation:us-west-2:accountgoeshere:stack/sample-stack/stackid',
        'ResponseURL': 'https://test.com',
        'ResourceProperties': {
            'teamname-environment': 'team1-dev',
            'ServiceToken': 'lambdaarn',
            'appname': 'app1'
        },
        'RequestType': 'Create',
        'ServiceToken': 'arn:aws:lambda:us-west-2:accountgoeshere:function:lambdafunction',
        'ResourceType': 'Custom::Lookup',
        'RequestId': 'ramdonid',
        'LogicalResourceId': 'CUSTOMLOOKUP'
    }
    handler(request1, None)
    handler(request2, None)
