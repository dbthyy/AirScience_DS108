import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
import re


def crawl_planetrip(url, brand):
    driver = webdriver.Edge()
    driver.get(url)
    sleep(5)
    wait = WebDriverWait(driver, 50)

    check_direct_flight = wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//div[@class='css-1dbjc4n r-1awozwy r-18u37iz r-633pao']"
        "//div[@class='css-1dbjc4n r-1awozwy r-k200y r-1loqt21 r-18u37iz r-t60dpp r-1otgn73']"
    )))
    ActionChains(driver).move_to_element(check_direct_flight).click().perform()

    def click_brand_checkbox(driver, brand):
        try:
            xpath_brand_checkbox = f"//div[@data-testid='airline-filter-collapsible-item-{brand}']//div[contains(@class, 'r-t60dpp')]"
            checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpath_brand_checkbox))
            )
            ActionChains(driver).move_to_element(checkbox).click().perform()
        except (TimeoutException, NoSuchElementException):
            return False
        return True
    if brand:
        has_result = click_brand_checkbox(driver, brand)
        if not has_result:
            driver.quit()
            return False

    df = pd.DataFrame(
        columns=[
            'flight_id',
            'brand',
            'price',
            'start_time',
            'start_day',
            'end_time',
            'end_day',
            'destination',
            'trip_time',
            'hand_luggage',
            'checked_baggage',
            'crawl_date'])

    flight_id = []
    brand = []
    price = []
    start_time = []
    start_day = []
    end_time = []
    end_day = []
    destination = []
    trip_time = []
    hand_luggage = []
    checked_baggage = []
    crawl_date = []
    today = datetime.datetime.now().strftime('%d-%m-%Y')
    crawl_date = [today] * 1000

    # Cuộn trang để tải dữ liệu
    initial_page_length = driver.execute_script(
        "return document.body.scrollHeight")
    num_steps = 1000000
    scroll_step = initial_page_length // 200
    for i in range(num_steps):
        scroll_position = scroll_step * (i + 1)
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        driver.execute_script("return window.scrollY")
        new_height = driver.execute_script("return document.body.scrollHeight")

        if scroll_position >= new_height:
            break
    driver.execute_script("window.scrollTo(0, 0)")

    # Lấy dữ liệu từ trang web
    elements = driver.find_elements(
        By.XPATH,
        "//div[@class='css-1dbjc4n r-9nbb9w r-otx420 r-1i1ao36 r-1x4r79x']"
    )

    brand_elements = wait.until(EC.visibility_of_all_elements_located((
        By.XPATH,
        "//div[@class='css-1dbjc4n r-1habvwh r-18u37iz r-1ssbvtb']//"
        "div[@class='css-901oao css-cens5h r-uh8wd5 r-majxgm r-fdjqy7']"
    )))
    price_elements = wait.until(EC.visibility_of_all_elements_located((
        By.XPATH,
        "//div[@class='css-1dbjc4n r-obd0qt r-eqz5dr r-9aw3ui r-knv0ih r-ggk5by']"
        "//h3[@class='css-4rbku5 css-901oao r-uh8wd5 r-b88u0q r-rjixqe r-fdjqy7']"
    )))
    detail = wait.until(EC.visibility_of_all_elements_located((
        By.XPATH,
        "//div[@class='css-1dbjc4n r-13awgt0 r-18u37iz r-f4gmv6 r-1777fci']"
    )))

    old_element = []
    for i, j in zip(range(len(elements)), detail):
        if elements[i] in old_element:
            continue
        ActionChains(driver).move_to_element(j).click().perform()

        old_element.append(elements[i])

        flight_id.append(i + 1)

        brand.append(brand_elements[i].text)

        price.append(price_elements[i].text)

        start_time_elements = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='css-1dbjc4n r-e8mqni r-1d09ksm r-1h0z5md r-ttb5dx']"
                 "//div[@class='css-901oao r-uh8wd5 r-1b43r93 r-majxgm r-rjixqe r-5oul0u r-fdjqy7']")))
        start_time.append(start_time_elements.text)

        end_time_elements = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH,
                 "//div[@class='css-1dbjc4n r-e8mqni r-1d09ksm r-1h0z5md r-q3we1 r-ttb5dx']"
                 "//div[@class='css-901oao r-uh8wd5 r-1b43r93 r-majxgm r-rjixqe r-fdjqy7']")))
        end_time.append(end_time_elements.text)

        start_date_elements = wait.until(EC.visibility_of_element_located((
            By.XPATH,
            "//div[@class='css-1dbjc4n r-e8mqni r-1d09ksm r-1h0z5md r-ttb5dx']"
            "//div[@class='css-901oao r-uh8wd5 r-majxgm r-fdjqy7']"
        )))
        start_day.append(start_date_elements.text)

        end_date_elements = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH,
                 "//div[@class='css-1dbjc4n r-e8mqni r-1d09ksm r-1h0z5md r-q3we1 r-ttb5dx']"
                 "//div[@class='css-901oao r-uh8wd5 r-majxgm r-fdjqy7']")))

        end_day.append(end_date_elements.text)

        trip_time_elements = wait.until(EC.visibility_of_element_located((
            By.XPATH,
            "//div[@class='css-901oao r-13awgt0 r-uh8wd5 r-majxgm r-fdjqy7']"
        )))
        trip_time.append(trip_time_elements.text)

        destination_elements = wait.until(EC.visibility_of_element_located((
            By.XPATH,
            "//div[@class='css-1dbjc4n r-e8mqni r-1habvwh r-13awgt0 r-1h0z5md r-q3we1']"
        )))
        destination.append(destination_elements.text)

        baggage_element = wait.until(EC.presence_of_all_elements_located((
            By.XPATH,
            "//div[@class='css-901oao r-13awgt0 r-uh8wd5 r-1b43r93 r-majxgm r-rjixqe r-19u6a5r r-fdjqy7']"
        )))
        for baggage in baggage_element:
            text = baggage.text.lower()
            match = re.search(r'(\d+)\s*kg', text)
            weight = int(match.group(1)) if match else 0
            if "xách tay" in text:
                hand_luggage.append(weight)
            elif "hành lý" in text:
                checked_baggage.append(weight)

    new_df = pd.DataFrame(list(zip(flight_id,
                                   brand,
                                   price,
                                   start_time,
                                   start_day,
                                   end_time,
                                   end_day,
                                   trip_time,
                                   destination,
                                   hand_luggage,
                                   checked_baggage,
                                   crawl_date)),
                          columns=['flight_id',
                                   'brand',
                                   'price',
                                   'start_time',
                                   'start_day',
                                   'end_time',
                                   'end_day',
                                   'trip_time',
                                   'destination',
                                   'hand_luggage',
                                   'checked_baggage',
                                   'crawl_date'])

    df = pd.concat([df, new_df], axis=0, ignore_index=True)

    flight_id = []
    brand = []
    price = []
    start_time = []
    end_time = []
    start_day = []
    end_day = []
    trip_time = []
    destination = []
    hand_luggage = []
    checked_baggage = []
    crawl_date = [today] * 1000
    j.click()
    sleep(5)

    df.to_csv('planetrip_raw.csv', index=False, encoding='utf-8-sig')
    driver.quit()
    return True


def filter_user_inputs(filename='user_input.csv'):
    user_input = pd.read_csv(filename)
    if user_input.empty:
        return False

    row = user_input.iloc[0]
    hand_luggage = int(row['hand_luggage'])
    checked_baggage = int(row['checked_baggage'])
    start_hour = row['start_hour']
    destination = row['destination']

    df = pd.read_csv('planetrip_raw.csv')
    if df is None or df.empty:
        return False

    def in_time_slot(row, input_slot):
        try:
            start_time_str = str(row['start_time']).strip()
            if 'h' in start_time_str:
                hour = int(start_time_str.split('h')[0])
            elif ':' in start_time_str:
                hour = int(start_time_str.split(':')[0])
            else:
                return False
            start_str, end_str = input_slot.split('-')
            start_hour = int(start_str.strip().split(':')[0])
            end_hour = int(end_str.strip().split(':')[0])
            return start_hour <= hour < end_hour
        except BaseException:
            return False
    df = df[df.apply(lambda row: in_time_slot(row, start_hour), axis=1)]

    def direct_flight(row):
        text = row['destination']
        match = re.search(r'\((\w{3})\)', text)
        if match:
            return destination == match.group(1)
    df = df[df.apply(direct_flight, axis=1)]

    df['destination'] = df['destination'].replace(
        'Hà Nội (HAN)\r\nSân bay Nội Bài\r\nNhà ga 1',
        'Hà Nội (HAN)\r\nSân bay Nội Bài'
    )

    df['price'] = df['price'].str.extract(r'([\d\.]+)')

    def check_luggage(row, hand_luggage, checked_baggage):
        return (row['hand_luggage'] >= hand_luggage) and (
            row['checked_baggage'] >= checked_baggage)
    df = df[df.apply(lambda row: check_luggage(
        row, hand_luggage, checked_baggage), axis=1)]

    df = df.reset_index(drop=True)
    if df.empty:
        return False
    df.to_csv('planetrip_filtered.csv', index=False, encoding='utf-8-sig')
    return True
