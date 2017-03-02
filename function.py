# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with
# the License. A copy of the License is located at
#     http://aws.amazon.com/apache2.0/
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import os
from models.connector_dynamodb import connector_dynamodb
from models.constants import constants
import json
import boto3
import decimal
import ast
from boto3.dynamodb.conditions import Key, Attr
import requests

objdynamodbconnector = connector_dynamodb()


def initialize():
    if os.getenv('method') is None:
        os.environ["method"] = "query"
    objdynamodbconnector.initialize()


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
            respond_cloudformation(event, constants.SUCCESSMESSAGE.value,data)
        return get_data(event['ResourceProperties'])
    else:
        respond_cloudformation(event, constants.SUCCESSMESSAGE.value)
        return


def insert_data(response):
    objdynamodbconnector.get_dynamodb_client().put_item(
        TableName=constants.TABLENAME.value,
        Item={
            'teamname-environment': {'S': response['teamname-environment']},
            'appname': {'S': response['appname']},
            'info': {'S': str(response['info'])}
        }
    )


def load_data(file="sampledata/sampledata.json"):
    with open(file) as configuration_file:
        mappings = json.load(configuration_file, parse_float=decimal.Decimal)
    return mappings


def get_data(event):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table(constants.TABLENAME.value)
    response = table.query(
        KeyConditionExpression=Key(constants.DYNAMODBTABLEATTRIBUTE1.value).eq(event['teamname-environment']) \
                               & Key(constants.DYNAMODBTABLEATTRIBUTE2.value).eq(event['appname'])
    )

    for item in response['Items']:
        objkeypair = ast.literal_eval(item['info'])
        if 'lookup' in event:
            print(objkeypair[event['lookup']])
            return objkeypair[event['lookup']]
        else:
            print(objkeypair)
            return objkeypair


def respond_cloudformation(event, status, data=None):
    responseBody = {
        'Status': status,
        'Reason': 'See the details in CloudWatch Log Stream',
        'PhysicalResourceId': 'CloudWatch log stream',
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': data
    }

    print('Response = ' + json.dumps(responseBody))
    requests.put(event['ResponseURL'], data=json.dumps(responseBody))


# This is the test harness
if __name__ == '__main__':
    request1 = {
        'StackId': 'arn:aws:cloudformation:us-west-2:accountgoeshere:stack/sample-stack/stackidgoeshere',
        'ResponseURL': 'https://test.com',
        'ResourceProperties': {
            'teamname-environment': 'team1-dev',
            'ServiceToken': 'lambdaarn',
            'appname': 'app1',
            'lookup': 'Vpc'
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
