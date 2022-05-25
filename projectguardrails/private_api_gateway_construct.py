from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    custom_resources as cr,
    aws_ec2 as ec2,
    aws_iam as iam,
    )


class PrivateApiGateway(Construct):

    
    def __init__(self, scope: Construct, id:str, 
        vpc,
        getalltenantitems_lambda,
        getitemsfortenant_lambda,
        # postadditem_lambda,
        # putupdateitem_lambda,
        # deletedeleteitem_lambda,
        gettenantusers_lambda,
        **kwargs):
        super().__init__(scope,id,**kwargs)
        

        
        #Adds a new interface endpoint to the vpc for the private api gateway
        private_api_gateway_endpoint = vpc.add_interface_endpoint(
            "apiGw",
            service = ec2.InterfaceVpcEndpointAwsService.APIGATEWAY
            )
        
        #Creates A private API gaateway 
        self.private_api_gateway = apigw.LambdaRestApi(
        self, 'private-api-gateway',
        handler = getitemsfortenant_lambda,
        rest_api_name = "Private API Gateway to Lambda App Layer",
        endpoint_configuration = apigw.EndpointConfiguration(
            types=[apigw.EndpointType.PRIVATE],
            vpc_endpoints=[private_api_gateway_endpoint]
            ),
        policy = iam.PolicyDocument(
            statements=[
            iam.PolicyStatement(
                effect = iam.Effect.ALLOW,
                principals = [iam.AnyPrincipal()],
                actions = ["execute-api:Invoke"],
                resources = [cdk.Fn.join('',['execute-api:/','*'])]
            ),
            iam.PolicyStatement(
                effect = iam.Effect.DENY,
                principals=[iam.AnyPrincipal()],
                actions=["execute-api:Invoke"],
                resources=[cdk.Fn.join('',['execute-api:/','*'])],
                conditions={
                    "StringNotEquals":{
                        "aws:sourceVpc":vpc.vpc_id
                    }
                }
            )
        ])
        
        )
        
        



        # We define the JSON Schema for the transformed valid response
        tenant_items_response_model = self.private_api_gateway.add_model("TenantItemsModell",
            content_type="application/json",
            model_name="TenantItemsModell",
            schema=apigw.JsonSchema(
                schema=apigw.JsonSchemaVersion.DRAFT4,
                title="tenantitems",
                type=apigw.JsonSchemaType.OBJECT,
                properties={
                    "Items": apigw.JsonSchema(
                        type=apigw.JsonSchemaType.ARRAY,
                        items=apigw.JsonSchema(
                            type=apigw.JsonSchemaType.OBJECT,
                            properties={
                                "task_id":apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
                                "tenant_id":apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
                                "user_id":apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
                                "task_description":apigw.JsonSchema(type=apigw.JsonSchemaType.STRING)
                            }
                        )
                    ),
                    "message":apigw.JsonSchema(
                        type=apigw.JsonSchemaType.STRING
                        )
                    
                },
                additional_properties=False,
            )
        )
    
        # postput_items_response_model = self.private_api_gateway.add_model("PostPutItemsModel",
        #     content_type="application/json",
        #     model_name="PostPutItemsModel",
        #     schema=apigw.JsonSchema(
        #         schema=apigw.JsonSchemaVersion.DRAFT4,
        #         title="tenantitems",
        #         type=apigw.JsonSchemaType.OBJECT,
        #         properties={
        #             "Items": apigw.JsonSchema(
        #                 type=apigw.JsonSchemaType.ARRAY,
        #                 items=apigw.JsonSchema(
        #                     type=apigw.JsonSchemaType.OBJECT,
        #                     properties={
        #                         "task_id":apigw.JsonSchema(type=apigw.JsonSchemaType.INTEGER),
        #                         "tenant_id":apigw.JsonSchema(type=apigw.JsonSchemaType.INTEGER),
        #                         "user_id":apigw.JsonSchema(type=apigw.JsonSchemaType.INTEGER),
        #                         "task_description":apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
        #                     }
        #                 )
        #             ),
        #             "message":apigw.JsonSchema(
        #                 type=apigw.JsonSchemaType.STRING
        #                 )
                    
        #         },
        #         additional_properties=False,
        #     )
        # )    
        

        # delete_item_response_model = self.private_api_gateway.add_model("DeleteItemModel",
        #     content_type="application/json",
        #     model_name="DeleteItemModel",
        #     schema=apigw.JsonSchema(
        #         schema=apigw.JsonSchemaVersion.DRAFT4,
        #         title="tenantitems",
        #         type=apigw.JsonSchemaType.OBJECT,
        #         properties={
        #             "Items": apigw.JsonSchema(
        #                 type=apigw.JsonSchemaType.ARRAY,
        #                 items=apigw.JsonSchema(
        #                     type=apigw.JsonSchemaType.OBJECT,
        #                     properties={
        #                         "task_id":apigw.JsonSchema(type=apigw.JsonSchemaType.INTEGER),
        #                         "tenant_id":apigw.JsonSchema(type=apigw.JsonSchemaType.INTEGER),
        #                         "user_id":apigw.JsonSchema(type=apigw.JsonSchemaType.INTEGER)
                                
        #                     }
        #                 )
        #             ),
        #             "message":apigw.JsonSchema(
        #                 type=apigw.JsonSchemaType.STRING
        #                 )
                    
        #         },
        #         additional_properties=False,
        #     )
        # ) 
        

        gettenantusers_response_model = self.private_api_gateway.add_model("GetTenantUsersModel",
            content_type="application/json",
            model_name="GetTenantUsersModel",
            schema=apigw.JsonSchema(
                schema=apigw.JsonSchemaVersion.DRAFT4,
                title="tenantinfo",
                type=apigw.JsonSchemaType.OBJECT,
                properties={
                    "Items": apigw.JsonSchema(
                        type=apigw.JsonSchemaType.ARRAY,
                        items=apigw.JsonSchema(
                            type=apigw.JsonSchemaType.OBJECT,
                            properties={
                                "tenant_id":apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
                                "user_id":apigw.JsonSchema(type=apigw.JsonSchemaType.STRING),
                                "user_email":apigw.JsonSchema(type=apigw.JsonSchemaType.STRING)
                            }
                        )
                    ),
                    "message":apigw.JsonSchema(
                        type=apigw.JsonSchemaType.STRING
                        )
                    
                },
                additional_properties=False,
            )
        ) 
        
        
        
        successful_getitem_method_response = apigw.MethodResponse(
            status_code="200",
        
            # the properties below are optional
            response_models={
                "application/json":tenant_items_response_model
            },
            response_parameters={
                "method.response.header.Content-Type": True
            }
        )
        
        
        # successful_postputitem_method_response = apigw.MethodResponse(
        #     status_code="200",
        #     # the properties below are optional
        #     response_models={
        #         "application/json":postput_items_response_model
        #     },
        #     response_parameters={
        #         "method.response.header.Content-Type": True
        #     }
        # )
        
        # unsuccessful_postputitem_method_response = apigw.MethodResponse(
        #     status_code="500",
        #     # the properties below are optional
        #     response_models={
        #         "application/json":postput_items_response_model
        #     },
        #     response_parameters={
        #         "method.response.header.Content-Type": True
        #     }
        # )
        
        
        # successful_deleteitem_method_response = apigw.MethodResponse(
        #     status_code="200",
        
        #     # the properties below are optional
        #     response_models={
        #         "application/json":delete_item_response_model
        #     },
        #     response_parameters={
        #         "method.response.header.Content-Type": True
        #     }
        # )
        
        # unsuccessful_deleteitem_method_response = apigw.MethodResponse(
        #     status_code="500",
        
        #     # the properties below are optional
        #     response_models={
        #         "application/json":delete_item_response_model
        #     },
        #     response_parameters={
        #         "method.response.header.Content-Type": True
        #     }
        # )
        
        unsuccessful_gettenantusers_method_response = apigw.MethodResponse(
            status_code="500",
        
            # the properties below are optional
            response_models={
                "application/json":gettenantusers_response_model
            },
            response_parameters={
                "method.response.header.Content-Type": True
            }
        )
        
        
        resource_getalltenantitems = self.private_api_gateway.root.add_resource("getalltenantitems")
        resource_getalltenantitems.add_method(
            "GET", apigw.LambdaIntegration(getalltenantitems_lambda), 
            method_responses = [successful_getitem_method_response]
            ) #/getalltenantitems
        
        
        resource_getitemsforttenant = self.private_api_gateway.root.add_resource("getitemsfortenant")
        resource_getitemsforttenant.add_method(
            "GET", apigw.LambdaIntegration(getitemsfortenant_lambda),
            method_responses = [successful_getitem_method_response]
            ) #/getitemsfortenant
        
        
        
        # resource_postadditem = self.private_api_gateway.root.add_resource("additem")
        # resource_postadditem.add_method(
        #     "POST", apigw.LambdaIntegration(postadditem_lambda),
        #     method_responses = [successful_postputitem_method_response, unsuccessful_postputitem_method_response]
        #     ) #/additem
        
        
        # resource_putupdateitem = self.private_api_gateway.root.add_resource("updateitem")
        # resource_putupdateitem.add_method(
        #     "PUT", apigw.LambdaIntegration(putupdateitem_lambda),
        #     method_responses = [successful_postputitem_method_response, unsuccessful_postputitem_method_response]
        #     ) #/updateitem
        
        
        # resource_deletedeleteitem = self.private_api_gateway.root.add_resource("deleteitem")
        # resource_deletedeleteitem.add_method(
        #     "DELETE", apigw.LambdaIntegration(deletedeleteitem_lambda),
        #     method_responses = [successful_deleteitem_method_response, unsuccessful_deleteitem_method_response]
        #     ) #/deleteitem
    
        resource_gettenantusers = self.private_api_gateway.root.add_resource("getlistofusers")
        resource_gettenantusers.add_method(
            "GET", apigw.LambdaIntegration(gettenantusers_lambda),
            method_responses = [unsuccessful_gettenantusers_method_response]
            )