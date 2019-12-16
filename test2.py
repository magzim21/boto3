import boto3
import pip
from botocore.exceptions import ClientError

# Installing boto3
# def install(package):
#     if hasattr(pip, 'main'):
#         pip.main(['install', package])
#     else:
#         pip._internal.main(['install', package])
#
# if __name__ == '__main__':
#     install('boto3')

# Creating/finding key pair file
client = boto3.client('ec2')
try:
    outfile = open('ec2-keypair.pem', 'w')
    key_pair = client.create_key_pair(KeyName='maxim_o')
    # key_pair = str(key_pair)
    print(key_pair)
    outfile.write(key_pair)

except Exception as e:
    print(e)

# Creating magnetic volume
response_vol = client.create_volume(
    AvailabilityZone='eu-west-1a',
    Size=1,
    VolumeType='standard',
)
# print(response_vol)
client.create_tags(
                Resources=[response_vol['VolumeId']],
                Tags=[{
                    "Key":"Name",
                    "Value":"maxim_o"
                }]
            )
# response_vol.add_tag("Name","maxim_o")

# Creating security group  (no duplicates)
response_vpcs = client.describe_vpcs()
vpc_id = response_vpcs.get('Vpcs', [{}])[0].get('VpcId', '')

try:
    response_sg = client.create_security_group(GroupName='maxim_o',
                                         Description='DESCRIPTION')
                                             # VpcId=vpc_id)
    security_group_id = response_sg['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    data = client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 80,
             'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print('Ingress Successfully Set %s' % data)
except ClientError as e:
    print(e)

ec2 = boto3.resource('ec2')
instances = ec2.create_instances(
	ImageId='ami-07a3c7461cc82f8ff',
	MinCount=1,
	MaxCount=1,
	KeyName='maxim_o',
	InstanceType="t2.micro",
    SecurityGroups=[
        'maxim_o',
    ],
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'maxim_o'
                },
            ]
        },
    ],
    Placement={
        'AvailabilityZone': 'eu-west-1a',
        # 'Affinity': 'string',
        # 'GroupName': 'string',
        # 'PartitionNumber': 123,
        # 'HostId': 'string',
        # 'Tenancy': 'default'|'dedicated'|'host',
        # 'SpreadDomain': 'string',
        # 'HostResourceGroupArn': 'string'
    },
)

response_att_vol = client.attach_volume(
    Device='xvdh',
    InstanceId=instances[0].instance_id,
    VolumeId=response_vol['Attachments']['VolumeId'],
    # DryRun=True|False
)