import os
import time

from django.core.management.base import BaseCommand, CommandError

import schedule
from selenium import webdriver

from storage.models import GraphicCard
from storage.utils.computeruniverse_parser import parse_graphic_cards_catalogue


class Command(BaseCommand):
    help = 'Parsing graphic cards names, links, prices from https://www.computeruniverse.net/'

    def check_price_change(self, graphic_card):
        pass

    def parse_graphic_cards(self):
        chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')
        driver = webdriver.Chrome(chromedriver_path)

        graphic_cards = parse_graphic_cards_catalogue(driver)

        time.sleep(10)
        driver.quit()

        self.stdout.write(self.style.SUCCESS('\nSuccessfully parsed graphic cards from computeruniverse graphic cards catalogue.\n\nNew graphic cards was added into database:'))

        created_graphic_cards = []
        for graphic_card in graphic_cards:
            graphic_card, is_graphic_card_created = GraphicCard.objects.get_or_create(
                name=graphic_card['name'],
                url=graphic_card['url'],
                defaults = {
                    'old_price': graphic_card['price']['old_price'],
                    'current_eur_price': graphic_card['price']['current_eur_price'],
                    'current_rub_price': graphic_card['price']['current_rub_price']
                }
            )

            if is_graphic_card_created:
                created_graphic_cards.append(graphic_card)
                self.stdout.write(self.style.SUCCESS(graphic_card.name))

        if not created_graphic_cards:
            self.stdout.write(self.style.WARNING('New graphic cards are not found\n'))

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        schedule.every(3).seconds.do(self.parse_graphic_cards)

        while True:
            schedule.run_pending()
            time.sleep(1)
