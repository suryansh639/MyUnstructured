import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
USERS_TABLE = os.environ['USERS_TABLE']
users_table = dynamodb.Table(USERS_TABLE)

def handler(event, context):
    try:
        # Get user from JWT
        claims = event['requestContext']['authorizer']['jwt']['claims']
        user_id = claims['sub']
        
        # Get user data
        response = users_table.get_item(Key={'user_id': user_id})
        
        if 'Item' not in response:
            return {'statusCode': 404, 'body': json.dumps({'error': 'User not found'})}
        
        user = response['Item']
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'user_id': user_id,
                'email': user.get('email'),
                'name': user.get('name'),
                'credits': int(user.get('credits', 0)),
                'plan': user.get('plan', 'free')
            })
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
