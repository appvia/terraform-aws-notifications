import json
from enum import Enum
from typing import Any, Dict, Optional, Union, Self

from aws_lambda_powertools import Logger
logger = Logger()

from render import Render
from notification_emblems import __ATTENTION_URL__, __WARNING_URL__

"""
2024-Sept-03
Apparently Teams does not supports the latest Adaptive card format - using V1.2
Has a useful designer: https://dev.teams.microsoft.com/cards.
You need a Microsoft account to use - it will store you card templates under your account to come back and touch up.
"""


class TeamsPriorityColor(Enum):
  """Maps Aws  notification state to teams message format color"""

  # Arrgghhh!!!! Teams color=Warning is showing red in V1.2 - having to use Accent

  NO_ERROR = "Default"
  INFO = "Default"
  LOW = "Default"
  ADVISORY = "Accent"
  WARNING = "Accent"
  MEDIUM = "Accent"
  ERROR = "Attention"
  HIGH = "Attention"
  CRITICAL = "Attention"

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

    imageIconItems = []
    postColor = TeamsPriorityColor.NO_ERROR.value
    if alarm['priority'] == "ERROR":
      imageIconItems.append({
          "type": "Image",
          "url": __ATTENTION_URL__,
          "width": "50px",
          "height": "50px"
        })
      postColor = TeamsPriorityColor.ERROR.value
    elif alarm['priority'] == "WARNING":
      imageIconItems.append({
        "type": "Image",
        "url": __WARNING_URL__,
        "width": "50px",
        "height": "50px"
      })
      postColor = TeamsPriorityColor.WARNING.value

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
                "items": imageIconItems + [
                  {
                    "type": "TextBlock",
                    "text": f"CloudWatch: `{alarm['name']}`",
                    "weight": "Bolder",
                    "size": "Large",
                    "wrap": True,
                    "color": postColor,
                  },
                  {
                    "type": "TextBlock",
                    "text": f"`{alarm['description']}`",
                    "wrap": True,
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
                        "title": "New State",
                        "value": f"`{alarm['state']}`"
                      },
                      {
                        "title": "Old State",
                        "value": f"`{alarm['old_state']}`"
                      },
                    ]
                  },
                  {
                    "type": "TextBlock",
                    "text": f"`{alarm['reason']}`",
                    "wrap": True,
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

    imageIconItems = []
    postColor = TeamsPriorityColor.NO_ERROR.value
    if finding['priority'] == "HIGH":
      imageIconItems.append({
          "type": "Image",
          "url": __ATTENTION_URL__,
          "width": "50px",
          "height": "50px"
        })
      postColor = TeamsPriorityColor.ERROR.value
    elif finding['priority'] == "MEDIUM":
      imageIconItems.append({
        "type": "Image",
        "url": __WARNING_URL__,
        "width": "50px",
        "height": "50px"
      })
      postColor = TeamsPriorityColor.WARNING.value

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
                "items": imageIconItems + [
                  {
                    "type": "TextBlock",
                    "text": f"`GuardDuty: {finding['title']}`",
                    "weight": "Bolder",
                    "size": "Large",
                    "wrap": True,
                    "color": postColor,
                  },
                  {
                    "type": "TextBlock",
                    "text": f"`{finding['description']}`",
                    "wrap": True,
                  },
                  {
                    "type": "FactSet",
                    "facts": [
                      {
                        "title": "ID",
                        "value": f"`{finding['id']}`"
                      },
                      {
                        "title": "Severity/Score",
                        "value": f"`{finding['severity']}/{finding['severity_score']}`"
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

    imageIconItems = []
    postColor = TeamsPriorityColor.NO_ERROR.value
    if alert['priority'] == "HIGH":
      imageIconItems.append({
          "type": "Image",
          "url": __ATTENTION_URL__,
          "width": "50px",
          "height": "50px"
        })
      postColor = TeamsPriorityColor.ERROR.value
    elif alert['priority'] == "MEDIUM":
      imageIconItems.append({
        "type": "Image",
        "url": __WARNING_URL__,
        "width": "50px",
        "height": "50px"
      })
      postColor = TeamsPriorityColor.WARNING.value

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
                "items": imageIconItems + [
                  {
                    "type": "TextBlock",
                    "text": f"`AWS Health: {alert['service']}`",
                    "weight": "Bolder",
                    "size": "Large",
                    "wrap": True,
                    "color": postColor,
                  },
                  {
                    "type": "TextBlock",
                    "text": f"`{alert['description']}`",
                    "wrap": True,
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
                    "text": f"[The Healthcheck]({alert['url']})",
                    "wrap": True,
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

    imageIconItems = []
    postColor = TeamsPriorityColor.NO_ERROR.value
    if status['priority'] == "ERROR":
      imageIconItems.append({
          "type": "Image",
          "url": __ATTENTION_URL__,
          "width": "50px",
          "height": "50px"
        })
      postColor = TeamsPriorityColor.ERROR.value
    elif status['priority'] == "WARNING":
      imageIconItems.append({
        "type": "Image",
        "url": __WARNING_URL__,
        "width": "50px",
        "height": "50px"
      })
      postColor = TeamsPriorityColor.WARNING.value

    facts: list[Dict[str, Any]] = []
    backup_fields = status['backup_fields']
    for k, v in backup_fields.items():
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
                "items": imageIconItems + [
                  {
                    "type": "TextBlock",
                    "text": f"`AWS Backup: {status['backup_id']}`",
                    "weight": "Bolder",
                    "size": "Large",
                    "wrap": True,
                    "color": postColor,
                  },
                  {
                    "type": "TextBlock",
                    "text": f"`{status['description']}`",
                    "wrap": True,
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

  def __format_security_hub_status(self: Self, finding: Dict[str, Any]) -> Dict[str, Any]:
    """Format AWS Security Hub finding facts into teams message format

    :params finding: budget facts
    :returns: formatted teams message payload
    """
    imageIconItems = []
    postColor = TeamsPriorityColor.NO_ERROR.value
    if finding['priority'] == "CRITICAL" or finding['priority'] == "HIGH":
      imageIconItems.append({
          "type": "Image",
          "url": __ATTENTION_URL__,
          "width": "50px",
          "height": "50px"
        })
      postColor = TeamsPriorityColor.ERROR.value
    elif finding['priority'] == "MEDIUM":
      imageIconItems.append({
        "type": "Image",
        "url": __WARNING_URL__,
        "width": "50px",
        "height": "50px"
      })
      postColor = TeamsPriorityColor.WARNING.value

    resourcesField: list[Dict[str, Any]] = []
    idx = 1
    for  resource in finding['resources']:
      resourceId = resource["id"]
      resourceType = resource["type"]
      resourcesField.append({
        "title": f"Type {idx}",
        "value": f"`{resourceType}`",
      })
      resourcesField.append({
        "title": f"Arn {idx}",
        "value": f"`{resourceId}`",
      })
      idx += 1
    
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
                "items": imageIconItems + [
                  {
                    "type": "TextBlock",
                    "text": f"Security Hub: {finding['source']}",
                    "weight": "Bolder",
                    "size": "Large",
                    "wrap": True,
                    "color": postColor,
                  },
                  {
                    "type": "FactSet",
                    "facts": [
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
                        "title": "Severity",
                        "value": f"`{finding['severity']}`"
                      },
                      {
                        "title": "Source",
                        "value": f"`{finding['source']}`"
                      },
                      {
                        "title": "Providerr",
                        "value": f"`{finding['ruleProvider']} v{finding['providerVersion']}`"
                      },
                      {
                        "title": "Category",
                        "value": f"`{finding['providerCategory']}`"
                      },
                      {
                        "title": "Rule",
                        "value": f"`{finding['ruleId']}`"
                      },
                    ]
                  },
                  {
                    "type": "TextBlock",
                    "text": f"`{finding['description']}`",
                    "wrap": True,
                  },
                  {
                    "type": "FactSet",
                    "facts": [] + resourcesField,
                    "wrap": True,
                  },
                ]
              },
              {
                "type": "Container",
                "items": [
                  {
                    "type": "TextBlock",
                    "text": f"[The Finding]({finding['url']})",
                    "wrap": True,
                  }
                ]
              }
            ]
          }
        }
      ]
    }

  def __format_budget_alert(self: Self, alarm: Dict[str, Any]) -> Dict[str, Any]:
    """Format Budget alarm facts into Slack message format

    :params message: Budget facts
    :returns: formatted Slack message payload
    """
    return {
      "type": "message",
      "attachments": [
        {
          "contentType": "application/vnd.microsoft.card.adaptive",
          "content": {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "fallbackText": f"Budget Alarm: {alarm['subject']}",
            "version": "1.2",
            "body": [
              {
                "type": "Container",
                "items": [
                  {
                    "type": "Image",
                    "url": __WARNING_URL__,
                    "width": "50px",
                    "height": "50px"
                  },
                  {
                    "type": "TextBlock",
                    "text": f"Budget Alarm: {alarm['subject']}",
                    "weight": "Bolder",
                    "size": "Large",
                    "wrap": True,
                    "color": TeamsPriorityColor.WARNING.value
                  },
                  {
                    "type": "RichTextBlock",
                    "inlines": [
                      {
                        "type": "TextRun",
                        "text": f"{alarm['info']}"
                      }
                    ]
                  }
                ]
              }
            ]
          }
        }
      ]
    }

  def __format_savings_plan_alert(self: Self, alarm: Dict[str, Any]) -> Dict[str, Any]:
    """Format Savings Plan alarm facts into Slack message format

    :params message: Savings Plans facts
    :returns: formatted Slack message payload
    """
    return {
      "type": "message",
      "attachments": [
        {
          "contentType": "application/vnd.microsoft.card.adaptive",
          "content": {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "fallbackText": f"Savings Plan Alarm: {alarm['subject']}",
            "version": "1.2",
            "body": [
              {
                "type": "Container",
                "items": [
                  {
                    "type": "Image",
                    "url": __WARNING_URL__,
                    "width": "50px",
                    "height": "50px"
                  },
                  {
                    "type": "TextBlock",
                    "text": f"Savings Plan Alarm: {alarm['subject']}",
                    "weight": "Bolder",
                    "size": "Large",
                    "wrap": True,
                    "color": TeamsPriorityColor.WARNING.value
                  },
                  {
                    "type": "RichTextBlock",
                    "inlines": [
                      {
                        "type": "TextRun",
                        "text": f"{alarm['info']}"
                      }
                    ]
                  }
                ]
              }
            ]
          }
        }
      ]
    }
  
  def __format_DMS_notification(self: Self, event: Dict[str, Any]) -> Dict[str, Any]:
    """Format DMS notificatoin facts into teams message format

    :params alarm: DMS notification facts
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
                    "text": f"DMS Notification: {event['title']}",
                    "weight": "Bolder",
                    "size": "Large",
                    "wrap": True,
                    "color": "default",
                  },
                  {
                    "type": "FactSet",
                    "facts": [
                      {
                        "title": "At",
                        "value": f"`{event['at']}`"
                      },
                      {
                        "title": "At (Epoch)",
                        "value": f"`{event['at_epoch']}`"
                      },
                      {
                        "title": "Source",
                        "value": f"`{event['source']}`"
                      },
                      {
                        "title": "Source Id",
                        "value": f"`{event['source_id']}`"
                      }
                    ]
                  },
                  {
                    "type": "TextBlock",
                    "text": f"`{event['documentation']}`",
                    "wrap": True,
                  }
                ]
              },
              {
                "type": "Container",
                "items": [
                  {
                    "type": "TextBlock",
                    "text": f"[The Event]({event['url']})",
                    "wrap": True,
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
                    "weight": "Bolder",
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
      case "CloudWatch":
        payload = self.__format_cloudwatch_alarm(alarm=parsedMessage)
      case "GuardDuty":
        payload = self.__format_guard_duty_finding(finding=parsedMessage)
      case "Health":
        payload = self.__format_health_check_alert(alert=parsedMessage)
      case "Backup":
        payload = self.__format_backup_status(status=parsedMessage)
      case "SecurityHub":
        payload = self.__format_security_hub_status(finding=parsedMessage)
      case "Budget":
        payload = self.__format_budget_alert(alarm=parsedMessage)
      case "SavingsPlan":
        payload = self.__format_savings_plan_alert(alarm=parsedMessage)
      case "DMS":
        payload = self.__format_DMS_notification(event=parsedMessage)
      case "Unknown":
        payload = self.__format_default(message=originalMessage, subject=subject)

    return payload
