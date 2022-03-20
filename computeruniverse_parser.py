import os
import time
from urllib.parse import urljoin

from selenium import webdriver
from bs4 import BeautifulSoup
from tqdm import tqdm


def scroll_page(driver):
    for scroll_height in range(1000, 12001, 500):
        js_scroll_script = r'window.scrollTo({{top: {}, behavior: "smooth"}});'.format(scroll_height)
        driver.execute_script(js_scroll_script)
        time.sleep(1)

    driver.execute_script('window.scrollTo({left: 0, top: document.body.scrollHeight, behavior: "smooth"});')


def go_next_page(driver):
    next_page_css_selector = 'ul.Pagination li.Pagination__naviButton button.Pagination__naviButton__inner span.icon-arrow'
    next_page_link = driver.find_elements_by_css_selector(next_page_css_selector)[-1]
    next_page_link.click()


def combine_prices(prices):
    combined_prices = []
    price_sequence = {}

    price_sequence_start_index = 0
    for index, price in enumerate(prices):
        if price.replace(' ','').isalpha():
            old_price_index = index + 1
            current_eur_price_index = index + 2
            current_rub_price_index = index + 3
            price_sequence_start_index = index + 4
            continue
        elif index == price_sequence_start_index:
            current_eur_price_index = index
            current_rub_price_index = index + 1
            price_sequence_start_index = index + 2

        price = float(price.replace('\xa0', '').replace('.', '').replace(',', '.')[:-1])

        if index == old_price_index:
            price_sequence['old_price'] = price
        elif index == current_eur_price_index:
            price_sequence['current_eur_price'] = price
        elif index == current_rub_price_index:
            price_sequence['current_rub_price'] = price
            combined_prices.append(price_sequence)

            price_sequence = {}

    return combined_prices


def parse_last_page_number(driver):
    soup = BeautifulSoup(driver.page_source, 'lxml')

    pagination_tags_selector = 'ul.Pagination li'
    pagination_tags = soup.select(pagination_tags_selector)
    pagination_numbers = [pagination_tag.text for pagination_tag in pagination_tags if pagination_tag.text]
    last_page_number = int(pagination_numbers[-1])

    return last_page_number


def parse_graphic_cards_page(driver):
    soup = BeautifulSoup(driver.page_source, 'lxml')

    graphic_cards_names_tags_selector = '.c-pl__main--rows .c-productItem .c-productItem__head a'
    graphic_cards_names_tags = soup.select(graphic_cards_names_tags_selector)
    graphic_cards_names = [graphic_card_name_tag.text for graphic_card_name_tag in graphic_cards_names_tags if graphic_card_name_tag.text]

    graphic_cards_relative_urls_tags_selector = '.c-pl__main--rows .c-productItem .c-productItem__head a[href]'
    graphic_cards_relative_urls_tags = soup.select(graphic_cards_relative_urls_tags_selector)
    graphic_cards_relative_urls = [graphic_card_relative_url_tag['href'] for graphic_card_relative_url_tag in graphic_cards_relative_urls_tags if graphic_card_relative_url_tag.text]

    graphic_cards_prices_tags_selector = '.c-pl__main--rows .c-productItem .price-box span' #  span
    graphic_cards_prices_tags = soup.select(graphic_cards_prices_tags_selector)
    graphic_cards_prices = [graphic_card_price_tag.text for graphic_card_price_tag in graphic_cards_prices_tags]

    return graphic_cards_names, graphic_cards_relative_urls, graphic_cards_prices


def prepare_parsed_graphic_cards_page(parsed_graphic_cards_page):
    graphic_cards_names, graphic_cards_relative_urls, graphic_cards_prices = parsed_graphic_cards_page

    graphic_cards_full_urls = [urljoin('https://www.computeruniverse.net/', graphic_card_relative_url) for graphic_card_relative_url in graphic_cards_relative_urls]
    graphic_cards_combined_prices = combine_prices(graphic_cards_prices)

    graphic_cards_page = []
    for name, url, price in zip(graphic_cards_names, graphic_cards_full_urls, graphic_cards_combined_prices):
        graphic_card = {}
        graphic_card['name'] = name
        graphic_card['url'] = url
        graphic_card['price'] = price

        graphic_cards_page.append(graphic_card)

    return graphic_cards_page


def parse_graphic_cards_catalogue(driver):
    url = 'https://www.computeruniverse.net/en/c/hardware-components/pci-express-graphics-cards?page=1'
    driver.get(url)

    time.sleep(5)
    last_page_number = parse_last_page_number(driver)
    pages_numbers = range(1, last_page_number + 1)

    graphic_cards = []
    for page_number in tqdm(pages_numbers):
        time.sleep(5)
        scroll_page(driver)
        time.sleep(5)

        parsed_graphic_cards_page = parse_graphic_cards_page(driver)
        graphic_cards_page = prepare_parsed_graphic_cards_page(parsed_graphic_cards_page)
        graphic_cards.extend(graphic_cards_page)

        go_next_page(driver)

    return graphic_cards


def main():
    chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')
    driver = webdriver.Chrome(chromedriver_path)

    graphic_cards = parse_graphic_cards_catalogue(driver)

    print(graphic_cards)

    time.sleep(10)
    driver.quit()


if __name__ == '__main__':
    main()
