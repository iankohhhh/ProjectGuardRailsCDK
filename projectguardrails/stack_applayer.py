from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    aws_dynamodb as ddb,
    aws_lambda as _lambda,
    custom_resources as cr,
    aws_ec2 as ec2,
    Stack,
    )
    
class ApplicationLayer(Stack):

        
    
    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
    

        
        #CREATES THE DYNAMODB TABLE NAMED TASKS
        dynamodb_tasks_table = ddb.Table(
            self, 'dynamo-tasks',
            table_name = "todotasks",
            partition_key = {'name':'tenant_id', 'type': ddb.AttributeType.NUMBER},
            sort_key = {'name':'user_id','type':ddb.AttributeType.NUMBER},
            removal_policy = cdk.RemovalPolicy.DESTROY,
        )
    
        #POPULATES THE DYNAMODB TABLE WITH INITIAL DATA
        self.populate_dynamo_cr = cr.AwsCustomResource(
            self, "populate-dynamo-todotasks",
            on_create = cr.AwsSdkCall(
                service = "DynamoDB",
                action = "batchWriteItem",
                parameters={
                    "RequestItems":{
                        'todotasks':[
                            {
                                'PutRequest':{
                                    'Item':{
                                        'tenant_id':{
                                            'N':'111',
                                        },
                                        'user_id':{
                                            'N':'1',
                                        },
                                        'task_id':{
                                            'N':'1'
                                        },
                                        'task_description':{
                                            'S':'This is task 1 for user 1 belonging to tenant 111',
                                        },
                                    },
                                    
                                },
                            },
                            {
                                'PutRequest':{
                                    'Item':{
                                        'tenant_id':{
                                            'N':'111',
                                        },
                                        'user_id':{
                                            'N':'2',
                                        },
                                        'task_id':{
                                            'N':'1'
                                        },
                                        'task_description':{
                                            'S':'This is task 1 for user 2 belonging to tenant 111',
                                        },
                                    },
                                    
                                },
                            },
                            {
                                'PutRequest':{
                                    'Item':{
                                        'tenant_id':{
                                            'N':'222',
                                        },
                                        'user_id':{
                                            'N':'1',
                                        },
                                        'task_id':{
                                            'N':'1'
                                        },
                                        'task_description':{
                                            'S':'This is task 1 for user 1 belonging to tenant 222',
                                        },
                                    },
                                    
                                },
                            },
                            {
                                'PutRequest':{
                                    'Item':{
                                        'tenant_id':{
                                            'N':'222',
                                        },
                                        'user_id':{
                                            'N':'2',
                                        },
                                        'task_id':{
                                            'N':'1'
                                        },
                                        'task_description':{
                                            'S':'This is task 1 for user 2 belonging to tenant 222',
                                        },
                                    },
                                    
                                },
                                
                            },
                        ]
                    }
                },
                
                physical_resource_id = cr.PhysicalResourceId.of(
                    dynamodb_tasks_table.table_name
                ),
                
            ),
            policy = cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources = cr.AwsCustomResourcePolicy.ANY_RESOURCE
                ),
            
        )
        
        #CREATES THE DYNAMODB TABLE NAMED TENANTS
        dynamodb_tenants_table = ddb.Table(
            self, 'dynamo-tenantusers',
            table_name = "tenantusers",
            partition_key = {'name':'tenant_id', 'type': ddb.AttributeType.NUMBER},
            sort_key = {'name':'user_id', 'type': ddb.AttributeType.NUMBER},
            removal_policy = cdk.RemovalPolicy.DESTROY,
        )
        
        
        #POPULATES THE DYNAMODB TABLE WITH INITIAL DATA
        self.populate_dynamodb_tenants_table= cr.AwsCustomResource(
            self, "populate-tenantusers-dynamo-cr",
            on_create = cr.AwsSdkCall(
                service = "DynamoDB",
                action = "batchWriteItem",
                parameters={
                    "RequestItems":{
                        'tenantusers':[
                            {
                                'PutRequest':{
                                    'Item':{
                                        'tenant_id':{
                                            'N':'111',
                                        },
                                        'tenant_name':{
                                            'S':'Company 111',
                                        },
                                        'user_id':{
                                            'N':'1',
                                        },
                                        'user_email':{
                                            'S':'user_id_1_tenant_111@example.com',
                                        },
                                        'hashed_pw':{
                                            'S':'$2a$04$u4J4.mez2o.IUJk.tidrTOgdWFstXYz5zaxJH.5/fejBGrQ4OqwaO',
                                        },                                       

                                    },
                                    
                                },
                            },
                            {
                                'PutRequest':{
                                    'Item':{
                                        'tenant_id':{
                                            'N':'111',
                                        },
                                        'tenant_name':{
                                            'S':'Company 111',
                                        },
                                        'user_id':{
                                            'N':'2',
                                        },
                                        'user_email':{
                                            'S':'user_id_2_tenant_111@example.com',
                                        },
                                        'hashed_pw':{
                                            'S':'$eoirofier.mez2o.IUJk.tidrTOgdWFstXYz5zaxJH.5/fejBGrQ4OqwaO',
                                        },                                       

                                    },
                                    
                                },
                            },
                            {
                                'PutRequest':{
                                    'Item':{
                                        'tenant_id':{
                                            'N':'111',
                                        },
                                        'tenant_name':{
                                            'S':'Company 111',
                                        },
                                        'user_id':{
                                            'N':'3',
                                        },
                                        'user_email':{
                                            'S':'user_id_3_tenant_111@example.com',
                                        },
                                        'hashed_pw':{
                                            'S':'$ee930r2u83.mez2o.IUJk.tidrTOgdWFstXYz5zaxJH.5/fejBGrQ4OqwaO',
                                        },                                       

                                    },
                                    
                                },
                            },
                            {
                                'PutRequest':{
                                    'Item':{
                                        'tenant_id':{
                                            'N':'222',
                                        },
                                        'tenant_name':{
                                            'S':'Company 222',
                                        },
                                        'user_id':{
                                            'N':'1',
                                        },
                                        'user_email':{
                                            'S':'user_id_1_tenant_222@example.com',
                                        },
                                        'hashed_pw':{
                                            'S':'$ee930r2u83.mez2o.IUJk.tidrTOgdWFstXYz5zaxJH.5/fejBGrQ4OqwaO',
                                        },                                       

                                    },
                                    
                                },
                            },
                            {
                                'PutRequest':{
                                    'Item':{
                                        'tenant_id':{
                                            'N':'222',
                                        },
                                        'tenant_name':{
                                            'S':'Company 222',
                                        },
                                        'user_id':{
                                            'N':'2',
                                        },
                                        'user_email':{
                                            'S':'user_id_2_tenant_222@example.com',
                                        },
                                        'hashed_pw':{
                                            'S':'$ee930r2u83.mez2o.IUJk.tidrTOgdWFstXYz5zaxJH.5/fejBGrQ4OqwaO',
                                        },                                       

                                    },
                                    
                                },
                            }
                        ]
                    }
                },
                
                physical_resource_id = cr.PhysicalResourceId.of(
                    dynamodb_tenants_table.table_name
                ),
                
            ),
            policy = cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources = cr.AwsCustomResourcePolicy.ANY_RESOURCE
                ),
            
        )
        
        #--------------------------------------------------------------CREATING LAMBDA FUNCTIONS------------------------------------------------------------------------------#
        
        #CREATE LAMBDA FUNCTION FOR endpoint [GET] /getitemsfortenant
        self.getitemsfortenant_lambda = _lambda.Function(
            self,"getitemsfortenant-lambda",
            runtime = _lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset("applayer-lambda"),
            handler = "getitemsfortenant.lambda_handler",
            vpc = vpc,
            vpc_subnets = ec2.SubnetSelection(
                subnet_type = ec2.SubnetType.PRIVATE_WITH_NAT
            ),
        )
        
        #GRANTS THE LAMBDA FUNCTION READ AND WRITE ACCESS TO DYNAMODB TABLE
        dynamodb_tasks_table.grant_read_write_data(self.getitemsfortenant_lambda)
        
        
        #CREATE LAMBDA FUNCTION FOR endpoint [GET] /getalltenantitems
        self.getalltenantitems_lambda = _lambda.Function(
            self,"getalltenantitems-lambda",
            runtime = _lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset("applayer-lambda"),
            handler = "getalltenantitems.lambda_handler",
            vpc = vpc,
            vpc_subnets = ec2.SubnetSelection(
                subnet_type = ec2.SubnetType.PRIVATE_WITH_NAT
            ),
        )
        
        #GRANTS THE LAMBDA FUNCTION READ AND WRITE ACCESS TO DYNAMODB TABLE
        dynamodb_tasks_table.grant_read_write_data(self.getalltenantitems_lambda)

        
        # #CREATE LAMBDA FUNCTION FOR endpoint [POST] /additem
        # self.postadditem_lambda = _lambda.Function(
        #     self,"postadditem-lambda",
        #     runtime = _lambda.Runtime.PYTHON_3_9,
        #     code = _lambda.Code.from_asset("applayer-lambda"),
        #     handler = "postadditem.lambda_handler",
        #     vpc = vpc,
        #     vpc_subnets = ec2.SubnetSelection(
        #         subnet_type = ec2.SubnetType.PRIVATE_WITH_NAT
        #     ),
        # )
        
        # #GRANTS THE LAMBDA FUNCTION READ AND WRITE ACCESS TO DYNAMODB TABLE
        # dynamodb_tasks_table.grant_read_write_data(self.postadditem_lambda)
        
        
        # #CREATE LAMBDA FUNCTION FOR endpoint [PUT] /updateitem
        # self.putupdateitem_lambda = _lambda.Function(
        #     self,"putupdateitem-lambda",
        #     runtime = _lambda.Runtime.PYTHON_3_9,
        #     code = _lambda.Code.from_asset("applayer-lambda"),
        #     handler = "putupdateitem.lambda_handler",
        #     vpc = vpc,
        #     vpc_subnets = ec2.SubnetSelection(
        #         subnet_type = ec2.SubnetType.PRIVATE_WITH_NAT
        #     ),
        # )
        
        # #GRANTS THE LAMBDA FUNCTION READ AND WRITE ACCESS TO DYNAMODB TABLE
        # dynamodb_tasks_table.grant_read_write_data(self.putupdateitem_lambda)
        
        
        # #CREATE LAMBDA FUNCTION FOR endpoint [DELETE] /deletitem
        # self.deletedeleteitem_lambda = _lambda.Function(
        #     self,"deletedeleteitem-lambda",
        #     runtime = _lambda.Runtime.PYTHON_3_9,
        #     code = _lambda.Code.from_asset("applayer-lambda"),
        #     handler = "deletedeleteitem.lambda_handler",
        #     vpc = vpc,
        #     vpc_subnets = ec2.SubnetSelection(
        #         subnet_type = ec2.SubnetType.PRIVATE_WITH_NAT
        #     ),
        # )
        # #GRANTS THE LAMBDA FUNCTION READ AND WRITE ACCESS TO DYNAMODB TABLE
        # dynamodb_tasks_table.grant_read_write_data(self.deletedeleteitem_lambda)
        
        
        #CREATE LAMBDA FUNCTION FOR gettenantusers /getlistofusers
        self.gettenantusers_lambda = _lambda.Function(
            self,"gettenantusers-lambda",
            runtime = _lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset("applayer-lambda"),
            handler = "gettenantusers.lambda_handler",
            vpc = vpc,
            vpc_subnets = ec2.SubnetSelection(
                subnet_type = ec2.SubnetType.PRIVATE_WITH_NAT
            ),
        )
        
        #GRANTS THE LAMBDA FUNCTION READ AND WRITE ACCESS TO DYNAMODB TABLE

        dynamodb_tenants_table.grant_read_write_data(self.gettenantusers_lambda)
        

        
        