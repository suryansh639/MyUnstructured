import json
import boto3
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
cognito = boto3.client('cognito-idp')

USERS_TABLE = os.environ['USERS_TABLE']
USER_POOL_CLIENT_ID = os.environ['USER_POOL_CLIENT_ID']

users_table = dynamodb.Table(USERS_TABLE)

def handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')
        name = body.get('name', '')
        
        if not email or not password:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Email and password required'})}
        
        # Create user in Cognito
        try:
            response = cognito.sign_up(
                ClientId=USER_POOL_CLIENT_ID,
                Username=email,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'name', 'Value': name}
                ]
            )
            user_id = response['UserSub']
        except cognito.exceptions.UsernameExistsException:
            return {'statusCode': 409, 'body': json.dumps({'error': 'User already exists'})}
        
        # Create user in DynamoDB with initial credits
        users_table.put_item(Item={
            'user_id': user_id,
            'email': email,
            'name': name,
            'credits': 5,
            'plan': 'free',
            'created_at': datetime.utcnow().isoformat(),
            'api_key': str(uuid.uuid4())
        })
        
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'message': 'User registered successfully',
                'user_id': user_id,
                'email': email,
                'credits': 5
            })
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
