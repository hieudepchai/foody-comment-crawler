import os
import pandas as pd
import warnings
from dataclasses import dataclass
from time import sleep
from typing import List, Union, Dict
from loguru import logger
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webelement import WebElement

from common_utils import CommonUtils

os.environ['WDM_LOG_LEVEL'] = '0'
warnings.filterwarnings("ignore")

@dataclass
class Comment:
    commentor: str
    content: str
    date_time: str
    rating: float   
    shop_name: str
    shop_url: str
    shop_n_comments: int
    shop_rating: float
    updated_at: str


class FoodShop:

    def __init__(self, name: str, url: str, updated_at: str) -> None:
        self.name = name
        self.url = url
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        return self.__dict__
        
class FoodyCommentCrawler:
    HOMEPAGE_URL: str = "https://www.foody.vn/"
    SCROLL_PAUSE_TIME: float = 0.5
    USERNAME = "liberty.sun25651@gmail.com"
    PASSWORD = "Foody1234"
    FOODSHOP_CSV_PATH = 'results/foodshops.csv'
    MAX_ITEMS = 500
    MAX_RETRIES = 5

    def get_driver_path(self) -> str:
        return ChromeDriverManager(path='.').install() 

    def create_driver(self, headless: bool = False, debug_mode: bool = False, fast_load: bool = True) -> webdriver.Chrome:
        # driver = getattr(threadLocal, 'driver', None)
        driver = None
        if driver is None:
            options= webdriver.ChromeOptions()
            capa = DesiredCapabilities.CHROME
            # options.add_argument(f'"user-data-dir={self.profile_path}
            options.add_argument('--log-level=3')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--ignore-certificate-errors-spki-list')
            # prefs = {
            #     "download.default_directory": self.save_dir,
            #     "download.prompt_for_download": False,
            #     "download.directory_upgrade": True,
            #     "safebrowsing.enabled": True
            # }
            # options.add_experimental_option("prefs", prefs)
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            if fast_load:
                capa["pageLoadStrategy"] = "none"
            if debug_mode:
                options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')
            if headless:
                options.add_argument("--headless")
            driver_path = self.get_driver_path()
            driver = webdriver.Chrome(executable_path=driver_path, options=options, desired_capabilities=capa, service_log_path=os.devnull)
            # setattr(threadLocal, 'driver', driver)
        return driver

    def wait_find(self, driver: webdriver.Chrome, selector_str: str, selector_type: str = 'css', num_ele: str = 'one', timeout: int = 20, wait_type: int = 'present' ,stop_loading: bool = False) -> Union[WebElement,List[WebElement]]:
        wait = WebDriverWait(driver, timeout)
        try:
            if wait_type == 'present':
                if num_ele == 'one':
                    if selector_type == 'css':
                        ele = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR , selector_str)))
                    elif selector_type == 'tag':
                        ele = wait.until(EC.presence_of_element_located((By.TAG_NAME , selector_str)))
                    elif selector_type == 'class':
                        ele = wait.until(EC.presence_of_element_located((By.CLASS_NAME, selector_str)))
                elif num_ele == 'many':
                    if selector_type == 'css':
                        ele = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR , selector_str)))
                    elif selector_type == 'tag':
                        ele = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME , selector_str)))
                    elif selector_type == 'class':
                        ele = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, selector_str))) 

            elif wait_type == 'clickable':
                if num_ele == 'one':
                    if selector_type == 'css':
                        ele = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR , selector_str)))
                    elif selector_type == 'tag':
                        ele = wait.until(EC.element_to_be_clickable((By.TAG_NAME , selector_str)))
                    elif selector_type == 'class':
                        ele = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, selector_str)))

            elif wait_type == 'visible':
                if num_ele == 'one':
                    if selector_type == 'css':
                        ele = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR , selector_str)))
                    elif selector_type == 'tag':
                        ele = wait.until(EC.visibility_of_element_located((By.TAG_NAME , selector_str)))
                    elif selector_type == 'class':
                        ele = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, selector_str))) 
                elif num_ele == 'many':
                    if selector_type == 'css':
                        ele = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR , selector_str)))
                    elif selector_type == 'tag':
                        ele = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME , selector_str)))
                    elif selector_type == 'class':
                        ele = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, selector_str))) 
        except Exception as e:
            return None
        
        if stop_loading:
            driver.execute_script("window.stop();")
            
        return ele
    
    def instant_find(self, driver: webdriver.Chrome, selector_str: str, selector_type: str = 'css', num_ele: str = 'one') -> Union[WebElement,List[WebElement]]:
        try:
            if num_ele == 'one':
                if selector_type == 'css':
                    ele = driver.find_element_by_css_selector(selector_str)
                elif selector_type == 'tag':
                    ele = driver.find_element_by_tag_name(selector_str)
                elif selector_type == 'class':
                    ele = driver.find_element_by_class_name(selector_str)
            elif num_ele == 'many':
                if selector_type == 'css':
                    ele = driver.find_elements_by_css_selector(selector_str)
                elif selector_type == 'tag':
                    ele = driver.find_elements_by_tag_name(selector_str)
                elif selector_type == 'class':
                    ele = driver.find_elements_by_class_name(selector_str)

        except Exception as e:
            return None
        return ele

    def scroll_to_bottom(self, driver: webdriver.Chrome):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def move_and_click(self, driver: webdriver.Chrome, ele: WebElement):
        ActionChains(driver).move_to_element(ele).click().perform()

    def login(self, driver: webdriver.Chrome):
        driver.get("https://id.foody.vn/account/login?returnUrl=https://www.foody.vn/")
        username_input = self.wait_find(driver=driver, selector_str="#Email", selector_type="css", num_ele="one")
        username_input.send_keys(self.USERNAME)
        password_input = self.wait_find(driver=driver, selector_str="#Password", selector_type="css", num_ele="one")
        password_input.send_keys(self.PASSWORD)
        login_btn = self.wait_find(driver=driver, selector_str="#bt_submit", selector_type="css", num_ele="one")
        login_btn.click()

    def get_content_item_elements(self, driver: webdriver.Chrome) -> List[WebElement]:
        n_items: int = 0
        content_item_eles: List[WebElement] = []
        n_tries = 1
        while 1:
            self.scroll_to_bottom(driver)
            sleep(self.SCROLL_PAUSE_TIME)
            content_item_eles: List[WebElement] = self.wait_find(driver=driver, selector_str="content-item", selector_type='class', num_ele='many')
            if len(content_item_eles) == n_items:
                break
            n_items = len(content_item_eles)

        curr_n_items = len(content_item_eles)
        def export_food_shops(food_shops: List[dict]) -> None:
            foodshop_df = pd.DataFrame.from_dict(food_shops)
            foodshop_df.to_csv(self.FOODSHOP_CSV_PATH, index=False)
        food_shops: List[dict] = self.get_food_shops(driver=driver, content_item_eles=content_item_eles)
        export_food_shops(food_shops)

        while 1:
            try:
                xemthem_btn_ele = self.wait_find(driver=driver, selector_str="#ajaxRequestDiv > div > div.content-container.fd-clearbox.ng-scope > div.pn-loadmore.fd-clearbox.ng-scope > a > label", selector_type='css', num_ele='one')
                if xemthem_btn_ele:
                    self.move_and_click(driver, xemthem_btn_ele)
                    sleep(0.5)
                    self.scroll_to_bottom(driver)
                    sleep(self.SCROLL_PAUSE_TIME)
                    content_item_eles: List[WebElement] = self.wait_find(driver=driver, selector_str="content-item", selector_type='class', num_ele='many')
                    logger.info(f"{len(content_item_eles)} / {self.MAX_ITEMS} ~ {(len(content_item_eles)*100/self.MAX_ITEMS):.2f} % items loaded")
                    food_shops.append(self.get_food_shops(driver, content_item_eles[curr_n_items:]))
                    export_food_shops(food_shops)   
                if len(content_item_eles) >= self.MAX_ITEMS or xemthem_btn_ele is None:
                    food_shops.append(self.get_food_shops(driver, content_item_eles[curr_n_items:]))
                    export_food_shops(food_shops)  
                    break
                n_tries = 1
                curr_n_items = len(content_item_eles)
            except Exception as e:
                logger.error(str(e))
                if n_tries > self.MAX_RETRIES:
                    break
                n_tries += 1
                continue
        return content_item_eles

    def get_food_shops(self, driver: webdriver.Chrome, content_item_eles: List[WebElement]) -> List[dict]:
        def process(content_item_ele: WebElement) -> FoodShop:
            title_ele: WebElement = content_item_ele.find_element_by_class_name("title")
            a_ele: WebElement = title_ele.find_element_by_tag_name("a")
            name: str = a_ele.text
            url: str = self.HOMEPAGE_URL + (a_ele.get_attribute("href") or "")
            updated_at: str = CommonUtils.get_date_time()
            food_shop = FoodShop(name=name, url=url, updated_at=updated_at)
            return food_shop
        food_shops: List[FoodShop] = CommonUtils.process_list(inputs=content_item_eles, func=process, desc="Getting food shops", method='multi')
        food_shops = [shop.to_dict() for shop in food_shops]
        # foodshop = pd.DataFrame.from_dict(food_shops)
        # foodshop.to_csv(self.FOODSHOP_CSV_PATH, index=False)
        return food_shops

    def go_get_food_shops(self):
        driver = self.create_driver()
        driver.get(self.HOMEPAGE_URL)
        # login
        self.login(driver)
        # get FoodShop information
        content_item_eles: List[WebElement] = self.get_content_item_elements(driver)
        driver.quit()

    def go_get_comments(self):
        driver = self.create_driver()
        driver.get(self.HOMEPAGE_URL)
        # login
        self.login(driver)


if __name__ == "__main__":
    crawler = FoodyCommentCrawler()
    crawler.go_get_food_shops()