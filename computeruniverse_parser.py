import os
import time

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def get_perf_log_on_load(url, headless=True, filter=None):
    # init Chrome driver (Selenium)
    options = Options()
    options.add_experimental_option('w3c', False) ### added this line
    options.headless = headless
    cap = DesiredCapabilities.CHROME
    cap["loggingPrefs"] = {"performance": "ALL"}
    ### installed chromedriver.exe and identify path
    chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')
    driver = webdriver.Chrome(executable_path=chromedriver_path, desired_capabilities=cap, options=options)
    # record and parse performance log
    driver.get(url)
    time.sleep(5)
    if filter:
        log = [item for item in driver.get_log("performance") if filter in str(item)]
    else:
        log = driver.get_log("performance")
    driver.close()

    return log


def scroll_page(driver):
    for scroll_height in range(1000, 12001, 500):
        js_scroll_script = r'window.scrollTo({{top: {}, behavior: "smooth"}});'.format(scroll_height)
        driver.execute_script(js_scroll_script)
        time.sleep(1)

    driver.execute_script('window.scrollTo({left: 0, top: document.body.scrollHeight, behavior: "smooth"});')


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


def parse_graphic_cards_page(driver):
    soup = BeautifulSoup(driver.page_source, 'lxml')
    # graphic_cards_selector = '.c-pl__main--rows .c-productItem'
    # graphic_cards = soup.select(graphic_cards_selector)
    graphic_cards_names_tags_selector = '.c-pl__main--rows .c-productItem .c-productItem__head a'
    graphic_cards_names_tags = soup.select(graphic_cards_names_tags_selector)
    graphic_cards_names = [graphic_card_name_tag.text for graphic_card_name_tag in graphic_cards_names_tags if graphic_card_name_tag.text]
    print(graphic_cards_names)

    # for graphic_card_name in graphic_cards_names:
    #     print(graphic_card_name)

    graphic_cards_prices_tags_selector = '.c-pl__main--rows .c-productItem .price-box span' #  span
    graphic_cards_prices_tags = soup.select(graphic_cards_prices_tags_selector)
    print(graphic_cards_prices_tags)
    graphic_cards_prices = [graphic_card_price_tag.text for graphic_card_price_tag in graphic_cards_prices_tags]
    print(graphic_cards_prices)

    combined_prices = combine_prices(graphic_cards_prices)

    return graphic_cards_names, combined_prices


def parse_last_page_number(driver):
    soup = BeautifulSoup(driver.page_source, 'lxml')

    pagination_tags_selector = 'ul.Pagination li'
    pagination_tags = soup.select(pagination_tags_selector)
    pagination_numbers = [pagination_tag.text for pagination_tag in pagination_tags if pagination_tag.text]
    last_page_number = int(pagination_numbers[-1])

    return last_page_number


def go_next_page(driver):
    next_page_css_selector = 'ul.Pagination li.Pagination__naviButton button.Pagination__naviButton__inner span.icon-arrow'
    next_page_link = driver.find_elements_by_css_selector(next_page_css_selector)[-1]
    print(next_page_link)
    next_page_link.click()


def prepare_parsed_graphic_cards_page(parsed_graphic_cards_page):
    graphic_cards_names, combined_prices = parsed_graphic_cards_page

    graphic_cards_page = []
    for name, price in zip(graphic_cards_names, combined_prices):
        graphic_card = {}
        graphic_card['name'] = name
        graphic_card['price'] = price

        graphic_cards_page.append(graphic_card)

    return graphic_cards_page


def main():
    # graphic_cards_prices = ['NEW', '285,71\xa0€', '267,23\xa0€', '40\xa0084,50\xa0₽']
    # graphic_cards_names = ['EVGA GeForce GTX1650 SC Ultra 4GB', '']
    # graphic_cards_prices = ['NEW', '285,71\xa0€', '267,23\xa0€', '40\xa0084,50\xa0₽', '233,23\xa0€', '40\xa0000,50\xa0₽']

    # graphic_cards_prices = ['Old price', '252,09\xa0€', '226,88\xa0€', '34\xa0032,00\xa0₽', 'Old price', '268,90\xa0€', '242,86\xa0€', '36\xa0429,00\xa0₽', 'Old price', '1.158,82\xa0€', '1.050,41\xa0€', '157\xa0561,50\xa0₽', 'Old price', '647,05\xa0€', '613,44\xa0€', '92\xa0016,00\xa0₽', 'Old price', '830,22\xa0€', '747,06\xa0€', '112\xa0059,00\xa0₽', 'Old price', '959,08\xa0€', '831,09\xa0€', '124\xa0663,50\xa0₽', 'Old price', '1.268,07\xa0€', '1.168,06\xa0€', '175\xa0209,00\xa0₽', 'Old price', '952,30\xa0€', '836,13\xa0€', '125\xa0419,50\xa0₽', 'Old price', '827,94\xa0€', '755,46\xa0€', '113\xa0319,00\xa0₽', 'Old price', '1.462,18\xa0€', '1.385,71\xa0€', '207\xa0856,50\xa0₽', 'Old price', '1.256,30\xa0€', '1.134,45\xa0€', '170\xa0167,50\xa0₽', 'Old price', '1.276,47\xa0€', '1.088,24\xa0€', '163\xa0236,00\xa0₽', 'Old price', '628,54\xa0€', '545,38\xa0€', '81\xa0807,00\xa0₽', 'Old price', '797,48\xa0€', '713,45\xa0€', '107\xa0017,50\xa0₽', 'Old price', '588,23\xa0€', '352,10\xa0€', '52\xa0815,00\xa0₽', 'Old price', '494,96\xa0€', '445,34\xa0€', '66\xa0801,00\xa0₽', '1.663,03\xa0€', '249\xa0454,50\xa0₽', 'Old price', '403,35\xa0€', '294,11\xa0€', '44\xa0116,50\xa0₽', 'Old price', '378,14\xa0€', '344,53\xa0€', '51\xa0679,50\xa0₽', 'Old price', '478,15\xa0€', '377,31\xa0€', '56\xa0596,50\xa0₽']
    # graphic_cards_names = ['GIGABYTE Radeon RX 6500 XT EAGLE 4GB', '', 'Gigabyte Radeon RX 6500 XT Gaming OC 4GB', '', 'GIGABYTE GeForce RTX3080 GAMING OC LHR 12GB', '', 'GIGABYTE AORUS GeForce RTX 3060 Ti Elite Rev.2 LHR 8GB', '', 'GIGABYTE GeForce RTX 3070 Ti VISION OC 8GB', '', 'GIGABYTE AORUS GeForce RTX 3070 Ti MASTER LHR 8GB', '', 'Gigabyte Radeon RX6900XT Gaming OC 16.0 GB OC  Enthusiast graphics card', '', 'MSI Radeon RX6800 Gaming X Trio 16.0 GB  Enthusiast graphics card', '', 'MSI GeForce RTX 3070 Ti VENTUS 3X OC 8.0 GB OC  Enthusiast graphics card', '', 'MSI GeForce RTX 3080 Ti SUPRIM X 12 GB  Enthusiast graphics card', '', 'GIGABYTE AORUS GeForce RTX3080 MASTER LHR 12GB', '', 'MSI GeForce RTX 3080 GAMING Z TRIO LHR 12GB', '', 'MSI GeForce RTX 3060 Ti GAMING X 8G LHR 8GB', '', 'GIGABYTE GeForce RTX 3070 Ti Gaming OC LHR 8.0 GB OC  Enthusiast graphics card', '', 'MSI GeForce RTX2060 VENTUS GP OC 6.0 GB', '', 'MSI GeForce RTX 3060 GAMING X LHR 12 GB', '', 'MSI GeForce RTX3090 GAMING X TRIO 24 GB  Enthusiast graphics card', '', 'GIGABYTE GeForce GTX 1660 OC 6G 6.0 GB OC  High End graphics card', '', 'GIGABYTE GeForce RTX 3050 GAMING OC 8GB', '', 'MSI GeForce RTX 2060 VENTUS 12G OC 12GB', '']
    # combined_prices = combine_prices(graphic_cards_prices)


    chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')
    driver = webdriver.Chrome(chromedriver_path)

    url = 'https://www.computeruniverse.net/en/c/hardware-components/pci-express-graphics-cards?page=1'
    driver.get(url)

    time.sleep(5)
    last_page_number = parse_last_page_number(driver)

    graphic_cards = []
    for page_number in range(1, last_page_number + 1):
        time.sleep(5)
        scroll_page(driver)
        time.sleep(5)

        parsed_graphic_cards_page = parse_graphic_cards_page(driver)

        graphic_cards_page = prepare_parsed_graphic_cards_page(parsed_graphic_cards_page)


        graphic_cards.extend(graphic_cards_page)

        go_next_page(driver)

    print(graphic_cards)

    time.sleep(10)
    driver.quit()


if __name__ == '__main__':
    main()
