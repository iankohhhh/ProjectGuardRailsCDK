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
        table = dynamodb.Table("tenantusers")
        items = table.query(
            KeyConditionExpression=Key('tenant_id').eq(tenant_id)
        )
        return {
            'statusCode':200,
            'body': json.dumps({
                "Items":items["Items"],
                "message":"Successfully retrieved data",
            },cls=DecimalEncoder)
        } 
    except Exception as e:
        return {
            'statusCode':500,
            'body': json.dumps("Item retrieval failed")
        }
