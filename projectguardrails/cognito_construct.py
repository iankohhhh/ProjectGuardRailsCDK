from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    aws_cognito as cognito,
    custom_resources as cr,
    aws_apigateway as apigw,
    )
import random
import string
class Cognito(Construct):

    
    def __init__(self, scope: Construct, id:str,
        tenant_id_field,
        bucket_name,
        **kwargs):
        super().__init__(scope,id,**kwargs)
        
        #Creates User Pool
        self.tenant_userpool = cognito.UserPool(self, "tenants-userpool",
        user_pool_name = "tenants",
        custom_attributes = {
            tenant_id_field :cognito.NumberAttribute(min=1, max=999, mutable=False)
        }
        
        )
        

        #Populates User Pool with Mock Data
        populate_userpool_with_tenant = cr.AwsCustomResource(
            self, "populate-tenant-userpool_with_mock_tenant",
            on_create = cr.AwsSdkCall(
                service = "CognitoIdentityServiceProvider",
                action = "adminCreateUser",
                parameters={
                    "UserPoolId":self.tenant_userpool.user_pool_id,
                    "Username": "tenant_111",
                    "TemporaryPassword":"Password123!",
                    "UserAttributes":[
                        {
                            "Name":"email",
                            "Value":"tenant_111@example.com"
                        },
                        
                        {
                            "Name":"name",
                            "Value":"tenant_111"
                        },
                        {
                            "Name":"custom:"+tenant_id_field,
                            "Value":"111"
                        }
                        
                    ]
                },
                physical_resource_id = cr.PhysicalResourceId.of(
                    self.tenant_userpool.user_pool_id
                ),
            ),
            policy = cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources = cr.AwsCustomResourcePolicy.ANY_RESOURCE
                ),
        )
        
        #Adding app client ot user pool
        userpool_client = self.tenant_userpool.add_client("app-client",
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    implicit_code_grant=True
                ),
             scopes = [cognito.OAuthScope.OPENID],
             callback_urls = ["http://localhost:5000/callbackmockurl"]
            )
            
        )


        #Add Domain For Hosted UI
        self.tenant_userpool.add_domain("MyCognitoDomain",
            cognito_domain = cognito.CognitoDomainOptions(
                domain_prefix = userpool_client.user_pool_client_id
                )
        )
        
        self.auth = apigw.CognitoUserPoolsAuthorizer(self, "tenantAuthorizer",
            cognito_user_pools = [self.tenant_userpool]
            )
        