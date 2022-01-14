import os
from io import BytesIO

import pandas as pd
import tweepy
import requests

url_4G = 'https://raw.githubusercontent.com/denpayanara/musen_test/main/tweet_data/Rakuten_4G.csv'
img_4G = 'https://raw.githubusercontent.com/denpayanara/musen_test/main/tweet_data/diff_Rakuten_4G.png'

url_rep = 'https://raw.githubusercontent.com/denpayanara/musen_test/main/tweet_data/Rakuten_Repeater.csv'
img_rep = 'https://raw.githubusercontent.com/denpayanara/musen_test/main/tweet_data/diff_Rakuten_Repeater.png'

musen = {
    '4G(包括免許)': [url_4G, img_4G],
    '陸上移動中継局(包括免許)': [url_rep, img_rep]
    }

def tweet(key, url):

    df = pd.read_csv(url[0])

    # 差分ありのみ抽出
    df_diff = df[df["増減数"] != 0]

    # 差分ありの時
    if len(df_diff) > 0:

        api_key = os.environ["API_KEY"]
        api_secret = os.environ["API_SECRET_KEY"]
        access_token = os.environ["ACCESS_TOKEN"]
        access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

        # 都道府県の合計行を抽出
        df_pref = df_diff.query('市区町村名 == "滋賀県" or 市区町村名 == "京都府" or 市区町村名 == "大阪府" or 市区町村名 == "兵庫県" or 市区町村名 == "奈良県" or 市区町村名 == "奈良県" or 市区町村名 == "和歌山県"')
    
        pref = []
        
        for i, row in df_pref.iterrows():
            pref.append(f"{row.iloc[0]} {row.iloc[1]:+}")

        text = "\n".join(pref)

        tweet = f"{key}更新\n\n{text}\n\n奈良県の詳細\nhttps://script.google.com/macros/s/AKfycbx6OjIvfSwa9CJJ_arw5H08HwewIk7NXUGEDOX81f8Vi79piLqskVXpCO-o9Kw4ZrBQ3w/exec\n\n#楽天モバイル #近畿 #bot"

        print(tweet)

        auth = tweepy.OAuthHandler(api_key, api_secret)

        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth)
        
        media_ids = []

        img_url = url[1]

        img = requests.get(img_url).content

        res_media_ids = api.media_upload(filename='img.png', file=BytesIO(img))

        media_ids.append(res_media_ids.media_id)

        api.update_status(status = tweet, media_ids = media_ids)

for key, url in musen.items():

    tweet(key, url)
