# -*- coding: utf-8 -*-
"""
    Notify Slack
    ------------

    Receives event payloads that are parsed and sent to Slack

"""

import json
import logging
import os
import urllib.parse
import urllib.request
from enum import Enum
from typing import Any, Dict, Optional, Union, cast
from urllib.error import HTTPError

import msgParser

class SlackPriorityColor(Enum):
    """Maps Aws  notification state to Slack message format color"""

    NO_ERROR = "good"
    LOW = "#777777"
    ADVISORY = "#777777"
    WARNING = "warning"
    MEDIUM = "warning"
    ERROR = "danger"
    HIGH = "danger"

def format_cloudwatch_alarm(alarm: Dict[str, Any]) -> Dict[str, Any]:
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

def format_guard_duty_finding(finding: Dict[str, Any]) -> Dict[str, Any]:
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
                "title": "Account ID",
                "value": f"`{finding['account_id']}`",
                "short": True,
            },
            {
                "title": "Count",
                "value": f"`{finding['count']}`",
                "short": True,
            },
            {
                "title": "Region",
                "value": f"`{finding['region']}`",
                "short": True,
            },
        ]
    }

def format_health_check_alert(alert: Dict[str, Any]) -> Dict[str, Any]:
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
                "title": "Account Id",
                "value": f"`{alert['account_id']}`",
                "short": True,
            },
            {
                "title": "Category",
                "value": f"`{alert['category']}`",
                "short": True,
            },
            {
                "title": "Region",
                "value": f"`{alert['region']}`",
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
                "title": "Affected Resources",
                "value": f"{alert['resources']}",
                "short": False,
            },
        ],
    }

def format_backup_status(status: Dict[str, Any]) -> Dict[str, Any]:
    """Format AWS Backup facts into teams message format

    :params finding: Backup facts
    :returns: formatted teams message payload
    """

    logging.info(f"WA DEBUG: format_backup_status: {status}")

    fields: list[Dict[str, Any]] = []
    backup_fields = status['backup_fields']
    for k, v in backup_fields.items():
        # fields.append({"value": k, "short": False})
        # fields.append({"value": f"`{v}`", "short": False})
        fields.append({
            "title": k,
            "value": f"`{v}`",
            "short": False,
        })

    logging.info(f"WA DEBUG format_backup_status the parsed fields: {fields}")

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
                "title": "Region",
                "value": f"`{status['region']}`",
                "short": True,
            },
            {
                "title": "Priority",
                "value": f"`{status['priority']}`",
                "short": True,
            },
            {
                "title": "Start Time",
                "value": f"`{status['start_time']}`",
                "short": False,
            },
        ] + fields,
    }

def format_default(
    message: Union[str, Dict], subject: Optional[str] = None
) -> Dict[str, Any]:
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

def get_slack_message_payload(
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

    slack_channel = os.environ["SLACK_CHANNEL"]
    slack_username = os.environ["SLACK_USERNAME"]
    slack_emoji = os.environ["SLACK_EMOJI"]

    payload = {
        "channel": slack_channel,
        "username": slack_username,
        "icon_emoji": slack_emoji,
    }

    attachment = None
    match (parsedMessage['action']):
        case "cloudwatch":
            attachment = format_cloudwatch_alarm(alarm=parsedMessage)
        case "guardduty":
            attachment = format_guard_duty_finding(finding=parsedMessage)
        case "health":
            attachment = format_health_check_alert(alert=parsedMessage)
        case "backup":
            attachment = format_backup_status(status=parsedMessage)
        case "unknown":
            attachment = format_default(message=originalMessage, subject=subject)

    if attachment:
        payload["attachments"] = [attachment]  # type: ignore

    return payload


def send_slack_notification(payload: Dict[str, Any]) -> str:
    """
    Send notification payload to Slack

    :params payload: formatted Slack message payload
    :returns: response details from sending notification
    """

    slack_url = os.environ["SLACK_WEBHOOK_URL"]
    if not slack_url.startswith("http"):
        slack_url = msgParser.decrypt_url(slack_url)

    data = urllib.parse.urlencode({"payload": json.dumps(payload)}).encode("utf-8")
    req = urllib.request.Request(slack_url)

    if os.environ.get("LOG_EVENTS", "False") == "True":
        logging.info(f"Event logging enabled (slack payload): `{json.dumps(payload)}`")

    try:
        result = urllib.request.urlopen(req, data)
        return json.dumps({"code": result.getcode(), "info": result.info().as_string()})

    except HTTPError as e:
        logging.error(f"{e}: result")
        return json.dumps({"code": e.getcode(), "info": e.info().as_string()})


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Lambda function to parse notification events and forward to Slack

    :param event: lambda expected event object
    :param context: lambda expected context object
    :returns: none
    """

    if os.environ.get("LOG_EVENTS", "False") == "True":
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
            subject=subject
        )
        payload = get_slack_message_payload(
            parsedMessage=parserResults.parsedMsg,
            originalMessage=message,
            subject=subject,
        )
        response = send_slack_notification(payload=payload)

    if json.loads(response)["code"] != 200:
        response_info = json.loads(response)["info"]
        logging.error(
            f"Error: received status `{response_info}` using event `{event}` and context `{context}`"
        )


#    return response
