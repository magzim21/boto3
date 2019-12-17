# Boto3 practice

### Prerequisites
```sh
$ pip install boto3
$ pip3 install awscli
$ aws configure --profile maxim_o
AWS Access Key ID [None]: <Access Key ID>
AWS Secret Access Key [None]: <Secret Access Key>
Default region name [None]: eu-west-1
Default output format [None]: json
```
### Run script
```
$ AWS_PROFILE=maxim_o python simple_script.py
```
### My comments
For full **idempotency** I could experiment with "**os**" module for istalling **prerequisites** and work around with **ssm** sessions, but I was out of time. Thank you for feedback!
Access keys were attached to an email. 

#### Task objectives
Write idempotent python3 script
- Create EC2 instance in existing VPC.
- Create security group which allows only 22 and 80 inbound ports and attach it to the instance.
- Create new EBS volume with "magnetic" type, 1GB size and attach it to the instance.
- Connect to the instance via ssh, format and mount additional volume.

#### Output: 
Script file(s) in the provided private AWS codecommit repository and a name or a link of the repository.
#### Important:
It’s necessary to tag any created AWS resources with name/surname while working on the test task, otherwise they will be terminated.
Do NOT expose provided AWS access/secret keys in the public, otherwise the test task will be considered as failed.

