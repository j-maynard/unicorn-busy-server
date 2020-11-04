import os

import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
BUSYLIGHT_ID = int(os.getenv('BUSYLIGHT_ID'))

class DiscordBot(commands.Bot):
    connectedMember = None
    url = "http://127.0.0.1:5000"

    def setStatusOnBusylight(self, status):
        if status == 'dnd':
            requests.post(f"{self.url}/busy")
        elif status == "online":
            requests.post(f"{self.url}/available")
        elif status == "idle":
            requests.post(f"{self.url}/away")
        elif status == "offline":
            requests.get(f"{self.url}/off")

    async def on_ready(self):
        for guild in bot.guilds:
            if guild.id == GUILD:
                break
        print(
            f'{bot.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})\n'
        )

        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')

    async def on_member_update(self, before, after):
        if before.status != after.status:  # to only run on status
            if self.connectedMember == after.id:
                self.setStatusOnBusylight(after.raw_status)

intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.guilds = True
bot = DiscordBot(command_prefix="!", intents=intents)

@bot.command(name="connect", help="Connect the current user this busy light.  Requires ID of busylight")
async def user_connect(context, id: int):
    global BUSYLIGHT_ID, bot
    if BUSYLIGHT_ID != id:
        return
    
    if bot.connectedMember == None:
        bot.connectedMember = context.author.id
        bot.setStatusOnBusylight(context.author.raw_status)
        await context.send(f"Member {context.author.name} has connected their status to the Busylight")
    else:
        if bot.connectedMember == context.author.id:
            await context.send("You've already connected your status to this busylight.")
        else:
            await context.send(f"A user already connect their their status to this Busylight")

@bot.command(name="disconnect", help="Disconnects the current user from this busy light.  Requires ID of busylight")
async def user_disconnect(context, id: int):
    global BUSYLIGHT_ID, bot
    if BUSYLIGHT_ID != id:
        return
    
    bot.connectedMember = None
    await context.send(f"Member {context.author.name} has disconnected their status from Busylight")

bot.run(TOKEN)