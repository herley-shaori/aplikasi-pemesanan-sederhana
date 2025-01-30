from aws_cdk import aws_ec2 as ec2
from aws_cdk import Tags

def create_vpc(scope, id, env_config):
    return ec2.Vpc(scope, "CICDVPC",
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


def create_security_group(scope, id, vpc, env_config):
    sg = ec2.SecurityGroup(scope, f"{env_config['resource_name']}",
                           vpc=vpc,
                           description="Public EC2 Security Group.",
                           )

    sg.add_ingress_rule(
        peer=ec2.Peer.any_ipv4(),
        connection=ec2.Port.tcp(80),
        description="Allow HTTP access from internet."
    )
    sg.add_ingress_rule(
        peer=ec2.Peer.any_ipv4(),
        connection=ec2.Port.tcp(8501),
        description="Allow HTTP access for Streamlit."
    )
    sg.add_ingress_rule(
        peer=sg,
        connection=ec2.Port.all_traffic(),
        description="Allow all traffic within the security group."
    )
    return sg

def create_ec2_instance(scope, id, vpc, security_group, role):
    # Define user data script to install CodeDeploy agent
    user_data = ec2.UserData.for_linux()
    user_data.add_commands(
        "#!/bin/bash",
        "yum update -y",
        "yum install -y ruby wget",
        "cd /home/ec2-user",
        "wget https://aws-codedeploy-us-east-1.s3.amazonaws.com/latest/install",
        "chmod +x ./install",
        "./install auto",
        "service codedeploy-agent start",
        "yum install -y python3-pip",
        "pip3 freeze > requirements.txt",
        "pip3 install -r requirements.txt",
        "pip3 install streamlit==1.36.0 --ignore-installed"
    )

    instance = ec2.Instance(
        scope,
        id,
        vpc=vpc,
        vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        security_group=security_group,
        instance_type=ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MICRO),
        machine_image=ec2.MachineImage.latest_amazon_linux2023(),
        role=role,
        user_data=user_data  # Add user data to the instance
    )

    # Add tags to the EC2 instance
    Tags.of(instance).add("Project", "CICD")
    return instance