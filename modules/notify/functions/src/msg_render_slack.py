import json
from enum import Enum
from typing import Any, Dict, Optional, Union, Self

from aws_lambda_powertools import Logger
logger = Logger()

from render import Render

class SlackPriorityColor(Enum):
  """Maps Aws  notification state to Slack message format color"""

  NO_ERROR = "good"
  INFO = "good"
  LOW = "#777777"
  ADVISORY = "#777777"
  WARNING = "warning"
  MEDIUM = "warning"
  ERROR = "danger"
  HIGH = "danger"
  CRITICAL = "danegr"

class SlackRender(Render):
  """
  Render for slack payload
  """

  def __init__(self: Self):
    super(SlackRender, self).__init__()
  
  def __format_cloudwatch_alarm(self: Self, alarm: Dict[str, Any]) -> Dict[str, Any]:
    """Format CloudWatch alarm facts into Slack message format

    :params message: CloudWatch facts
    :returns: formatted Slack message payload
    """
    return {
        "color": SlackPriorityColor[alarm["priority"]].value,
        "fallback": "Alarm %s triggered" % (alarm["name"]),
        "title": f"CloudWatch Alarm: {alarm['name']}",
        "title_link": f"{alarm['url']}",
        "text": f"{alarm['description']}",
        "ts": alarm['at_epoch'],
        "fields": [
          {
            "title": "When",
            "value": f"`{alarm['at']}`",
            "short": False,
          },
          {
            "title": "Account Name",
            "value": f"`{alarm['account_name']}`",
            "short": True,
          },
          {
            "title": "Account ID",
            "value": f"`{alarm['account_id']}`",
            "short": True,
          },
          {
            "title": "Region",
            "value": f"`{alarm['alarm_arn_region']}`",
            "short": True,
          },
          {
            "title": "Region Locale",
            "value": f"`{alarm['region']}`",
            "short": True,
          },
          {
            "title": "Alarm reason",
            "value": f"{alarm['reason']}",
            "short": False,
          },
          {
            "title": "Old State",
            "value": f"`{alarm['old_state']}`",
            "short": True,
          },
          {
            "title": "Current State",
            "value": f"`{alarm['state']}`",
            "short": True,
          }
        ],
    }

  def __format_guard_duty_finding(self: Self, finding: Dict[str, Any]) -> Dict[str, Any]:
    """Format GuardDuty alarm facts into Slack message format

    :params message: GuardDuty facts
    :returns: formatted Slack message payload
    """
    return {
      "color": SlackPriorityColor[finding["priority"]].value,
      "fallback": f"GuardDuty Finding: {finding['title']}",
      "title": f"GuardDuty Finding: {finding['title']}",
      "title_link": f"{finding['url']}#/findings?search=id%3D{finding['id']}",
      "text": f"{finding['description']}",
      "ts": finding['at_epoch'],
      "fields": [
        {
          "title": "Finding Type",
          "value": f"`{finding['type']}`",
          "short": False,
        },
        {
          "title": "First Seen",
          "value": f"`{finding['first_seen']}`",
          "short": True,
        },
        {
          "title": "Last Seen",
          "value": f"`{finding['last_seen']}`",
          "short": True,
        },
        {
          "title": "Severity",
          "value": f"`{finding['severity']}`",
          "short": True,
        },
        {
          "title": "Count",
          "value": f"`{finding['count']}`",
          "short": True,
        },
        {
          "title": "Account Name",
          "value": f"`{finding['account_name']}`",
          "short": True,
        },
        {
          "title": "Account ID",
          "value": f"`{finding['account_id']}`",
          "short": True,
        },
        {
          "title": "Region",
          "value": f"`{finding['region']}`",
          "short": True,
        },
      ]
    }

  def __format_health_check_alert(self: Self, alert: Dict[str, Any]) -> Dict[str, Any]:
    """Format AWS Healthcheck facts into Slack message format

    :params message: HealthCheck facts
    :returns: formatted Slack message payload
    """
    return {
      "color": SlackPriorityColor[alert["priority"]].value,
      "fallback": f"New AWS Health Event for {alert['service']}",
      "title": f"AWS Health Event for service: {alert['service']}",
      "title_link": f"{alert['url']}",
      "text": f"{alert['description']}",
      "ts": alert['at_epoch'],
      "fields": [
        {
          "title": "Affected Service",
          "value": f"`{alert['service']}`",
          "short": True,
        },
        {
          "title": "Category",
          "value": f"`{alert['category']}`",
          "short": True,
        },
        {
          "title": "Account Name",
          "value": f"`{alert['account_name']}`",
          "short": True,
        },
        {
          "title": "Account Id",
          "value": f"`{alert['account_id']}`",
          "short": True,
        },
        {
          "title": "Start Time",
          "value": f"`{alert['start_time']}`",
          "short": True,
        },
        {
          "title": "End Time",
          "value": f"`{alert['end_time']}`",
          "short": True,
        },
        {
          "title": "Code",
          "value": f"`{alert['code']}`",
          "short": False,
        },
        {
          "title": "Region",
          "value": f"`{alert['region']}`",
          "short": False,
        },
        {
          "title": "Affected Resources",
          "value": f"{alert['resources']}",
          "short": False,
        },
      ],
    }

  def __format_backup_status(self: Self, status: Dict[str, Any]) -> Dict[str, Any]:
    """Format AWS Backup facts into teams message format

    :params finding: Backup facts
    :returns: formatted teams message payload
    """

    fields: list[Dict[str, Any]] = []
    backup_fields = status['backup_fields']
    for k, v in backup_fields.items():
      fields.append({
        "title": k,
        "value": f"`{v}`",
        "short": False,
      })

    return {
      "color": SlackPriorityColor[status["priority"]].value,
      "fallback": f"Backup event for {status['backup_id']}",
      "title": f"Backup event for {status['backup_id']}",
      # "title_link": f"{status['url']}",
      "text": f"{status['description']}",
      # "ts": alert['at_epoch'],
      "fields": [
        {
          "title": "Backup Id",
          "value": f"`{status['backup_id']}`",
          "short": False,
        },
        {
          "title": "Account Name",
          "value": f"`{status['account_name']}`",
          "short": True,
        },
        {
          "title": "Account Id",
          "value": f"`{status['account_id']}`",
          "short": True,
        },
        {
          "title": "Status",
          "value": f"`{status['status']}`",
          "short": True,
        },
        {
          "title": "Priority",
          "value": f"`{status['priority']}`",
          "short": True,
        },
        {
          "title": "Region",
          "value": f"`{status['region']}`",
          "short": True,
        },
        {
          "title": "Start Time",
          "value": f"`{status['start_time']}`",
          "short": True,
        },
      ] + fields,
    }

  def __format_security_hub_status(self: Self, finding: Dict[str, Any]) -> Dict[str, Any]:
    """Format Seucrity Hub finding  facts into Slack message format

    :params finding: Security Hub facts
    :returns: formatted Slack message payload
    """
    resourcesField: list[Dict[str, Any]] = []
    idx = 1
    for  resource in finding['resources']:
      resourceId = resource["id"]
      resourceType = resource["type"]
      resourcesField.append({
        "title": f"Type {idx}",
        "value": f"`{resourceType}`",
        "short": True,
      })
      resourcesField.append({
        "title": f"Arn {idx}",
        "value": f"`{resourceId}`",
        "short": False,
      })
      idx += 1

    return {
        "color": SlackPriorityColor[finding["priority"]].value,
        "fallback": "Security Hub finding %s triggered" % (finding["source"]),
        "title": f"Security Hub finding: {finding['source']}",
        "title_link": f"{finding['url']}",
        "text": f"{finding['description']}",
        # "ts": alarm['at_epoch'],
        "fields": [
          {
            "title": "Account Name",
            "value": f"`{finding['account_name']}`",
            "short": True,
          },
          {
            "title": "Account ID",
            "value": f"`{finding['account_id']}`",
            "short": True,
          },
          {
            "title": "Region",
            "value": f"`{finding['region']}`",
            "short": False,
          },
          {
            "title": "Provider",
            "value": f"`{finding['ruleProvider']} v{finding['providerVersion']}`",
            "short": True,
          },
          {
            "title": "Category",
            "value": f"`{finding['providerCategory']}`",
            "short": True,
          },
          {
            "title": "Rule Id",
            "value": f"`{finding['ruleId']}`",
            "short": False,
          },
        ] + resourcesField,
    }

  def __format_budget_alert(self: Self, alarm: Dict[str, Any]) -> Dict[str, Any]:
    """Format Budget alarm facts into Slack message format

    :params message: Budget facts
    :returns: formatted Slack message payload
    """
    return {
        "color": SlackPriorityColor.HIGH.value,
        "fallback": "Budget %s triggered" % (alarm["subject"]),
        "title": f"Budget Alarm: {alarm['subject']}",
        "mrkdwn_in": ["value"],
        "fields": [
          {
            "value": f"{alarm['info']}",
            "short": False,
          }
        ],
    }

  def __format_savings_plan_alert(self: Self, alarm: Dict[str, Any]) -> Dict[str, Any]:
    """Format Savings Plan alarm facts into Slack message format

    :params message: Savings Plans facts
    :returns: formatted Slack message payload
    """
    return {
        "color": SlackPriorityColor.HIGH.value,
        "fallback": "Savings Plan %s triggered" % (alarm["subject"]),
        "title": f"Savings Plan Alarm: {alarm['subject']}",
        "text": f"{alarm['info']}",
    }
  
  def __format_DMS_notification(self: Self, event: Dict[str, Any]) -> Dict[str, Any]:
    """Format DMS notification facts into Slack message format

    :params message: DMS notificatoin facts
    :returns: formatted Slack message payload
    """
    return {
        "color": SlackPriorityColor.WARNING.value,
        "fallback": "DMS Notification %s triggered" % (event["title"]),
        "title": f"DMS Notification: {event['title']}",
        "title_link": f"{event['url']}",
        "text": f"{event['documentation']}",
        "ts": event['at_epoch'],
        "fields": [
          {
            "title": "When",
            "value": f"`{event['at']}`",
            "short": True,
          },
          {
            "title": "When (Epoch)",
            "value": f"`{event['at_epoch']}`",
            "short": True,
          },
          {
            "title": "Source",
            "value": f"`{event['source']}`",
            "short": True,
          },
          {
            "title": "Source ID",
            "value": f"`{event['source_id']}`",
            "short": True,
          }
        ]
    }

  def __format_default(self: Self, message: Union[str, Dict], subject: Optional[str] = None) -> Dict[str, Any]:
    """
    Default formatter, converting event into Slack message format

    :params message: SNS message body containing message/event
    :returns: formatted Slack message payload
    """

    attachments = {
      "fallback": "A new message",
      "text": "AWS notification",
      "title": subject if subject else "Message",
      "mrkdwn_in": ["value"],
    }
    fields = []

    if type(message) is dict:
      for k, v in message.items():
        value = f"{json.dumps(v)}" if isinstance(v, (dict, list)) else str(v)
        fields.append({"title": k, "value": f"`{value}`", "short": len(value) < 25})
    else:
      fields.append({"value": message, "short": False})

    if fields:
      attachments["fields"] = fields  # type: ignore

    return attachments

  def payload(
    self: Self,
    parsedMessage: Union[str, Dict],
    originalMessage: Union[str, Dict],
    subject: Optional[str] = None
  ) -> Dict:
    """
    Given the parsed AWS message, format into Slack message payload

    Note - uses legacy attachments: https://api.slack.com/reference/messaging/attachments.
    Should migrate to newer "blocks".

    :params parsedMessage: the parsed message with "action" detailing message type
    :returns: Slack message payload
    """

    payload = {
    }

    attachment = None
    logger.debug('Successfully parsed SNS record', parsed=parsedMessage)
    match (parsedMessage['action']):
      case "CloudWatch":
        attachment = self.__format_cloudwatch_alarm(alarm=parsedMessage)
      case "GuardDuty":
        attachment = self.__format_guard_duty_finding(finding=parsedMessage)
      case "Health":
        attachment = self.__format_health_check_alert(alert=parsedMessage)
      case "Backup":
        attachment = self.__format_backup_status(status=parsedMessage)
      case "SecurityHub":
        attachment = self.__format_security_hub_status(finding=parsedMessage)
      case "Budget":
        attachment = self.__format_budget_alert(alarm=parsedMessage)
      case "SavingsPlan":
        attachment = self.__format_savings_plan_alert(alarm=parsedMessage)
      case "DMS":
        attachment = self.__format_DMS_notification(event=parsedMessage)
      case "Unknown":
        attachment = self.__format_default(message=originalMessage, subject=subject)

    if attachment:
        payload["attachments"] = [attachment]  # type: ignore

    return payload
