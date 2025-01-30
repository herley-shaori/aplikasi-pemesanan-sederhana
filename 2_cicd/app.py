#!/usr/bin/env python3
import json
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import Tags

from codecommit_config import create_codecommit_repo
from ec2_config import create_vpc, create_security_group, create_ec2_instance
from iam_config import create_ec2_role
from codepipeline_config import create_codepipeline

# Read the environment.json file
with open('environment.json', 'r') as f:
    env_config = json.load(f)

class CICDStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create CodeCommit repository
        repo = create_codecommit_repo(self, f"{env_config['resource_name']}")

        # Create VPC
        vpc = create_vpc(self, f"{env_config['resource_name']}", env_config)

        # Create Security Group
        ec2publicsg = create_security_group(self, f"{env_config['resource_name']}", vpc, env_config)
        Tags.of(ec2publicsg).add("Name", f"{env_config['resource_name']}")

        # Create IAM role for EC2 instance
        role = create_ec2_role(self, f"{env_config['resource_name']}")

        # Create EC2 instance
        ec2_instance = create_ec2_instance(self, "EC2Instance", vpc, ec2publicsg, role)

        # Create CodePipeline with Deploy Stage
        create_codepipeline(self, f"{env_config['resource_name']}-Pipeline", repo, ec2_instance)

app = cdk.App()
CICDStack(app, f"{env_config['resource_name']}", env={'region': 'ap-southeast-3'})
app.synth()