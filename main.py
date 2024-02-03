import logging
import os

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from parser import check_website

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def start(update: Update, _) -> None:
    await update.message.reply_text("Hi! Use /set <time interval [seconds/minutes/days]>"
                                    "<amount> (example /set m30) to set periodic task.")


async def check(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job

    links = await check_website()

    for key, values in links.items():
        await context.bot.send_message(job.chat_id, text=f"{values['link']}\n{values['price']} руб.")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""

    current_jobs = context.job_queue.get_jobs_by_name(name)

    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:

        args_dict = {'d': 'days', 's': 'seconds', 'm': 'minutes'}
        period = context.args[0]

        unit = period[0]
        if unit not in args_dict:
            await update.effective_message.reply_text("Sorry we can not figure out this period setting!")
            return

        try:
            value = int(period[1:])
        except Exception as e:
            print(e)
            await update.effective_message.reply_text("Sorry we can not figure out this period setting!")
            return

        if value < 0:
            await update.effective_message.reply_text("Sorry we can not figure out this period setting!")
            return

        datetime_start = datetime.now(timezone.utc)
        delta_args = {args_dict[unit]: value}
        delta = timedelta(**delta_args)

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(check, interval=delta, first=datetime_start, chat_id=chat_id, name=str(chat_id))

        text = "Job successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)


async def healthcheck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    current_jobs = context.job_queue.jobs()
    text = f"{current_jobs=}"
    await update.message.reply_text(text)


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ.get('TG_TOKEN')).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.add_handler(CommandHandler("healthcheck", healthcheck))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
