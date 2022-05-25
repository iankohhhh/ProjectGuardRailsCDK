
# Welcome to Project GuardRails!

Quip Reference: https://quip-amazon.com/7pYLA2KB28eN/Project-GuardRails

Project GuardRails aims to add an additional layer of security to multi-tenant applications by
inspecting the response body of a request to the application layer. Upon inspection, the repsonse body is
evaluated against 2 criterias before being allowed to be passed to the client side.

Project GuardRails ensures that: 

1. The response body follows the schema specified in the OpenAPI file. This prevent's any form of SQL injection aimed to retrieve additional unauthorized data.

2. The tenant identification field within the response body matches the tenant identification in the JWT token provided by AWS Cognito. 

This ensures that each tenant is only able to retrieve their own respective data, preventing any breach in other tenant's data.





# Step 1. Setting up the environment

## Install the required dependencies.

```
pip install -r requirements.txt
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Be sure to bootstrap the CDK environment before deployment
```
cdk bootstrap
```

## To deploy ProjectGuardRails, with the command listed below,

1. Edit the parameter uploadobjectname to the file name of your OpenAPI json file

2. Edit the parameter tenantidfield to the name of the tenant id field you wish to specify

```
cdk deploy --all --parameters ProjectGuardRailsStack:uploadobjectname=OpenAPIfile.json --parameters ProjectGuardRailsStack:tenantidfield=tenant_id --parameters ProjectGuardRailsStack:errorcountthreshold=3 --require-approval never
```



# Step 2. Upload your OpenAPI file to S3 with the AWS Console

Upon deployment of the CDK stacks, an S3 bucket has been created for you to upload your OpenAPI file as an S3 object. 

To retrieve the OpenAPI file based on the sample application, export an OpenAPI file written in JSON from the Private API Gateway in your console. 

Upload your OpenAPI file to the S3 bucket that has been provisioned and ensure that your filename follows the parameter you have entered in your cdk deploy command.

As per default value, your OpenAPI file should be named "OpenAPIFile.json"

