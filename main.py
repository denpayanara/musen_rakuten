# 総務省電波利用HPのメンテナンスお知らせbot

import datetime
import os
import re
import ssl
from urllib import request

from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage
# import requests
import tweepy

url = 'https://www.tele.soumu.go.jp/j/new/emergency/index.htm'

ctx = ssl.create_default_context()

ctx.options |= 0x4

with request.urlopen(url, context=ctx) as res:
    soup = BeautifulSoup(res.read(), 'html.parser', from_encoding='UTF-8')

# システム停止期間のpタグ内に「停止期間」が含まれている場合実行

# 直近の発表日及びコメント
# soup.select('p.mt-m')[0].text

# 直近のシステム停止期間
# soup.select('p')[1]

# イレギュラーsample「中止」
# soup.select('p')[5].text

# イレギュラーsample停止期間が複数
# soup.select('p')[7].text

downtime_str_0 = soup.select('p')[5].text

if '停止期間' in downtime_str_0:

    downtime_list_0 = downtime_str_0.splitlines()

    downtime_list_0.pop(0)

    # print(downtime_list_0)

    downtime_list_1 = []

    for v1 in downtime_list_0:

        downtime_list_1.append(re.findall('\d{4}年\d{1,}月\d{1,}日', v1))

    # print(downtime_list_1)

    downtime_datetime_list = []

    for v2 in downtime_list_1:

        for v3 in v2:

            downtime_datetime_list.append(datetime.datetime.strptime(v3, '%Y年%m月%d日').date())

# 今日の年月日を取得
now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
today = now.date()

downtime_str_1 = '\n'.join(downtime_list_0)

# メッセージ作成

message = f"総務省電波利用HPのシステムメンテナンスのお知らせ\n\n【システム停止期間】\n{downtime_str_1}\n\n"

message += '詳細については下記URLをご参照下さい。\n'

message += 'https://www.tele.soumu.go.jp/j/new/emergency/index.htm'

for v4 in downtime_datetime_list:

    # print(v4)

    # システム停止期間が明日行われる場合に通知

    if v4 == today + datetime.timedelta(days=1):

        print(message)

        # Twitter

        api_key = os.environ["API_KEY"]
        api_secret = os.environ["API_SECRET_KEY"]
        access_token = os.environ["ACCESS_TOKEN"]
        access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        # ツイート送信
        api.update_status(status = message)

        # LINE
        # LINEチャンネルのアクセストークン忘れた

        # line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

        # # LINE送信
        # line_bot_api.broadcast(messages = TextSendMessage(text = message))

        break
