import boto3
import datetime

def aws_creds_verifier(role, external_id, user_id):
    client = boto3.client('sts')
    try:
        result = client.assume_role(
                RoleArn=role,
                RoleSessionName='RoleSession-'+str(user_id)+'-'+str(datetime.datetime.now().strftime("%s")),
                ExternalId=external_id
        )
        client = boto3.client(
            'ec2',
            aws_access_key_id=result['Credentials']['AccessKeyId'],
            aws_secret_access_key=result['Credentials']['SecretAccessKey'],
            aws_session_token=result['Credentials']['SessionToken'],
            region_name='us-east-1',
        )
        result = client.describe_regions()
        status_code = result['ResponseMetadata']['HTTPStatusCode']
        return {'code': status_code, 'msg': ''}
    except Exception as e:
        if 'response' in e and e.response['Error']['Code'] == 'AuthFailure':
            return {'code': 404, 'msg': str(e.response['Error']['Code'])}
        else:
            return {'code': 404, 'msg': str(e)}
