from webexteamssdk import WebexTeamsAPI

WEBEX_TOKEN = "YzYxZjg2N2UtNTZmNi00YzhkLTgzOWUtZmRjZGQ1YWUxN2M3NmIwOGZiODAtZGZh_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f"
WEBEX_ROOM_ID = "Y2lzY29zcGFyazovL3VzL1JPT00vNTVlODM2MjAtMDBjZC0xMWVjLWE5NGEtOTE0MWYxY2FlM2M5"

# webex API instance
webexAPI = WebexTeamsAPI(access_token=WEBEX_TOKEN)

# mock data
mv_loc = "Warehouse"
snapshot_url = "https://safetyskills.com/wp-content/uploads/2020/11/Head-Face-and-Eye-Protection.jpeg"
people_count = "1"
detected_name = "Bob"
missing_ppe = "Gloves, Mask"
event_time = "19-Aug-2021 (10:10)"

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
                            "text": "Location:",
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
def postCard_ppeViolation(mv_loc, snapshot_url, people_count, detected_name, missing_ppe, event_time, room_id):

    iconUrl = "https://raw.githubusercontent.com/mfakbar/meraki-ppe-detection/main/IMAGES/warning_notification.png"

    # payload parameter
    CARD_CONTENT["body"][0]["columns"][0]["items"][0]["url"] = iconUrl
    CARD_CONTENT["body"][0]["columns"][1]["items"][1]["text"] = "PPE VIOLATION DETECTED"
    CARD_CONTENT["body"][0]["columns"][1]["items"][1]["color"] = "Attention"
    CARD_CONTENT["body"][1]["columns"][1]["items"][0][
        "text"] = '[' + mv_loc + '](' + snapshot_url + ')'
    CARD_CONTENT["body"][1]["columns"][1]["items"][1]["text"] = people_count
    CARD_CONTENT["body"][1]["columns"][1]["items"][2]["text"] = detected_name
    CARD_CONTENT["body"][1]["columns"][1]["items"][3]["text"] = missing_ppe
    CARD_CONTENT["body"][1]["columns"][1]["items"][4]["text"] = event_time
    CARD_CONTENT["body"][2]["url"] = snapshot_url

    webexAPI.messages.create(
        roomId=room_id,
        text="If you see this your client cannot render Webex adaptive cards",
        attachments=[{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": CARD_CONTENT
        }]
    )
    print("Card posted!")


postCard_ppeViolation(mv_loc, snapshot_url, people_count,
                      detected_name, missing_ppe, event_time, WEBEX_ROOM_ID)
