import os
import threading
from dotenv import load_dotenv

import discord
from discord.ext import commands
import flask

# Do I have to do this? Is there a way to like have python default import a .py? maybe that's what __init__.py is for?
# I don't understand how this wasn't immediately answered via google.
from settings.settings import Settings
from lobby.lobby import Lobby
from sync.sync import Sync

app = flask.Flask(__name__)
global bot

@app.route("/lobby/<path:path>")
def route_lobby_redirect(path):
    return flask.redirect(f"steam://joinlobby/{path}", code=301)

def run_flask_http():
    app.run(host="0.0.0.0", port=3000)

def run_flask_https():
    certs = f"/etc/letsencrypt/live/neffytron.com"
    app.run(host="0.0.0.0", port=3001, ssl_context=(f"{certs}/fullchain.pem", f"{certs}/privkey.pem"))

def run(token):
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    global bot
    bot = commands.Bot(command_prefix="!", intents=intents,
        allowed_contexts=discord.app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True),
        allowed_installs=discord.app_commands.AppInstallationType(guild=True, user=True),
    )

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}\nSetting up cogs")
        await bot.add_cog(Settings(bot))
        await bot.add_cog(Lobby(bot))
        await bot.add_cog(Sync(bot))
        print('Set up cogs')
    bot.run(token)

if __name__ == "__main__":
    load_dotenv()
    http_thread = threading.Thread(target=run_flask_http, daemon=True)
    https_thread = threading.Thread(target=run_flask_https, daemon=True)
    http_thread.start()
    https_thread.start()
    run(os.getenv('TOKEN'))
