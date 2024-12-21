#!/usr/bin/env python3
import os

import aws_cdk as cdk

from constructs import Construct
from aws_cdk import (
    aws_iam as iam,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs_patterns as ecs_patterns,
    aws_certificatemanager as acm,
    aws_route53_targets as targets,
    aws_ecr_assets as ecr_assets,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as targets,
    aws_dynamodb as dynamodb,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
    Stack,
    Duration,
    CfnOutput,
    aws_dynamodb as ddb,
)

aws_region = "eu-west-2"
account_id = "834803522181"


class EmlabCdkStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ecr.Repository.from_repository_arn(
            self,
            id,
            repository_arn="arn:aws:ecr:eu-west-2:834803522181:repository/emlab",
        )

        vpc = ec2.Vpc(
            self,
            "EmlabVpc",
            max_azs=2,
            cidr="10.0.0.0/16",
            gateway_endpoints={
                "S3": ec2.GatewayVpcEndpointOptions(
                    service=ec2.GatewayVpcEndpointAwsService.S3
                )
            },
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    cidr_mask=24,
                    reserved=False,
                    subnet_type=ec2.SubnetType.PUBLIC,
                ),
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True,
            nat_gateways=1,
        )

        vpc.add_interface_endpoint(
            "ECR",
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
        )
        vpc.add_interface_endpoint(
            "ECRDocker",
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
        )
        vpc.add_interface_endpoint(
            "CloudWatchLogsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
        )
        vpc.add_interface_endpoint(
            "KMS",
            service=ec2.InterfaceVpcEndpointAwsService.KMS,
        )

        # # VPC Interface Endpoints
        # ec2.InterfaceVpcEndpoint(
        #     self,
        #     "VPC Endpoint Docker",
        #     vpc=vpc,
        #     service=ec2.InterfaceVpcEndpointService(
        #         f"com.amazonaws.{aws_region}.ecr.dkr"
        #     ),
        # )

        # ec2.InterfaceVpcEndpoint(
        #     self,
        #     "VPC Endpoint ECR API",
        #     vpc=vpc,
        #     service=ec2.InterfaceVpcEndpointService(
        #         f"com.amazonaws.{aws_region}.ecr.api"
        #     ),
        # )

        my_security_group = ec2.SecurityGroup(
            self,
            "PublicSecurityGroup",
            vpc=vpc,
            description="Allow all traffic",
            allow_all_outbound=True,
        )
        my_security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(5432), "Allow all traffic"
        )

        # Define an ECS cluster
        cluster = ecs.Cluster(self, "EmlabCluster", vpc=vpc)

        # Domain configuration
        domain_name = "emlab.ai"

        # Request a certificate
        certificate = acm.Certificate(
            self,
            "SiteCertificate",
            domain_name=domain_name,
            validation=acm.CertificateValidation.from_dns(),  # Automatically validate the certificate using DNS
        )

        # Create a security group for the database
        db_security_group = ec2.SecurityGroup(
            self,
            "DbSecurityGroup",
            vpc=vpc,
            description="Allow inbound traffic on port 5432 from the service security group",
            allow_all_outbound=True,
        )

        # Define the task definition
        task_definition = ecs.FargateTaskDefinition(
            self, "WebServer", memory_limit_mib=1024, cpu=512
        )

        # Add a container to the task definition

        web_server_image = ecr_assets.DockerImageAsset(
            self,
            "WebServerImage",
            directory="../src",
            file="./build/web/Dockerfile",
            platform=ecr_assets.Platform.LINUX_AMD64,
        )

        db_secret_arn = "arn:aws:secretsmanager:eu-west-2:834803522181:secret:rds!db-a90903e6-e624-477c-b17e-66e7bd4dce76-b5ZhUM"
        github_secret_arn = "arn:aws:secretsmanager:eu-west-2:834803522181:secret:prod/githubcert-ybijhW"
        gemini_secret_arn = "arn:aws:secretsmanager:eu-west-2:834803522181:secret:prod/gcp_gemini_key-UXAptV"

        db_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "db_secret_arn", db_secret_arn
        )
        github_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "github_secret_arn", github_secret_arn
        )
        gemini_secret = secretsmanager.Secret.from_secret_name_v2(
            self, "gemini_secret_arn", gemini_secret_arn
        )

        container = task_definition.add_container(
            "EmlabContainer",
            image=ecs.ContainerImage.from_docker_image_asset(web_server_image),
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="WebServer",
                log_group=logs.LogGroup(
                    self,
                    "WebServerLogGroup",
                    log_group_name="/aws/ecs/WebServer",
                    retention=logs.RetentionDays.ONE_WEEK,
                    removal_policy=cdk.RemovalPolicy.DESTROY,
                ),
            ),
            environment={
                "DB_SQL_SECRET_ARN": db_secret_arn,
                "AUTH0_DOMAIN": "emlab.uk.auth0.com",
                "AUTH0_CLIENTID": "3Dl2QwlW35gS8oQ6xXiG0nzCyy1g1GAq",
            },
        )

        container.add_port_mappings(ecs.PortMapping(container_port=8080))

        # Application Load Balanced Fargate Service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "EmlabServer",
            cluster=cluster,
            desired_count=1,
            task_definition=task_definition,
            public_load_balancer=True,
            assign_public_ip=True
        )

        fargate_service.target_group.configure_health_check(
            path="/health",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
            healthy_threshold_count=2,
            unhealthy_threshold_count=2,
        )

        # Add HTTPS listener
        fargate_service.load_balancer.add_listener(
            "HttpsListener2",
            port=443,
            certificates=[certificate],
            default_action=elbv2.ListenerAction.forward([fargate_service.target_group]),
        )

        db_security_group.add_ingress_rule(
            peer=fargate_service.service.connections.security_groups[0],
            connection=ec2.Port.tcp(5432),
        )

        db_secret.grant_read(fargate_service.task_definition.task_role)

        # fargate_service.task_definition.task_role.add_to_policy(
        #     iam.PolicyStatement(
        #         actions=["secretsmanager:GetSecretValue"], resources=[db_secret_arn]
        #     )
        # )

        # AutoScaling policy
        scaling = fargate_service.service.auto_scale_task_count(max_capacity=1)

        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )

        # Import the existing DynamoDB table and grant read/write permissions
        emlab_githubevents_table = dynamodb.Table.from_table_name(
            self,
            "ImportedTable",
            table_name="emlab_githubevents",  # Replace with your table name
        )

        emlab_githubevents_table.grant_read_write_data(
            fargate_service.task_definition.task_role
        )
        github_secret.grant_read(fargate_service.task_definition.task_role)
        gemini_secret.grant_read(fargate_service.task_definition.task_role)

        # github_import_stream = kinesis.Stream(
        #     self, "github_import", stream_name="github_import"
        # )
        # github_events_stream = kinesis.Stream(
        #     self, "github_events", stream_name="github_events"
        # )
        # ai_agent_events_stream = kinesis.Stream(
        #     self, "ai_agent_events", stream_name="ai_agent_events"
        # )

        # Define the md64 image asset
        # lamda_image = ecr_assets.DockerImageAsset(
        #     self,
        #     "LambdaImage",
        #     directory="../src",
        #     file="./build/lambda/Dockerfile",
        #     platform=ecr_assets.Platform.LINUX_AMD64,
        # )

        # Create the Lambda function using the Docker image
        # process_github_import_lambda_function = _lambda.DockerImageFunction(
        #     self,
        #     "ImportLambdaFunction",
        #     code=_lambda.DockerImageCode.from_ecr(
        #         repository=lamda_image.repository,
        #         tag=lamda_image.image_tag,
        #         cmd=["lambda_github_import.handler"],
        #     ),
        #     reserved_concurrent_executions=3,
        #     vpc=vpc,
        #     memory_size=512,
        #     vpc_subnets=ec2.SubnetSelection(
        #         subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
        #     ),
        #     timeout=Duration.seconds(600),
        #     environment={"DB_SQL_SECRET_ARN": db_secret_arn},
        # )

        # process_github_events_lambda_function = _lambda.DockerImageFunction(
        #     self,
        #     "EventsLambdaFunction",
        #     code=_lambda.DockerImageCode.from_ecr(
        #         repository=lamda_image.repository,
        #         tag=lamda_image.image_tag,
        #         cmd=["lambda_github_events.handler"],
        #     ),
        #     vpc=vpc,
        #     memory_size=512,
        #     reserved_concurrent_executions=3,
        #     vpc_subnets=ec2.SubnetSelection(
        #         subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
        #     ),
        #     timeout=Duration.seconds(15),
        #     environment={"DB_SQL_SECRET_ARN": db_secret_arn},
        # )

        # process_ai_agent_events_lambda_function = _lambda.DockerImageFunction(
        #     self,
        #     "AiAgentLambdaFunction",
        #     code=_lambda.DockerImageCode.from_ecr(
        #         repository=lamda_image.repository,
        #         tag=lamda_image.image_tag,
        #         cmd=["lambda_ai_agent_events.handler"],
        #     ),
        #     vpc=vpc,
        #     memory_size=512,
        #     reserved_concurrent_executions=3,
        #     vpc_subnets=ec2.SubnetSelection(
        #         subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
        #     ),
        #     timeout=Duration.seconds(15),
        #     environment={"DB_SQL_SECRET_ARN": db_secret_arn},
        # )

        # table.grant_read_write_data(process_github_events_lambda_function)

        # process_github_import_lambda_function.role.add_to_policy(
        #     iam.PolicyStatement(
        #         actions=["secretsmanager:GetSecretValue"], resources=[github_secret_arn]
        #     )
        # )

        # process_ai_agent_events_lambda_function.role.add_to_policy(
        #     iam.PolicyStatement(
        #         actions=["secretsmanager:GetSecretValue"],
        #         resources=[gemini_secret_arn, github_secret_arn],
        #     )
        # )

        # process_github_events_lambda_function.role.add_to_policy(
        #     iam.PolicyStatement(
        #         actions=["secretsmanager:GetSecretValue"], resources=[github_secret_arn]
        #     )
        # )

        # Grant the Lambda function permissions to read the secret
        # db.secret.grant_read(process_github_import_lambda_function.role)
        # process_github_import_lambda_function.role.add_to_policy(
        #     iam.PolicyStatement(
        #         actions=["secretsmanager:GetSecretValue"], resources=[db_secret_arn]
        #     )
        # )
        # github_import_stream.grant_read(process_github_import_lambda_function)
        # Create a Kinesis event source
        # kinesis_import_event_source = lambda_event_source.KinesisEventSource(
        #     github_import_stream,  # the Kinesis stream
        #     starting_position=_lambda.StartingPosition.TRIM_HORIZON,
        # )
        # process_github_import_lambda_function.add_event_source(
        #     kinesis_import_event_source
        # )

        # db.secret.grant_read(process_ai_agent_events_lambda_function.role)
        # process_ai_agent_events_lambda_function.role.add_to_policy(
        #     iam.PolicyStatement(
        #         actions=["secretsmanager:GetSecretValue"], resources=[db_secret_arn]
        #     )
        # )
        # ai_agent_events_stream.grant_read(process_ai_agent_events_lambda_function)
        # Create a Kinesis event source
        # kinesis_ai_agent_event_source = lambda_event_source.KinesisEventSource(
        #     ai_agent_events_stream,  # the Kinesis stream
        #     starting_position=_lambda.StartingPosition.TRIM_HORIZON,
        # )
        # process_ai_agent_events_lambda_function.add_event_source(
        #     kinesis_ai_agent_event_source
        # )

        # Create a Kinesis event source
        # db.secret.grant_read(process_github_events_lambda_function.role)
        # process_github_events_lambda_function.role.add_to_policy(
        #     iam.PolicyStatement(
        #         actions=["secretsmanager:GetSecretValue"], resources=[db_secret_arn]
        #     )
        # )

        # ai_agent_events_stream.grant_write(process_github_events_lambda_function)
        # github_events_stream.grant_read(process_github_events_lambda_function)

        # kinesis_events_event_source = lambda_event_source.KinesisEventSource(
        #     github_events_stream,  # the Kinesis stream
        #     starting_position=_lambda.StartingPosition.TRIM_HORIZON,
        # )
        # process_github_events_lambda_function.add_event_source(
        #     kinesis_events_event_source
        # )

        # dynamodb_usertable = ddb.Table(
        #     self,
        #     "emlab_user_profile",
        #     partition_key=ddb.Attribute(
        #         name="tid",  # name of the column, tenant_id+user_id
        #         type=ddb.AttributeType.STRING,
        #     ),
        #     removal_policy=RemovalPolicy.DESTROY,  # NOT recommended for production
        # )

        CfnOutput(
            self,
            "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name,
        )


app = cdk.App()
EmlabCdkStack(
    app,
    "EmlabCdkStack",
    env=cdk.Environment(account=account_id, region=aws_region),
)

app.synth()
