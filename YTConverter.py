from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from pytube import YouTube
from moviepy.editor import *
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)
    if 'youtube.com/watch?v=' in event.message.text:
        url = event.message.text
        try:
            video_file = download_video(url)
            wav_file = convert_to_wav(video_file)
            
            print("WAV file saved:", wav_file)  # 添加這個print語句，顯示WAV文件的保存路徑
            
            # 在這裡添加上傳到雲端存儲的邏輯，並獲取下載連結
            
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"WAV 檔案已保存: {wav_file}"))

            # 清理下載的影片和轉換後的檔案
            os.remove(video_file)
            os.remove(wav_file)
        except Exception as e:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"發生錯誤: {str(e)}"))

def download_video(url):
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    return video.download()

def convert_to_wav(file_path):
    clip = AudioFileClip(file_path)
    wav_path = file_path.replace(".mp4", ".wav")
    clip.write_audiofile(wav_path, codec='pcm_s16le')
    return wav_path

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
