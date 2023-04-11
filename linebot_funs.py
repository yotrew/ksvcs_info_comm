import json
from flask import Flask, render_template, request
from linebot import ( LineBotApi, WebhookHandler)
#引入所有LINE的event
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)

from telegram_bot import TG_MSG2USER
import config
APP_NAME=config.APP_NAME
import datetime
line_bot_api= LineBotApi('Channel access token')
handler = WebhookHandler('Channel secret')

col_code=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']

#try:
#    gc
#except NameError:#Ref:https://stackoverflow.com/questions/1592565/determine-if-variable-is-defined-in-python
import pygsheets
import pandas as pd
#Ref:https://www.maxlist.xyz/2018/09/25/python_googlesheet_crud/

gc = pygsheets.authorize(service_file='./googlesheet.json')
#url="https://docs.google.com/spreadsheets/d/1hUvFmq4kDJQHO2EdJo0i6TQFfCb4jSfOatotnqH9B9M"
url="https://docs.google.com/spreadsheets/d/1LBeZARWJMLMWkJj7jMVm9M83x3qEqwRpKirFwMzEgS8"
import time
gc_flag=False
def gclock():
    global gc_flag
    cnt=0
    while gc_flag:
        time.sleep(0.5)
        if cnt>=50:
            return False
        cnt+=1


def test(msg,userid,replytoken):
    global gc_flag
    if gclock():    
        ReplyMsg(1,replytoken,"發生錯誤,請等一下再重新傳送!!")
        #TG_MSG2USER(APP_NAME+"\n"+f"gc_lock:{cnt}\n")
        return

    gc_flag=True
    time.sleep(2)
    sht = gc.open_by_url(url)
    #選取by名稱
    stu_wks = sht.worksheet_by_title("學生名單")

    stu_data = stu_wks.get_as_df(numerize=False)#Ref:https://hackmd.io/@wh91008/r1pL28_wB
    r, c = stu_data.shape

    data=msg.split("-")
    stu_cls,stu_no,stu_name,_=who(userid)

    gc_flag=False
    ReplyMsg(1,replytoken,"Test!測試!")

#只讀一次
sht = gc.open_by_url(url) #Ref:https://hackmd.io/@Yun-Cheng/GoogleSheets
#----選單----------------
def menu(userid,msg,replytoken):
    cmd=msg.split("-")[0]
    #sht = gc.open_by_url(url) #Ref:https://hackmd.io/@Yun-Cheng/GoogleSheets
    
    #選取by名稱
    class_wks = sht.worksheet_by_title("各班股長")
    class_data = class_wks.get_as_df(numerize=False,include_tailing_empty=False)#Ref:https://hackmd.io/@wh91008/r1pL28_wB
    r, c = class_data.shape
    print("資料量:",r,c)
    row=-1#資料所在列
    userdata=None
    sid=None
    cnt=0
    for i in range(0,r):
        cnt+=1
        if cnt>80:
            break
        if userid.strip()==class_data.iloc[i,0]:
            #userdata=class_data.iloc[i].tolist()
            FlexMessage = json.load(open("./flexmsg/menu.json",'r',encoding='utf-8'))
            return ReplyMsg(2,replytoken,'選單',flexmsg=FlexMessage)
            break
    print(cnt)
    return ReplyMsg(1,replytoken,f"你尚未登錄資訊股長,請輸入 學號-班級 登錄為資訊股長後再使用.")


#---登錄----
def reg(userid,msg,replytoken):
    #sht = gc.open_by_url(url)
    #選取by名稱
    class_wks = sht.worksheet_by_title("各班股長")
    class_data = class_wks.get_as_df(numerize=False,include_tailing_empty=False)#Ref:https://hackmd.io/@wh91008/r1pL28_wB
    r, c = class_data.shape
    data=msg.split("-")
    row=-1#資料所在列
    for i in range(0,r):
        if userid.strip()==class_data.iloc[i,0]:
            class_=class_data.iloc[i].tolist()
            return ReplyMsg(1,replytoken,f"你已登錄為{class_[1]}班資訊股長")
    #print(data,userid)
    #print("Register...",msg,r,c)
    class_=None
    row=-1#資料所在列
    for i in range(0,r):
        if data[1].strip()==class_data.iloc[i,1]:
            class_=class_data.iloc[i].tolist()
            row=i
            #print(stu)
            if class_[0]!=None and len(class_[0].strip())!=0:
                return ReplyMsg(1,replytoken,f"已有人登錄{data[1]}班資訊股長,有任何問題請洽{config.TEACHER}!")
            break
    if(row==-1):
        return ReplyMsg(1,replytoken,f"找不到此{data[1]}班,請確認")

    class_wks.update_value(f'{col_code[0]}{row+2}', userid.strip()) #要加回標題列和index從0開始
    class_wks.update_value(f'{col_code[2]}{row+2}',"'"+data[0]) #要加回標題列和index從0開始
    ReplyMsg(1,replytoken,f"你已登錄{data[1]}班的資訊股長")
    return True


#-----每天狀況回報----------------
def daily(userid,msg,replytoken):
    shname={"回報":"每天狀況回報","報修":"報修"}
    cmd=msg.split("-")[0]
    data=msg.split("-")[1].split(":")

    #sht = gc.open_by_url(url)
    #選取by名稱
    class_wks = sht.worksheet_by_title("各班股長")
    class_data = class_wks.get_as_df(numerize=False,include_tailing_empty=False)#Ref:https://hackmd.io/@wh91008/r1pL28_wB
    daily_wks = sht.worksheet_by_title(shname[cmd])
    daily_data = daily_wks.get_as_df(numerize=False,include_tailing_empty=False)#Ref:https://hackmd.io/@wh91008/r1pL28_wB
    r, c = class_data.shape
    row=-1#資料所在列
    userdata=None
    sid=None
    for i in range(0,r):
        if userid.strip()==class_data.iloc[i,0]:
            userdata=class_data.iloc[i].tolist()
            if cmd=="回報":
                daily_wks.insert_rows(1, number=1, values=[userdata[1],data[0],data[1],data[2],datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")], inherit=False)
                return ReplyMsg(1,replytoken,f"回報訊息已收到.")
            if cmd=="報修":
                daily_wks.insert_rows(1, number=1, values=[userdata[1],data[0],data[1],datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")], inherit=False)
                TG_MSG2USER(config.APP_NAME+"\n"+f"{userdata[1]}班,{userdata[2]}報修{data[0]}教室:\n{data[1]}\n")
                return ReplyMsg(1,replytoken,f"報修訊息已收到,瞭解後會儘速處理")
            break
    else:
        return ReplyMsg(1,replytoken,f"你尚未登錄資訊股長,請輸入 學號-班級 登錄為資訊股長後再回報")


#---
def flex_btns(btns,text_prefix=""):
    flex_msg={
      "type": "bubble",
      "body": {
        "type": "box",
        "layout": "vertical",
        "spacing": "md",
        "contents": []
      }
    }
    style="secondary"
    for item in btns:
        btn={
          "type": "button",
          "action": {
            "type": "message",
          },
          "adjustMode": "shrink-to-fit"
        }
        btn["action"]["label"]=item
        btn["action"]["text"]=text_prefix+item
        if style=="secondary":
            style="primary"
        else:
            style="secondary"
        btn["style"]=style
        flex_msg["body"]["contents"].append(btn)
    return flex_msg


#------ReplyMsg-----------------------
def ReplyMsg(msgtype,replytoken,msg,flexmsg=None,name=None,icon_url=None):
    try:
        if(msgtype==1):
            line_bot_api.reply_message(
                replytoken,
                TextSendMessage(text=msg)
            )
        if(msgtype==2):
            line_bot_api.reply_message(replytoken, 
                FlexSendMessage(msg,flexmsg)
            )
        return True
    except Exception as e:
        NOW=datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        #Ref:https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/372720/
        IP=request.remote_addr
        with open("log.err","a+") as fn:
            fn.write(f"ReplyMsg:{IP,replytoken,msg,e,NOW}\n")
        return True


#------PushMsg-------------------------------------
def PushMsg(msgtype,user_id,msg,flexmsg=None,name=None,icon_url=None):
    try:
        if(msgtype==1):
            line_bot_api.push_message(
                user_id, [
                    TextSendMessage(text=msg)
                ]
            )
        if(msgtype==2):
            line_bot_api.push_message(user_id, 
                FlexSendMessage(msg,flexmsg)
            )
    except Exception as e:
        NOW=datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        #Ref:https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/372720/
        IP=request.remote_addr
        with open("log.err","a+") as fn:
            fn.write(f"PushMsg:{IP,replytoken,msg,e,NOW}\n")
        return True

