import csv
import io
import boto3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from botocore.exceptions import NoRegionError
from prettytable import PrettyTable


class AWSResourceChecker:
    def __init__(self):
        self.csv_data = []
        self.csv_data.append(['Resource Type', 'Property checked', 'Status', 'Resource Name'])

    def check_and_save_resources(self):
        region = 'ap-south-1'  # Mumbai region
        print(f"\nChecking resources in region: {region}")
        self.check_and_save_s3_buckets(region)
        self.check_and_save_security_groups(region)
        self.check_and_save_rds_instances(region)
        self.check_cloudtrail_on_ec2_instances(region)
        self.check_api_gateway_resources(region)
        self.check_vpc(region)
        return self.generate_report()

    def check_and_save_rds_instances(self, region):
        rds = boto3.client('rds', region_name=region)
        response = rds.describe_db_instances()
        row_data = []

        for db_instance in response['DBInstances']:
            db_instance_identifier = db_instance['DBInstanceIdentifier']

            if db_instance['ReadReplicaDBInstanceIdentifiers']:
                print(f"Read replicas are enabled for RDS instance: {db_instance_identifier}")
            else:
                row_data.append(db_instance_identifier)

            if db_instance['StorageEncrypted']:
                print(f"Default encryption is enabled for RDS instance: {db_instance_identifier}")
            else:
                row_data.append(db_instance_identifier)

            if 'EnableCloudwatchLogsExports' in db_instance and 'error' not in db_instance['EnableCloudwatchLogsExports']:
                print(f"All logs are enabled for RDS instance: {db_instance_identifier}")
            else:
                row_data.append(db_instance_identifier)

        if len(row_data) == 0:
            self.csv_data.append(['RDS', 'Read replicas default encryption log enablement', '\u2713', '-'])
        else:
            self.csv_data.append(['RDS', 'Read replicas default encryption log enablement', 'X', ', '.join(row_data)])

    def check_vpc(self, region):
        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.describe_vpcs()
        vpc_id = response['Vpcs'][0]['VpcId']  # Assuming only one VPC for simplicity
        row_data = []

        try:
            ec2.describe_vpcs(VpcIds=[vpc_id])
            print(f"VPC with ID {vpc_id} exists.")
        except ec2.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidVpcID.NotFound':
                row_data.append(f"VPC with ID {vpc_id} does not exist.")
            else:
                print(f"Error occurred: {e}")

        response = ec2.describe_internet_gateways(Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}])
        if response['InternetGateways']:
            print("Internet gateway exists in the VPC.")
        else:
            row_data.append("No internet gateway exists in the VPC.")

        response = ec2.describe_nat_gateways(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        if response['NatGateways']:
            print("NAT gateway exists in the VPC.")
        else:
            row_data.append("No NAT gateway exists in the VPC.")

        if len(row_data) == 0:
            self.csv_data.append(['VPC', 'Input VPC existence Internet gateway NAT gateway', '\u2713', '-'])
        else:
            self.csv_data.append(['VPC', 'Input VPC existence Internet gateway NAT gateway', 'X', ', '.join(row_data)])

    def check_api_gateway_resources(self, region):
        apigateway = boto3.client('apigateway', region_name=region)
        apis = apigateway.get_rest_apis()
        row_data = []

        for api in apis['items']:
            api_id = api['id']
            api_name = api['name']

            stages = apigateway.get_stages(restApiId=api_id)
            if stages['item']:
                print(f"API Gateway {api_name} ({api_id}) has deployed stages.")

                resources = apigateway.get_resources(restApiId=api_id)
                for resource in resources['items']:
                    resource_id = resource['id']
                    resource_name = resource['path']

                    methods = apigateway.get_resource_methods(restApiId=api_id, resourceId=resource_id)
                    for method in methods.values():
                        if method.get('apiKeyRequired') or method.get('authorizationType') == 'CUSTOM':
                            print(f"Resource {resource_name} in API Gateway {api_name} ({api_id}) has API key or custom authorization.")
                        else:
                            row_data.append(f"{resource_name} in API Gateway {api_name} ({api_id})")
            else:
                row_data.append(api_name)

        if len(row_data) == 0:
            self.csv_data.append(['API Gateway', 'API Gateway resources with API key or custom authorization', '\u2713', '-'])
        else:
            self.csv_data.append(['API Gateway', 'API Gateway resources with API key or custom authorization', 'X', ', '.join(row_data)])

    def check_and_save_s3_buckets(self, region):
        s3 = boto3.client('s3', region_name=region)
        response = s3.list_buckets()
        row_data = []

        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            bucket_acl = s3.get_bucket_acl(Bucket=bucket_name)
            bucket_encryption = s3.get_bucket_encryption(Bucket=bucket_name)
            public_access_block = self.get_public_access_block(s3, bucket_name)
            if not public_access_block:
                try:
                    website_configuration = s3.get_bucket_website(Bucket=bucket_name)
                    print(f"The S3 bucket {bucket_name} is configured for static website hosting.")
                    # You can add more information about the website configuration if needed
                except s3.exceptions.NoSuchWebsiteConfiguration:
                    print(f"The S3 bucket {bucket_name} is not configured for static website hosting.")
                    row_data.append(bucket_name)

        if len(row_data) == 0:
            self.csv_data.append(['S3', 'S3 public access ', '\u2713', '-'])
        else:
            self.csv_data.append(['S3', 'S3 public access ', 'X', ', '.join(row_data)])

    def check_and_save_security_groups(self, region):
        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.describe_security_groups()
        row_data = []

        for security_group in response['SecurityGroups']:
            group_id = security_group['GroupId']
            group_name = security_group['GroupName']

            instances_attached = self.check_ec2_instances_attached(ec2, group_id)

            if not instances_attached:
                for ingress_rule in security_group.get('IpPermissions', []):
                    for ip_range in ingress_rule.get('IpRanges', []):
                        if ip_range['CidrIp'] == '0.0.0.0/0':
                            rule_description = f"{ingress_rule['IpProtocol']} from {ip_range['CidrIp']}"
                            print(f"Security Group {group_name} ({group_id}) allows {rule_description} in region {region}.")
                            row_data.append(group_name)

        if len(row_data) == 0:
            self.csv_data.append(['Security Group', 'Check for 0.0.0.0 access in security group', '\u2713', '-'])
        else:
            self.csv_data.append(['Security Group', 'Check for 0.0.0.0 access in security group', 'X', ', '.join(row_data)])

    def check_ec2_instances_attached(self, ec2, group_id):
        ec2_instances = ec2.describe_instances(Filters=[{'Name': 'instance.group-id', 'Values': [group_id]}])

        if ec2_instances['Reservations']:
            instance_ids = [instance['InstanceId'] for reservation in ec2_instances['Reservations'] for instance in reservation['Instances']]
            return True
        else:
            return False

    def get_public_access_block(self, s3, bucket_name):
        try:
            response = s3.get_public_access_block(Bucket=bucket_name)
            return response['PublicAccessBlockConfiguration']
        except s3.exceptions.NoSuchPublicAccessBlockConfiguration:
            return None

    def check_cloudtrail_on_ec2_instances(self, region):
        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.describe_instances()
        row_data = []

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                cloudtrail_enabled = any(tag['Key'] == 'cloudtrail' and tag['Value'].lower() == 'enabled' for tag in instance.get('Tags', []))

                if cloudtrail_enabled:
                    print(f"CloudTrail is enabled for EC2 instance {instance_id} in region {region}.")
                else:
                    row_data.append(instance_id)

        if len(row_data) == 0:
            self.csv_data.append(['CloudTrail', 'Check for cloud trial enable ', '\u2713', '-'])
        else:
            self.csv_data.append(['CloudTrail', 'Check for cloud trial enable ', 'X', ', '.join(row_data)])

    def generate_report(self):
        csv_output = io.StringIO()
        csv_writer = csv.writer(csv_output)
        csv_writer.writerows(self.csv_data)
        csv_content = csv_output.getvalue()

        pdf_output = io.BytesIO()
        doc = SimpleDocTemplate(pdf_output, pagesize=letter)
        table = Table(self.csv_data)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), 'grey'),
            ('TEXTCOLOR', (0, 0), (-1, 0), 'white'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), 'white'),
            ('GRID', (0, 0), (-1, -1), 0.5, 'black'),
        ]))

        doc.build([table])
        pdf_content = pdf_output.getvalue()

        return {
            'csv': csv_content,
            'pdf': pdf_content
        }

def lambda_handler():
    awss = AWSResourceChecker()
    report = awss.check_and_save_resources()

    # Create an SES client
    ses = boto3.client('ses', region_name='ap-south-1')

    # Email configurations
    sender_email = 'vishalvinayram5432@gmail.com'
    recipient_email = 'vishalvinayram811@gmail.com'
    subject = 'AWS Resource Report'

    # Create email body with HTML content
    html_body = generate_html_report(report)

    # Send email with HTML body
    ses.send_email(
        Destination={'ToAddresses': [recipient_email]},
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': html_body
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject
            }
        },
        Source=sender_email
    )

    print('Email sent successfully!')

def generate_html_report(report):
    csv_report = format_csv_report(report['csv'])

    html_body = f"""
    <html>
    <head></head>
    <body>
    <h2>AWS Resource Report</h2>
    <h3>CSV Report:</h3>
    {csv_report}
    <h3>PDF Report:</h3>
    </body>
    </html>
    """

    return html_body
def format_csv_report(csv_content):
    # Parse CSV content and format into PrettyTable
    lines = csv_content.strip().split('\n')
    headers = lines[0].split(',')
    rows = [line.split(',', maxsplit=len(headers) - 1) for line in lines[1:]]

    # Create PrettyTable object with headers
    table = PrettyTable()
    table.field_names = headers

    # Add rows to the PrettyTable
    for row in rows:
        table.add_row(row)

    return table.get_html_string()


def format_pdf_report(pdf_content):
    return pdf_content

lambda_handler()