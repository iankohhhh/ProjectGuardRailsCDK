from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    aws_wafv2 as wafv2,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    custom_resources as cr,
    aws_ec2 as ec2,
    aws_iam as iam,
    )


class WebApplicationFirewall(Construct):

    
    def __init__(self, scope: Construct, id:str,
        public_api_gateway,
        **kwargs):
        super().__init__(scope,id,**kwargs)
        
        #Provisions IP Set for Web ACL rule
        self.cfn_ipset = wafv2.CfnIPSet(self, "MyCfnIPSet",
            ip_address_version="IPV4",
            #Invalid IP according to RFC 5737
            addresses = [],
            scope = "REGIONAL",
            name="GuardRailsIpSet"
        )
        
        
        #Create Web ACL
        self.cfn_web_acl = wafv2.CfnWebACL(self, "MyCfnWebACL",
        default_action=wafv2.CfnWebACL.DefaultActionProperty(
            allow=wafv2.CfnWebACL.AllowActionProperty(
                custom_request_handling=wafv2.CfnWebACL.CustomRequestHandlingProperty(
                    insert_headers=[wafv2.CfnWebACL.CustomHTTPHeaderProperty(
                        name="name",
                        value="value"
                    )]
                )
            ),
        ),
        scope="REGIONAL",
        visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
            cloud_watch_metrics_enabled=False,
            metric_name="guardrailsrequests",
            sampled_requests_enabled=False
        ),
        description="description",
        name="GuardRailsWebACL",
        rules=[wafv2.CfnWebACL.RuleProperty(
            name="IPSetMatchRule",
            priority=123,
            statement=wafv2.CfnWebACL.StatementProperty(
                ip_set_reference_statement={
                    "arn": self.cfn_ipset.attr_arn,
                },
            ),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                cloud_watch_metrics_enabled=False,
                metric_name="metricName",
                sampled_requests_enabled=False
            ),
            action=wafv2.CfnWebACL.RuleActionProperty(
                block=wafv2.CfnWebACL.BlockActionProperty(
                    custom_response=wafv2.CfnWebACL.CustomResponseProperty(
                        response_code=403,
    
            
                    )
                ),
            ),
    
        )],
        
        )
        
        
        #Associates Web ACL with Public API Gateway
        cfn_web_acl_association = wafv2.CfnWebACLAssociation(self, "MyCfnWebACLAssociation",
            resource_arn="arn:aws:apigateway:" + public_api_gateway.env.region + "::/restapis/" + public_api_gateway.rest_api_id + "/stages/"  + public_api_gateway.deployment_stage.stage_name,
            web_acl_arn= self.cfn_web_acl.attr_arn,
        )
        
        
        
        
        