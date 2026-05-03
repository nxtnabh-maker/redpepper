import discord
from discord.ext import commands, tasks
import datetime
import os
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "RedPepper is Online!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

TOKEN = os.environ.get("DISCORD_TOKEN")
WELCOME_CH_ID = 1491394274963488929
RULES_CH_ID = 1491399916814209085

def get_suffix(n):
    if 11 <= n % 100 <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")

@tasks.loop(seconds=60)
async def status_task():
    await bot.change_presence(
        status=discord.Status.online, 
        activity=discord.Activity(type=discord.ActivityType.watching, name="Drago Members")
    )

@bot.event
async def on_ready():
    print(f"RedPepper Direct System Online: {bot.user}")
    if not status_task.is_running():
        status_task.start()

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    global WELCOME_CH_ID
    WELCOME_CH_ID = ctx.channel.id
    await ctx.send(f"✅ **Success!** Welcome messages will now be sent in {ctx.channel.mention}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CH_ID)
    if not channel: 
        return
    
    count = len(member.guild.members) 
    suffix = get_suffix(count)
    
    embed = discord.Embed(
        title=f"Welcome {member.name} to Drago!",
        description=f"You are the **{count}{suffix}** member!\n\npls head over to <#{RULES_CH_ID}> before heading towards the chat",
        color=0x2f3136
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Welcome {member.name} to Drago you are the {count}{suffix} member!")
    
    await channel.send(content=f"Welcome {member.mention} to **Drago**!", embed=embed)

spam_data = {}

@bot.event
async def on_message(message):
    if message.author.bot or message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return
    
    uid = message.author.id
    now = datetime.datetime.now()
    spam_data.setdefault(uid, []).append(now)
    spam_data[uid] = [t for t in spam_data[uid] if (now - t).seconds < 5]
    
    if len(spam_data[uid]) > 6:
        try:
            await message.author.timeout(datetime.timedelta(minutes=15), reason="RedPepper Anti-Spam")
            await message.channel.send(f"🚫 {message.author.mention} timed out for spamming.", delete_after=10)
        except: 
            pass
            
    await bot.process_commands(message)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    if TOKEN:
        bot.run(TOKEN)
