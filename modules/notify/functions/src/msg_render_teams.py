import json
from enum import Enum
from typing import Any, Dict, Optional, Union, Self

from aws_lambda_powertools import Logger
logger = Logger()

from render import Render

class TeamsPriorityColor(Enum):
  """Maps Aws  notification state to teams message format color"""

  NO_ERROR = "good"
  WARNING = "warning"
  ERROR = "danger"

class TeamsRender(Render):
  """
  Render for Teams payload
  """

  def __init__(self: Self):
    super(TeamsRender, self).__init__()

  def __format_cloudwatch_alarm(self: Self, alarm: Dict[str, Any]) -> Dict[str, Any]:
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
                        "title": "Account Name",
                        "value": f"`{alarm['account_name']}`"
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

  def __format_guard_duty_finding(self: Self, finding: Dict[str, Any]) -> Dict[str, Any]:
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
                        "title": "Account Name",
                        "value": f"`{finding['account_name']}`"
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

  def __format_health_check_alert(self: Self, alert: Dict[str, Any]) -> Dict[str, Any]:
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
                        "title": "Account Name",
                        "value": f"`{alert['account_name']}`"
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

  def __format_backup_status(self: Self, status: Dict[str, Any]) -> Dict[str, Any]:
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
                        "title": "Account Name",
                        "value": f"`{status['account_name']}`"
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


  def __format_default(self: Self, message: Union[str, Dict], subject: Optional[str] = None) -> Dict[str, Any]:
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


  # on quick inspection it looks as though this method content is duplicated and can be moved into
  #  the base class. However, formatting is very specific to each provider and thus it is not
  #  abstracted here.
  def payload(
    self: Self,
    parsedMessage: Union[str, Dict],
    originalMessage: Union[str, Dict],
    subject: Optional[str] = None
  ) -> Dict:
    """
    Given the parsed AWS message, format into teams message payload

    :params parsedMessage: the parsed message with "action" detailing message type
    :returns: teams message payload
    """

    logger.debug('Successfully parsed SNS record', parsed=parsedMessage)
    match (parsedMessage['action']):
      case "cloudwatch":
        payload = self.__format_cloudwatch_alarm(alarm=parsedMessage)
      case "guardduty":
        payload = self.__format_guard_duty_finding(finding=parsedMessage)
      case "health":
        payload = self.__format_health_check_alert(alert=parsedMessage)
      case "backup":
        payload = self.__format_backup_status(status=parsedMessage)
      case "unknown":
        payload = self.__format_default(message=originalMessage, subject=subject)

    return payload
