#!/usr/bin/env python3
import os

import aws_cdk as cdk

from projectguardrails.stack_projectguardrails import ProjectguardrailsStack
from projectguardrails.stack_applayer import ApplicationLayer
from projectguardrails.stack_vpc import CdkVpcStack


app = cdk.App()

#VPC STACK
vpc_stack = CdkVpcStack(app,"CdkVPCStack")

#APPLICATION LAYER STACK (DYNAMODB AND LAMBDA APP)
app_stack = ApplicationLayer(app, "ApplicationLayerStack",
    vpc=vpc_stack.vpc)
    
#PROJECT GUARDRAILS
projectguardrails_stack = ProjectguardrailsStack(app,"ProjectGuardRailsStack",
    vpc=vpc_stack.vpc,
    getalltenantitems_lambda=app_stack.getalltenantitems_lambda,
    getitemsfortenant_lambda=app_stack.getitemsfortenant_lambda,
    # postadditem_lambda=app_stack.postadditem_lambda,
    # putupdateitem_lambda=app_stack.putupdateitem_lambda,
    # deletedeleteitem_lambda=app_stack.deletedeleteitem_lambda,
    gettenantusers_lambda=app_stack.gettenantusers_lambda,
    )

app.synth()
