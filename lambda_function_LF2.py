import json
import boto3
import requests
from boto3.dynamodb.conditions import Key, Attr
import urllib3
import os
import logging
from datetime import datetime

host = 'https://search-cc22summer-mbue4ha2ihiytex2ibutckudha.us-east-1.es.amazonaws.com/'
region = 'us-east-1' 
service = 'es'
index = "restaurants"
url = host  + index + '/_search'

def lambda_handler(event, context):
    # TODO implement
    
    # pull message from SQS
    try:
        sqs_client = boto3.client("sqs", region_name=region)
    except Exception as e:
        print(e)
    
    queue_url = 'https://sqs.us-east-1.amazonaws.com/509327864642/restaurants_suggest'
    sqs_response = sqs_client.receive_message(
        QueueUrl = queue_url,
        AttributeNames= ['SentTimestamp'],
        MaxNumberOfMessages = 1,
        MessageAttributeNames = ['ALL'],
        VisibilityTimeout = 0,
        WaitTimeSeconds = 0
        )
    message = sqs_response['Messages'][0]
    m_body = json.loads(message["Body"])
    receiptHandle = message["ReceiptHandle"]
    
    print(sqs_response['Messages'])
    print(m_body)
    print(receiptHandle)
    
    cuisine = m_body["cuisine"]
    location = m_body["location"]
    print(location)
    numberOfGroup = m_body["numberOfGroup"]
    email = m_body["email"]
    visit_date = m_body["date"]
    visit_time = m_body["time"]
    
    # delete pulled message in SQS
    
    delete_response = sqs_client.delete_message(
        QueueUrl = queue_url,
        ReceiptHandle = receiptHandle
    )
    
    # update location name
    if location == "manhattan" or location == "Manhattan": location = "New York"
    if location == "brooklyn": location = location.capitalize()
    if location == "jersey city" or location == "Jersey city": location = "Jersey City"
    if location == "astoria": location = "Astoria"

    
    # search in elastic
    
    headers = { "Content-Type": "application/json" }
    
    query1 = {
        "size": 800,
        "query": {
            "multi_match": {
                "query": cuisine,
                "fields": ["cuisine"]
            }
        }
    }
    r1 = requests.get(url, auth=("test1", "CC22Summer!!!"), headers=headers, data=json.dumps(query1))
    rdata1 = json.loads(r1.text)
    result1 = rdata1['hits']['hits']
    
    ridlist1 = []
    
    for row in result1:
        rid = row['_source']['id']
        ridlist1.append(rid)
    
    print(ridlist1)
    
    # search in DynamoDB
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('yelp-restaurants')

    cuisine_cap = cuisine.capitalize()
    # convert time format
    d = datetime.strptime(visit_time, "%H:%M")
    
    message_SNS = "Hello! Here are my " +  cuisine_cap + " restaurant suggestions for " + numberOfGroup + " people, for " +visit_date + " at " + d.strftime("%I:%M %p") + " : "
    
    
    i = 1
    
    for id in ridlist1:
        if i== 4: break
        resp1 = table.query(KeyConditionExpression=Key('businessid').eq(id), FilterExpression=Attr('city').eq(location))
        if resp1['Items']: 
            message_SNS +="" + str(i) + ". " + resp1['Items'][0]['name'] + ", located at " + resp1['Items'][0]['address1']
            if i != 3 : 
                message_SNS += ", "
            else : 
                message_SNS += "."
            i = i + 1
    
    message_SNS += " Enjoy your meal!"
    print(message_SNS)
    print(location)
    
    
    logging.basicConfig(format="[%(levelname)s] [%(name)s] [%(asctime)s]: %(message)s",
                        level="INFO")
    logger = logging.getLogger(__name__)
    
    sns = boto3.client('sns', region_name='us-east-1')
    sns.publish(TopicArn="arn:aws:sns:us-east-1:509327864642:restaurant_sns",
                Message= json.dumps(message_SNS))
    response = {
        "sessionAttributes": {},
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": 'Fulfilled',
            "message": {
                'contentType': 'PlainText',
                'content': ''
            }
        }
    }
        




    
    return response

