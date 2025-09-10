from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import commands
import os
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Intents (required)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Needed to mention members properly

# Create bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Store votes in memory
votes = set()  # store user IDs of voters

# ---------- EVENTS ----------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()  # sync slash commands
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
        super().__init__(timeout=None)  # persistent view

    @discord.ui.button(label="Vote (0)", style=discord.ButtonStyle.success, custom_id="vote_button")
    async def vote(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        if user_id in votes:
            votes.remove(user_id)
            await interaction.response.send_message("You removed your vote!", ephemeral=True)
        else:
            votes.add(user_id)
            await interaction.response.send_message("You voted!", ephemeral=True)
        # Update the vote count label
        button.label = f"Vote ({len(votes)})"
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Show Voters", style=discord.ButtonStyle.secondary, custom_id="show_voters")
    async def show_voters(self, interaction: discord.Interaction, button: discord.ui.Button):
        if votes:
            user_list = []
            for user_id in votes:
                user = await bot.fetch_user(user_id)
                user_list.append(user.name)
            await interaction.response.send_message(
                f"Voters ({len(votes)}): {', '.join(user_list)}", ephemeral=True
            )
        else:
            await interaction.response.send_message("No votes yet.", ephemeral=True)

# ---------- COMMAND TO START VOTE ----------
@bot.command()
async def startvote(ctx):
    """Starts a voting message with two buttons: Vote and Show Voters"""
    view = VoteView()
    await ctx.send("Click the buttons below to vote or see voters:", view=view)

# ---------- SESSION COMMANDS ----------
@bot.command()
async def startsession(ctx):
    """Starts a session by pinging all voters and clearing the vote list"""
    if votes:
        mentions = []
        for user_id in votes:
            user = await bot.fetch_user(user_id)
            mentions.append(user.mention)

        embed = discord.Embed(
            title="📢 Session Started",
            description=f"The following members are called to session:\n{', '.join(mentions)}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

        votes.clear()  # reset voter list
    else:
        await ctx.send("❌ No voters to start a session with.")

@bot.command()
async def endsession(ctx):
    """Ends a session"""
    embed = discord.Embed(
        title="⏹️ Session Ended",
        description="The session has now ended.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

# ---------- SLASH COMMAND: INFRACT ----------
@bot.tree.command(name="infract", description="Issue an infraction against a member")
async def infract(interaction: discord.Interaction, member: discord.Member, action: str, reason: str):
    # Build the embed
    embed = discord.Embed(
        title="⚠️ Infraction Issued",
        color=discord.Color.red()
    )
    embed.add_field(name="👤 Member", value=member.mention, inline=True)
    embed.add_field(name="🛠️ Action", value=action, inline=True)
    embed.add_field(name="📝 Reason", value=reason, inline=False)
    embed.set_footer(text=f"Issued by {interaction.user}", icon_url=interaction.user.avatar.url)

    # Find the channel by ID
    channel = interaction.guild.get_channel(1412339191290921048)

    if channel:
        # Send the ping + embed in one message to that channel
        await channel.send(content=f"{member.mention} ⚠️ You have received an infraction.", embed=embed)
        await interaction.response.send_message("✅ Infraction logged.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Could not find the infraction log channel.", ephemeral=True)