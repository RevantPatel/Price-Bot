import os
import asyncio
import logging
import re
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from database import initialize, add_watch, get_user_watches, delete_watch, stream_watches, update_price
from scraper import fetch_product_details

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AMAZON_URL_PATTERN = r"https?://(www\.)?amazon\.([a-z\.]{2,5})/.*?/dp/([A-Z0-9]{10})"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Online.\n1. Paste Amazon Link.\n2. /list to view.\n3. /stop_ID to delete.")

def extract_amazon_url(url: str) -> str | None:
    match = re.search(AMAZON_URL_PATTERN, url)
    if match:
        return f"https://www.amazon.{match.group(2)}/dp/{match.group(3)}"
    return url if "amazon" in url and "/dp/" in url else None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message_text = update.message.text.strip()
        user_id = update.effective_user.id
        
        if "amazon" not in message_text and "amzn" not in message_text:
            await update.message.reply_text("Not an Amazon link.")
            return

        clean_url = extract_amazon_url(message_text) or message_text
        await update.message.reply_text("Checking price...")

        title, price = await asyncio.to_thread(fetch_product_details, clean_url)

        if title and price:
            if await add_watch(user_id, clean_url, title, price):
                await update.message.reply_text(f"Tracking Started!\n{title[:60]}...\nPrice: {price}")
            else:
                await update.message.reply_text("Already tracking this item.")
        else:
            await update.message.reply_text("Failed to fetch data.")
    except Exception as e:
        logging.error(f"CRITICAL ERROR in handle_message: {e}", exc_info=True)
        await update.message.reply_text("An internal error occurred. Please checks logs.")

async def list_watches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    watches = await get_user_watches(user_id)

    if not watches:
        await update.message.reply_text("List is empty.")
        return

    output = "Your Watchlist:\n\n"
    for row in watches:
        output += f"ID {row[0]} | {row[2]}\n{row[1][:30]}...\n/stop_{row[0]}\n\n"
    
    chunk_size = 4000
    for i in range(0, len(output), chunk_size):
        await update.message.reply_text(output[i:i+chunk_size])

async def stop_watch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        watch_id = int(update.message.text.split("_")[1])
        await delete_watch(watch_id, update.effective_user.id)
        await update.message.reply_text(f"Item {watch_id} deleted.")
    except Exception:
        await update.message.reply_text("Error deleting item.")

async def run_price_check(context: ContextTypes.DEFAULT_TYPE):
    try:
        logging.info("Starting background price check job...")
        connection, cursor = await stream_watches()
        try:
            while True:
                batch = await cursor.fetchmany(10)
                if not batch:
                    break
                
                tasks = [process_watch_check(context, row) for row in batch]
                await asyncio.gather(*tasks)
                await asyncio.sleep(2)
        finally:
            await cursor.close()
            await connection.close()
    except Exception as e:
        logging.error(f"CRITICAL ERROR in run_price_check: {e}", exc_info=True)

async def process_watch_check(context, row):
    try:
        watch_id, url, old_price, user_id, title = row
        _, new_price = await asyncio.to_thread(fetch_product_details, url)

        if new_price and new_price != old_price:
            diff = new_price - old_price
            emoji = "📉" if diff < 0 else "📈"
            
            if diff < 0:
                msg = f"{emoji} PRICE DROP!\n{title[:50]}...\nOld: {old_price}\nNew: {new_price}\nDiff: {diff:.2f}\n{url}"
                await context.bot.send_message(chat_id=user_id, text=msg)
            
            await update_price(watch_id, new_price)
    except Exception as e:
        logging.error(f"Error processing watch {row[0]}: {e}")

if __name__ == '__main__':
    logging.info("Initializing Bot...")
    
    # Check for token explicitly and log error if missing
    if not TELEGRAM_TOKEN:
        logging.critical("TELEGRAM_TOKEN is missing! Please set it in Railway Variables.")
        exit(1)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(initialize())
        logging.info("Database initialized.")

        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("list", list_watches))
        app.add_handler(MessageHandler(filters.Regex(r"^/stop_(\d+)$"), stop_watch))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        app.job_queue.run_repeating(run_price_check, interval=1800, first=10)
        
        logging.info("Bot is starting polling...")
        app.run_polling()
    except Exception as e:
        logging.critical(f"Bot execution failed: {e}", exc_info=True)