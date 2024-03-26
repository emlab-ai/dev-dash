import json
import logging

from azure.functions import EventHubEvent
from typing import List
from ..services.githubService import GithubService

def main(events: List[EventHubEvent]):
    githubService = GithubService()
    for event in events:
        try:
            bodyStr = event.get_body().decode('utf-8')
            logging.info('Python EventHub trigger processed an event: %s', bodyStr)
            body = json.loads(bodyStr)
            
            githubService.process_event(body["event_type"], body["delivery_id"], body["installation_target_type"], body["installation_target_id"], body["data"])
        
        except Exception as e:
            logging.error('Error processing event: %s', e)
            pass
