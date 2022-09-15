# Dining-Concierge-Chatbot

## Brief Description

This project is to build a web-based Dinining Concierge Chatbot that sends users restaurant suggestions given a set of preferences that users provide the chatbot with through conversation.

![image](https://user-images.githubusercontent.com/91846138/185481314-3afcd18e-b563-4e9f-87cf-59e3cd9d8b43.png)

![image](https://user-images.githubusercontent.com/91846138/185481393-e0367436-4558-4ccd-94c7-963f04dfb39f.png)

![image](https://user-images.githubusercontent.com/91846138/185481463-77e597c1-e80e-4afe-84fb-e1864f9034f2.png)


## Frontend

Use the frontend starter application to interface with Amazon Lex service. Below is the link to the frontend code.

https://github.com/ndrppnc/cloud-hw1-starter

![image](https://user-images.githubusercontent.com/91846138/185465489-c619412f-8b7a-4756-80a8-8c0fe61a876b.png)

## Connection between frontend and backend

Use Amazon API Gateway to set up API. A post method is created to send the parameters collected from the user to the backend

![image](https://user-images.githubusercontent.com/91846138/185469842-b0206a45-68c7-4a6b-8ff8-a7733cced000.png)


## Backend
### Amazon Lex
A chat bot is created in Amazon Lex. Implemented greeting, dining suggestion and thank you intents in the bot. For dining suggesting intent, the following parameters need to be collected from the user through conversation:

- Location
- Cuisine type
- Dining time
- Number of people
- Email address

### Collect data from Yelp API
Collect 5000+ randon resturants information for New York City area. See yelppull.py file for code details.

![image](https://user-images.githubusercontent.com/91846138/185472278-3012425c-afe5-4aeb-8ef9-401252c0f0b3.png)

### DynamoDB
Store yelp restaurant info in DynamoDB.

![image](https://user-images.githubusercontent.com/91846138/185472747-38ccbce7-da61-479d-8833-b6738aac4585.png)

### ElasticSearch
Create ElasticSearch index to store partial information for each restaurant for searching purpose. See below as example:

![image](https://user-images.githubusercontent.com/91846138/185477295-dfbfd82e-60f6-40c8-8dc9-cea2c4156de5.png)

### SQS
Store the customer requests in SQS queue to make the application asynchonous.

### SNS
Use SNS to send customers over restaurant suggestion text message to their email addresses.

### Lambda Function
- Lambda Function LF0: connect API Gateway with Amazon Lex bot to perform the chat operation.
- Lambda Function LF1: pass parameters collected in Amazon Lex to SQS.
- Lambda Function LF2: act as queue worker. 
    - pull message from SQS
    - get a random restaurant recommendation for the cuisine collected through conversation from ElasticSearch and DynamoDB
    - format recommendation suggestion and send it over to the customer using SNS
    
### CloudWatch
Use to trigger Lambda Function LF2 every a few seconds


