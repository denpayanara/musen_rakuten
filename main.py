import datetime
import json
import re
import ssl
from urllib import request, parse

import pandas as pd
import plotly.figure_factory as ff

Rakuten_4G = {
    # 1:免許情報検索  2: 登録情報検索
    "ST": 1,
    # 詳細情報付加 0:なし 1:あり
    "DA": 1,
    # スタートカウント
    "SC": 1,
    # 取得件数
    "DC": 1,
    # 出力形式 1:CSV 2:JSON 3:XML
    "OF": 2,
    # 無線局の種別
    "OW": "FB_H",
    # 所轄総合通信局
    "IT": "E",
    # 免許人名称/登録人名称
    "NA": "楽天モバイル",
}

Rakuten_Repeater = {
    # 1:免許情報検索  2: 登録情報検索
    "ST": 1,
    # 詳細情報付加 0:なし 1:あり
    "DA": 1,
    # スタートカウント
    "SC": 1,
    # 取得件数
    "DC": 1,
    # 出力形式 1:CSV 2:JSON 3:XML
    "OF": 2,
    # 無線局の種別
    "OW": "FBR_H",
    # 所轄総合通信局
    "IT": "E",
    # 免許人名称/登録人名称
    "NA": "楽天モバイル",
}

def musen_api(d):

    # APIリクエスト条件にShift_JIS(CP943C)を指定する様に記載があるが取得件数0件となる為utf-8を指定
    params = parse.urlencode(d, encoding="utf-8")

    # ヘッダーが無いと403Forbidden
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    } 

    req = request.Request(f'https://www.tele.soumu.go.jp/musen/list?{params}', headers=headers)

    ctx = ssl.create_default_context()

    ctx.options |= 0x4

    with request.urlopen(req, context=ctx) as res:
        return json.loads(res.read())

def fetch_cities(s):

    # lst = re.findall("(\S+)\(([0-9,]+)\)", s)

    lst = re.findall("(\S+?)\s*\(([0-9,]+)\)", s)

    df0 = pd.DataFrame(lst, columns=["市区町村名", "開設局数"])
    df0["開設局数"] = df0["開設局数"].str.strip().str.replace(",", "").astype(int)

    flag = df0["市区町村名"].str.endswith(("都", "道", "府", "県"))

    df0["都道府県名"] = df0["市区町村名"].where(flag).fillna(method="ffill")

    return df0

def Data_Wrangling(data):

    data = (
        data["musen"][0]["detailInfo"]["note"]
        .split("\\n", 2)[2]
        .replace("\\n", " ")
        .strip()
        )
    return data

def df_edit(df0):
    
    # 関西圏のみを抽出
    df1 = df0.query(
        '都道府県名 == "滋賀県" or \
        都道府県名 == "京都府" or \
        都道府県名 == "大阪府" or \
        都道府県名 == "兵庫県" or \
        都道府県名 == "奈良県" or \
        都道府県名 == "和歌山県"'
        ).reset_index(drop=True)

    # カラム名と並び順を変更
    df2 = df1.reindex(columns=['都道府県名', '市区町村名', '開設局数'])

    return df2

def city_merge(df0):

    # 市区町村リスト読込
    df_code = pd.read_csv(
        "city_list.csv",
        dtype={"団体コード": int, "都道府県名": str, "郡名": str, "市区町村名": str},
        ).set_index('団体コード')

    df_code["市区町村名"] = df_code["郡名"].fillna("") + df_code["市区町村名"].fillna("")

    df_code.drop("郡名", axis=1, inplace=True)

    # 空の都道府県名に追記
    df_code.loc[250007, '市区町村名'] = '滋賀県'
    df_code.loc[260002, '市区町村名'] = '京都府'
    df_code.loc[270008, '市区町村名'] = '大阪府'
    df_code.loc[280003, '市区町村名'] = '兵庫県'
    df_code.loc[290009, '市区町村名'] = '奈良県'
    df_code.loc[300004, '市区町村名'] = '和歌山県'

    df_code = df_code.reset_index()

    # df_codeとdf2をマージ
    df1 = ( pd.merge(df_code, df0, on=["都道府県名", "市区町村名"], how="left") )

    df1['開設局数'] = df1['開設局数'].fillna(0).astype(int)

    df1["団体コード"] = df1["団体コード"].astype(int)

    df1.sort_values("団体コード", inplace=True)

    df1 = df1.set_index('団体コード')

    df1 =  df1.reset_index(drop=True)

    return df1

def output(df, musen):
    
    df_kinki = df

    # 差分計算
    # 前日の値を取得
    yest_data = pd.read_csv(f'tweet_data/{musen}.csv')

    df_kinki.insert(loc = 2, column = '増減数', value = df['開設局数'] - yest_data['開設局数'])
    df_kinki.insert(loc = 4, column = '前回', value = yest_data['開設局数'])

    # 奈良県用の差分DataFrame作成
    # 奈良県を抽出し都道府県名列を削除
    df_nara = df_kinki[df_kinki["都道府県名"] == '奈良県']
    df_nara.drop(columns='都道府県名', inplace=True)

    # 奈良県の郡名を削除
    df_nara['市区町村名'] = df_nara['市区町村名'].str.replace("^(山辺郡|生駒郡|磯城郡|宇陀郡|高市郡|北葛城郡|吉野郡)", "", regex=True)

    # df_naraの差分ある時のみ保存
    if len(df_nara[df_nara["増減数"] != 0]) > 0:

        df_nara.to_csv(f'nara/diff_{musen}_nara.csv', index=False, encoding="utf_8_sig")

        # 奈良県用の最終更新日を書き込んだXMLファイルを作成
        f = open(f'nara/{musen}_LastUpdate_Nara.xml', 'w', encoding='UTF-8')
        f.write(f'<?xml version="1.0" encoding="UTF-8" ?><{musen}_Nara><date>{now.strftime("%Y/%m/%d %H:%M")}</date></{musen}_Nara>')
        f.close()
    
    # 近畿圏用の差分DataFrame作成
    # 近畿圏の都道府県名列を削除
    df_kinki.drop(columns='都道府県名', inplace=True)

    # 保存(Tweet botのツイートチェック用データ)
    df_kinki.to_csv(f'tweet_data/{musen}.csv', index=False, encoding="utf_8_sig")

    # 増減数が0で無いものを抽出
    df_kinki_diff = df_kinki.query('増減数 != 0 ')

    # 差分がある時、ツイート用の画像を作成し保存
    if len(df_kinki_diff) > 0:
        
        # plotlyで近畿圏のデータをプロット
        fig = ff.create_table(df_kinki_diff)

        # 下部に余白を付けて更新日を表記
        fig.update_layout(
            title_text = now.strftime("%Y年%m月%d日") + ' 時点のデータです。',
            title_x = 0.98,
            title_y = 0.025,
            title_xanchor = 'right',
            title_yanchor = 'bottom',
            # 余白の設定
            margin = dict(l = 0, r = 0, t = 0, b = 45)
        ) 

        # タイトルフォントサイズ
        fig.layout.title.font.size = 10

        fig.write_image(f'tweet_data/diff_{musen}.png', engine='kaleido', scale=1)
    

# 今日の年月日を取得 
now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
today = now.date()

# 年月
str_month = today.strftime("%y/%m")

# 月日
str_today = today.strftime("%Y/%m/%d")

# Rakuten_4G

# データ取得
data_4G_1 = musen_api(Rakuten_4G)

# データラングリング
data_4G_2 = Data_Wrangling(data_4G_1)

# フェッチ
data_4G_3 = fetch_cities(data_4G_2)

# データフレーム編集
data_4G_4 = df_edit(data_4G_3)

# 市区町村リストとマージ
Rakuten_4G_df = city_merge(data_4G_4)

output(Rakuten_4G_df, 'Rakuten_4G')

# 【月別差分(4G)】

# csv読み込み_月別
df_before_month = pd.read_csv('csv/musen_month.csv')

# 差分を求め今日の日付がcolumns[3]と等しければ
if df_before_month.columns[3] == str_month:
    df_before_month[str_month] = ( Rakuten_4G_df['開設局数'] - df_before_month['開設局数'] ) + df_before_month[str_month]

else:
    df_before_month.insert(loc = 3, column = str_month, value = Rakuten_4G_df['開設局数'] - df_before_month['開設局数'])
    
# 【日別差分(4G)】

# csv読み込み_日別
df_before_day = pd.read_csv('csv/musen_day.csv')

# 4列目の日付と今日の日付が異なれば
if df_before_day.columns[3] != str_today:

  # 前回の値から最新の差分を求め4列目に挿入
  df_before_day.insert(loc = 3, column = str_today, value = Rakuten_4G_df['開設局数'] - df_before_day['開設局数'])
  

# 月別と日別データの開設局数を最新に書き替え
today_value = Rakuten_4G_df.loc[:,'開設局数']

df_before_month['開設局数'] = today_value

df_before_day['開設局数'] = today_value

df_before_month.to_csv('csv/musen_month.csv', index=False, encoding="utf_8_sig")

df_before_day.to_csv('csv/musen_day.csv', index=False, encoding="utf_8_sig")

# Rakuten_Repeater

# データ取得
data_Rep_1 = musen_api(Rakuten_Repeater)

# データラングリング
data_Rep_2 = Data_Wrangling(data_Rep_1)

# フェッチ
data_Rep_3 = fetch_cities(data_Rep_2)

# データフレーム編集
data_Rep_4 = df_edit(data_Rep_3)

# 市区町村リストとマージ
data_Rep_df = city_merge(data_Rep_4)

output(data_Rep_df, 'Rakuten_Repeater')

# フェムトセル

# データラングリング
femto = (
    data_4G_1["musen"][1]["detailInfo"]["note"]
    .split("\\n", 2)[2]
    .replace("\\n", " ")
    .strip()
)

# フェッチ
se_femto = fetch_cities(femto)

# データフレーム編集
data_femto_1 = df_edit(se_femto)

# 市区町村リストとマージ
data_femto_df = city_merge(data_femto_1)

# 保存
data_femto_df.to_csv(f'csv/femto.csv', index=False, encoding="utf_8_sig")
