from flask import Flask
from threading import Thread
import os
import discord
from discord.ext import commands
# ----- KEEP-ALIVE WEB SERVER -----
app = Flask("")

@app.route("/")
def home():
    return "Bot is running."

def run():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run).start()

# ----- DISCORD BOT -----
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN not set!")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
# ---------- BOT START ----------

import os
import discord
from discord.ext import commands

# Optional: debug print to ensure code is running
print("Bot starting...")

# Read token from Render environment variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN environment variable not set!")

# ---------- INTENTS ----------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Needed to mention members properly

# ---------- CREATE BOT ----------
bot = commands.Bot(command_prefix="!", intents=intents)

# Store votes in memory
votes = set()

# ---------- EVENTS ----------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

# ---------- NORMAL COMMAND ----------
@bot.command()
async def hello(ctx):
    embed = discord.Embed(
        title="Hello there!",
        description=f"Hello {ctx.author.mention}! 👋",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=ctx.author.avatar.url)
    embed.set_footer(text="Skibidi")
    await ctx.send(embed=embed)

# ---------- VOTE BUTTON VIEW ----------
class VoteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Vote (0)", style=discord.ButtonStyle.success, custom_id="vote_button")
    async def vote(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        if user_id in votes:
            votes.remove(user_id)
            await interaction.response.send_message("You removed your vote!", ephemeral=True)
        else:
            votes.add(user_id)
            await interaction.response.send_message("You voted!", ephemeral=True)
        button.label = f"Vote ({len(votes)})"
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Show Voters", style=discord.ButtonStyle.secondary, custom_id="show_voters")
    async def show_voters(self, interaction: discord.Interaction, button: discord.ui.Button):
        if votes:
            user_list = [await bot.fetch_user(uid) for uid in votes]
            await interaction.response.send_message(
                f"Voters ({len(votes)}): {', '.join(u.name for u in user_list)}", ephemeral=True
            )
        else:
            await interaction.response.send_message("No votes yet.", ephemeral=True)

# ---------- START VOTE ----------
@bot.command()
async def startvote(ctx):
    view = VoteView()
    await ctx.send("Click the buttons below to vote or see voters:", view=view)

# ---------- SESSION COMMANDS ----------
@bot.command()
async def startsession(ctx):
    if votes:
        mentions = [ (await bot.fetch_user(uid)).mention for uid in votes ]
        embed = discord.Embed(
            title="📢 Session Started",
            description=f"The following members are called to session:\n{', '.join(mentions)}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
        votes.clear()
    else:
        await ctx.send("❌ No voters to start a session with.")

@bot.command()
async def endsession(ctx):
    embed = discord.Embed(
        title="⏹️ Session Ended",
        description="The session has now ended.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

# ---------- SLASH COMMAND ----------
@bot.tree.command(name="infract", description="Issue an infraction against a member")
async def infract(interaction: discord.Interaction, member: discord.Member, action: str, reason: str):
    embed = discord.Embed(title="⚠️ Infraction Issued", color=discord.Color.red())
    embed.add_field(name="👤 Member", value=member.mention, inline=True)
    embed.add_field(name="🛠️ Action", value=action, inline=True)
    embed.add_field(name="📝 Reason", value=reason, inline=False)
    embed.set_footer(text=f"Issued by {interaction.user}", icon_url=interaction.user.avatar.url)

    channel = interaction.guild.get_channel(1412339191290921048)
    if channel:
        await channel.send(content=f"{member.mention} ⚠️ You have received an infraction.", embed=embed)
        await interaction.response.send_message("✅ Infraction logged.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Could not find the infraction log channel.", ephemeral=True)

# ---------- RUN BOT ----------
bot.run(TOKEN)