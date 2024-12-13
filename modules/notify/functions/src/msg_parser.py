import array
import base64
import json
import os
import re
import urllib.parse
from datetime import datetime
from enum import Enum
from math import floor
from typing import Any, Callable, Dict, Optional, Union, cast

import boto3
from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.utilities.typing import LambdaContext

from render import Render
from ssm_param import get_parameter

logger = Logger()
powertools_namespace = os.environ["POWERTOOLS_SERVICE_NAME"]
metrics = Metrics(namespace=powertools_namespace)

# Set default region if not provided
REGION = os.environ.get("AWS_REGION", "us-east-1")

# Service URLS may, optionally, be redirect through Identity Center
IDENTITY_CENTER_URL = os.environ.get("IDENTITY_CENTER_URL", "")
IDENTITY_CENTER_ROLE = os.environ.get("IDENTITY_CENTER_ROLE", "")
# clean up URL
if IDENTITY_CENTER_URL.endswith("/"):
    IDENTITY_CENTER_URL = IDENTITY_CENTER_URL[:-1]
if IDENTITY_CENTER_URL.endswith("console"):
    IDENTITY_CENTER_URL = IDENTITY_CENTER_URL[:-8]

# Create client so its cached/frozen between invocations
KMS_CLIENT = boto3.client("kms", region_name=REGION)


def get_account_mappings() -> dict:
    try:
        parameter_arn = os.environ.get("AWS_ORGANISATIONS_ACCOUNTS_ID_TO_NAME_PARAMETER_ARN")
        if not parameter_arn:
            logger.error(
                "Missing required environment variable: AWS_ORGANISATIONS_ACCOUNTS_ID_TO_NAME_PARAMETER_ARN"
            )
            return {}

        return get_parameter(parameter_arn)
    except Exception as e:
        logger.exception(f"Error retrieving account mappings: {e}")
        return {}


ACCOUNT_ID_TO_NAME = get_account_mappings()


class AwsService(Enum):
    """AWS service supported by function"""

    cloudwatch = "cloudwatch"
    guardduty = "guardduty"
    securityhub = "securityhub"


def decrypt_url(encrypted_url: str) -> str:
    """Decrypt encrypted URL with KMS

    :param encrypted_url: URL to decrypt with KMS
    :returns: plaintext URL
    """
    try:
        decrypted_payload = KMS_CLIENT.decrypt(
            CiphertextBlob=base64.b64decode(encrypted_url)
        )
        return decrypted_payload["Plaintext"].decode()
    except Exception as e:
        raise e


def get_service_url(region: str, service: str) -> str:
    """Get the appropriate service URL for the region

    :param region: name of the AWS region - not used on a
    :param service: name of the AWS service
    :returns: AWS console url formatted for the region and service provided
    """

    try:
        service_name = AwsService[service].value
        service_url = f"{service_name}/home?region={region}"

        if region.startswith("us-gov-"):
            return f"https://console.amazonaws-us-gov.com/{service_url}"
        else:
            return f"https://console.aws.amazon.com/{service_url}"

    except KeyError:
        print(f"Service {service} is currently not supported")
        raise


def get_target_url(account_id: str, absoluteUrl: str = None) -> str:
    """Redirect via identity center if defined

    :param account_id: the originating account id to use when using Identity Center redirects
    :param absoluteUrl: if the service is "absolute", then this is the target url
    :returns: AWS console url formatted for the given URL, account & role iv via Identity Center
    """
    if len(IDENTITY_CENTER_URL) > 0 and account_id != None:
        return f"{IDENTITY_CENTER_URL}/#/console?account_id={account_id}&role_name={IDENTITY_CENTER_ROLE}&destination={urllib.parse.quote(absoluteUrl)}"
    else:
        return f"{absoluteUrl}"


class AwsAction(Enum):
    """The individual AWS service types parsed"""

    CLOUDWATCH = "CloudWatch"
    GUARDDUTY = "GuardDuty"
    HEALTH_CHECK = "Health"
    BACKUP = "Backup"
    BUDGET = "Budget"
    SAVINGS_PLAN = "SavingsPlan"
    SECURITY_HUB = "SecurityHub"
    DMS = "DMS"
    COST_ANOMALY = "CostAnomaly"
    UNKNOWN = "Unknown"


class CloudWatchAlarmPriority(Enum):
    """Maps CloudWatch notification state to a normalised priority"""

    OK = "NO_ERROR"
    INSUFFICIENT_DATA = "WARNING"
    ALARM = "ERROR"


def parse_cloudwatch_alarm(message: Dict[str, Any], snsRegion: str) -> Dict[str, Any]:
    """Parse CloudWatch alarm event into CloudWatch facts format

    :params message: SNS message body containing CloudWatch alarm event
    :snsRegion: AWS region of the SNS topic
    :returns: CloudWatch facts
    """
    action = AwsAction.CLOUDWATCH.value
    priority = CloudWatchAlarmPriority[message["NewStateValue"]].value
    name = message["AlarmName"]
    alarmRegion = message["Region"]
    at = message["StateChangeTime"]
    atDT = datetime.fromisoformat(message["StateChangeTime"])
    atEpoch = atDT.timestamp()
    description = message["AlarmDescription"]
    account_id = message["AWSAccountId"]
    account_name = ACCOUNT_ID_TO_NAME.get(account_id, "")
    reason = message["NewStateReason"]
    state = message["NewStateValue"]
    old_state = message["OldStateValue"]
    alarm_arn = message["AlarmArn"]
    alarm_arn_region = message["AlarmArn"].split(":")[3]

    cloudwatch_service_url = get_target_url(
        account_id=account_id,
        absoluteUrl=get_service_url(region=alarm_arn_region, service="cloudwatch"),
    )
    cloudwatch_url = f"{cloudwatch_service_url}#alarm:alarmFilter=ANY;name={urllib.parse.quote(name)}"

    return {
        "action": action,
        "priority": priority,
        "name": name,
        "description": description,
        "url": cloudwatch_url,
        "at": at,
        "at_epoch": floor(atEpoch),
        "account_id": account_id,
        "account_name": account_name,
        "reason": reason,
        "state": state,
        "old_state": old_state,
        "region": alarmRegion,
        "topic_region": snsRegion,
        "alarm_arn": alarm_arn,
        "alarm_arn_region": alarm_arn_region,
    }


class GuardDutylarmPriority(Enum):
    """Maps GuardDuty finding severity to normalised priority"""

    Low = "LOW"
    Medium = "MEDIUM"
    High = "HIGH"


def parse_guardduty_finding(message: Dict[str, Any], snsRegion: str) -> Dict[str, Any]:
    """
    Parse GuardDuty finding event into Slack message format

    :params message: SNS message body containing GuardDuty finding event
    :snsRegion: AWS region of the SNS topic
    :returns: formatted Slack message payload
    """

    detail = message["detail"]
    service = detail.get("service", {})
    region = message["region"]

    severity_score = detail.get("severity")
    if severity_score < 4.0:
        severity = "Low"
    elif severity_score < 7.0:
        severity = "Medium"
    else:
        severity = "High"

    priority = GuardDutylarmPriority[severity].value
    title = detail.get("title")
    description = detail["description"]
    type = detail["type"]
    first_seen = service["eventFirstSeen"]
    last_seen = service["eventLastSeen"]
    account_id = detail["accountId"]
    account_name = ACCOUNT_ID_TO_NAME.get(account_id, "")
    count = service["count"]
    guard_duty_id = detail["id"]

    guardduty_url = get_target_url(
        account_id=account_id,
        absoluteUrl=get_service_url(region=region, service="guardduty"),
    )

    atDT = datetime.fromisoformat(service["eventLastSeen"])
    atEpoch = atDT.timestamp()

    return {
        "action": AwsAction.GUARDDUTY.value,
        "priority": priority,
        "title": title,
        "description": description,
        "region": region,
        "type": type,
        "first_seen": first_seen,  # ISO timestamp
        "last_seen": last_seen,  # ISO timestamp
        "severity": severity,
        "severity_score": severity_score,
        "account_id": account_id,
        "account_name": account_name,
        "count": count,
        "url": guardduty_url,
        "id": guard_duty_id,
        "at_epoch": atEpoch,
    }


class AwsHealthCategoryPriroity(Enum):
    """Maps AWS Health eventTypeCategory to to a normalised priority"""

    accountNotification = "LOW"
    scheduledChange = "MEDIUM"
    issue = "HIGH"


def parse_aws_health(message: Dict[str, Any], snsRegion: str) -> Dict[str, Any]:
    """
    Parse AWS Health event into Slack message format

    :params message: SNS message body containing AWS Health event
    :snsRegion: AWS region of the SNS topic
    :returns: formatted Slack message payload
    """

    detail = message["detail"]
    resources = ",".join(message.setdefault("resources", ["<unknown>"]))
    service = detail.get("service", "<unknown>")
    account_id = message["account"]
    account_name = ACCOUNT_ID_TO_NAME.get(account_id, "")
    category = detail["eventTypeCategory"]
    code = detail.get("eventTypeCode")
    description = detail["eventDescription"][0]["latestDescription"]
    start_time = detail.get("startTime", "<unknown>")
    end_time = detail.get("endTime", "<unknown>")

    # the originating region for the Health Check is in the detail.eventArn
    eventArn = detail["eventArn"]
    eventRegion = eventArn.split(":")[3]
    aws_health_url = f"https://phd.aws.amazon.com/phd/home?region={eventRegion}#/dashboard/open-issues"

    priority = AwsHealthCategoryPriroity[detail["eventTypeCategory"]].value

    atDT = datetime.fromisoformat(message["time"])
    atEpoch = atDT.timestamp()

    return {
        "action": AwsAction.HEALTH_CHECK.value,
        "priority": priority,
        "description": description,
        "region": eventRegion,
        "category": category,
        "account_id": account_id,
        "account_name": account_name,
        "url": aws_health_url,
        "at_epoch": atEpoch,
        "start_time": start_time,  # Locale timestamp TZ=GMT
        "end_time": end_time,  # Locale timestamp TZ=GMT
        "code": code,
        "service": service,
        "resources": resources,
    }


def aws_backup_field_parser(message: str) -> Dict[str, str]:
    """
    Parser for AWS Backup event message. It extracts the fields and returns a dictionary.

    :params message: message containing AWS Backup string
    :returns: dictionary containing the fields extracted from the message
    """
    # Order is somewhat important, working in reverse order of the message payload
    # to reduce right most matched values
    field_names = {
        "BackupJob ID": r"(BackupJob ID : ).*",
        "Resource ARN": r"(Resource ARN : ).*[.]",
        "Recovery point ARN": r"(Recovery point ARN: ).*[.]",
    }
    fields = {}

    for fname, freg in field_names.items():
        match = re.search(freg, message)
        if match:
            value = match.group(0).split(" ")[-1]
            fields[fname] = value.removesuffix(".")

            # Remove the matched field from the message
            message = message.replace(match.group(0), "")

    return fields


class AwsBackupPriroity(Enum):
    """Maps AWS Backup status to to a normalised priority"""

    COMPLETED = "NO_ERROR"
    EXPIRED = "WARNING"
    FAILED = "ERROR"


def parse_aws_backup(message: str, messageAttributes: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse AWS Backup event into normalised facts

    :params message: SNS message body containing AWS Backup event
    :params messageAttributes: SNS message attributes containing AWS Backup additional info
    :returns: set of normalised parameters
    """

    description = message.split(".")[0]
    backup_fields = aws_backup_field_parser(message)

    start_time = messageAttributes["StartTime"]["Value"]  # ISO timestamp
    account_id = messageAttributes["AccountId"]["Value"]
    account_name = ACCOUNT_ID_TO_NAME.get(account_id, "")
    backup_id = messageAttributes["Id"]["Value"]
    status = messageAttributes["State"]["Value"]
    region = backup_fields["Resource ARN"].split(":")[3]

    priority = AwsBackupPriroity[status].value

    # note - no epoch_at because there is no timestamp when the event occured at message level
    #        or message attributes
    # atDT = datetime.fromisoformat(message["time"])
    # atEpoch = atDT.timestamp()

    return {
        "action": AwsAction.BACKUP.value,
        "priority": priority,
        "status": status,
        "region": region,
        "account_id": account_id,
        "account_name": account_name,
        "backup_id": backup_id,
        "start_time": start_time,
        "backup_fields": backup_fields,
        "description": description,
    }


def parse_aws_budget(subject: str, message: str) -> Dict[str, Any]:
    """
    Parse AWS Budget alert into normalised facts

    :params subject: SNS subject body containing AWS Budget alert
    :params message: SNS message body containing AWS Budget alert
    :returns: set of normalised parameters
    """
    subjectPrefix = len("AWS Budgets:")
    parsedSubject = subject[subjectPrefix:]

    # the message is already a formatted message using newlines for separation
    #  little to gain from parsing the message details
    return {
        "action": AwsAction.BUDGET.value,
        "subject": parsedSubject,
        "info": message,
    }


def parse_aws_savings_plan(subject: str, message: str) -> Dict[str, Any]:
    """
    Parse AWS Savings Plan alert into normalised facts

    :params subject: SNS subject body containing AWS Savings Plan alert
    :params message: SNS message body containing AWS Savings Plan alert
    :returns: set of normalised parameters
    """
    subjectPrefix = len("Savings Plans Coverage Alert:")
    parsedSubject = subject[subjectPrefix:]

    # the message is already a formatted message using newlines for separation
    #  little to gain from parsing the message details
    return {
        "action": AwsAction.SAVINGS_PLAN.value,
        "subject": parsedSubject,
        "info": message,
    }


class SecurityHubPriority(Enum):
    """Maps SecurityHub severity state to a normalised 3 level priority"""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def parse_security_hub_finding(
    message: Dict[str, Any], snsRegion: str
) -> Dict[str, Any]:
    """Format Secuirty Hub finding event into Security Hub finding facts format

    :params message: SNS message body containing Security Hub event
    :region: AWS region where the event originated from
    :returns: Security Hub facts
    """

    severity: str = message["Severity"]
    priority = SecurityHubPriority[severity].value

    # GeneratorId includes the source of the description
    source = message["GeneratorId"]
    description = message["Description"]

    """
    The format of the finding - following subscription within the ARN split by “/”:

        [0] - Provider

        [1] - always 'v'

        [2] - version

        [3] - category

        [4]  - always finding

        [5] - Rule ID

        0, 1, 2 and 3 is tge “GeneratorID”.
    """
    findingIdParts = (message["FindingId"].split(":")[5]).split("/")
    provider = findingIdParts[1]
    version = findingIdParts[3]
    category = findingIdParts[4]
    rule_id = findingIdParts[6]

    # an oversight from AWS is that none of the events include a timestamp for when the event occurred
    # at = message["StateChangeTime"]
    # atDT = datetime.fromisoformat(message["StateChangeTime"])
    # atEpoch = atDT.timestamp()

    # Security Hub event includes the account name (no need to map)
    #  but it doesn't include the account ID - take from the finding id
    account_id = message["FindingId"].split(":")[4]
    account_name = message["AccountName"]
    region = message["FindingId"].split(":")[3]

    # not done any real investigztion into the service url yet!!!!!!
    service_url = get_target_url(
        account_id=account_id,
        absoluteUrl=get_service_url(region=region, service="securityhub"),
    )
    url = f"{service_url}#findings?search=GeneratorId%3D%255Coperator%255C%253AEQUALS%255C%253A{urllib.parse.quote(source)}"

    # light touch parse on each resource
    resources: list[Dict[str, Any]] = []
    for resource in message["Resources"]:
        resources.append(
            {
                "type": resource["Type"],
                "id": resource["Id"],
            }
        )

    return {
        "action": AwsAction.SECURITY_HUB.value,
        "priority": priority,
        "severity": severity,
        "source": source,
        "description": description,
        "account_id": account_id,
        "account_name": account_name,
        "region": region,
        "ruleProvider": provider,
        "providerVersion": version,
        "providerCategory": category,
        "ruleId": rule_id,
        "resources": resources,
        "url": url,
        # "at": at,
        # "at_epoch": floor(atEpoch),
    }


def parse_dms_notification(message: Dict[str, Any], snsRegion: str) -> Dict[str, Any]:
    """Format DMS notification event into DMS Notification facts format

    :params message: SNS message body containing DMS notification event
    :snsRegion: AWS region of the SNS topic
    :returns: DMS notification facts
    """

    title = message["Event Message"]
    documentation = message["Event ID"]
    source = message["Event Source"]
    source_id = message["SourceId"]
    url = message["Identifier Link"]

    at = message["Event Time"]
    atDT = datetime.fromisoformat(at)
    atEpoch = atDT.timestamp()

    # DMS notificatoin has zero identification of the account!!!!!!
    # account_id = message["FindingId"].split(":")[4]
    # account_name = message["AccountName"]
    # region = message["FindingId"].split(":")[3]

    return {
        "action": AwsAction.DMS.value,
        "title": title,
        "source": source,
        "source_id": source_id,
        "documentation": documentation,
        "url": url,
        "at": at,
        "at_epoch": floor(atEpoch),
    }


class CostAnomalyPriority(Enum):
    """Maps Cost Anomaly severity state to a normalised 3 level priority"""

    GOOD = "GOOD"
    WARNING = "WARNING"
    ERROR = "ERROR"


def parse_cost_anomaly(message: Dict[str, Any]) -> Dict[str, Any]:
    """Format Cost Anomaly event into facts

    :params message: SNS message body containing Security Hub event
    :returns: Cost Anomaly facts
    """

    # if the anomaly current score is lower than max then it's a warning
    # if the anomaly current score is equal to max then it's an error (the current event is the max)
    anomaly_score = message["anomalyScore"]
    current_anomaly_score = anomaly_score["currentScore"]
    max_anomaly_score = anomaly_score["maxScore"]

    if current_anomaly_score < max_anomaly_score:
        priority = CostAnomalyPriority.WARNING.value
    else:
        priority = CostAnomalyPriority.ERROR.value

    # to use for the identity center style url
    originatingAccountId = message["accountId"]
    originatingUrl = message["anomalyDetailsLink"]
    url = get_target_url(account_id=originatingAccountId, absoluteUrl=originatingUrl)

    # start and end
    startedAt = message["anomalyStartDate"]
    startedAtDT = datetime.fromisoformat(startedAt)
    startedAtEpoch = startedAtDT.timestamp()
    endedAt = message["anomalyEndDate"]
    endedAtDT = datetime.fromisoformat(endedAt)
    endedAtEpoch = endedAtDT.timestamp()

    # the anomaly
    anomaly_id = message["anomalyId"]
    anomaly_dimension = message["dimensionalValue"]
    monitor_name = message["monitorName"]

    # the impact
    impact = message["impact"]
    expected_spend = impact["totalExpectedSpend"]
    actual_spend = impact["totalActualSpend"]
    total_impact = impact["totalImpact"]

    # cost anomaly includes the account id and name that originated the anomaly (linked)
    # assuming the first root cause
    rootCauses = message["rootCauses"][0]
    account_id = rootCauses["linkedAccount"]
    account_name = rootCauses["linkedAccountName"]
    region = rootCauses["region"]
    service = rootCauses["service"]
    usage = rootCauses["usageType"]

    return {
        "action": AwsAction.COST_ANOMALY.value,
        "priority": priority,
        "started": startedAt,
        "ended": endedAt,
        "anomaly_id": anomaly_id,
        "monitor_name": monitor_name,
        "expected_spend": expected_spend,
        "actual_spend": actual_spend,
        "total_impact": total_impact,
        "account_id": account_id,
        "account_name": account_name,
        "region": region,
        "service": service,
        "usage": usage,
        "url": url,
    }


class AwsParsedMessage:
    parsedMsg: Dict[str, Any]
    originalMsg: Dict[str, Any]
    actionType: str

    def __init__(
        self, parsed: Dict[str, Any], original: Dict[str, Any], actionType: str
    ) -> Any:
        self.parsedMsg = parsed
        self.originalMsg = original
        self.actionType = actionType


def get_message_payload(
    message: Union[str, Dict],
    region: str,
    messageAttributes: Dict[str, Any],
    subject: Optional[str] = None,
) -> AwsParsedMessage:
    """
    Parse notification message and format into fact based message for each expected action type

    :params message: SNS message body notification payload
    :params region: AWS region where the SNS event originated from
    :params subject: Optional subject line from SNS message
    :returns: facts dictionary object ("action" given the fact type)
    """

    if isinstance(message, str):
        try:
            message = json.loads(message)
        except json.JSONDecodeError:
            pass

    message = cast(Dict[str, Any], message)

    # to handle manual posting of messages via SNS, handle the case where subject is not defined
    if subject == None:
        subject = ""

    if "AlarmName" in message:
        parsedMsg = parse_cloudwatch_alarm(message, snsRegion=region)

    elif subject == "Security Hub Finding":
        parsedMsg = parse_security_hub_finding(message=message, snsRegion=region)

    elif subject == "DMS Notification Message":
        parsedMsg = parse_dms_notification(message=message, snsRegion=region)

    elif (
        isinstance(message, Dict) and message.get("detail-type") == "GuardDuty Finding"
    ):
        parsedMsg = parse_guardduty_finding(message=message, snsRegion=region)

    elif isinstance(message, Dict) and message.get("detail-type") == "AWS Health Event":
        parsedMsg = parse_aws_health(message=message, snsRegion=region)

    elif subject == "Notification from AWS Backup":
        parsedMsg = parse_aws_backup(
            message=str(message), messageAttributes=messageAttributes
        )

    elif subject.startswith("AWS Budgets:"):
        parsedMsg = parse_aws_budget(subject=subject, message=str(message))

    elif subject.startswith("Savings Plans Coverage Alert:"):
        parsedMsg = parse_aws_savings_plan(subject=subject, message=str(message))

    elif subject.startswith("AWS Cost Management:"):
        parsedMsg = parse_cost_anomaly(message=message)

    else:
        parsedMsg = {
            "action": AwsAction.UNKNOWN.value,
        }

    metricType = parsedMsg["action"]
    metrics.add_metric(name=f"{metricType}", unit=MetricUnit.Count, value=1)

    return AwsParsedMessage(
        parsed=parsedMsg, original=message, actionType=parsedMsg["action"]
    )


def parse_sns(
    snsRecords: Union[str, Dict],
    vendor_send_to_function: Callable,
    renderer: Render,
    rendererSuccessCode: int,
) -> bool:
    is_no_error = True

    logger.debug("Number of SNS records", num_records=len(snsRecords))

    for record in snsRecords:
        sns = record["Sns"]
        subject = sns["Subject"]
        message = sns["Message"]
        region = sns["TopicArn"].split(":")[3]
        messageAttributes = sns["MessageAttributes"]

        parserResults = get_message_payload(
            message=message,
            region=region,
            messageAttributes=messageAttributes,
            subject=subject,
        )

        if parserResults.actionType == AwsAction.UNKNOWN.value:
            logger.warning(
                "Unexpected event type",
                record=record,
            )

        payload = renderer.payload(
            parsedMessage=parserResults.parsedMsg,
            originalMessage=parserResults.originalMsg,
            subject=subject,
        )
        response = vendor_send_to_function(payload=payload)

        response_code = json.loads(response)["code"]
        if response_code != rendererSuccessCode:
            is_no_error = False
            response_info = json.loads(response)["info"]
            logger.error(
                "Unexpected vendor response",
                code={"expected": rendererSuccessCode, "received": response_code},
                info=response_info,
                record=record,
            )

    return is_no_error
