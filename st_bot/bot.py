import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
from aiohttp import web
import os

# Простой веб-сервер для того, чтобы Render не усыплял бота
async def handle(request):
    return web.Response(text="ST Bot is running!")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class TicketButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Подать заявку 📝", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        category_name = "🌕 Заявка на вступление в клан 🌕"
        category = discord.utils.get(guild.categories, name=category_name)
        
        if not category:
            category = await guild.create_category(category_name)

        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"У вас уже есть открытая заявка: {existing_channel.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        close_view = CloseTicketView()
        application_form = (
            f"Привет, {interaction.user.mention}! Заполните, пожалуйста, анкету для вступления в клан ST:\n\n"
            "• **Сколько у вас часов:**\n"
            "• **Сколько вам лет:**\n"
            "• **Насколько вы адекватны от 0 до 10:**\n"
            "• **Есть ли у вас VAC/EAC баны:**\n"
            "• **Сколько готовы играть в день:**\n"
            "• **Что вы умеете лучше всего:**\n"
            "• **Ссылка на ваш стим профиль (обязательно должен быть открыт):**\n\n"
            "Скопируйте этот список, заполните ответы ниже и ожидайте ответа администрации!"
        )

        await ticket_channel.send(application_form, view=close_view)
        await interaction.response.send_message(f"Ваша заявка успешно создана: {ticket_channel.mention}", ephemeral=True)

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Закрыть тикет 🔒", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Тикет будет удален через 5 секунд...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

@bot.event
async def on_ready():
    print(f'Бот {bot.user} успешно запущен и готов к работе!')

@bot.command()
@commands.has_permissions(administrator=True)
async def ticket(ctx):
    view = TicketButton()
    text = (
        "**Требования для вступления в клан ST:**\n\n"
        "🟢 **Возраст:** от 14 лет\n"
        "🟢 **Часы в Rust:** от 500+ часов\n"
        "🟢 **Адекватность:** быть адекватным\n"
        "🟢 **Онлайн:** от 5 часов в день\n\n"
        "*Каждая заявка рассматривается индивидуально — поэтому возможны исключения*\n\n"
        "Нажмите на кнопку ниже, чтобы подать заявку:"
    )
    await ctx.send(text, view=view)
    await ctx.message.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def rules(ctx):
    rules_text = (
        "**1. 🛡️ Общие правила и Поведение**\n\n"
        "• **Уважение в отряде:** Любые оскорбления соклановцев, разжигание внутренних конфликтов и ссоры в голосовом чате — **СТРОГО ЗАПРЕЩЕНЫ**. Все споры решаются с лидером/замом лично в ЛС.\n\n"
        "• **Адекватность в чате:** Не токсичить и не позорить тег клана в общем чате сервера. Оставьте разговоры на поле боя.\n\n"
        "• **Чистота и Честность:** Запрещено использование любого стороннего ПО (читы, скрипты на отдачу, макросы, багоюз). Использование софта = немедленный бан.\n\n"
        "• **Информация — сила:** Запрещен слив информации о базе (пароли от замков, коды от ТК, количество лута) посторонним лицам."
    )
    await ctx.send(rules_text)
    await ctx.message.delete()

# Запускаем и веб-сервер, и бота одновременно
async def main():
    await start_web_server()
    # Безопасное чтение токена из переменных окружения на сервере (или вставка напрямую для теста)
    token = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN')
    await bot.start(token)

asyncio.run(main())