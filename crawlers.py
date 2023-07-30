from datetime import date, datetime
from typing import Dict, List, Literal, Tuple
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver

import requests


class InterparkCrawler:
    INTERPARK_MUSICAL_KIND_CODE: str = "01011"
    INTERPARK_CONSERT_KIND_CODE: str = "01003"

    def _extract_goods_code(self, base_html: str) -> List[str]:
        soup = BeautifulSoup(base_html, "html5lib")
        a_tag_list = soup.select("a")
        href_list = [a_tag["href"] for a_tag in a_tag_list]
        filtered_href = [
            href for href in href_list if len(href.split("GoodsCode=")) == 2
        ]
        return [href.split("GoodsCode=")[1] for href in filtered_href]

    def _get_uri_for_goods_list(self, kind_of_goods: str, play_date: str) -> str:
        goods_list_uri = "http://ticket.interpark.com/tiki/special/TPCalendar.asp"
        return "%s?ImgYn=Y&Ca=&KindOfGoods=%s&KindOfFlag=P&PlayDate=%s" % (
            goods_list_uri,
            kind_of_goods,
            play_date,
        )

    def crawl_performance_list(
        self,
        search_date: date,
        kind_code: Literal["01011", "01003"],
    ) -> List[str]:
        search_date_str = search_date.strftime("%Y%m%d")
        uri_for_crawling = self._get_uri_for_goods_list(kind_code, search_date_str)
        response = requests.get(uri_for_crawling)
        return self._extract_goods_code(response.text)

    def _close_popup(self, driver: WebDriver):
        try:
            driver.find_element(by=By.CLASS_NAME, value="popupCloseBtn").click()
            driver.implicitly_wait(0.1)
        except Exception:
            pass

    def _get_driver(self, performance_id: str) -> WebDriver:
        driver = webdriver.Chrome()

        driver.get(f"https://tickets.interpark.com/goods/{performance_id}")
        driver.implicitly_wait(1.0)
        return driver

    def _get_casting_names(self, driver: WebDriver) -> List[str]:
        casting_name_elements = driver.find_elements(
            by=By.CLASS_NAME, value="castingName"
        )
        return [
            casting_name_element.text for casting_name_element in casting_name_elements
        ]

    def _get_region(self, driver: WebDriver) -> str:
        driver.find_element(
            by=By.CSS_SELECTOR, value="[data-popup='info-place']"
        ).click()
        driver.implicitly_wait(0.2)
        return (
            driver.find_element(by=By.CSS_SELECTOR, value=".popPlaceInfo")
            .find_element(by=By.TAG_NAME, value="span")
            .text.split()[0]
        )

    def _get_date_range(self, driver: WebDriver) -> Tuple[str, str]:
        date_range = driver.find_element(
            by=By.CSS_SELECTOR, value=".infoDesc > .infoText"
        ).text
        start_date = datetime.strptime(date_range.split()[0], "%Y.%m.%d")
        if len(date_range.split()) >= 2:
            end_date = datetime.strptime(date_range.split()[1][1:], "%Y.%m.%d")
        else:
            end_date = start_date
        return (start_date, end_date)

    def crawl_performance(self, performance_id: str) -> Dict:
        driver = self._get_driver(performance_id)
        self._close_popup(driver)
        title = driver.find_element(by=By.CLASS_NAME, value="prdTitle").text
        poster = driver.find_element(by=By.CLASS_NAME, value="posterBoxImage")
        place = driver.find_element(
            by=By.CSS_SELECTOR, value="[data-popup='info-place']"
        ).text.split("(")[0]
        casting_names = self._get_casting_names(driver)
        region = self._get_region(driver)
        start_date, end_date = self._get_date_range(driver)
        ret = {
            "title": title,
            "poster": poster.get_attribute("src"),
            "place": place,
            "casting_names": casting_names,
            "region": region,
            "start_date": start_date,
            "end_date": end_date,
        }
        driver.quit()
        return ret
