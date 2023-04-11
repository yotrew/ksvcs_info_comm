import requests,json
CHANNEL_ACCESS_TOKEN="CHANNEL_ACCESS_TOKEN"
TelegramBotAPI = "https://api.telegram.org/bot" + CHANNEL_ACCESS_TOKEN + "/"; 

def TG_MSG2USER(msg,chat_id = "your chat id"):
    global keyboard
    payload= { "chat_id": chat_id,  "text": msg}

    url=TelegramBotAPI + "sendMessage"
    r=requests.post(url,data=payload)

