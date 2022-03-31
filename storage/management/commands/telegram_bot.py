from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from storage.models import GraphicCard
from storage.models import TelegramUser

import telebot


class IsAccess(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the user have activate account with permission to access bot functionality or not
    key='is_access'

    @staticmethod
    def check(message: telebot.types.Message):
        telegram_user = TelegramUser.objects.get(telegram_id=message.from_user.id)

        return telegram_user.is_active


class TelegramBot(telebot.TeleBot):
    def __init__(self, token):
        super().__init__(token)
        bot = self

        def create_main_menu():
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True) #, one_time_keyboard=True)
            graphic_card_button = telebot.types.KeyboardButton("Видеокарты")
            bot_settings_button = telebot.types.KeyboardButton("Настройки бота")
            markup.add(graphic_card_button)
            markup.add(bot_settings_button)

            return markup

        def create_settings_menu():
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            min_graphic_card_price_button = telebot.types.KeyboardButton("Минимальная цена за видеокарту")
            max_graphic_card_price_button = telebot.types.KeyboardButton("Максимальная цена за видеокарту")
            main_menu_button = telebot.types.KeyboardButton("Главное меню")
            markup.add(min_graphic_card_price_button)
            markup.add(max_graphic_card_price_button)
            markup.add(main_menu_button)

            return markup

        def create_graphic_cards_output_template(graphic_cards):
            graphic_cards_output_template = ''
            for graphic_card in graphic_cards:
                graphic_card_output_template = f'*{graphic_card.name}*\
                                                 \nСтарая цена: {graphic_card.old_price} EUR\
                                                 \nНовая цена: {graphic_card.current_eur_price} EUR\
                                                 \nЦена по курсу: {graphic_card.current_rub_price} руб.\
                                                 \n{graphic_card.url}'
                graphic_cards_output_template = graphic_cards_output_template + graphic_card_output_template + '\n\n'

            return graphic_cards_output_template

        @bot.message_handler(commands=["start"])
        def start(message):
            telegram_user_id = message.from_user.id
            telegram_user, is_telegram_user_created = TelegramUser.objects.get_or_create(telegram_id=telegram_user_id)

            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            main_menu_button = telebot.types.KeyboardButton("Главное меню")
            markup.add(main_menu_button)

            if is_telegram_user_created:
                bot.send_message(
                    message.chat.id,
                    'Ваша учетная запись успешно зарегистрирована.\nОбратитесь к администратору ресурса для активации вашей учетной записи.',
                )
            elif not telegram_user.is_active:
                bot.send_message(
                    message.chat.id,
                    'Ваша учетная запись не активирована.\nОбратитесь к администратору ресурса для активации вашей учетной записи.',
                )
            else:
                bot.send_message(
                    message.chat.id,
                    'Ваша учетная запись успешно активирована.\nНажмите кнопку "Главное меню" для начала работы с ботом.',
                    reply_markup=markup
                )

        @bot.message_handler(commands=["MinPrice"], is_access=True)
        def get_min_price_filter(message):
            try:
                min_price = int(message.text.split()[-1])
                telegram_user = TelegramUser.objects.get(telegram_id=message.from_user.id)
                telegram_user.min_price = min_price
                telegram_user.save()
                bot.send_message(
                    message.chat.id,
                    f'Теперь вам будут показаны видеокарты начиная с {min_price} рублей.',
                )
            except ValueError:
                bot.send_message(
                    message.chat.id,
                    'Введите корректную цену числом. Пример ввода:\n/MinPrice 20000',
                )

        @bot.message_handler(commands=["MaxPrice"], is_access=True)
        def get_max_price_filter(message):
            try:
                max_price = int(message.text.split()[-1])
                telegram_user = TelegramUser.objects.get(telegram_id=message.from_user.id)
                telegram_user.max_price = max_price
                telegram_user.save()
                bot.send_message(
                    message.chat.id,
                    f'Теперь вам будут показаны видеокарты до {max_price} рублей.',
                )
            except ValueError:
                bot.send_message(
                    message.chat.id,
                    'Введите корректную цену числом. Пример ввода:\n/MaxPrice 100000',
                )

        @bot.message_handler(content_types=["text"], text=['Главное меню'], is_access=True)
        def handle_main_menu(message):
            bot.send_message(
                message.chat.id,
                'Нажми кнопку "Видеокарты", чтобы получить список имеющихся видеокарт.\nНажмите кнопку "Настройки", чтобы перейти к настройкам бота.',
                reply_markup=create_main_menu()
            )

        @bot.message_handler(content_types=["text"], text=['Настройки бота'], is_access=True)
        def handle_bot_settings(message):
            bot.send_message(
                message.chat.id,
                'Настройте бота. Ограничьте цены присылаемых вам видеокарт требуемым диапазоном.',
                reply_markup=create_settings_menu()
            )

        @bot.message_handler(content_types=["text"], text=['Видеокарты'], is_access=True)
        def handle_graphic_cards(message):
            telegram_user = TelegramUser.objects.get(telegram_id=message.from_user.id)
            graphic_cards = GraphicCard.objects.all()
            if telegram_user.min_price:
                graphic_cards = graphic_cards.filter(current_rub_price__gte=telegram_user.min_price)
            if telegram_user.max_price:
                graphic_cards = graphic_cards.filter(current_rub_price__lte=telegram_user.max_price)

            graphic_cards_output_template = create_graphic_cards_output_template(graphic_cards)

            splitted_text = telebot.util.smart_split(graphic_cards_output_template, chars_per_string=3000)
            for text in splitted_text:
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode="Markdown"
                )

        @bot.message_handler(content_types=["text"], text=['Минимальная цена за видеокарту'], is_access=True)
        def handle_min_price_filter(message):
            bot.send_message(
                message.chat.id,
                'Введите цену в рублях, начиная с которой вы хотите получать предложения видеокарт. Пример ввода:\n/MinPrice 20000',
            )

        @bot.message_handler(content_types=["text"], text=['Максимальная цена за видеокарту'], is_access=True)
        def handle_max_price_filter(message):
            bot.send_message(
                message.chat.id,
                'Введите цену в рублях, до которой вы хотите получать предложения видеокарт. Пример ввода:\n/MaxPrice 100000',
            )


class Command(BaseCommand):
    help = 'Telegram bot. Sending parsing results of computeruniverse graphic cards.'

    def handle(self, *args, **options):
        telegram_bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)
        telegram_bot.add_custom_filter(telebot.custom_filters.TextMatchFilter())
        telegram_bot.add_custom_filter(IsAccess())
        telegram_bot.infinity_polling()
