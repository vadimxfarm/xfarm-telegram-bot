import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# Завантажуємо .env
load_dotenv()

# Імпортуємо функції БД
from database import init_db, save_farmer, get_farmer

# Налаштування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ Не встановлено TELEGRAM_BOT_TOKEN!")

# Стани для діалогу
ASK_CITY, ASK_CROPS, ASK_CROPS_UPDATE = range(3)  # ← змінено з 2 на 3

class XFarmBot:
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        farmer = get_farmer(user.id)

        if farmer and farmer[0]:  # місто вже вказано
            await update.message.reply_text(
                f"🌾 З поверненням, {user.first_name}! Оберіть опцію:",
                reply_markup=self.get_main_menu()
            )
        else:
            # Ініціалізуємо профіль
            save_farmer(user.id, user.username, user.first_name)
            await update.message.reply_text(
                "🌤 Щоб давати точні поради, скажіть, у якому місті ви працюєте? (наприклад: Київ, Харків)",
                reply_markup=ReplyKeyboardRemove()
            )
            return ASK_CITY

    def get_main_menu(self):
        keyboard = [
            [KeyboardButton("🌱 Мої рослини"), KeyboardButton("🌤 Погода")],
            [KeyboardButton("📅 План робіт"), KeyboardButton("📄 PDF-звіт")],
            [KeyboardButton("⚙️ Змінити культури"), KeyboardButton("❓ Допомога")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    async def ask_city(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        city = update.message.text.strip()
        user = update.effective_user
        save_farmer(user.id, city=city)
        await update.message.reply_text(
            f"✅ Місто: {city}. А які культури ви вирощуєте? (наприклад: пшениця, кукурудза, соняшник)"
        )
        return ASK_CROPS

    async def ask_crops(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        crops = update.message.text.strip()
        user = update.effective_user
        save_farmer(user.id, crops=crops)
        await update.message.reply_text(
            f"✅ Культури: {crops}.\nТепер у вас повний профіль! 🌾",
            reply_markup=self.get_main_menu()
        )
        return ConversationHandler.END

    async def update_crops_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Початок оновлення культур."""
        await update.message.reply_text(
            "✏️ Введіть нові культури (наприклад: пшениця, кукурудза):",
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_CROPS_UPDATE

    async def update_crops(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Збереження нових культур."""
        crops = update.message.text.strip()
        user = update.effective_user
        save_farmer(user.id, crops=crops)
        await update.message.reply_text(
            f"✅ Культури оновлено: {crops}",
            reply_markup=self.get_main_menu()
        )
        return ConversationHandler.END

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        if text == "🌱 Мої рослини":
            farmer = get_farmer(update.effective_user.id)
            if farmer and farmer[1]:
                await update.message.reply_text(f"Ви вирощуєте: {farmer[1]}")
            else:
                await update.message.reply_text("Спочатку вкажіть культури через /start")
        
        elif text == "🌤 Погода":
            farmer = get_farmer(update.effective_user.id)
            if farmer and farmer[0]:
                from weather import get_weather
                weather_info = get_weather(farmer[0])
                await update.message.reply_text(weather_info)
            else:
                await update.message.reply_text("Спочатку вкажіть місто через /start")
        
        elif text == "📅 План робіт":
            farmer = get_farmer(update.effective_user.id)
            if farmer and farmer[1]:
                from work_plan import get_work_plan
                tasks = get_work_plan(farmer[1])
                response = "📆 *Ваш план робіт на цей місяць:*\n\n" + "\n".join(tasks)
                await update.message.reply_text(response, parse_mode="Markdown")
            else:
                await update.message.reply_text("Спочатку вкажіть культури через /start")
        
        elif text == "📄 PDF-звіт":
            from pdf_report import generate_pdf_report
            import os
            import tempfile

            pdf_path = os.path.join(tempfile.gettempdir(), f"agro_report_{update.effective_user.id}.pdf")

            try:
                success = generate_pdf_report(update.effective_user.id, pdf_path)
                if success:
                    with open(pdf_path, "rb") as pdf_file:
                        await update.message.reply_document(
                            pdf_file,
                            caption="📄 Ваш агрономічний звіт (PDF)"
                        )
                else:
                    await update.message.reply_text("Спочатку заповніть профіль через /start")
            except Exception as e:
                await update.message.reply_text("⚠️ Помилка генерації PDF. Спробуйте пізніше.")
            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
        
        elif text == "⚙️ Змінити культури":
            return await self.update_crops_start(update, context)
        
        elif text == "❓ Допомога":
            help_text = (
                "ℹ️ *Як користуватися ботом:*\n\n"
                "1. Натисніть *🌱 Мої рослини*, щоб побачити культури.\n"
                "2. *🌤 Погода* — прогноз для вашого регіону.\n"
                "3. *📅 План робіт* — що робити цього місяця.\n"
                "4. *📄 PDF-звіт* — зберегти план у форматі PDF.\n"
                "5. *⚙️ Змінити культури* — оновити список культур.\n\n"
                "Усі дані зберігаються автоматично!"
            )
            await update.message.reply_text(help_text, parse_mode="Markdown")
        
        else:
            await update.message.reply_text("Не розумію. Оберіть опцію з меню.")
# Головна функція
def main():
    init_db()  # створює базу при запуску
    bot = XFarmBot()
    app = ApplicationBuilder().token(TOKEN).build()

        # Діалог для збору профілю та оновлення культур
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", bot.start),
            MessageHandler(filters.Regex("^⚙️ Змінити культури$"), bot.update_crops_start)
        ],
        states={
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.ask_city)],
            ASK_CROPS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.ask_crops)],
            ASK_CROPS_UPDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.update_crops)],
        },
        fallbacks=[CommandHandler("start", bot.start)]
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))

    print("✅ X Farm Bot із збереженням даних запущено!")
    app.run_polling()

if __name__ == "__main__":
    main()