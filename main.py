import os
import discord
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
DIFY_KEY = os.environ.get('DIFY_API_KEY')

# --- Renderのスリープ防止用Webサーバー設定 ---
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write("Bot is running!".encode('utf-8'))

    def log_message(self, format, *args):
        pass # ログを非表示

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), KeepAliveHandler)
    print(f"Web server started on port {port}")
    server.serve_forever()

# Webサーバーを別スレッドで起動
threading.Thread(target=run_web_server, daemon=True).start()
# ---------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        cleaned_text = message.content.replace(f'<@{client.user.id}>', '').strip()
        if not cleaned_text:
            return
        async with message.channel.typing():
            try:
                headers = {'Authorization': f'Bearer {DIFY_KEY}', 'Content-Type': 'application/json'}
                data = {'inputs': {}, 'query': cleaned_text, 'response_mode': 'blocking', 'user': str(message.author.id)}
                res = requests.post('https://api.dify.ai/v1/chat-messages', json=data, headers=headers)
                res_data = res.json()
                if 'answer' in res_data:
                    await message.reply(res_data['answer'])
                else:
                    await message.reply(f"Difyからエラーが返ってきました: {res_data}")
            except Exception as e:
                await message.reply(f"エラーが発生しました: {str(e)}")

client.run(TOKEN)
