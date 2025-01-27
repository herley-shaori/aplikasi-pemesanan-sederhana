#!/usr/bin/env python3
import os

import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
    aws_codecommit as codecommit,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    aws_lambda as lambda_,
    aws_iam as iam,
    RemovalPolicy
)


class CICDStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket
        bucket = s3.Bucket(self, "SourceBucket",
                           versioned=True,
                           encryption=s3.BucketEncryption.S3_MANAGED,
                           bucket_name="codecommitsource-herley",
                           removal_policy=RemovalPolicy.DESTROY,  # For easy cleanup during testing
                           auto_delete_objects=True  # For easy cleanup during testing
                           )

        # Create CodeCommit repository
        repo = codecommit.Repository(self, "CodeCommitRepo",
                                     repository_name="simple-ordering-app",
                                     description="CodeCommit repository created with CDK."
                                     )

        # Create Lambda function to handle S3 events
        handler = lambda_.Function(self, "S3EventHandler",
                                   runtime=lambda_.Runtime.PYTHON_3_8,
                                   handler="index.handler",
                                   code=lambda_.Code.from_asset("lambda"),
                                   environment={
                                       "REPO_NAME": repo.repository_name,
                                       "BUCKET_NAME": bucket.bucket_name
                                   }
                                   )

        # Grant Lambda function permissions to access CodeCommit
        handler.add_to_role_policy(iam.PolicyStatement(
            actions=["codecommit:CreateCommit", "codecommit:GetBranch", "codecommit:PutFile"],
            resources=[repo.repository_arn]
        ))

        # Grant Lambda function permissions to read from S3
        bucket.grant_read(handler)

        # Create notification configuration
        notification = s3n.LambdaDestination(handler)

        # Add S3 event notification for object creation
        bucket.add_object_created_notification(
            notification,
            s3.NotificationKeyFilter(prefix="codecommit/")
        )

        # Grant S3 permission to invoke Lambda
        handler.add_permission(
            "AllowS3Invoke",
            principal=iam.ServicePrincipal("s3.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_account=self.account,
            source_arn=bucket.bucket_arn
        )


app = cdk.App()
CICDStack(app, "CICDStack", env={'region': 'ap-southeast-3'})
app.synth()
