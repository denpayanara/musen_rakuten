from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage

# LINE
line_bot_api = LineBotApi(os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

# LINE送信
line_bot_api.broadcast(
    messages = [
        TextSendMessage(text = 'LINE送信テスト'),
    ]
)

