import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from storage.models import GraphicCard
from storage.models import TelegramUser
from storage.management.commands.telegram_bot import TelegramBot

import schedule


class Command(BaseCommand):
    help = 'Script check parsing results and push tg users if graphic cards prices was updated'

    def notify(self):
        telegram_bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)
        is_notify = telegram_bot.notify_tg_users_about_graphic_cards_price_change()

        if is_notify:
            self.stdout.write(self.style.SUCCESS('New updated cards was found. Telegram users was notified successfully.'))
        else:
            self.stdout.write(self.style.WARNING('New updated cards was not found.'))

    def handle(self, *args, **options):

        schedule.every(3).seconds.do(self.notify)

        while True:
            schedule.run_pending()
            time.sleep(1)
