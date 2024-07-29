# -*- coding: utf-8 -*-
"""
    Notify Teams
    ------------

    Receives event payloads that are parsed and sent to Teams

"""

import json
import logging
import os
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from enum import Enum
from typing import Any, Dict, Optional, Union, cast
from urllib.error import HTTPError

LOG_EVENTS = os.environ['LOG_EVENTS']   # Log only if "True"

import msgParser

class TeamsPriorityColor(Enum):
    """Maps Aws  notification state to teams message format color"""

    NO_ERROR = "good"
    WARNING = "warning"
    ERROR = "danger"

def format_cloudwatch_alarm(alarm: Dict[str, Any]) -> Dict[str, Any]:
    """Format CloudWatch alarm facts into teams message format

    :params alarm: CloudWatch facts
    :returns: formatted teams message payload
    """
    return {
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
                    "text": f"`{alarm['name']}`",
                    "weight": "bolder",
                    "size": "medium"
                  },
                  {
                    "type": "TextBlock",
                    "text": f"`{alarm['description']}`"
                  },
                  {
                    "type": "FactSet",
                    "facts": [
                      {
                        "title": "At",
                        "value": f"`{alarm['at']}`"
                      },
                      {
                        "title": "Account Id",
                        "value": f"`{alarm['account_id']}`"
                      },
                      {
                        "title": "Region",
                        "value": f"`{alarm['alarm_arn_region']}`"
                      },
                                            {
                        "title": "Region Locale",
                        "value": f"`{alarm['region']}`"
                      },
                      {
                        "title": "Old State",
                        "value": f"`{alarm['old_state']}`"
                      },
                      {
                        "title": "New State",
                        "value": f"`{alarm['state']}`"
                      }
                    ]
                  },
                  {
                    "type": "TextBlock",
                    "text": f"`{alarm['reason']}`"
                  }
                ]
              },
              {
                "type": "Container",
                "items": [
                  {
                    "type": "TextBlock",
                    "text": f"[The Alarm]({alarm['url']})"
                  }
                ]
              }
            ]
          }
        }
      ]
    }

def format_guard_duty_finding(finding: Dict[str, Any]) -> Dict[str, Any]:
    """Format GuardDuty facts into teams message format

    :params finding: GuardDuty facts
    :returns: formatted teams message payload
    """

    return {
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
                    "text": f"`GuardDuty Finding: {finding['title']}`",
                    "weight": "bolder",
                    "size": "medium"
                  },
                  {
                    "type": "TextBlock",
                    "text": f"`{finding['description']}`"
                  },
                  {
                    "type": "FactSet",
                    "facts": [
                      {
                        "title": "ID",
                        "value": f"`{finding['id']}`"
                      },
                      {
                        "title": "Severity",
                        "value": f"`{finding['severity']}`"
                      },
                      {
                        "title": "Account Id",
                        "value": f"`{finding['account_id']}`"
                      },
                      {
                        "title": "Region",
                        "value": f"`{finding['region']}`"
                      },
                      {
                        "title": "First Seen",
                        "value": f"`{finding['first_seen']}`"
                      },
                      {
                        "title": "Last Seen",
                        "value": f"`{finding['last_seen']}`"
                      },
                      {
                        "title": "Count",
                        "value": f"`{finding['count']}`"
                      },
                    ]
                  }
                ]
              },
              {
                "type": "Container",
                "items": [
                  {
                    "type": "TextBlock",
                    "text": f"[The Finding]({finding['url']}#/findings?search=id%3D{finding['id']})"
                  }
                ]
              }
            ]
          }
        }
      ]
    }

def format_health_check_alert(alert: Dict[str, Any]) -> Dict[str, Any]:
    """Format AWS HealthCheck facts into teams message format

    :params finding: Healthcheck facts
    :returns: formatted teams message payload
    """

    return {
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
                    "text": f"`AWS Health Event for service: {alert['service']}`",
                    "weight": "bolder",
                    "size": "medium"
                  },
                  {
                    "type": "TextBlock",
                    "text": f"`{alert['description']}`"
                  },
                  {
                    "type": "FactSet",
                    "facts": [
                      {
                        "title": "Category",
                        "value": f"`{alert['category']}`"
                      },
                      {
                        "title": "Priority",
                        "value": f"`{alert['priority']}`"
                      },
                      {
                        "title": "Code",
                        "value": f"`{alert['code']}`"
                      },
                      {
                        "title": "Account Id",
                        "value": f"`{alert['account_id']}`"
                      },
                      {
                        "title": "Region",
                        "value": f"`{alert['region']}`"
                      },
                      {
                        "title": "Start Time",
                        "value": f"`{alert['start_time']}`"
                      },
                      {
                        "title": "End Time",
                        "value": f"`{alert['end_time']}`"
                      },
                      {
                        "title": "Affected Resources",
                        "value": f"`{alert['resources']}`"
                      },
                    ]
                  }
                ]
              },
              {
                "type": "Container",
                "items": [
                  {
                    "type": "TextBlock",
                    "text": f"[The Healthcheck]({alert['url']})"
                  }
                ]
              }
            ]
          }
        }
      ]
    }

def format_backup_status(status: Dict[str, Any]) -> Dict[str, Any]:
    """Format AWS Backup facts into teams message format

    :params finding: Backup facts
    :returns: formatted teams message payload
    """

    facts: list[Dict[str, Any]] = []
    backup_fields = status['backup_fields']
    for k, v in backup_fields.items():
        # fields.append({"value": k, "short": False})
        # fields.append({"value": f"`{v}`", "short": False})
        facts.append({
            "title": k,
            "value": f"`{v}`",
        })

    return {
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
                    "text": f"`AWS Backup: {status['backup_id']}`",
                    "weight": "bolder",
                    "size": "medium"
                  },
                  {
                    "type": "TextBlock",
                    "text": f"`{status['description']}`"
                  },
                  {
                    "type": "FactSet",
                    "facts": [
                      {
                        "title": "Backup Id",
                        "value": f"`{status['backup_id']}`"
                      },
                      {
                        "title": "Account Id",
                        "value": f"`{status['account_id']}`"
                      },
                      {
                        "title": "Region",
                        "value": f"`{status['region']}`"
                      },
                      {
                        "title": "Status",
                        "value": f"`{status['status']}`"
                      },
                      {
                        "title": "Priority",
                        "value": f"`{status['priority']}`"
                      },
                      {
                        "title": "Start Time",
                        "value": f"`{status['start_time']}`"
                      },
                    ] + facts
                  }
                ]
              }
            ]
          }
        }
      ]
    }


def format_default(
    message: Union[str, Dict], subject: Optional[str] = None
) -> Dict[str, Any]:
    """
    Default formatter, converting event into teams message format

    :params message: SNS message body containing message/event
    :returns: formatted teams message payload
    """

    title =  subject if subject else "Message"
    facts = []

    if type(message) is dict:
        for k, v in message.items():
            value = f"{json.dumps(v)}" if isinstance(v, (dict, list)) else str(v)
            facts.append({"title": k, "value": f"`{value}`"})
    else:
        facts.append({"value": message, "short": False})

    return {
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
                    "text": title,
                    "weight": "bolder",
                    "size": "medium"
                  },
                  {
                    "type": "FactSet",
                    "facts": facts
                  }
                ]
              }
            ]
          }
        }
      ]
    }


def get_teams_message_payload(
    parsedMessage: Union[str, Dict],
    originalMessage: Union[str, Dict],
    subject: Optional[str] = None
) -> Dict:
    """
    Given the parsed AWS message, format into teams message payload

    :params parsedMessage: the parsed message with "action" detailing message type
    :returns: teams message payload
    """

    match (parsedMessage['action']):
        case "cloudwatch":
            payload = format_cloudwatch_alarm(alarm=parsedMessage)
        case "guardduty":
            payload = format_guard_duty_finding(finding=parsedMessage)
        case "health":
            payload = format_health_check_alert(alert=parsedMessage)
        case "backup":
            payload = format_backup_status(status=parsedMessage)
        case "unknown":
            payload = format_default(message=originalMessage, subject=subject)

    return payload


def send_teams_notification(payload: Dict[str, Any]) -> str:
    """
    Send notification payload to teams

    :params payload: formatted teams message payload
    :returns: response details from sending notification
    """
    teams_url = os.environ["TEAMS_WEBHOOK_URL"]
    if not teams_url.startswith("http"):
        teams_url = msgParser.decrypt_url(teams_url)
    
    if LOG_EVENTS == "True":
      logging.info(f"Event logging enabled (teams payload) to {teams_url}: `{payload}`")

    req = Request(teams_url, json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        response = urlopen(req)
        response.read()
        logging.info("Message posted")
        return json.dumps({"code": response.getcode(), "info": response.info().as_string()})
    except HTTPError as e:
        logging.error("Request failed: %d %s", e.code, e.reason)
        return json.dumps({"code": e.getcode(), "info": e.info().as_string()})
    except URLError as e:
        logging.error("Server connection failed: %s", e.reason)
        return json.dumps({"code": 500, "info": "Unexpected error"})

def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Lambda function to parse notification events and forward to teams

    :param event: lambda expected event object
    :param context: lambda expected context object
    :returns: none
    """

    if LOG_EVENTS == "True":
        logging.info(f"Event logging enabled (Event): `{json.dumps(event)}`")

    for record in event["Records"]:
        sns = record["Sns"]
        subject = sns["Subject"]
        message = sns["Message"]
        region = sns["TopicArn"].split(":")[3]
        messageAttributes = sns["MessageAttributes"]

        parserResults = msgParser.get_message_payload(
          message=message,
          region=region,
          messageAttributes=messageAttributes,
          subject=subject,
        )
        payload = get_teams_message_payload(
          parsedMessage=parserResults.parsedMsg,
          originalMessage=message,
          subject=subject,
        )
        response = send_teams_notification(payload=payload)

    if json.loads(response)["code"] != 202:
        response_info = json.loads(response)["info"]
        logging.error(
            f"Error: received status `{response_info}` using event `{event}` and context `{context}`"
        )

    return response
