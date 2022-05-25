import json
import boto3

from decimal import Decimal

#Handle the decimal
class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)


def lambda_handler(event, context):
    # TODO implement
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("todotasks")
    items = table.scan()
    print(items)
    
    return {
        'statusCode':200,
        'body': json.dumps({
            "Items":items["Items"],
            "message":"Successfully retrieved data for all tenants"
        },cls=DecimalEncoder)
    } 
