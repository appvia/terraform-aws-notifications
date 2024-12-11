import os
import json
import urllib3
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_parameter(parameter_arn):
    """
    Retrieve a parameter from AWS Systems Manager Parameter Store using the Lambda extension

    Args:
        parameter_arn (str): The ARN of the parameter to retrieve

    Returns:
        dict: Parameter value and metadata if successful, error details if unsuccessful
    """
    http = urllib3.PoolManager()

    session_token = os.environ['AWS_SESSION_TOKEN']

    headers = {
        'X-Aws-Parameters-Secrets-Token': session_token
    }

    endpoint = f"http://localhost:2773/systemsmanager/parameters/get?name={parameter_arn}"

    try:
        logger.info(f"Attempting to retrieve parameter with ARN: {parameter_arn}")
        response = http.request('GET', endpoint, headers=headers)

        if response.status == 200:
            parameter_data = json.loads(response.data.decode('utf-8'))
            return {
                'success': True,
                'value': parameter_data['Parameter']['Value'],
                'arn': parameter_arn
            }
        else:
            error_message = response.data.decode('utf-8')
            logger.error(f"Failed to retrieve parameter. Status: {response.status}, Error: {error_message}")
            return {
                'success': False,
                'error': error_message,
                'status_code': response.status
            }

    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'status_code': 500
        }

def test_parameter_access(parameter_arn):
    """
    Test direct access to a parameter using boto3

    Args:
        parameter_arn (str): The ARN of the parameter to test

    Returns:
        bool: True if parameter is accessible, False otherwise
    """
    try:
        import boto3
        ssm = boto3.client('ssm')
        response = ssm.get_parameter(
            Name=parameter_arn,
            WithDecryption=True
        )
        logger.info(f"Direct SSM access successful: {response['Parameter']['Name']}")
        return True
    except Exception as e:
        logger.error(f"Direct SSM access failed: {str(e)}")
        return False

