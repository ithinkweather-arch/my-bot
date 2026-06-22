import os
import discord
import requests

TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
DIFY_KEY = os.environ.get('DIFY_API_KEY')

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
                    await message.reply("Difyからの応答にエラーが発生しました。")
            except Exception as e:
                await message.reply(f"エラーが発生しました: {str(e)}")

client.run(TOKEN)
