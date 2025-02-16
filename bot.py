import datetime

import discord
from discord import Interaction
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


class MinecraftNicknameModal(discord.ui.Modal):
    def __init__(self, event_id: int, user_id: int) -> None:
        super().__init__(title='Установка ника в майнкрафте')
        self.event_id = event_id
        self.user_id = user_id
        self.add_item(discord.ui.InputText(label="Ваш ник в майнкрафте", required=True))

    async def callback(self, interaction: Interaction):
        g_table = google_table_manager.GoogleTableManager(service_file='./auth.json', debug=True)
        g_table.set_user_mc_nick(self.event_id, self.user_id, self.children[0].value)
        await interaction.respond(content='Успешно!', ephemeral=True)


class OpenMinecraftNicknameModal(discord.ui.View):
    def __init__(self, event_id: int, user_id: int) -> None:
        super().__init__()
        self.event_id = event_id
        self.user_id = user_id

    @discord.ui.button(label='Завершить регистрацию', style=discord.ButtonStyle.blurple)
    async def on_click(self, button: discord.ui.Button, interaction: discord.Interaction):
        button.disabled = True
        button.style = discord.ButtonStyle.green
        await interaction.response.send_modal(MinecraftNicknameModal(self.event_id, self.user_id))
        embed = interaction.message.embeds[0].to_dict()
        embed['color'] = 0x00ff00
        embed['description'] = embed['description'].replace('\nДля завершения регистрации нажмите кнопку ниже', '')
        await interaction.edit_original_message(view=self, embed=discord.Embed.from_dict(embed))


@bot.slash_command(name='make_announcement', description='Создать анонс ивента')
async def cmd_make_announcement(
        ctx: discord.ApplicationContext,
        event_id: discord.Option(int, name='айди', required=True)
):
    if ADMIN_ROLE_ID not in [role.id for role in ctx.author.roles]:
        embed = discord.Embed(
            color=0xff0000,
            title=f'❌ Недостаточно полномочий'
        )
        await ctx.respond(embed=embed, ephemeral=True)
        return
    await ctx.defer()
    g_table = google_table_manager.GoogleTableManager('./auth.json')
    event = g_table.get_event(int(event_id))
    date = event['date']
    title = event['name']
    description = event['description']
    channel = ctx.channel
    embed = discord.Embed(
        color=0x00ff00,
        title=f'Анонс ивента "{title}"',
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
            description=f'Вы **уже записаны** на ивент {event['name']}, '
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
        description=f'Вы записались на ивент **{event['name']}**, '
                    f'который пройдет **{event["date"].strftime("%d.%m в %H:%M")}**\n'
                    f'Для завершения регистрации нажмите кнопку ниже\n\n'
                    f'Если вы передумали участвовать в ивенте, то напишите <@669760356448731139>'
    )
    await dm_channel.send(embed=embed, view=OpenMinecraftNicknameModal(event_id, user.id))


@bot.slash_command(name='add_event', description='добавить ивент')
async def cmd_add_event(
        ctx: discord.ApplicationContext,
        title: discord.Option(str, name='название', description='название ивента, например мафия', required=True),
        date: discord.Option(str, name='дата', description='дата в формате дд.мм чч:мм', required=True),
        description: discord.Option(str, name='описание', description='описание ивента', required=False)
):
    date = datetime.datetime.strptime(date, '%d.%m %H:%M')
    await ctx.defer()
    g_table = google_table_manager.GoogleTableManager('./auth.json', debug=True)
    event_id = g_table.add_event(title, date, description)
    await ctx.respond(f'Ивент "{title}" успешно добавлен на дату {date.strftime("%d.%m %H:%M")} '
                      f'с айди `{event_id}` и '
                      f'{f'описанием {description}' if description is not None else 'без описания'}\n'
                      f'Ссылка: {g_table.get_main_table().worksheet('id', event_id).url}', ephemeral=True)


bot.run(TOKEN)
