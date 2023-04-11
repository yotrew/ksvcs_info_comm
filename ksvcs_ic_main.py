#Ref:https://stackoverflow.com/questions/36465899/how-to-run-flask-server-in-the-background
#sudo nohup python3 x.py > log.txt 2>&1 &

#Ref:https://github.com/line/line-bot-sdk-python/blob/master/examples/flask-kitchensink/app.py
from flask import Flask, request, abort, render_template

from linebot import ( LineBotApi, WebhookHandler
)
from linebot.exceptions import (InvalidSignatureError)
#from linebot.models import (MessageEvent, TextMessage, TextSendMessage ,ImageMessage,)
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

#from datetime import datetime
import datetime
import time
import os
from telegram_bot import TG_MSG2USER
import config
import web_funs
APP_NAME=config.APP_NAME
app = Flask(__name__,template_folder=config.template_dir)
app.config["UPLOAD_FOLDER"]=config.upload_files_path
app.config['MAX_CONTENT_LENGTH']=10*1024*1024 #10MB

import linebot_funs as lbf
line_bot_api= lbf.line_bot_api#LineBotApi('Channel access token')
handler = lbf.handler #WebhookHandler('Channel secret')


cmds={"登錄":lbf.reg,"選單":lbf.menu,"回報":lbf.daily,"報修":lbf.daily,
        }

#app.static_folder="templates"
#@app.route("/<string:msg>") #
@app.route("/liff/<string:fn>", methods=['GET','POST']) #
def templates(fn):
    #print(title,col_title)
    #return app.send_static_file(fn)
    return render_template(fn,**locals())

@app.route("/", methods=['GET', 'POST'])
def index():
    name = request.args.get('name') #Ref:https://medium.com/seaniap/python-web-flask-get-post%E5%82%B3%E9%80%81%E8%B3%87%E6%96%99-2826aeeb0e28
    return "Hi..."+"<br/>這裡是"+f"[{APP_NAME}]"

#回報
@app.route("/report", methods=['GET', 'POST'])
def report():
    ins=[]
    fieldlen=6
    msg=""
    for i in range(1,fieldlen+1):
        ins.append(request.values.get('in'+str(i)))
    
    #print(ins)
    if len(ins)==fieldlen:
        state="No good"
        if ins[3]=="good":
            ins[3]="G"
            state="Good"
        elif ins[3]=="nonuse":
            ins[3]="NU"
            state="未使用"
        else:
            ins[3]="NG"
        if ins[0]!=None and len(ins[2])>=2:
            #print(ins)
            web_funs.report(ins)
            time.sleep(0.3)
        msg=f"你({ins[2]})回報了{ins[0]}教室,狀況:{state},{ins[4]}"
        tgmsg=f"({ins[2]})回報了{ins[0]}教室,狀況:{state},{ins[4]}"
    
    if ins[0]!=None and (ins[2]==None or len(ins[2])<2):
        if ins[2].isdigit() and len(ins[2])!=6:
            msg="你學號未填或格式錯誤"
        else:
            msg="你學號未填"
    
    if ins[0]==None:
        msg=""
    now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if ins[4]!="" and ins[4]!=None:
        TG_MSG2USER(APP_NAME+"\n"+now+f"{tgmsg}")
    return render_template('report.htm',html_title="上課後回報",form_action="report",msg=msg)


#---接收LineBot訊息
@app.route("/linebot", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    #print(body)
    body = request.get_data(as_text=True)
    #print(body)
    app.logger.info("Request body: " + body)

# handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'


#接收到文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    msg="發生錯誤!"
    print("-"*50)
    print(event)
    #print(event.source.user_id)
    try:
        #print(event)
        if event.source.type=="group":#訊息傳到群組,不做任何回應
            return ""
        usrcmd=event.message.text.split("-")[0]
        if len(usrcmd)==6:
            usrcmd="登錄"
        cmds[usrcmd](event.source.user_id,event.message.text,event.reply_token)
        lbf.gc_flag=False
    
    except KeyError as e:
        msg="本程式無法瞭解你的指令!\n若有任何問題,請使用(選單->留言)功能留言給資訊祕書!"
        stu_cls,stu_no,stu_name,sid=lbf.who(event.source.user_id)
        TG_MSG2USER(APP_NAME+"\n"+f"{stu_cls}/{stu_no}/{stu_name}/{sid}\n"+event.message.text)
        #Reply Message
        lbf.ReplyMsg(1,event.reply_token,msg)
    '''
    except Exception as e:
        NOW=datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        #Ref:https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/372720/
        with open("log.err","a+") as fn:
            fn.write(f"handle_text_message:{NOW,e}\n")
        msg="伺服器發生錯誤,請再重新傳送.\n"
        print(e)
        lbf.ReplyMsg(1,event.reply_token,msg)
    '''
    return ""


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    msg=""
    if event.source.type=="group":#訊息傳到群組,不做任何回應
        return ""
    if(event.message.type=="image"):
        message_content = line_bot_api.get_message_content(event.message.id)
        #filename=datetime.now()+".png"
        filename=event.source.user_id[-5:]+"_"+str(event.timestamp)+".png"
        #print(filename)

        #Ref:https://github.com/line/line-bot-sdk-python
        with open("./imgs/"+filename, 'wb') as fd:#Line收到的影像都會被轉成PNG??
            for chunk in message_content.iter_content(): 
                fd.write(chunk)
        msg="你傳的是圖片訊息..."
    lbf.ReplyMsg(1,event.reply_token,msg)
    #line_bot_api.reply_message(
    #    event.reply_token,
    #    TextSendMessage(text=msg))
    return ""


#others message type
@handler.add(MessageEvent)
def handle_message(event):
    #print(event.source.user_id)
    if event.source.type=="group":#訊息傳到群組,不做任何回應
        return ""
    #print("handle_message():",event.message.type)
    msg="不支援你傳送訊息的格式...(如:貼圖)"
    #Reply Message
    lbf.ReplyMsg(1,event.reply_token,msg)
    #line_bot_api.reply_message(
    #    event.reply_token,
    #    TextSendMessage(text=msg))

#Main    
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5012)
    #app.run(host="0.0.0.0",port=5001,ssl_context=('yotrewcsieio.crt', 'yotrewcsieio.key'))#Ref:https://medium.com/@charming_rust_oyster_221/flask-%E9%85%8D%E7%BD%AE-https-%E7%B6%B2%E7%AB%99-ssl-%E5%AE%89%E5%85%A8%E8%AA%8D%E8%AD%89-36dfeb609fa8
'''
#Ref:https://stackoverflow.com/questions/44871578/how-to-capture-ctrl-c-for-killing-a-flask-python-script
import sys
import signal
def handler(signal, frame):
  print('CTRL-C pressed!')
  sys.exit(0)
signal.signal(signal.SIGINT, handler)
'''
