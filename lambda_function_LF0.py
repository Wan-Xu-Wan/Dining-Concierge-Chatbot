import boto3
import json

client = boto3.client('lex-runtime',region_name='us-east-1', aws_access_key_id='*',aws_secret_access_key='*')


def lambda_handler(event, context):
    last_user_message = event['messages'][0]['unstructured']['text'];
    print(last_user_message)
    botMessage = "Please try again.";
    # user = event['identityID']
    if last_user_message is None or len(last_user_message) < 1:
        return {
            'statusCode': 200,
            'headers': {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },

            'body': json.dumps(botMessage)
        }

    response = client.post_text(botName='cuisineBot',
                                botAlias='version_One',
                                userId='test',
                                inputText=last_user_message)
    if response['message'] is not None or len(response['message']) > 0:
        res_message = response['message']
        print(res_message)
    return {
        'statusCode': 200,
        'body': json.dumps(res_message)
    }
