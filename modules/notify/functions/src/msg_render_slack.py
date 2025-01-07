import json
from enum import Enum
from typing import Any, Dict, Optional, Self, Union

from aws_lambda_powertools import Logger

logger = Logger()

from notification_emblems import __ATTENTION_URL__, __WARNING_URL__
from render import Render

"""
Using Slack legacy webhook posts format: https://api.slack.com/reference/messaging/attachments.
Teams supports embebbing base64 encoded data within image URL. Slack however does not. And it's "image_url"
 property cannot be used to control the size of the icon.
With legacy format, continuing to use attachment colour bar.
"""


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
    CRITICAL = "danger"


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
        imageIconItems = []
        if alarm["priority"] == "ERROR":
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[alarm["priority"]].value,
                    "image_url": __ATTENTION_URL__,
                    "title": f"CloudWatch: {alarm['name']}",
                    "title_link": f"{alarm['url']}",
                }
            )
        elif alarm["priority"] == "WARNING":
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[alarm["priority"]].value,
                    "image_url": __WARNING_URL__,
                    "title": f"CloudWatch: {alarm['name']}",
                    "title_link": f"{alarm['url']}",
                }
            )
        else:
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[alarm["priority"]].value,
                    "title": f"CloudWatch: {alarm['name']}",
                    "title_link": f"{alarm['url']}",
                }
            )

        return imageIconItems + [
            {
                "color": SlackPriorityColor[alarm["priority"]].value,
                "fallback": "Alarm %s triggered" % (alarm["name"]),
                "text": f"{alarm['description']}",
                "ts": alarm["at_epoch"],
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
                        "title": "Current State",
                        "value": f"`{alarm['state']}`",
                        "short": True,
                    },
                    {
                        "title": "Old State",
                        "value": f"`{alarm['old_state']}`",
                        "short": True,
                    },
                ],
            }
        ]

    def __format_guard_duty_finding(
        self: Self, finding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format GuardDuty alarm facts into Slack message format

        :params message: GuardDuty facts
        :returns: formatted Slack message payload
        """
        imageIconItems = []
        if finding["priority"] == "HIGH":
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[finding["priority"]].value,
                    "image_url": __ATTENTION_URL__,
                    "title": f"GuardDuty: {finding['title']}",
                    "title_link": f"{finding['url']}#/findings?search=id%3D{finding['id']}",
                }
            )
        elif finding["priority"] == "MEDIUM":
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[finding["priority"]].value,
                    "image_url": __WARNING_URL__,
                    "title": f"GuardDuty: {finding['title']}",
                    "title_link": f"{finding['url']}#/findings?search=id%3D{finding['id']}",
                }
            )
        else:
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[finding["priority"]].value,
                    "title": f"GuardDuty: {finding['title']}",
                    "title_link": f"{finding['url']}#/findings?search=id%3D{finding['id']}",
                }
            )

        return imageIconItems + [
            {
                "color": SlackPriorityColor[finding["priority"]].value,
                "fallback": f"GuardDuty Finding: {finding['title']}",
                "text": f"{finding['description']}",
                "ts": finding["at_epoch"],
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
                        "title": "Severity/Score",
                        "value": f"`{finding['severity']}/{finding['severity_score']}`",
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
                ],
            }
        ]

    def __format_health_check_alert(
        self: Self, alert: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format AWS Healthcheck facts into Slack message format

        :params message: HealthCheck facts
        :returns: formatted Slack message payload
        """
        imageIconItems = []
        if alert["priority"] == "HIGH":
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[alert["priority"]].value,
                    "image_url": __ATTENTION_URL__,
                    "title": f"AWS Health: {alert['service']}",
                    "title_link": f"{alert['url']}",
                }
            )
        elif alert["priority"] == "MEDIUM":
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[alert["priority"]].value,
                    "image_url": __WARNING_URL__,
                    "title": f"AWS Health: {alert['service']}",
                    "title_link": f"{alert['url']}",
                }
            )
        else:
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[alert["priority"]].value,
                    "title": f"AWS Health: {alert['service']}",
                    "title_link": f"{alert['url']}",
                }
            )

        return imageIconItems + [
            {
                "color": SlackPriorityColor[alert["priority"]].value,
                "fallback": f"New AWS Health Event for {alert['service']}",
                "text": f"{alert['description']}",
                "ts": alert["at_epoch"],
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
        ]

    def __format_backup_status(self: Self, status: Dict[str, Any]) -> Dict[str, Any]:
        """Format AWS Backup facts into teams message format

        :params finding: Backup facts
        :returns: formatted teams message payload
        """
        imageIconItems = []
        if status["priority"] == "ERROR":
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[status["priority"]].value,
                    "image_url": __ATTENTION_URL__,
                    "title": f"Backup : {status['backup_id']}",
                    # "title_link": f"{status['url']}",
                }
            )
        elif status["priority"] == "WARNING":
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[status["priority"]].value,
                    "image_url": __WARNING_URL__,
                    "title": f"Backup : {status['backup_id']}",
                    # "title_link": f"{status['url']}",
                }
            )
        else:
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[status["priority"]].value,
                    "title": f"Backup : {status['backup_id']}",
                    # "title_link": f"{status['url']}",
                }
            )

        fields: list[Dict[str, Any]] = []
        backup_fields = status["backup_fields"]
        for k, v in backup_fields.items():
            fields.append(
                {
                    "title": k,
                    "value": f"`{v}`",
                    "short": False,
                }
            )

        return imageIconItems + [
            {
                "color": SlackPriorityColor[status["priority"]].value,
                "fallback": f"Backup event for {status['backup_id']}",
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
                ]
                + fields,
            }
        ]

    def __format_security_hub_status(
        self: Self, finding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format Security Hub finding  facts into Slack message format

        :params finding: Security Hub facts
        :returns: formatted Slack message payload
        """
        imageIconItems = []
        if finding["priority"] == "CRITICAL" or finding["priority"] == "HIGH":
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[finding["priority"]].value,
                    "image_url": __ATTENTION_URL__,
                    "title": f"Security Hub: {finding['source']}",
                    "title_link": f"{finding['url']}",
                }
            )
        elif finding["priority"] == "MEDIUM":
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[finding["priority"]].value,
                    "image_url": __WARNING_URL__,
                    "title": f"Security Hub: {finding['source']}",
                    "title_link": f"{finding['url']}",
                }
            )
        else:
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[finding["priority"]].value,
                    "title": f"Security Hub: {finding['source']}",
                    "title_link": f"{finding['url']}",
                }
            )

        resourcesField: list[Dict[str, Any]] = []
        idx = 1
        for resource in finding["resources"]:
            resourceId = resource["id"]
            resourceType = resource["type"]
            resourcesField.append(
                {
                    "title": f"Type {idx}",
                    "value": f"`{resourceType}`",
                    "short": True,
                }
            )
            resourcesField.append(
                {
                    "title": f"Arn {idx}",
                    "value": f"`{resourceId}`",
                    "short": False,
                }
            )
            idx += 1

        return imageIconItems + [
            {
                "color": SlackPriorityColor[finding["priority"]].value,
                "fallback": "Security Hub finding %s triggered" % (finding["source"]),
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
                        "short": True,
                    },
                    {
                        "title": "Severity",
                        "value": f"`{finding['severity']}`",
                        "short": True,
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
                ]
                + resourcesField,
            }
        ]

    def __format_budget_alert(self: Self, alarm: Dict[str, Any]) -> Dict[str, Any]:
        """Format Budget alarm facts into Slack message format

        :params message: Budget facts
        :returns: formatted Slack message payload
        """
        return [
            {
                "color": SlackPriorityColor.HIGH.value,
                "image_url": __WARNING_URL__,
                "title": f"Budget: {alarm['subject']}",
            },
            {
                "color": SlackPriorityColor.HIGH.value,
                "fallback": "Budget %s triggered" % (alarm["subject"]),
                "mrkdwn_in": ["value"],
                "fields": [
                    {
                        "value": f"{alarm['info']}",
                        "short": False,
                    }
                ],
            },
        ]

    def __format_savings_plan_alert(
        self: Self, alarm: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format Savings Plan alarm facts into Slack message format

        :params message: Savings Plans facts
        :returns: formatted Slack message payload
        """
        return [
            {
                "color": SlackPriorityColor.HIGH.value,
                "image_url": __WARNING_URL__,
                "title": f"Savings Plan: {alarm['subject']}",
            },
            {
                "color": SlackPriorityColor.HIGH.value,
                "fallback": "Savings Plan %s triggered" % (alarm["subject"]),
                "mrkdwn_in": ["value"],
                "fields": [
                    {
                        "value": f"{alarm['info']}",
                        "short": False,
                    }
                ],
            },
        ]

    def __format_DMS_notification(self: Self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format DMS notification facts into Slack message format

        :params message: DMS notificatoin facts
        :returns: formatted Slack message payload
        """
        return [
            {
                "color": SlackPriorityColor.WARNING.value,
                "fallback": "DMS Notification %s triggered" % (event["title"]),
                "title": f"DMS Notification: {event['title']}",
                "title_link": f"{event['url']}",
                "text": f"{event['documentation']}",
                "ts": event["at_epoch"],
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
                    },
                ],
            }
        ]

    def __format_cost_anomaly(self: Self, anomaly: Dict[str, Any]) -> Dict[str, Any]:
        """Format Costing Anomaly facts into slack message format

        :params anomaly: cost anomaly facts
        :returns: formatted slack message payload
        """
        imageIconItems = []
        if anomaly["priority"] == "ERROR":
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[anomaly["priority"]].value,
                    "image_url": __ATTENTION_URL__,
                    "title": f"Cost Anomaly: {anomaly['usage']}",
                    "title_link": f"{anomaly['url']}",
                }
            )
        elif anomaly["priority"] == "WARNING":
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[anomaly["priority"]].value,
                    "image_url": __WARNING_URL__,
                    "title": f"Cost Anomaly: {anomaly['usage']}",
                    "title_link": f"{anomaly['url']}",
                }
            )
        else:
            imageIconItems.append(
                {
                    "color": SlackPriorityColor[anomaly["priority"]].value,
                    "title": f"Cost Anomaly: {anomaly['usage']}",
                    "title_link": f"{anomaly['url']}",
                }
            )

        return imageIconItems + [
            {
                "color": SlackPriorityColor[anomaly["priority"]].value,
                "fallback": "Cost Anomaly:  %s triggered" % (anomaly["usage"]),
                "text": f"{anomaly['monitor_name']}",
                # "ts": alarm['at_epoch'],
                "fields": [
                    {
                        "title": "Account Name",
                        "value": f"`{anomaly['account_name']}`",
                        "short": True,
                    },
                    {
                        "title": "Account ID",
                        "value": f"`{anomaly['account_id']}`",
                        "short": True,
                    },
                    {
                        "title": "Region",
                        "value": f"`{anomaly['region']}`",
                        "short": True,
                    },
                    {
                        "title": "Service",
                        "value": f"`{anomaly['service']}`",
                        "short": True,
                    },
                    {
                        "title": "Started At",
                        "value": f"`{anomaly['started']}`",
                        "short": True,
                    },
                    {
                        "title": "Ended At",
                        "value": f"`{anomaly['ended']}`",
                        "short": True,
                    },
                    {
                        "title": "Expended Spend ($)",
                        "value": f"`{anomaly['expected_spend']}`",
                        "short": True,
                    },
                    {
                        "title": "Actual Spend ($)",
                        "value": f"`{anomaly['actual_spend']}`",
                        "short": True,
                    },
                    {
                        "title": "Impact",
                        "value": f"`{anomaly['total_impact']}`",
                        "short": True,
                    },
                    {
                        "title": "ID",
                        "value": f"`{anomaly['anomaly_id']}`",
                        "short": False,
                    },
                ],
            }
        ]

    def __format_default(
        self: Self, message: Union[str, Dict], subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Default formatter, converting event into Slack message format

        :params message: SNS message body containing message/event
        :returns: formatted Slack message payload
        """

        attachment = {
            "fallback": "A new message",
            "text": "AWS notification",
            "title": subject if subject else "Message",
            "mrkdwn_in": ["value"],
        }
        fields = []

        if type(message) is dict:
            for k, v in message.items():
                value = f"{json.dumps(v)}" if isinstance(v, (dict, list)) else str(v)
                fields.append(
                    {"title": k, "value": f"`{value}`", "short": len(value) < 25}
                )
        else:
            fields.append({"value": message, "short": False})

        if fields:
            attachment["fields"] = fields  # type: ignore

        return [attachment]

    def payload(
        self: Self,
        parsedMessage: Union[str, Dict],
        originalMessage: Union[str, Dict],
        subject: Optional[str] = None,
    ) -> Dict:
        """
        Given the parsed AWS message, format into Slack message payload

        Note - uses legacy attachments: https://api.slack.com/reference/messaging/attachments.
        Should migrate to newer "blocks".

        :params parsedMessage: the parsed message with "action" detailing message type
        :returns: Slack message payload
        """

        payload = {}

        attachments = None
        logger.debug("Successfully parsed SNS record", parsed=parsedMessage)
        match (parsedMessage["action"]):
            case "CloudWatch":
                attachments = self.__format_cloudwatch_alarm(alarm=parsedMessage)
            case "GuardDuty":
                attachments = self.__format_guard_duty_finding(finding=parsedMessage)
            case "Health":
                attachments = self.__format_health_check_alert(alert=parsedMessage)
            case "Backup":
                attachments = self.__format_backup_status(status=parsedMessage)
            case "SecurityHub":
                attachments = self.__format_security_hub_status(finding=parsedMessage)
            case "Budget":
                attachments = self.__format_budget_alert(alarm=parsedMessage)
            case "SavingsPlan":
                attachments = self.__format_savings_plan_alert(alarm=parsedMessage)
            case "DMS":
                attachments = self.__format_DMS_notification(event=parsedMessage)
            case "CostAnomaly":
                attachments = self.__format_cost_anomaly(anomaly=parsedMessage)
            case "Unknown":
                attachments = self.__format_default(
                    message=originalMessage, subject=subject
                )

        if attachments:
            payload["attachments"] = attachments  # type: ignore

        return payload
