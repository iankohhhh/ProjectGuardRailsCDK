import json
import boto3
import os
import requests
import urllib.request
import time
from jose import jwk, jwt
from jose.utils import base64url_decode
from requests import Request
from json import load

from openapi_core.validation.response.validators import ResponseValidator
from openapi_core.validation.request.datatypes import RequestParameters, OpenAPIRequest
from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.contrib.requests import RequestsOpenAPIResponse
from openapi_core import create_spec

#--------------------------------------------------------COGNITO DETAILS --------------------------------------------------------

region = os.environ['cognito_region']
userpool_id= os.environ['cognito_userpool_id']

keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(region, userpool_id)

# instead of re-downloading the public keys every time we download them only on cold start
with urllib.request.urlopen(keys_url) as f:
    response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']


# #------------------------------------------------- Pull Swagger API doc from S3 -------------------------------------------------

#Instantiate s3 client
s3_client = boto3.client("s3")
#Pull bucket name from  CDK and object key name from CDK
S3_BUCKET = os.environ['bucket_name']
object_key = os.environ['object_name']

file_content = s3_client.get_object(
    Bucket=S3_BUCKET, Key=object_key)['Body']
spec_dict = load(file_content)
spec = create_spec(spec_dict)

#--------------------------------------------- Recursive way to find list of tenant id ---------------------------------------------

#Returns a list of id's in a list. Check if all id's in this list is equals to JWT
def get_list_of_tid(y,id_parameter):
    list_of_tid = []
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                if a == id_parameter:
                    list_of_tid.append(x[a])
                flatten(x[a],name+ a +'_')
        elif type(x) is list:
            i=0
            for a in x:
                flatten(a,name + str(i) + '_')
                i += 1
    flatten(y)
    return list_of_tid
                

# #--------------------------------------------------------Update WAF IPSet----------------------------------------------------------

def check_sourceip_ddb(source_ip):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("GuardrailsSourceIpCounter")
    #If item exists, add counter +=1
    table.update_item(
        Key={
            'source_ip': source_ip
        },
        UpdateExpression="SET error_count = if_not_exists(error_count, :start) + :inc",
    
        ExpressionAttributeValues={
            ':inc': 1,
            ':start': 1,
        },
        ReturnValues="UPDATED_NEW"
    )
    item = table.get_item(Key={'source_ip': source_ip})
    error_count = item["Item"]["error_count"]
    if error_count > int(os.environ["error_count_threshold"]):
        return True
    


ipset_name = os.environ['ipset_name']
def update_ipset(ip_ranges):
    client = boto3.client('wafv2')
    target_ip_sets = {}
    token = []
    for i in client.list_ip_sets(Scope='REGIONAL')['IPSets']:
        if ipset_name in i['Name']:
            target_ip_sets.update({i['Name']:i['Id']})
            token = i['LockToken']

    for k, v in target_ip_sets.items():
        client.update_ip_set(
        Name=k,
        Scope='REGIONAL',
        Id=v,
        Addresses=ip_ranges,
        LockToken=token
        )


#---------------------------------------------------------LAMBDA HANDLER --------------------------------------------------------

def lambda_handler(event, context):
    
    
#----------------------------------------------------------VERIFYING JWT---------------------------------------------------------
    #Get authoerization token and decode the signature to get the tenant_id field within the jwt
    token = event["headers"]["Authorization"]
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    #search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False
        
    #Construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    #decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    # since we passed the verification, we can now safely use the unverified claims
    claims = jwt.get_unverified_claims(token)
    
    #We extract the tenant_id from the jwt and assign variable tenant_id_jwt to the value
    tenant_id_jwt = int(claims['custom:'+os.environ["tenant_id_field"]])
    
    
    
    
#---------------------------------------------------------HANDLE API REQUESTS --------------------------------------------------------
    
    #Private API Gateway API endpoint 
    api_endpoint = os.environ['private_api_gateway_endpoint']
    #Includes path at the back of the api endpoint e.g /getitemsforalltenants
    api_endpoint = api_endpoint[:-1] + event["path"]
    

    
    #Handling GET Requests
    #If query string parameter is absent, take tenant_id from JWT
    
    
    if event["httpMethod"] == "GET":
    #If there is query parameters:
        query_parameters = event['queryStringParameters']
        if query_parameters:
            #Handle query parameters
            api_endpoint += "?"
            for query_paramater_key in query_parameters:
                #Add to api_endpoint e.g /getitemsfortenant?tenant_id=111&
                api_endpoint+=query_paramater_key+"="+query_parameters[query_paramater_key]+"&"
            #Remove last "&" character e.g /getitemsfortenant?tenant_id=111
            api_endpoint = api_endpoint[:-1]
        #Invoke response_data
        response_data = requests.get(api_endpoint)
        openapi_request = RequestsOpenAPIRequest(
            Request('GET',api_endpoint)
            )
        
        
    #Handling POST Requests
    if event["httpMethod"]=="POST":
        #Retrieve request body data from event body
        data = event["body"]
        response_data = requests.post(api_endpoint,data=data)
        openapi_request = RequestsOpenAPIRequest(
            Request('POST',api_endpoint)
            )        
        
        
    #Handling PUT Requests
    if event["httpMethod"]=="PUT":
        #Retrieve request body data from event body
        data = event["body"]
        response_data = requests.put(api_endpoint,data=data)
        openapi_request = RequestsOpenAPIRequest(
            Request('PUT',api_endpoint)
            )       
            
    
    #Handling DELETE Requests
    if event["httpMethod"]=="DELETE":
        #Retrieve request body data from event body
        data = event["body"]
        response_data = requests.delete(api_endpoint,data=data)
        openapi_request = RequestsOpenAPIRequest(
            Request('DELETE',api_endpoint)
            )        
        
        
#---------------------------------------------------------RULES--------------------------------------------------------

# Rule 1: Checks that tenant_id field in the query string parameter == JWT, if not return an Unauthorized message

    if event['queryStringParameters'][os.environ["tenant_id_field"]]!=str(tenant_id_jwt):
        return {
        "isBase64Encoded": False,
        "statusCode": 401,
        # 'headers': {
        #     'Access-Control-Allow-Headers': '*',
        #     'Access-Control-Allow-Origin': '*',
        #     'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        #     },
        "body": json.dumps("Unauthorized. Tenant ID in JWT and Query string parameters do not match.")
        }



#Rule 2: Check Schema against OpenAPI definition file

    #Creates OpenAPI response from Requests library response object 
    openapi_response = RequestsOpenAPIResponse(response_data)
    #Creates response validator instance with spec file
    validator = ResponseValidator(spec)
    #Get result
    result = validator.validate(openapi_request,openapi_response)
    #raise errors if response invalid
    errors = result.errors
    request_source_ip = str(event['requestContext']['identity']['sourceIp'])

    if errors:
        #Update IP set in WAF to block the IP
        
        #If there is a source IP, e.g tested from Postman or a machine, not API Gateway
        if (request_source_ip != "test-invoke-source-ip"):
            
            #Check if error_count in dynamodb >= 3:
            if check_sourceip_ddb(request_source_ip) == True:
                
                #If it is true, update ipset to block
                update_ipset([request_source_ip+"/32"])
                
        #Return 401 error response
        return {
        "isBase64Encoded": False,
        "statusCode": 401,
        # 'headers': {
        #     'Access-Control-Allow-Headers': '*',
        #     'Access-Control-Allow-Origin': '*',
        #     'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        #     },
        "body": json.dumps("Unauthorized. The response body does not match the intended schema specified")
        }
        
        
#Rule 3: If no errors in rule 1, then proceed to check that every tenant id field in the response == tenant id field in JWT        

    else:
        #Use input parameter in cdk to search for key
        list_of_tid = get_list_of_tid(result.data, os.environ["tenant_id_field"])
        #If there is no items in the table
        if list_of_tid == []:
            return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "body": json.dumps(response_data.json())
            }
            
        for tid in list_of_tid:
            if int(tid) != tenant_id_jwt:
                
                #Update IP set in WAF to block the IP
                if (request_source_ip != "test-invoke-source-ip"):
            
                    # #Check if error_count in dynamodb >= 3:
                    if check_sourceip_ddb(request_source_ip):
                        
                        #If it is true, update ipset to block
                        update_ipset([request_source_ip+"/32"])
                #Return 401 error response
                return {
                "isBase64Encoded": False,
                "statusCode": 401,
                # 'headers': {
                #     'Access-Control-Allow-Headers': '*',
                #     'Access-Control-Allow-Origin': '*',
                #     'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                #     },
                "body": json.dumps("Unauthorized. Response data includes items that does not belong to tenant")
                }
        
        
    #If both checks are passed, return response data        
        return {
        "isBase64Encoded": False,
        "statusCode": 200,
        # 'headers': {
        #     'Access-Control-Allow-Headers': '*',
        #     'Access-Control-Allow-Origin': '*',
        #     'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        #     },
        "body": json.dumps(response_data.json())
        }
                
        
   

    