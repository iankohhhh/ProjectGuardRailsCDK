from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    custom_resources as cr,
    aws_ec2 as ec2,
    aws_iam as iam,
    )


class PublicApiGateway(Construct):

    
    def __init__(self, scope: Construct, id:str,
        guardrails_lambda,
        cognito_auth,
        **kwargs):
        super().__init__(scope,id,**kwargs)
        
        
        
        #Creates A public API gaateway 
        self.public_api_gateway = apigw.LambdaRestApi(
        self, 'public-api-gateway',
        handler = guardrails_lambda,
        rest_api_name = "Public API Gateway to GuardRails Lambda",
        default_method_options = apigw.MethodOptions(
            authorization_type = apigw.AuthorizationType.COGNITO,
            authorizer = cognito_auth
            )
          
        )
        
        
