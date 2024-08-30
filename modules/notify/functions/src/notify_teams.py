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

from msg_parser import parse_sns, decrypt_url
from msg_render_teams import TeamsRender
from render import Render

LOG_EVENTS = True if os.environ.get("LOG_EVENTS", "False") == "True" else False

def send_teams_notification(payload: Dict[str, Any]) -> str:
  """
  Send notification payload to teams

  :params payload: formatted teams message payload
  :returns: { code: integer, info: string}
  """
  teams_url = os.environ["TEAMS_WEBHOOK_URL"]
  if not teams_url.startswith("http"):
    teams_url = decrypt_url(teams_url)
  
  if LOG_EVENTS == True:
    logging.info(f"XTRA: Event logging enabled (teams payload) to {teams_url}: `{payload}`")

  req = Request(teams_url, json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
  try:
    response = urlopen(req)
    response.read()
    logging.info(f"Message posted: code({response.getcode()})")
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

    if LOG_EVENTS == True:
      logging.info(f"XTRA: Event logging enabled (Event): `{json.dumps(event)}`")

    renderer: Render = TeamsRender(
      logExtra=LOG_EVENTS
    )

    # Teams will return HTTP(202) on success - or will it?
    parse_sns_status: bool = parse_sns(
      event["Records"],
      send_teams_notification,
      renderer,
      202,
      logExtra=LOG_EVENTS
    )
    if not parse_sns_status:
      logging.error(
        f"Error: processing event `{event}` and context `{context}`"
      )
      raise Exception('Failed to process all SNS records')
    
    return {}
