from __future__ import print_function
import boto3
from constants import constants
table = constants.TABLENAME.value

class connector_dynamodb(object):


    def createtable(self):
        self.get_dynamodb_client().create_table(
            TableName=table,
            KeySchema=[
                {'AttributeName': constants.DYNAMODBTABLEATTRIBUTE1.value, 'KeyType': 'HASH'},
                {'AttributeName': constants.DYNAMODBTABLEATTRIBUTE2.value, 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': constants.DYNAMODBTABLEATTRIBUTE1.value, 'AttributeType': 'S'},
                {'AttributeName': constants.DYNAMODBTABLEATTRIBUTE2.value, 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        # Wait for table creation
        self.get_dynamodb_client().get_waiter('table_exists').wait(TableName=table)

    def get_dynamodb_client(self):
        return boto3.client(constants.DYNAMODBCLIENT.value, region_name=constants.DYNAMODBREGION.value)

    def initialize(self):
        try:
            self.get_dynamodb_client().describe_table(TableName=table)
        except Exception:
            self.createtable()
