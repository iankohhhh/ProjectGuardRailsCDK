import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

#Handle the decimal
class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)

def lambda_handler(event, context):
    tenant_id = int(event["queryStringParameters"]["tenant_id"])
    try:
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table("todotasks")
        items = table.query(
            KeyConditionExpression=Key('tenant_id').eq(tenant_id)
        )

        return {
            'statusCode':200,
            'body': json.dumps({
                "Items":items["Items"],
                "message":"Successfully retrieved data for tenant_id " + str(tenant_id)
            },cls=DecimalEncoder),
            # 'headers': {
            #     'Access-Control-Allow-Headers': '*',
            #     'Access-Control-Allow-Origin': '*',
            #     'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            # }
        } 
    except Exception as e:
        return {
            'statusCode':500,
            'body': json.dumps("Item retrieval failed for tenant_id "+ str(tenant_id))
        }
