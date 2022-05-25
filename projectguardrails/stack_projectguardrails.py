import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_iam as iam,
    aws_dynamodb as ddb,
    CfnParameter
)
from constructs import Construct
from .private_api_gateway_construct import PrivateApiGateway
from .guardrails_lambda_construct import GuardrailsLambda
from .public_api_gateway_construct import PublicApiGateway
from .cognito_construct import Cognito
from .waf_construct import WebApplicationFirewall

class ProjectguardrailsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, 
        vpc, 
        getalltenantitems_lambda,
        getitemsfortenant_lambda, 
        # postadditem_lambda,
        # putupdateitem_lambda,
        # deletedeleteitem_lambda,
        gettenantusers_lambda,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "ProjectguardrailsQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
        upload_object_name = CfnParameter(self, "upload-object-name", type="String",
            description="The name of the Amazon S3 object, the OpenAPI json file.")

        tenant_id_field = CfnParameter(self, "tenant-id-field", type="String",
            description="The name of the tenant id field defined in cognito.")
            
        error_count_threshold = CfnParameter(self, "error-count-threshold", type="String",
            description="The number of times an unauthorized request can occur before being blocked by WAF")
        
        bucket = s3.Bucket(self,"MyBucket",
            block_public_access = s3.BlockPublicAccess.BLOCK_ALL
            )
        
        
        private_api_gateway = PrivateApiGateway(
            self, "private-api-gateway", 
                vpc=vpc,
                getalltenantitems_lambda=getalltenantitems_lambda,
                getitemsfortenant_lambda=getitemsfortenant_lambda,
                # postadditem_lambda=postadditem_lambda,
                # putupdateitem_lambda=putupdateitem_lambda,
                # deletedeleteitem_lambda=deletedeleteitem_lambda,
                gettenantusers_lambda = gettenantusers_lambda
            )
            
        cognito = Cognito(
            self, "cognito-service",
            tenant_id_field.value_as_string,
            bucket.bucket_name,
            )
            
        #CREATES THE DYNAMODB TABLE NAMED sourceipcount
        dynamodb_sourceipcount =  ddb.Table(
            self, 'dynamodb-sourceipcounter',
            table_name = "GuardrailsSourceIpCounter",
            partition_key = {'name':'source_ip', 'type': ddb.AttributeType.STRING},
            removal_policy = cdk.RemovalPolicy.DESTROY,
        )
            
        
        guardrails_lambda = GuardrailsLambda(
            self, "guardrails-lambda-function",
            vpc = vpc,
            tenant_userpool_region=cognito.tenant_userpool.env.region,
            tenant_userpool_id=cognito.tenant_userpool.user_pool_id,
            private_api_gateway_url=private_api_gateway.private_api_gateway.url,
            bucket_name = bucket.bucket_name,
            object_name = upload_object_name.value_as_string,
            tenant_id_field = tenant_id_field.value_as_string,
            error_count_threshold=error_count_threshold.value_as_string,
            ipset_name = ""
            )
            
        public_api_gateway = PublicApiGateway(
            self, "public-api-gateway",
            guardrails_lambda = guardrails_lambda.guardrails_lambda,
            cognito_auth = cognito.auth,
            )
            
        web_application_firewall = WebApplicationFirewall(
            self, "web-application-firewall",
            public_api_gateway = public_api_gateway.public_api_gateway
            )
            
        guardrails_lambda.ipset_name = web_application_firewall.cfn_ipset.name
            
        #Permissions
        bucket.grant_read(guardrails_lambda.guardrails_lambda)
        guardrails_lambda.guardrails_lambda.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AWSWAFFullAccess"))
        dynamodb_sourceipcount.grant_read_write_data(guardrails_lambda.guardrails_lambda)