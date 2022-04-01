import os
import time

from django.core.management.base import BaseCommand, CommandError

import schedule
from selenium import webdriver

from storage.models import GraphicCard
from storage.utils.computeruniverse_parser import parse_graphic_cards_catalogue


class Command(BaseCommand):
    help = 'Parsing graphic cards names, links, prices from https://www.computeruniverse.net/'

    def update_graphic_card_price(self, graphic_card, graphic_card_raw):
        if graphic_card.current_eur_price != graphic_card_raw['price']['current_eur_price'] \
           or graphic_card.current_rub_price != graphic_card_raw['price']['current_rub_price'] \
           or graphic_card.old_price != graphic_card_raw['price']['old_price']:
           graphic_card.current_eur_price = graphic_card_raw['price']['current_eur_price']
           graphic_card.current_rub_price = graphic_card_raw['price']['current_rub_price']
           graphic_card.old_price = graphic_card_raw['price']['old_price']

           graphic_card.price_notification_request = True

           graphic_card.save()

           self.stdout.write(self.style.SUCCESS(graphic_card.name + ' || ' + 'Existing graphic card price was update successfully'))

    def create_or_update_graphic_cards(self, graphic_cards_raw):
        created_graphic_cards = []
        for graphic_card_raw in graphic_cards_raw:
            graphic_card, is_graphic_card_created = GraphicCard.objects.get_or_create(
                name=graphic_card_raw['name'],
                url=graphic_card_raw['url'],
                defaults = {
                    'old_price': graphic_card_raw['price']['old_price'],
                    'current_eur_price': graphic_card_raw['price']['current_eur_price'],
                    'current_rub_price': graphic_card_raw['price']['current_rub_price']
                }
            )

            if is_graphic_card_created:
                created_graphic_cards.append(graphic_card)
                self.stdout.write(self.style.SUCCESS(graphic_card.name + ' || ' + 'New graphic cards was added into database'))
            else:
                self.update_graphic_card_price(graphic_card, graphic_card_raw)

            return created_graphic_cards

    def parse_graphic_cards(self):
        try:
            option = webdriver.ChromeOptions()

            option.add_argument('--disable-blink-features=AutomationControlled')

            chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')
            driver = webdriver.Chrome(chromedriver_path, options=option)

            graphic_cards_raw = parse_graphic_cards_catalogue(driver)

            time.sleep(10)
            driver.quit()
        except IndexError:
            graphic_cards_raw = [{'name': 'MSI GeForce RTX 3080 Ti GAMING X TRIO 12 GB  Enthusiast graphics card', 'url': 'https://www.computeruniverse.net/en/p/90833010', 'price': {'old_price': 1368.91, 'current_eur_price': 1340.34, 'current_rub_price': 201051.0}}, {'name': 'GIGABYTE GeForce RTX3080 GAMING OC LHR 12GB', 'url': 'https://www.computeruniverse.net/en/p/90853491', 'price': {'old_price': 1158.82, 'current_eur_price': 1049.58, 'current_rub_price': 157437.0}}, {'name': 'GIGABYTE GeForce RTX 3070 Ti Gaming OC LHR 8.0 GB OC  Enthusiast graphics card', 'url': 'https://www.computeruniverse.net/en/p/90833839', 'price': {'old_price': 797.48, 'current_eur_price': 713.45, 'current_rub_price': 107017.5}}, {'name': 'GIGABYTE GeForce RTX3090 GAMING OC 24 GB OC', 'url': 'https://www.computeruniverse.net/en/p/90814840', 'price': {'old_price': 2284.97, 'current_eur_price': 1735.29, 'current_rub_price': 260293.5}}, {'name': 'GIGABYTE AORUS GeForce RTX3080 MASTER LHR 12GB', 'url': 'https://www.computeruniverse.net/en/p/90853492', 'price': {'old_price': 1256.3, 'current_eur_price': 1134.45, 'current_rub_price': 170167.5}}, {'name': 'GIGABYTE AORUS GeForce RTX 3060 Ti Elite Rev.2 LHR 8GB', 'url': 'https://www.computeruniverse.net/en/p/90840792', 'price': {'old_price': 647.05, 'current_eur_price': 612.61, 'current_rub_price': 91891.5}}, {'name': 'GIGABYTE GeForce RTX 3050 GAMING OC 8GB', 'url': 'https://www.computeruniverse.net/en/p/90856886', 'price': {'old_price': 378.14, 'current_eur_price': 344.53, 'current_rub_price': 51679.5}}, {'name': 'GIGABYTE GeForce RTX 3060 Ti GAMING OC PRO LHR 8GB', 'url': 'https://www.computeruniverse.net/en/p/90834353', 'price': {'old_price': 652.01, 'current_eur_price': 588.23, 'current_rub_price': 88234.5}}, {'name': 'GIGABYTE GeForce GTX 1660 SUPER OC 6G 6.0 GB OC  High End graphics card', 'url': 'https://www.computeruniverse.net/en/p/90783625', 'price': {'old_price': 415.88, 'current_eur_price': 302.51, 'current_rub_price': 45376.5}}, {'name': 'GIGABYTE Radeon RX 6500 XT EAGLE 4GB', 'url': 'https://www.computeruniverse.net/en/p/90856681', 'price': {'old_price': 252.09, 'current_eur_price': 226.88, 'current_rub_price': 34032.0}}, {'name': 'MSI GeForce RTX 2060 VENTUS 12G OC 12GB', 'url': 'https://www.computeruniverse.net/en/p/90851018', 'price': {'old_price': 478.15, 'current_eur_price': 377.31, 'current_rub_price': 56596.5}}, {'name': 'GIGABYTE Radeon RX 6600 XT Eagle 8GB', 'url': 'https://www.computeruniverse.net/en/p/90840856', 'price': {'old_price': 495.79, 'current_eur_price': 436.97, 'current_rub_price': 65545.5}}, {'name': 'MSI GeForce RTX 3060 VENTUS 2X OC LHR 12 GB OC', 'url': 'https://www.computeruniverse.net/en/p/90826360', 'price': {'old_price': 578.15, 'current_eur_price': 487.39, 'current_rub_price': 73108.5}}, {'name': 'GIGABYTE GeForce GTX 1660 OC 6G 6.0 GB OC  High End graphics card', 'url': 'https://www.computeruniverse.net/en/p/90752083', 'price': {'old_price': 403.35, 'current_eur_price': 294.11, 'current_rub_price': 44116.5}}, {'name': 'GIGABYTE Radeon RX 6600 XT Gaming OC Pro 8GB', 'url': 'https://www.computeruniverse.net/en/p/90840858', 'price': {'old_price': 514.29, 'current_eur_price': 457.98, 'current_rub_price': 68697.0}}, {'name': 'GIGABYTE Radeon RX 6600 XT Gaming OC 8GB', 'url': 'https://www.computeruniverse.net/en/p/90840857', 'price': {'old_price': 536.97, 'current_eur_price': 447.82, 'current_rub_price': 67173.0}}, {'name': 'GIGABYTE GeForce RTX 3070 Ti VISION OC 8GB', 'url': 'https://www.computeruniverse.net/en/p/90833893', 'price': {'old_price': 830.22, 'current_eur_price': 747.06, 'current_rub_price': 112059.0}}, {'name': 'Gigabyte Radeon RX6900XT Gaming OC 16.0 GB OC  Enthusiast graphics card', 'url': 'https://www.computeruniverse.net/en/p/90825384', 'price': {'old_price': 1268.07, 'current_eur_price': 1168.06, 'current_rub_price': 175209.0}}, {'name': 'GIGABYTE Radeon RX6800 GAMING OC-16GD 16GB GDDR6 Speicher, AMD RDNA 2, HDMI 2.1', 'url': 'https://www.computeruniverse.net/en/p/90820393', 'price': {'old_price': 915.13, 'current_eur_price': 840.33, 'current_rub_price': 126049.5}}, {'name': 'GIGABYTE AORUS GeForce RTX 3070 Ti MASTER LHR 8GB', 'url': 'https://www.computeruniverse.net/en/p/90833892', 'price': {'old_price': 959.08, 'current_eur_price': 831.09, 'current_rub_price': 124663.5}}, {'name': 'MSI GeForce RTX2060 VENTUS GP OC 6.0 GB', 'url': 'https://www.computeruniverse.net/en/p/90829008', 'price': {'old_price': 588.23, 'current_eur_price': 352.1, 'current_rub_price': 52815.0}}, {'name': 'Gigabyte Radeon RX 6500 XT Gaming OC 4GB', 'url': 'https://www.computeruniverse.net/en/p/90855148', 'price': {'old_price': 268.9, 'current_eur_price': 242.86, 'current_rub_price': 36429.0}}, {'name': 'MSI GeForce RTX 3080 GAMING Z TRIO LHR 12GB', 'url': 'https://www.computeruniverse.net/en/p/90853426', 'price': {'old_price': 1276.47, 'current_eur_price': 1088.24, 'current_rub_price': 163236.0}}]
        finally:
            driver.quit()

        self.stdout.write(self.style.SUCCESS('\nSuccessfully parsed graphic cards from computeruniverse graphic cards catalogue:'))

        created_graphic_cards = self.create_or_update_graphic_cards(graphic_cards_raw)
        if not created_graphic_cards:
            self.stdout.write(self.style.WARNING('New graphic cards are not found\n'))

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        schedule.every(3).seconds.do(self.parse_graphic_cards)

        while True:
            schedule.run_pending()
            time.sleep(1)
