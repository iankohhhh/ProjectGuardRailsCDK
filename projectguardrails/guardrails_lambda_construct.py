from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    custom_resources as cr,
    aws_ec2 as ec2,
    aws_iam as iam,
    Duration
    )


class GuardrailsLambda(Construct):

    
    def __init__(self, scope: Construct, id:str, 
        vpc,
        tenant_userpool_region,
        tenant_userpool_id,
        private_api_gateway_url,
        bucket_name,
        object_name,
        tenant_id_field,
        error_count_threshold,
        ipset_name,
        **kwargs):
        super().__init__(scope,id,**kwargs)
        
        
        jose_lambda_layer = _lambda.LayerVersion(self, 'jose-lambda-layer',
                  code = _lambda.AssetCode('guardrails-lambda/layers/jose'),
                  compatible_runtimes = [_lambda.Runtime.PYTHON_3_9],
        )
        
        requests_lambda_layer = _lambda.LayerVersion(self, 'requests-lambda-layer',
                  code = _lambda.AssetCode('guardrails-lambda/layers/requests'),
                  compatible_runtimes = [_lambda.Runtime.PYTHON_3_9],
        )
        
        openapi_core_layer = _lambda.LayerVersion(self, 'openapi-core-layer',
                  code = _lambda.AssetCode('guardrails-lambda/layers/openapi-core'),
                  compatible_runtimes = [_lambda.Runtime.PYTHON_3_9],
            )
            
        self.guardrails_lambda = _lambda.Function(
            self,"guardrails-lambda",
            runtime = _lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset("guardrails-lambda"),
            handler = "guardrails_lambda.lambda_handler",
            layers = [jose_lambda_layer,requests_lambda_layer,openapi_core_layer],
            vpc = vpc,
            timeout = Duration.seconds(10),
            environment={
                "cognito_region": tenant_userpool_region,
                "cognito_userpool_id": tenant_userpool_id,
                "private_api_gateway_endpoint": private_api_gateway_url,
                "bucket_name": bucket_name,
                "object_name": object_name,
                "tenant_id_field":tenant_id_field,
                "ipset_name":ipset_name,
                "error_count_threshold":error_count_threshold
            },
            vpc_subnets = ec2.SubnetSelection(
                subnet_type = ec2.SubnetType.PRIVATE_WITH_NAT
            ),
        )