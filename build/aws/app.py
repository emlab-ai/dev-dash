#!/usr/bin/env python3
import os

import aws_cdk as cdk

from constructs import Construct
from aws_cdk import (
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
    aws_elasticloadbalancingv2 as elbv2,
    aws_elasticloadbalancingv2_targets as targets,
    Aws, Stack, Duration, CfnOutput
)

aws_region = "eu-west-2"
account_id = '834803522181'

class EmlabCdkStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)            
        
        repository = ecr.Repository.from_repository_arn(
            self,
            id,
            repository_arn="arn:aws:ecr:eu-west-2:834803522181:repository/emlab")
                        
        
        vpc = ec2.Vpc(self, 
                        "EmlabVpc",
                        max_azs=2,
                        cidr="10.0.0.0/16",
                        gateway_endpoints={
                        "S3": ec2.GatewayVpcEndpointOptions(
                            service=ec2.GatewayVpcEndpointAwsService.S3
                        )},
                        subnet_configuration=[
                            ec2.SubnetConfiguration(
                                name="public", cidr_mask=24,
                                reserved=False, subnet_type=ec2.SubnetType.PUBLIC),
                            ec2.SubnetConfiguration(
                                name="private", cidr_mask=24,
                                reserved=False, subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
                            ec2.SubnetConfiguration(
                                name="DB", cidr_mask=24,
                                reserved=False, subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                            ),
                        ],
                        enable_dns_hostnames=True,
                        enable_dns_support=True,
                        nat_gateways=1
                      )
        
        # VPC Interface Endpoints
        ec2.InterfaceVpcEndpoint(self, "VPC Endpoint Docker",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointService(f"com.amazonaws.{aws_region}.ecr.dkr"),
        )

        ec2.InterfaceVpcEndpoint(self, "VPC Endpoint ECR API",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointService(f"com.amazonaws.{aws_region}.ecr.api"),
        )
        
        my_security_group = ec2.SecurityGroup(self, "PublicSecurityGroup",
            vpc=vpc,
            description="Allow all traffic",
            allow_all_outbound=True
        )
        my_security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(5432), "Allow all traffic")
        
        # Define an ECS cluster
        cluster = ecs.Cluster(self, "EmlabCluster", vpc=vpc )
        
        # Domain configuration
        domain_name = "emlab.ai"

        # Request a certificate
        certificate = acm.Certificate(self, "SiteCertificate",
            domain_name=domain_name,
            validation=acm.CertificateValidation.from_dns()  # Automatically validate the certificate using DNS
        )
        
        # Create a PostgreSQL RDS database
        db = rds.DatabaseInstance(
            self, "EmlabDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_16),
            credentials=rds.Credentials.from_generated_secret(username="emlabserver"),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO),
            vpc=vpc,
            allocated_storage=20,
            database_name="EmlabDatabase",
            delete_automated_backups=True,
            deletion_protection=False,
            backup_retention=Duration.days(0),
            security_groups=[],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )
        
        db.connections.allow_from_any_ipv4(ec2.Port.tcp(5432))
        
        # Define the task definition
        task_definition = ecs.FargateTaskDefinition(self, "TaskDef")

        # Add a container to the task definition
        
        container = task_definition.add_container(
            "EmlabContainer",
            image=ecs.ContainerImage.from_ecr_repository(repository, tag="latest"),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="EmlabContainer"),
            secrets={
                "DB_PASSWORD": ecs.Secret.from_secrets_manager(db.secret, field="password")
            },
            environment={
                "DB_USERNAME": "emlabserver",
                "DB_HOSTNAME": db.db_instance_endpoint_address,
                "DB_NAME": "EmlabDatabase"
            }
        )
        
        container.add_port_mappings(ecs.PortMapping(container_port=8080))
        
        # Define an ECS Fargate Service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "EmlabService",
            cluster=cluster,
            cpu=256,
            desired_count=1,
            task_definition=task_definition,
            memory_limit_mib=512,        
            public_load_balancer=False
        )
        
        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(443),
            description="Allow https inbound from VPC"
        )
        
        target_group = elbv2.ApplicationTargetGroup(
            self, "ALBTargetGroup",
            port=8080,
            vpc=vpc,
            targets=[fargate_service.service.load_balancer_target(container_name=container.container_name, container_port=container.container_port)],
        )
        
        # Create a listener for port 443
        listener_443 = fargate_service.load_balancer.add_listener(
            "Listener443",
            port=443,
            protocol=elbv2.ApplicationProtocol.HTTPS,
            certificates=[certificate],
            default_action=elbv2.ListenerAction.forward([target_group]),
        )
        
        # NLB setup
        nlb = elbv2.NetworkLoadBalancer(
            self, "EmlabNLB",
            vpc=vpc,
            internet_facing=True,
            cross_zone_enabled=True,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )
        
        nlb_http_target_group = elbv2.NetworkTargetGroup(
            self, f"BackendNLBTargetGroup-http",
            port=80,
            vpc=vpc,
            targets=[targets.AlbTarget(fargate_service.load_balancer, 80)]
        )
        
        nlb_https_target_group = elbv2.NetworkTargetGroup(
            self, f"BackendNLBTargetGroup-https",
            port=443,
            vpc=vpc,
            targets=[targets.AlbTarget(fargate_service.load_balancer, 443)]
        )
        
      
        listener_http = nlb.add_listener("ListenerHTTP", port=80)
        listener_http.add_target_groups("TGHTTP", nlb_http_target_group)

        listener_https = nlb.add_listener("ListenerHTTPS", port=443)
        listener_https.add_target_groups("TGHTTPS", nlb_https_target_group)
        
        # AutoScaling policy
        scaling = fargate_service.service.auto_scale_task_count(
            max_capacity=2
        )
        
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )
        
        github_import_stream = kinesis.Stream(self, "github_import", stream_name="github_import")
        github_events_stream = kinesis.Stream(self, "github_events", stream_name="github_events")
        
        # Define the Lambda function
        process_github_import_lambda_function = _lambda.Function(
            self, "process_github_import_events",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="process_github_import",
            code=_lambda.Code.from_asset("../../server/src"),
            environment={
                "DB_PASSWORD": str(ecs.Secret.from_secrets_manager(db.secret, field="password")),
                "STREAM_NAME": github_import_stream.stream_name,
                "DB_USERNAME": "emlabserver",
                "DB_HOSTNAME": db.db_instance_endpoint_address,
                "DB_NAME": "EmlabDatabase"
            }
        )
        
        # Grant the Lambda function permissions to read the secret
        db.secret.grant_read(process_github_import_lambda_function.role)
        
        # Ensure Lambda has permissions to write to the stream
        github_import_stream.grant_read(process_github_import_lambda_function)

        CfnOutput(
            self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name
        )
        

app = cdk.App()
EmlabCdkStack(app, "EmlabCdkStack",
    env=cdk.Environment(account=account_id, region=aws_region),
)

app.synth()
