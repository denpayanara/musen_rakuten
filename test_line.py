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

    # 【テスト】差分ありのみ抽出
    # df_diff = df[df["増減数"] != 0]
    df_diff = df[df["市区町村名"] == '奈良県']

    # 差分ありの時
    if len(df_diff) > 0:

        Line_Token = os.environ['LINE_TOKEN']

        # 都道府県の合計行を抽出
        df_pref = df_diff.query('市区町村名 == "滋賀県" or 市区町村名 == "京都府" or 市区町村名 == "大阪府" or 市区町村名 == "兵庫県" or 市区町村名 == "奈良県" or 市区町村名 == "奈良県" or 市区町村名 == "和歌山県"')
    
        pref = []
        
        for i, row in df_pref.iterrows():
            pref.append(f"{row.iloc[0]} {row.iloc[1]:+}")

        text = "\n".join(pref)

        tweet = f"{key}更新\n\n{text}\n\n奈良県の詳細\nhttps://script.google.com/macros/s/AKfycbx6OjIvfSwa9CJJ_arw5H08HwewIk7NXUGEDOX81f8Vi79piLqskVXpCO-o9Kw4ZrBQ3w/exec\n\n#楽天モバイル #近畿 #bot"

        print(tweet)

        token_dic = {'Authorization': 'Bearer' + ' ' + Line_Token}

        send_dic = {'message': tweet} 

        img = requests.get(img_4G).content

        img_data = BytesIO(img)

        files = {'imageFile': img_data}

for key, url in musen.items():

    tweet(key, url)
