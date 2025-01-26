#!/usr/bin/env python3
import os

import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import CfnCreationPolicy, CfnResourceSignal, Duration

class MonolitikStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC
        vpc = ec2.Vpc(self, "MonolitikVPC",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/26"),
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=28
                )
            ],
        )
        cdk.Tags.of(vpc).add("Name", "MonolitikVPC")

        ec2publicsg = ec2.SecurityGroup(self, "MonolitikSG",
                                        vpc=vpc,
                                        security_group_name="MonolitikSG-Public",
                                        description="Public EC2 Security Group.",
                                        )

        # Allow HTTP from anywhere
        ec2publicsg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP access from internet."
        )

        ec2publicsg.add_ingress_rule(
            peer=ec2publicsg,
            connection=ec2.Port.all_traffic(),
            description="Allow all traffic within the security group."
        )
        cdk.Tags.of(ec2publicsg).add("Name", "MonolitikSG")

        monolitik_bucket = s3.Bucket(self, "MonolitikBucket-Herley",
                                     removal_policy=cdk.RemovalPolicy.DESTROY)

        # Create IAM role for EC2 instance
        role = iam.Role(self, "EC2SSMRole",
                        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
                        )

        # Add SSM managed policy to the role
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        monolitik_bucket.grant_read_write(role)

        # Define user data with cfn-signal
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "#!/bin/bash",
            "yum update -y",
            "yum install -y aws-cfn-bootstrap awscli python3 python3-pip",
            "pip3 install streamlit",
            "echo 'alias python=python3' >> /etc/profile.d/python3.sh",
            "source /etc/profile.d/python3.sh",
            "# Signal the status from cfn-init",
            "/opt/aws/bin/cfn-signal -e $? --stack ${AWS::StackName} --resource MonolitikEC2Instance --region ${AWS::Region}"
        )

        ec2_instance = ec2.Instance(
            self,
            "MonolitikEC2Instance",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=ec2publicsg,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            role=role,
            user_data=user_data,
        )

        # Add CreationPolicy to wait for cfn-signal
        timeout_string = Duration.minutes(2).to_string()
        cfn_instance = ec2_instance.node.default_child
        cfn_instance.cfn_options.creation_policy = CfnCreationPolicy(
            resource_signal=CfnResourceSignal(
                count=1,
                timeout=timeout_string
            )
        )

app = cdk.App()
MonolitikStack(app, "MonolitikStack", env={'region': 'ap-southeast-3'})
app.synth()