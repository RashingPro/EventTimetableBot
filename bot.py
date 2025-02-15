import discord
from discord.ext import commands


with open('./config/token') as file:
    TOKEN = file.read()
bot = commands.Bot(command_prefix='!', help_command=None)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.slash_command(name='ping', description='Узнать пинг бота')
async def cmd_ping(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        color=0x0000ff,
        title=f'🏓 Понг!',
        description=f'Пинг: {round(bot.latency*1000)} ms'
    )
    await ctx.respond(embed=embed, ephemeral=True)

bot.run(TOKEN)
