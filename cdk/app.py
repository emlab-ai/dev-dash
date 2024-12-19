#!/usr/bin/env python3
import os

import aws_cdk as cdk

from constructs import Construct
from aws_cdk import (
    BundlingOptions,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_apigateway as apigw,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs_patterns as ecs_patterns,
    aws_lambda as _lambda,
    aws_kinesis as kinesis,
    aws_lambda_event_sources as lambda_event_source,
    aws_certificatemanager as acm,
    aws_route53_targets as targets,
    aws_rds as rds,
    aws_s3 as s3,
    aws_s3_assets as s3_assets,
    aws_ecr_assets as ecr_assets,
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as targets,
    aws_dynamodb as dynamodb,
    Aws,
    Stack,
    Duration,
    CfnOutput,
    RemovalPolicy,
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
                ec2.SubnetConfiguration(
                    name="private",
                    cidr_mask=24,
                    reserved=False,
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                ),
                ec2.SubnetConfiguration(
                    name="DB",
                    cidr_mask=24,
                    reserved=False,
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                ),
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True,
            nat_gateways=1,
        )

        # VPC Interface Endpoints
        ec2.InterfaceVpcEndpoint(
            self,
            "VPC Endpoint Docker",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointService(
                f"com.amazonaws.{aws_region}.ecr.dkr"
            ),
        )

        ec2.InterfaceVpcEndpoint(
            self,
            "VPC Endpoint ECR API",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointService(
                f"com.amazonaws.{aws_region}.ecr.api"
            ),
        )

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

        # Create a PostgreSQL RDS database
        # db = rds.DatabaseInstance(
        #     self, "EmlabDatabase",
        #     engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_16),
        #     credentials=rds.Credentials.from_generated_secret(username="emlabserver"),
        #     instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO),
        #     vpc=vpc,
        #     allocated_storage=20,
        #     database_name="EmlabDatabase",
        #     delete_automated_backups=True,
        #     deletion_protection=False,
        #     backup_retention=Duration.days(0),
        #     security_groups=[db_security_group],
        #     vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        # )

        # db.connections.allow_from_any_ipv4(ec2.Port.tcp(5432))

        # Define the task definition
        task_definition = ecs.FargateTaskDefinition(
            self, "TaskDef", memory_limit_mib=1024, cpu=512
        )

        # Add a container to the task definition

        flask_image = ecr_assets.DockerImageAsset(
            self,
            "WebServerImage",
            directory="../src",
            file="./build/web/Dockerfile",
            platform=ecr_assets.Platform.LINUX_AMD64,
        )

        db_secret_arn = "arn:aws:secretsmanager:eu-west-2:834803522181:secret:rds!db-a90903e6-e624-477c-b17e-66e7bd4dce76-b5ZhUM"

        container = task_definition.add_container(
            "EmlabContainer",
            image=ecs.ContainerImage.from_docker_image_asset(flask_image),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="WebServer"),
            environment={
                "DB_SQL_SECRET_ARN": db_secret_arn,
                "AUTH0_DOMAIN": "emlab.uk.auth0.com",
                "AUTH0_CLIENTID": "3Dl2QwlW35gS8oQ6xXiG0nzCyy1g1GAq",
            },
        )

        container.add_port_mappings(ecs.PortMapping(container_port=8080))

        # Define an ECS Fargate Service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "EmlabService",
            cluster=cluster,
            desired_count=1,
            task_definition=task_definition,
            public_load_balancer=False,
        )

        fargate_service.target_group.configure_health_check(
            path="/health",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
            healthy_threshold_count=2,
            unhealthy_threshold_count=2,
        )

        db_security_group.add_ingress_rule(
            peer=fargate_service.service.connections.security_groups[0],
            connection=ec2.Port.tcp(5432),
        )

        # db.secret.grant_read(fargate_service.task_definition.task_role)
        fargate_service.task_definition.task_role.add_to_policy(
            iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"], resources=[db_secret_arn]
            )
        )

        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(443),
            description="Allow https inbound from VPC",
        )

        target_group = elbv2.ApplicationTargetGroup(
            self,
            "ALBTargetGroup",
            port=8080,
            vpc=vpc,
            targets=[
                fargate_service.service.load_balancer_target(
                    container_name=container.container_name,
                    container_port=container.container_port,
                )
            ],
        )

        # Create a listener for port 443
        fargate_service.load_balancer.add_listener(
            "Listener443",
            port=443,
            protocol=elbv2.ApplicationProtocol.HTTPS,
            certificates=[certificate],
            default_action=elbv2.ListenerAction.forward([target_group]),
        )

        # NLB setup
        nlb = elbv2.NetworkLoadBalancer(
            self,
            "EmlabNLB",
            vpc=vpc,
            internet_facing=True,
            cross_zone_enabled=True,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        nlb_http_target_group = elbv2.NetworkTargetGroup(
            self,
            f"BackendNLBTargetGroup-http",
            port=80,
            vpc=vpc,
            targets=[targets.AlbTarget(fargate_service.load_balancer, 80)],
        )

        nlb_https_target_group = elbv2.NetworkTargetGroup(
            self,
            f"BackendNLBTargetGroup-https",
            port=443,
            vpc=vpc,
            targets=[targets.AlbTarget(fargate_service.load_balancer, 443)],
        )

        listener_http = nlb.add_listener("ListenerHTTP", port=80)
        listener_http.add_target_groups("TGHTTP", nlb_http_target_group)

        listener_https = nlb.add_listener("ListenerHTTPS", port=443)
        listener_https.add_target_groups("TGHTTPS", nlb_https_target_group)

        # AutoScaling policy
        scaling = fargate_service.service.auto_scale_task_count(max_capacity=2)

        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )

        github_import_stream = kinesis.Stream(
            self, "github_import", stream_name="github_import"
        )
        github_events_stream = kinesis.Stream(
            self, "github_events", stream_name="github_events"
        )
        ai_agent_events_stream = kinesis.Stream(
            self, "ai_agent_events", stream_name="ai_agent_events"
        )

        # Define the md64 image asset
        lamda_image = ecr_assets.DockerImageAsset(
            self,
            "LambdaImage",
            directory="../src",
            file="./build/lambda/Dockerfile",
            platform=ecr_assets.Platform.LINUX_AMD64,
        )

        # Create the Lambda function using the Docker image
        process_github_import_lambda_function = _lambda.DockerImageFunction(
            self,
            "ImportLambdaFunction",
            code=_lambda.DockerImageCode.from_ecr(
                repository=lamda_image.repository,
                tag=lamda_image.image_tag,
                cmd=["lambda_github_import.handler"],
            ),
            reserved_concurrent_executions=3,
            vpc=vpc,
            memory_size=512,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            timeout=Duration.seconds(600),
            environment={"DB_SQL_SECRET_ARN": db_secret_arn},
        )

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

        process_ai_agent_events_lambda_function = _lambda.DockerImageFunction(
            self,
            "AiAgentLambdaFunction",
            code=_lambda.DockerImageCode.from_ecr(
                repository=lamda_image.repository,
                tag=lamda_image.image_tag,
                cmd=["lambda_ai_agent_events.handler"],
            ),
            vpc=vpc,
            memory_size=512,
            reserved_concurrent_executions=3,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            timeout=Duration.seconds(15),
            environment={"DB_SQL_SECRET_ARN": db_secret_arn},
        )

        # Import the existing DynamoDB table and grant read/write permissions
        table = dynamodb.Table.from_table_name(
            self,
            "ImportedTable",
            table_name="emlab_githubevents"  # Replace with your table name
        )

        # table.grant_read_write_data(process_github_events_lambda_function)
        table.grant_read_write_data(fargate_service.task_definition.task_role)

        github_secret_arn = "arn:aws:secretsmanager:eu-west-2:834803522181:secret:prod/githubcert-ybijhW"
        gemini_secret_arn = "arn:aws:secretsmanager:eu-west-2:834803522181:secret:prod/gcp_gemini_key-UXAptV"
        process_github_import_lambda_function.role.add_to_policy(
            iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"], resources=[github_secret_arn]
            )
        )

        process_ai_agent_events_lambda_function.role.add_to_policy(
            iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"],
                resources=[gemini_secret_arn, github_secret_arn],
            )
        )

        # process_github_events_lambda_function.role.add_to_policy(
        #     iam.PolicyStatement(
        #         actions=["secretsmanager:GetSecretValue"], resources=[github_secret_arn]
        #     )
        # )

        # Grant the Lambda function permissions to read the secret
        # db.secret.grant_read(process_github_import_lambda_function.role)
        process_github_import_lambda_function.role.add_to_policy(
            iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"], resources=[db_secret_arn]
            )
        )
        github_import_stream.grant_read(process_github_import_lambda_function)
        # Create a Kinesis event source
        kinesis_import_event_source = lambda_event_source.KinesisEventSource(
            github_import_stream,  # the Kinesis stream
            starting_position=_lambda.StartingPosition.TRIM_HORIZON,
        )
        process_github_import_lambda_function.add_event_source(
            kinesis_import_event_source
        )

        # db.secret.grant_read(process_ai_agent_events_lambda_function.role)
        process_ai_agent_events_lambda_function.role.add_to_policy(
            iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"], resources=[db_secret_arn]
            )
        )
        ai_agent_events_stream.grant_read(process_ai_agent_events_lambda_function)
        # Create a Kinesis event source
        kinesis_ai_agent_event_source = lambda_event_source.KinesisEventSource(
            ai_agent_events_stream,  # the Kinesis stream
            starting_position=_lambda.StartingPosition.TRIM_HORIZON,
        )
        process_ai_agent_events_lambda_function.add_event_source(
            kinesis_ai_agent_event_source
        )

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
