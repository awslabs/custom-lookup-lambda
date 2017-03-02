from __future__ import print_function
from enum import Enum
class constants(Enum):
    DYNAMODBCLIENT='dynamodb'
    DYNAMODBREGION = 'us-west-2'
    TABLENAME = 'custom-lookup'
    DYNAMODBTABLEATTRIBUTE1 = 'teamname-environment'
    DYNAMODBTABLEATTRIBUTE2 = 'appname'
    SUCCESSMESSAGE = "SUCCESS"