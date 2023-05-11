import datetime
import os
from io import BytesIO
import time

from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage
import pandas as pd
import tweepy
import requests

csv_4G = 'tweet_data/Rakuten_4G.csv'
img_4G = 'tweet_data/diff_Rakuten_4G.png'
img_4G_url = 'https://raw.githubusercontent.com/denpayanara/musen_rakuten/main/tweet_data/diff_Rakuten_4G.png'

csv_rep = 'tweet_data/Rakuten_Repeater.csv'
img_rep = 'tweet_data/diff_Rakuten_Repeater.png'
img_rep_url = 'https://raw.githubusercontent.com/denpayanara/musen_rakuten/main/tweet_data/diff_Rakuten_Repeater.png'

musen = {
    '4G(包括免許)': [csv_4G, img_4G, img_4G_url],
    '陸上移動中継局(包括免許)': [csv_rep, img_rep, img_rep_url]
    }

# Twitterは停止

def send_message(key, v):

    df = pd.read_csv(v[0])

    # 差分ありのみ抽出
    df_diff = df[df["増減数"] != 0]

    # Twitter
    # api_key = os.environ["API_KEY"]
    # api_secret = os.environ["API_SECRET_KEY"]
    # access_token = os.environ["ACCESS_TOKEN"]
    # access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]
    # auth = tweepy.OAuthHandler(api_key, api_secret)
    # auth.set_access_token(access_token, access_token_secret)
    # api = tweepy.API(auth)

    # LINE
    line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])


    # 差分ありの時
    if len(df_diff) > 0:

        # 都道府県の合計行を抽出
        df_pref = df_diff.query('市区町村名 == "滋賀県" or 市区町村名 == "京都府" or 市区町村名 == "大阪府" or 市区町村名 == "兵庫県" or 市区町村名 == "奈良県" or 市区町村名 == "奈良県" or 市区町村名 == "和歌山県"')
    
        pref = []
        
        for i, row in df_pref.iterrows():
            pref.append(f"{row.iloc[0]} {row.iloc[1]:+}")

        text = "\n".join(pref)

        message = f"{key}更新\n\n{text}\n\n奈良県の詳細\nhttps://script.google.com/macros/s/AKfycbx6OjIvfSwa9CJJ_arw5H08HwewIk7NXUGEDOX81f8Vi79piLqskVXpCO-o9Kw4ZrBQ3w/exec\n\n#楽天モバイル #近畿 #bot"

        print(message)

        # 画像読込

        img_url = v[2]
        img = requests.get(img_url).content
        img_data = BytesIO(img)

        # ツイート送信
        # media_ids = []
        # res_media_ids = api.media_upload(filename = 'img.png', file = img_data)
        # media_ids.append(res_media_ids.media_id)
        # api.update_status(status = message, media_ids = media_ids)
        
        time.sleep(1)

        # LINE送信
        line_bot_api.broadcast(
            messages = [
                TextSendMessage(text = message),
                ImageSendMessage(
                    original_content_url = v[2],
                    preview_image_url = v[2]
                )
            ]
        )

    # '4G(包括免許)'の更新が無い場合
    # elif key == '4G(包括免許)':
        
    #     message = f"本日の{key}の更新はありません。\n\n#楽天モバイル #近畿 #bot"
    #     print(message)

    #     # ツイート送信
    #     api.update_status(status = message)

    #     time.sleep(1)

    #     # LINE送信
    #     line_bot_api.broadcast(messages = TextSendMessage(text = message))

for key, v in musen.items():

    # ツイートイメージの作成日時を取得して本日の場合にsend_message関数を実行

    t = os.path.getctime(v[1])
    d = datetime.date.fromtimestamp(t)

    # 今日の年月日を取得 
    # now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    now = datetime.datetime.utcnow()
    today = now.date()
    
    print(f'プログラムが実行した年月日は{today}です。')
    print(f'{key}のファイルの作成年月日は{d}です。')

    if d == today:
        send_message(key, v)
