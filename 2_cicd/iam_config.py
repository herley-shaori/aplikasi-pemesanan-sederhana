from aws_cdk import aws_iam as iam

def create_ec2_role(scope, id):
    role = iam.Role(scope, "EC2SSMRole",
                    assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                    )

    # Add SSM Managed Instance Core policy
    role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))

    # Add S3 Full Access policy
    role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))

    # Add CodeDeploy permissions
    role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2RoleforAWSCodeDeploy"))

    # Add additional CodeDeploy-specific permissions
    role.add_to_policy(iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=[
            "codedeploy:*",
            "s3:Get*",
            "s3:List*"
        ],
        resources=["*"]
    ))

    return role