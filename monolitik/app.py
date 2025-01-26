#!/usr/bin/env python3
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3

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
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(8501),
            description="Allow HTTP access for Streamlit."
        )

        ec2publicsg.add_ingress_rule(
            peer=ec2publicsg,
            connection=ec2.Port.all_traffic(),
            description="Allow all traffic within the security group."
        )
        cdk.Tags.of(ec2publicsg).add("Name", "MonolitikSG")

        monolitik_bucket = s3.Bucket(self, "monolitik-sistem",
                                     removal_policy=cdk.RemovalPolicy.DESTROY, auto_delete_objects=True)

        # Create IAM role for EC2 instance
        role = iam.Role(self, "EC2SSMRole",
                        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
                        )

        # Add SSM managed policy to the role
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        monolitik_bucket.grant_read_write(role)

        # User data script
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "#!/bin/bash",
            "yum install -y python3-pip",
            "pip3 freeze > requirements.txt",
            "pip3 install -r requirements.txt",
            "su ec2-user",
            "pip3 install streamlit==1.36.0 --ignore-installed",
            "cat << EOT > /home/main.py",
            "import streamlit as st",
            "",
            "def main():",
            "    st.title(\"Order Form\")",
            "",
            "    default_payload = {",
            "        \"jenis_pesanan\": \"makanan\",",
            "        \"id_pengguna\": 789,",
            "        \"nama_pemesan\": \"Herley\",",
            "        \"daftar_pesanan\": [",
            "            {",
            "                \"id_menu\": 101,",
            "                \"nama_menu\": \"Nasi Goreng Spesial\",",
            "                \"jumlah\": 2",
            "            },",
            "            {",
            "                \"id_menu\": 105,",
            "                \"nama_menu\": \"Es Teh Manis\",",
            "                \"jumlah\": 1",
            "            }",
            "        ],",
            "        \"metode_pembayaran\": \"tunai\"",
            "    }",
            "",
            "    jenis_pesanan = st.text_input(\"Jenis Pesanan\", default_payload[\"jenis_pesanan\"])",
            "    id_pengguna = st.number_input(\"ID Pengguna\", value=int(default_payload[\"id_pengguna\"]), step=1)",
            "    nama_pemesan = st.text_input(\"Nama Pemesan\", default_payload[\"nama_pemesan\"])",
            "    metode_pembayaran = st.text_input(\"Metode Pembayaran\", default_payload[\"metode_pembayaran\"])",
            "",
            "    st.subheader(\"Daftar Pesanan\")",
            "    daftar_pesanan = []",
            "    num_items = st.number_input(\"Jumlah Item Pesanan\", min_value=1, value=len(default_payload[\"daftar_pesanan\"]), step=1)",
            "",
            "    for i in range(num_items):",
            "        st.write(f\"**Item {i+1}**\")",
            "        if i < len(default_payload[\"daftar_pesanan\"]):",
            "            default_item = default_payload[\"daftar_pesanan\"][i]",
            "        else:",
            "            default_item = {\"id_menu\": \"\", \"nama_menu\": \"\", \"jumlah\": 1}",
            "",
            "        id_menu = st.number_input(f\"ID Menu {i + 1}\",",
            "                                  value=int(default_item[\"id_menu\"]) if default_item[\"id_menu\"] else 0, step=1,",
            "                                  key=f\"id_menu_{i}\")",
            "",
            "        nama_menu = st.text_input(f\"Nama Menu {i+1}\", value=default_item[\"nama_menu\"], key=f\"nama_menu_{i}\")",
            "        jumlah = st.number_input(f\"Jumlah {i+1}\", min_value=1, value=default_item[\"jumlah\"], step=1, key=f\"jumlah_{i}\")",
            "",
            "        daftar_pesanan.append({",
            "            \"id_menu\": int(id_menu) if id_menu else None,",
            "            \"nama_menu\": nama_menu,",
            "            \"jumlah\": int(jumlah)",
            "        })",
            "",
            "    if st.button(\"Submit Request\"):",
            "        payload = {",
            "            \"jenis_pesanan\": jenis_pesanan,",
            "            \"id_pengguna\": int(id_pengguna),",
            "            \"nama_pemesan\": nama_pemesan,",
            "            \"daftar_pesanan\": daftar_pesanan,",
            "            \"metode_pembayaran\": metode_pembayaran",
            "        }",
            "        st.write(\"Order Submitted!\")",
            "        st.write(\"Payload:\")",
            "        st.json(payload)",
            "",
            "if __name__ == \"__main__\":",
            "    main()",
            "EOT",
            "streamlit run /home/main.py"
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
            user_data_causes_replacement=True,
        )

app = cdk.App()
MonolitikStack(app, "MonolitikStack", env={'region': 'ap-southeast-3'})
app.synth()