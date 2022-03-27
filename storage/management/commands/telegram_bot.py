from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from storage.models import GraphicCard

import telebot


class TelegramBot(telebot.TeleBot):
    def __init__(self, token):
        super().__init__(token)
        bot = self

        @bot.message_handler(commands=["start"])
        def start(message, res=False):
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            graphic_card_button = telebot.types.KeyboardButton("Видеокарты")
            markup.add(graphic_card_button)
            bot.send_message(
                message.chat.id,
                'Нажми кнопку "Видеокарты", чтобы получить список имеющихся видеокарт',
                reply_markup=markup
            )

        @bot.message_handler(content_types=["text"])
        def handle_text(message):
            if message.text.strip() == 'Видеокарты':
                graphic_cards = GraphicCard.objects.all()
                graphic_cards_names = str([graphic_card.name for graphic_card in graphic_cards])
                bot.send_message(
                    message.chat.id,
                    'Вы написали: ' + message.text +'\n' + graphic_cards_names
                )


class Command(BaseCommand):
    help = 'Telegram bot. Sending parsing results of computeruniverse graphic cards.'

    def handle(self, *args, **options):
        telegram_bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)
        telegram_bot.polling(none_stop=True, interval=0)
