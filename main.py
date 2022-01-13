import datetime

# 今日の年月日を取得 
now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
today = now.date()

f = open('test/test_datetime.xml', 'w', encoding='UTF-8')
f.write(f'<?xml version="1.0" encoding="UTF-8" ?><date>{now.strftime("%Y/%m/%d %H:%M")}</date>')
f.close()
