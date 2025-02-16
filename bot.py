import datetime

import discord
from discord.ext import commands

from managers import google_table_manager

ADMIN_ROLE_ID = 1309498655992188948
INVISIBLE_TEXT = '||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||'

with open('./config/token') as file:
    TOKEN = file.read()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}\nBot is ready')


@bot.slash_command(name='ping', description='Узнать пинг бота')
async def cmd_ping(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        color=0x0000ff,
        title=f'🏓 Понг!',
        description=f'Пинг: {round(bot.latency*1000)} ms'
    )
    await ctx.respond(embed=embed, ephemeral=True)


@bot.slash_command(name='make_announcement', description='Создать анонс ивента')
async def cmd_make_announcement(
        ctx: discord.ApplicationContext,
        title: discord.Option(str, name='название', required=True),
        date: discord.Option(str, name='дата', required=True, description='формат дд.мм чч:мм'),
        event_id: discord.Option(int, name='айди', required=True),
        description: discord.Option(str, name='описание', required=False)
):
    if ADMIN_ROLE_ID not in [role.id for role in ctx.author.roles]:
        embed = discord.Embed(
            color=0xff0000,
            title=f'❌ Недостаточно полномочий'
        )
        await ctx.respond(embed=embed, ephemeral=True)
        return
    date = datetime.datetime.strptime(date, '%d.%m %H:%M')
    channel = ctx.channel
    embed = discord.Embed(
        color=0x00ff00,
        title=f'Анон ивента "{title}"',
        description=f'**Дата ивента:** {date.strftime('%d.%m %H:%M')}\n' +
                    (f'**Описание:** {'\n'.join(description.split('\\n'))}' if description is not None else '')
    )
    await channel.send(content=f'{INVISIBLE_TEXT}{event_id};', embed=embed)
    await ctx.delete()


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    channel = bot.get_guild(payload.guild_id).get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if message.author.id != bot.user.id:
        return
    message_text = message.content
    event_id = int(message_text.split('|')[-1].split(';')[0])
    user = channel.guild.get_member(payload.user_id)
    g_table = google_table_manager.GoogleTableManager('./auth.json', debug=True)
    event = g_table.get_event(event_id)

    if user.id in [x['user_id'] for x in event['members']]:
        await user.create_dm()
        dm_channel = user.dm_channel
        embed = discord.Embed(
            color=0xff0000,
            title=f'Ошибка!',
            description=f'Вы **уже записаны** на ивент {event['name']} '
                        f'который пройдет **{event["date"].strftime("%d.%m в %H:%M")}**\n\n'
                        f'Если вы передумали участвовать в ивенте, то напишите <@669760356448731139>'
        )
        await dm_channel.send(embed=embed)
        return

    g_table.book_user(event_id, payload.user_id, user.display_name, '')
    await user.create_dm()
    dm_channel = user.dm_channel
    embed = discord.Embed(
        color=0x0000ff,
        title=f'Запись на ивент',
        description=f'Вы записались на ивент **{event['name']}** '
                    f'который пройдет **{event["date"].strftime("%d.%m в %H:%M")}**\n\n'
                    f'Если вы передумали участвовать в ивенте, то напишите <@669760356448731139>'
    )
    await dm_channel.send(embed=embed)

bot.run(TOKEN)
