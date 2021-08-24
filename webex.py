import os
from dotenv import load_dotenv
from webexteamssdk import WebexTeamsAPI

# load Webex credentials
load_dotenv()
WEBEX_TOKEN = os.getenv('WEBEX_TOKEN')
WEBEX_ROOM_ID = os.getenv('WEBEX_ROOM_ID')

# webex API instance
webexAPI = WebexTeamsAPI(access_token=WEBEX_TOKEN)

# webex card payload
CARD_CONTENT = {
    "type": "AdaptiveCard",
    "body": [
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "Image",
                            "url": "Icon image url",  # parameter
                            "size": "Medium",
                            "height": "50px",
                            "backgroundColor": "White"
                        }
                    ],
                    "width": "auto"
                },
                {
                    "type": "Column",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Meraki PPE Detection",
                            "color": "Good",
                            "size": "Small",
                            "weight": "Lighter"
                        },
                        {
                            "type": "TextBlock",
                            "text": "PPE Violation Detected",  # parameter
                            "wrap": True,
                            "color": "Attention",  # parameter
                            "size": "Medium",
                            "spacing": "Small",
                            "weight": "Bolder"
                        }
                    ],
                    "width": "stretch"
                }
            ]
        },
        {
            "type": "ColumnSet",
            "columns": [
                {
                    "type": "Column",
                    "width": 35,
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Location / Cam ID:",
                            "color": "Light"
                        },
                        {
                            "type": "TextBlock",
                            "text": "People count:",
                            "weight": "Lighter",
                            "color": "Light",
                            "spacing": "Small"
                        },
                        {
                            "type": "TextBlock",
                            "text": "Detected names:",
                            "weight": "Lighter",
                            "color": "Light",
                            "spacing": "Small"
                        },
                        {
                            "type": "TextBlock",
                            "text": "Missing PPE:",
                            "weight": "Lighter",
                            "color": "Light",
                            "spacing": "Small"
                        },
                        {
                            "type": "TextBlock",
                            "text": "Date / Time:",
                            "weight": "Lighter",
                            "color": "Light",
                            "spacing": "Small"
                        }
                    ]
                },
                {
                    "type": "Column",
                    "width": 65,
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "Warehouse",  # parameter
                            "color": "Light"
                        },
                        {
                            "type": "TextBlock",
                            "text": "1",  # parameter
                            "color": "Light",
                            "weight": "Lighter",
                            "spacing": "Small"
                        },
                        {
                            "type": "TextBlock",
                            "text": "Bob",  # parameter
                            "color": "Light",
                            "weight": "Lighter",
                            "spacing": "Small"
                        },
                        {
                            "type": "TextBlock",
                            "text": "Facemask, Gloves",  # parameter
                            "weight": "Lighter",
                            "color": "Light",
                            "spacing": "Small"
                        },
                        {
                            "type": "TextBlock",
                            "text": "19 Aug 2021 10.00",  # parameter
                            "weight": "Lighter",
                            "color": "Light",
                            "spacing": "Small"
                        }
                    ]
                }
            ],
            "spacing": "Padding",
            "horizontalAlignment": "Center"
        },
        {
            "type": "Image",
            "url": "image_url"  # parameter
        },
    ],
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "version": "1.2"
}


# post webex card as notification
def post_card(mv_loc, snapshot_url, person_count, detected_name, missing_ppe, event_time):

    iconUrl = "https://raw.githubusercontent.com/mfakbar/meraki-ppe-detection/main/IMAGES/warning_notification.png"

    # payload parameter
    CARD_CONTENT["body"][0]["columns"][0]["items"][0]["url"] = iconUrl
    CARD_CONTENT["body"][0]["columns"][1]["items"][1]["text"] = "PPE VIOLATION DETECTED"
    CARD_CONTENT["body"][0]["columns"][1]["items"][1]["color"] = "Attention"
    CARD_CONTENT["body"][1]["columns"][1]["items"][0][
        "text"] = '[' + mv_loc + '](' + snapshot_url + ')'
    CARD_CONTENT["body"][1]["columns"][1]["items"][1]["text"] = person_count
    CARD_CONTENT["body"][1]["columns"][1]["items"][2]["text"] = detected_name
    CARD_CONTENT["body"][1]["columns"][1]["items"][3]["text"] = missing_ppe
    CARD_CONTENT["body"][1]["columns"][1]["items"][4]["text"] = event_time
    CARD_CONTENT["body"][2]["url"] = snapshot_url

    webexAPI.messages.create(
        roomId=WEBEX_ROOM_ID,
        text="If you see this your client cannot render Webex adaptive cards",
        attachments=[{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": CARD_CONTENT
        }]
    )
    print("Card posted!")


# post webex notification to the employee
def post_message(mv_loc, detected_email, event_time):
    webexAPI.messages.create(
        toPersonEmail=detected_email,
        text="Hello there, we have detected that you're not wearing one or more PPE at " +
        mv_loc + " (" + event_time +
        "). Your safety is our top priority. Please follow the PPE policy accordingly. Thanks!",
    )
    print("Message posted!")
