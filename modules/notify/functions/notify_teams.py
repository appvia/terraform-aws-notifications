# https://medium.com/@sebastian.phelps/aws-cloudwatch-alarms-on-microsoft-teams-9b5239e23b64
import json
import logging
import os
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

HOOK_URL = os.environ['TEAMS_WEBHOOK_URL']
LOG_EVENTS = os.environ['LOG_EVENTS']   # Log only if "True"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parse_cloudtrail_event(message_json_detail):
  if LOG_EVENTS == 'True':
    logger.info("message_json_detail: %s", json.dumps(message_json_detail))

  alarm_name = message_json_detail['eventName']
  
  reason = message_json_detail['errorMessage']

  data = {
    "colour": "d63333",
    "title": "Alert - %s - There is an issue: %s" % (reason.split(":")[6].split(" ")[0], alarm_name),
    "text": json.dumps({
      "Subject": alarm_name,
      "Type": message_json_detail['eventType'],
      "MessageId": message_json_detail['eventID'],
      "Message": reason,
      "Timestamp": message_json_detail['eventTime']
    })
  }
  # return data from the function
  return data



def lambda_handler(event, context):
    if LOG_EVENTS == 'True':
      logger.info("Event: %s", json.dumps(event))
    message = event['Records'][0]['Sns']['Message']

    message_json = json.loads(message)

    if 'AlarmName' in message_json:
      data = ""
      if is_cloudwatch_alarm(message):
        message_json = json.loads(event['Records'][0]['Sns']['Message'])
        alarm_name = message_json['AlarmName']
        alarm_desc = message_json['AlarmDescription']
        old_state = message_json['OldStateValue']
        new_state = message_json['NewStateValue']
        reason = message_json['NewStateReason']
        accountId = message_json['AWSAccountId']
        triggeredAt = message_json['StateChangeTime']
        region = message_json['Region']

        # formatting of Teams: https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-format?tabs=adaptive-md%2Cdesktop%2Cconnector-html
        # Advanced cards: https://learn.microsoft.com/en-us/microsoftteams/platform/task-modules-and-cards/cards/cards-reference
        message = {
          "type": "message",
          "attachments": [
            {
              "contentType": "application/vnd.microsoft.card.adaptive",
              "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.2",
                "body": [
                  {
                    "type": "Container",
                    "items": [
                      {
                        "type": "TextBlock",
                        "text": f"`{alarm_name}`",
                        "weight": "bolder",
                        "size": "medium"
                      },
                      {
                        "type": "TextBlock",
                        "text": f"`{alarm_desc}`"
                      },
                      {
                        "type": "FactSet",
                        "facts": [
                          {
                            "title": "At",
                            "value": f"`{triggeredAt}`"
                          },
                          {
                            "title": "Account Id",
                            "value": f"`{accountId}`"
                          },
                          {
                            "title": "Region",
                            "value": f"`{region}`"
                          },
                          {
                            "title": "Old State",
                            "value": f"`{old_state}`"
                          },
                          {
                            "title": "New State",
                            "value": f"`{new_state}`"
                          }
                        ]
                      },
                      {
                        "type": "TextBlock",
                        "text": f"`{reason}`"
                      }
                    ]
                  },
                  {
                    "type": "Container",
                    "items": [
                      {
                        "type": "TextBlock",
                        "text": "[The Alarm](https://todo)"
                      }
                    ]
                  }
                ]
              }
            }
          ]
        }

      else:
        data = {
          "colour": "d63333",
          "title": "Alert - There is an issue: %s" % event['Records'][0]['Sns']['Subject'],
          "text": json.dumps({
            "Subject": event['Records'][0]['Sns']['Subject'],
            "Type": event['Records'][0]['Sns']['Type'],
            "MessageId": event['Records'][0]['Sns']['MessageId'],
            "TopicArn": event['Records'][0]['Sns']['TopicArn'],
            "Message": event['Records'][0]['Sns']['Message'],
            "Timestamp": event['Records'][0]['Sns']['Timestamp']
          })
        }
        message = {
          "@context": "https://schema.org/extensions",
          "@type": "MessageCard",
          "themeColor": data["colour"],
          "title": data["title"],
          "text": data["text"]
        }
    elif 'detail-type' in message_json and message_json['detail-type'] == 'AWS Service Event via CloudTrail':
      logger.info("Parsing cloudtrail message json !!")
      data = parse_cloudtrail_event(message_json['detail'])
      message = {
        "@context": "https://schema.org/extensions",
        "@type": "MessageCard",
        "themeColor": data["colour"],
        "title": data["title"],
        "text": data["text"]
      }
    else:
      logger.error("None of the properties are present! %s", json.dumps(event['Records'][0]['Sns']['Message']))

    if LOG_EVENTS == 'True':
      logger.info("Request payload: %s", json.dumps(message))

    # Explicitly set Content-Type to 'application/json'
    req = Request(HOOK_URL, json.dumps(message).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted")
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)


def is_cloudwatch_alarm(message):
    try:
        message_json = json.loads(message)
        if message_json['AlarmName']:
            return True
        else:
            return False
    except ValueError as e:
        return False
