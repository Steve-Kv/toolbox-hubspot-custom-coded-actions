import os
import requests
from datetime import datetime

def main(event):
    # Get deal ID from the enrolled object
    deal_id = event["object"]["objectId"]

    # Get additional hubspot deal record values from input fields
    sms_sent_received_date_time = event.get("inputFields", {}).get("sms_sent_received_date_time")
    sms_sent_received_message = event.get("inputFields", {}).get("sms_sent_received_message")
    hubspot_owner_id = event.get("inputFields", {}).get("hubspot_owner_id")
    contact_hs_object_id = event.get("inputFields", {}).get("contact_hs_object_id")

    
    
    # Build the communication body based on input fields
		communication_body = ""

		if sms_sent_received_message:
			formatted_message_body = sms_sent_received_message.replace("\n", "<br>")
			communication_body += f"<p><strong>SMS message:</strong><br>{formatted_message_body}</p>"
		else:
			communication_body += "<p>No message body was provided.</p>"
		
		if not contact_hs_object_id:
			communication_body += (
				"<p><em>There was an issue and this activity wasn't also logged against the associated primary contact record</em></p>"
			)

      
      
    # Get the private app token from environment variables
    access_token = os.getenv("cca_activities")

    # HubSpot API endpoint
    url = "https://api.hubapi.com/crm/v3/objects/communications"

    # Headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Payload for the SMS communication
    payload = {
        "properties": {
            "hs_communication_channel_type": "SMS",
            "hs_communication_body": communication_body,
            "hs_communication_logged_from": "CRM",
            "hs_timestamp": sms_sent_received_date_time,
          	"hubspot_owner_id": hubspot_owner_id
        },
        "associations": [
    {
        "to": {"id": str(deal_id)},
        "types": [{
            "associationCategory": "HUBSPOT_DEFINED",
            "associationTypeId": 85  # Communication-to-Deal
        }]
    }
        ] + (
          [{
            "to": {"id": str(contact_hs_object_id)},
            "types": [{
              "associationCategory": "HUBSPOT_DEFINED",
              "associationTypeId": 81  # Communication-to-Contact
            }]
          }] if contact_hs_object_id else []
        )
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=payload)

    # Handle errors
    if response.status_code >= 400:
        raise Exception(f"HubSpot API error: {response.status_code} - {response.text}")

    # Return communication ID
    return {
        "status": "SMS communication logged",
        "communicationId": response.json().get("id")
    }
