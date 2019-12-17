import boto3
import pip
import time
from botocore.exceptions import ClientError

MY_TAG = 'maxim_o'

def main():
    client = boto3.client('ec2')

    # Generating access key pair  if not exists
    try:
        key_pair = client.create_key_pair(KeyName = MY_TAG)
        print(key_pair)

    except Exception as e:
        print(e)
    else:
        # Writing new in key-pair in a file
        outfile = open(MY_TAG + '.pem', 'w')
        outfile.write(key_pair['KeyMaterial'])
        outfile.close()

    # PREPARING MAGNETIC VOLUME
    ec2 = boto3.resource('ec2')
    volume_exists = False

    volume_iterator = ec2.volumes.all()
    # Trying to find available volumes
    for v in volume_iterator:
        try:
            if not v.attachments and v.volume_type == 'standard':
                for tag in v.tags:
                    if tag['Value'] == MY_TAG:
                        print("My volume available to attach: {0} {1} {2}".format(v.id, v.state, v.tags))
                        volume_exists = True
                        volume_id = v.id
        except:
            # Not every instance has tags. This causes key errors.
            continue

    # Creating magnetic volume
    if not volume_exists:
        response_vol = client.create_volume(
            AvailabilityZone='eu-west-1a',
            Size=1,
            VolumeType='standard',
        )
        client.create_tags(
                        Resources=[response_vol['VolumeId']],
                        Tags=[{
                            "Key":"Name",
                            "Value": MY_TAG
                        }]
                    )
        volume_id = response_vol['VolumeId']


    # CREATING SECURITY A GROUP

    try:
        response_sg = client.create_security_group(GroupName = MY_TAG,
                                             Description='SSH and HTTP')
        security_group_id = response_sg['GroupId']
        print('Security Group Created %s' % (security_group_id))

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

    # CREATING INSTANCES
    instances = ec2.create_instances(
        ImageId='ami-02df9ea15c1778c9c',
        MinCount=1,
        MaxCount=1,
        KeyName=MY_TAG,
        InstanceType="t2.micro",
        SecurityGroups=[
            MY_TAG ,
        ],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': MY_TAG
                    },
                ]
            },
        ],
        Placement={
            'AvailabilityZone': 'eu-west-1a',
        },
        UserData = open('./userData.sh').read(),
    )

    # Waiting for the instance to run before attaching
    print("Volume  {0} will be attached to {1}. Waiting 40 seconds to let instance run...".format(volume_id, instances[0].instance_id))
    time.sleep(40)
    # ATTACHING VOLUME TO the INSTANCE
    response_att_vol = client.attach_volume(
        Device='xvdh',
        InstanceId=instances[0].instance_id,
        VolumeId=volume_id,
    )

# Checking if my instance already exists (Idempotent script)
instance_exists = False
ec2 = boto3.resource('ec2')
for instance in ec2.instances.all():
    if instance.tags and instance.state['Name'] == 'running':
        for tag in instance.tags:
            if tag['Value'] == MY_TAG:
                # My instance found
                instance_exists = True
                print('Instance with name \033[33m{}\033[00m already exists.'.format(MY_TAG))
                exit(0)
if not instance_exists:
    main()