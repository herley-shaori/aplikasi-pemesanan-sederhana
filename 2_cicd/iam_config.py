from aws_cdk import aws_iam as iam

def create_ec2_role(scope, id):
    role = iam.Role(scope, "EC2SSMRole",
        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
    )
    role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
    return role
