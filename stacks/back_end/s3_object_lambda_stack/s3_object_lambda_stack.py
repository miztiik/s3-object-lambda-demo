from aws_cdk import aws_iam as _iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_s3objectlambda as _s3objlambda
from aws_cdk import aws_logs as _logs
from aws_cdk import core as cdk
from stacks.miztiik_global_args import GlobalArgs


class S3ObjectLambdaStack(cdk.Stack):

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        stack_log_level: str,
        sales_lambda_ap_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Add your stack resources below)

        # Create AWS XRay Layer
        boto3_layer = _lambda.LayerVersion(
            self,
            "boto3Layer",
            code=_lambda.Code.from_asset(
                "stacks/back_end/s3_object_lambda_stack/lambda_src/layer_code/boto3_python_37.zip"),
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_7,
                _lambda.Runtime.PYTHON_3_8
            ],
            license=f"Mystique Lambda Layer of Boto3, Refer to AWS for license.",
            description="Layer to for latest version of Boto3"
        )

        # Create Requests Layer
        requests_layer = _lambda.LayerVersion(
            self,
            "requestsLayer",
            code=_lambda.Code.from_asset(
                "stacks/back_end/s3_object_lambda_stack/lambda_src/layer_code/requests_python_37.zip"),
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_7,
                _lambda.Runtime.PYTHON_3_8
            ],
            description="Python requests Layer to make HTTP calls"
        )

        # Read Lambda Code
        try:
            with open("stacks/back_end/s3_object_lambda_stack/lambda_src/s3_object_lambda.py",
                      encoding="utf-8",
                      mode="r"
                      ) as f:
                s3_object_lambda_fn_code = f.read()
        except OSError:
            print("Unable to read Lambda Function Code")
            raise
        s3_object_lambda_fn = _lambda.Function(
            self,
            "s3ObjectLambda",
            function_name=f"miztiik_data_shield_fn",
            description="Process S3 requests in flight using lambda",
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.InlineCode(
                s3_object_lambda_fn_code),
            handler="index.lambda_handler",
            timeout=cdk.Duration.seconds(5),
            reserved_concurrent_executions=1,
            environment={
                "LOG_LEVEL": f"{stack_log_level}",
                "APP_ENV": "Production",
                "TRIGGER_RANDOM_DELAY": "True",
                "LD_LIBRARY_PATH": "/opt/python"
            },
            layers=[boto3_layer, requests_layer],
        )

        s3_object_lambda_fn_version = s3_object_lambda_fn.latest_version
        s3_object_lambda_fn_version_alias = _lambda.Alias(
            self,
            "s3ObjectLambdaFnAlias",
            alias_name="MystiqueAutomation",
            version=s3_object_lambda_fn_version
        )

        # Create Custom Loggroup for Producer
        s3_object_lambda_fn_lg = _logs.LogGroup(
            self,
            "s3ObjectLambdaFnLogGroup",
            log_group_name=f"/aws/lambda/{s3_object_lambda_fn.function_name}",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            retention=_logs.RetentionDays.ONE_DAY
        )

        # Allow permissions to trigger Object Lambda
        roleStmt1 = _iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=["*"],
            actions=["s3-object-lambda:WriteGetObjectResponse"]
        )
        roleStmt1.sid = "AllowObjectLambdaS3Access"
        s3_object_lambda_fn.add_to_role_policy(roleStmt1)

        # Restrict Produce Lambda to be invoked only from the stack owner account
        s3_object_lambda_fn.add_permission(
            "restrictLambdaInvocationToOwnAccount",
            principal=_iam.AccountRootPrincipal(),
            action="lambda:InvokeFunction",
            source_account=cdk.Aws.ACCOUNT_ID,
            # source_arn=sales_q.queue_arn
        )

        s3_obj_lambda_ap_attr_arn = _s3objlambda.CfnAccessPoint(
            self,
            "s3ObjectLambdaApConfig",
            name="miztiik-data-shield",
            object_lambda_configuration=_s3objlambda.CfnAccessPoint.ObjectLambdaConfigurationProperty(
                supporting_access_point=f"arn:aws:s3:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:accesspoint/{sales_lambda_ap_name}",
                transformation_configurations=[_s3objlambda.CfnAccessPoint.TransformationConfigurationProperty(
                    actions=["GetObject"],
                    content_transformation={
                        "AwsLambda": {
                            # "FunctionPayload": "{\"compressionType\":\"gzip\"}",
                            "FunctionArn": f"{s3_object_lambda_fn.function_arn}"
                        }
                    }
                )]
            )
        )

        self.s3_object_lambda_fn_role = s3_object_lambda_fn.role

        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_0 = cdk.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page."
        )

        output_1 = cdk.CfnOutput(
            self,
            "S3ObjectLambda",
            value=f"https://console.aws.amazon.com/lambda/home?region={cdk.Aws.REGION}#/functions/{s3_object_lambda_fn.function_name}",
            description="Process S3 requests in flight using lambda"
        )

        output_2 = cdk.CfnOutput(
            self,
            "S3ObjectLambdaArn",
            value=f"{s3_obj_lambda_ap_attr_arn.attr_arn}",
            description=f"The S3 Object Lambda access point bucket ARN"
        )
