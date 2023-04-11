from telegram_bot import TG_MSG2USER
import config
APP_NAME=config.APP_NAME
import datetime

col_code=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']

#try:
#    gc
#except NameError:#Ref:https://stackoverflow.com/questions/1592565/determine-if-variable-is-defined-in-python
import pygsheets
import pandas as pd
#Ref:https://www.maxlist.xyz/2018/09/25/python_googlesheet_crud/

gc = pygsheets.authorize(service_file='./googlesheet.json')
url="https://docs.google.com/spreadsheets/d/1LBeZARWJMLMWkJj7jMVm9M83x3qEqwRpKirFwMzEgS8"

#只讀一次
sht = gc.open_by_url(url) #Ref:https://hackmd.io/@Yun-Cheng/GoogleSheets
shname={"回報":"每天狀況回報","報修":"報修"}

def report(ins):
    #print("Web report...")
    daily_wks = sht.worksheet_by_title(shname["回報"])
    daily_data = daily_wks.get_as_df(numerize=False,include_tailing_empty=False)#Ref:https://hackmd.io/@wh91008/r1pL28_wB
    daily_wks.insert_rows(1, number=1, values=[ins[1],ins[0],ins[3],ins[4],"'"+ins[2],ins[5],datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S")], inherit=False)
    

