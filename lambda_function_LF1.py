"""
This sample demonstrates an implementation of the Lex Code Hook Interface
in order to serve a sample bot which manages orders for flowers.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'OrderFlowers' template.

For instructions on how to set up and test this bot, as well as additional samples,
visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""
import boto3
import datetime
import dateutil.parser
import json
import logging
import math
import os
import time
import re
from botocore.vendored import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ACCESS_ID = '*'
ACCESS_KEY= '*'
logging.basicConfig(format="[%(levelname)s] [%(name)s] [%(asctime)s]: %(message)s",
                    level="INFO")
logger = logging.getLogger(__name__)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False



def email_valid(s):
   pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
   if re.match(pat,s):
      return True
   return False



def validate_cusine_order(location,cuisine,numberOfGroup, date, dinning_time,email):
    cuisine_types = ['chinese', 'indian', 'japanese','mexican','american','italian']
    locations =['jersey city','manhattan','brooklyn']

    if location is not None and location.lower() not in locations:
        return build_validation_result(False,
                                       'LocationSlot',
                                       'We do not support {} area. We only offer recommendations for Manhattan, Jersey City and Brooklyn areas. Please type a location from those options.'.format(location))

    if cuisine is not None and cuisine.lower() not in cuisine_types:
        return build_validation_result(False,
                                       'Cuisine',
                                       'We do not support {} restaurant recommendations. We only offer recommendations for Chinese, Indian, Japanese, Mexican, American and Italian food. Please type a cuisine type from those options'.format(cuisine))
    
    if numberOfGroup is not None:
        numberOfGroup = int(numberOfGroup)
        if numberOfGroup > 20:
            return build_validation_result(False,
                                           'NumberofGroup',
                                           'Maximum 20 people allowed. Try again')
        if numberOfGroup <= 0:
            return build_validation_result(False,
                                           'NumberofGroup',
                                           'Please type a valid number')
    
    if date is not None:
        if not isvalid_date(date):
            return build_validation_result(False, 'DinningDate', 'I did not understand that, what date would you like to pick the flowers up?')
        elif datetime.datetime.strptime(date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'DinningDate', 'You can make reservation from tomorrow onwards.  What day would you like to restaurant?')

    if dinning_time is not None:
        if len(dinning_time) != 5:
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'DinningTime', None)

        hour, minute = dinning_time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            # Not a valid time; use a prompt defined on the build-time model.
            return build_validation_result(False, 'DinningTime', None)

        if hour < 10 or hour > 22:
            # Outside of business hours
            return build_validation_result(False, 'DinningTime', 'Our business hours are from 10 a m. to 10 p m. Can you specify a time during this range?')
        
    if email is not None:
        if not email_valid(email):
            return build_validation_result(False, 'email', 'Please type a valid email address')

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """


def resturant_suggest(intent_request):
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """

    location = get_slots(intent_request)["LocationSlot"]
    cuisine = get_slots(intent_request)["Cuisine"]
    numberOfGroup = get_slots(intent_request)["NumberofGroup"]
    date = get_slots(intent_request)["DinningDate"]
    dinning_time = get_slots(intent_request)["DinningTime"]
    email = get_slots(intent_request)["email"]
    source = intent_request['invocationSource']

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)

        validation_result = validate_cusine_order(location,cuisine,numberOfGroup, date, dinning_time,email)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])

        # Pass the price of the flowers back through session attributes to be used in various prompts defined
        # on the bot model.
        if intent_request['sessionAttributes'] is not None:
            output_session_attributes = intent_request['sessionAttributes']
        else:
            output_session_attributes = {}
        return delegate(output_session_attributes, get_slots(intent_request))

    # Order the flowers, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    print(email)
   
    msg = {"cuisine": cuisine, "location":location,"numberOfGroup":numberOfGroup,"email": email,"date":date,"time":dinning_time}
    sqs = boto3.client('sqs', region_name='us-east-1',aws_access_key_id=ACCESS_ID,
         aws_secret_access_key= ACCESS_KEY)
    attributes = {'sent_to_sqs_utc_date': {'DataType': 'String',
                                       'StringValue': datetime.datetime.utcnow().isoformat()}}
    send_response = sqs.send_message(QueueUrl= 'https://sqs.us-east-1.amazonaws.com/509327864642/restaurants_suggest',
                                 MessageAttributes=attributes,
                                 MessageBody=json.dumps(msg))
    logger.info("Send message response: %s", send_response)

    return close(intent_request['sessionAttributes'],
                 'Fulfilled',
                 {'contentType': 'PlainText',
                  'content': 'Thank you! You will recieve suggestion shortly'})


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return resturant_suggest(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)