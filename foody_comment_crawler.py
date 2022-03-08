import os
import pandas as pd
import warnings
import functools
import operator
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
    rating: str   
    shop_name: str
    shop_url: str
    shop_rating: str
    shop_n_comments: str
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
    MAX_ITEMS = 10000
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
            driver.maximize_window()
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

    def export_food_shops(self, food_shops: List[dict]) -> None:
        foodshop_df = pd.DataFrame.from_dict(food_shops)
        foodshop_df.to_csv(self.FOODSHOP_CSV_PATH, index=False)    

    def read_food_shops(self) -> List[FoodShop]:
        foodshop_df = pd.read_csv('results/foodshops.csv')
        food_shops: List[dict] = foodshop_df.to_dict(orient='records')
        food_shops = [FoodShop(**food_shop) for food_shop in food_shops]
        return food_shops

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
        food_shops: List[dict] = self.get_food_shops(driver=driver, content_item_eles=content_item_eles)
        self.export_food_shops(food_shops)

        while 1:
            try:
                xemthem_btn_ele = self.wait_find(driver=driver, selector_str="#ajaxRequestDiv > div > div.content-container.fd-clearbox.ng-scope > div.pn-loadmore.fd-clearbox.ng-scope > a > label", selector_type='css', num_ele='one')
                content_item_eles: List[WebElement] = []
                if xemthem_btn_ele:
                    self.move_and_click(driver, xemthem_btn_ele)
                    sleep(0.5)
                    self.scroll_to_bottom(driver)
                    sleep(self.SCROLL_PAUSE_TIME)
                    content_item_eles: List[WebElement] = self.wait_find(driver=driver, selector_str="content-item", selector_type='class', num_ele='many')
                    logger.info(f"{len(content_item_eles)} / {self.MAX_ITEMS} ~ {(len(content_item_eles)*100/self.MAX_ITEMS):.2f} % items loaded")
                if len(content_item_eles) > 0:
                    food_shops.extend(self.get_food_shops(driver, content_item_eles[curr_n_items:]))
                    self.export_food_shops(food_shops)   
                if len(content_item_eles) >= self.MAX_ITEMS or xemthem_btn_ele is None:
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

    def get_food_shops(self, content_item_eles: List[WebElement]) -> List[dict]:
        def process(content_item_ele: WebElement) -> FoodShop:
            title_ele: WebElement = content_item_ele.find_element_by_class_name("title")
            a_ele: WebElement = title_ele.find_element_by_tag_name("a")
            name: str = a_ele.text
            url: str = a_ele.get_attribute("href") or ""
            updated_at: str = CommonUtils.get_date_time()
            food_shop = FoodShop(name=name, url=url, updated_at=updated_at)
            return food_shop
        food_shops: List[FoodShop] = CommonUtils.process_list(inputs=content_item_eles, func=process, desc="Getting food shops", method='multi')
        food_shops = [shop.to_dict() for shop in food_shops]
        return food_shops

    def go_get_food_shops(self):
        driver = self.create_driver()
        driver.get(self.HOMEPAGE_URL)
        # login
        self.login(driver)
        # get FoodShop information
        content_item_eles: List[WebElement] = self.get_content_item_elements(driver)
        driver.quit()

    def get_comments_from_one_food_shop(self, food_shop: FoodShop) -> List[Comment]:
        driver = self.create_driver()
        driver.get(food_shop.url)
        # get all review item eles
        review_item_eles: List[WebElement] = []
        n_items: int = 0
        n_tries: int = 1
        comments: List[Comment] = []
        # get shop info
        shop_rating_ele: WebElement = self.wait_find(driver=driver, selector_str="#res-summary-point > div > div.microsite-top-points-block > div.microsite-point-avg")
        shop_rating = shop_rating_ele.text
        shop_n_comments_eles : WebElement = self.wait_find(driver=driver, selector_str="summary", selector_type='class', num_ele='many')
        for ele in shop_n_comments_eles:
            if "bình luận đã chia sẻ" in ele.text:
                shop_n_comments = ele.text.split(" ")[0]
                break
        # 
        while 1:
            review_item_eles: List[WebElement] = self.wait_find(driver=driver, selector_str="review-item", selector_type='class', num_ele='many')
            self.scroll_to_bottom(driver)
            sleep(self.SCROLL_PAUSE_TIME)
            if len(review_item_eles) == n_items:
                break
            n_items = len(review_item_eles)
        comments: List[Comment] = self.get_comment_info(review_item_eles=review_item_eles, shop_name=food_shop.name, shop_url=food_shop.url , shop_rating=shop_rating, shop_n_comments=shop_n_comments)
        while 1:
            try:
                xemthem_btn_eles: List[WebElement] = self.wait_find(driver=driver, selector_str="fd-btn-more", selector_type='class', num_ele='many')
                xemthem_btn_ele: WebElement
                for ele in xemthem_btn_eles:
                    if ele.accessible_name == "Xem thêm bình luận":
                        xemthem_btn_ele = ele
                        break
                if xemthem_btn_ele:
                    self.move_and_click(driver, xemthem_btn_ele)
                    sleep(0.5)
                    self.scroll_to_bottom(driver)
                    sleep(self.SCROLL_PAUSE_TIME)
                    review_item_eles: List[WebElement] = self.wait_find(driver=driver, selector_str="review-item", selector_type='class', num_ele='many')
                    if len(review_item_eles) > 0:
                        comments: List[Comment] = self.get_comment_info(review_item_eles=review_item_eles, shop_name=food_shop.name, shop_url=food_shop.url, shop_rating=shop_rating, shop_n_comments=shop_n_comments)
                    logger.info(f"{len(review_item_eles)} / {self.MAX_ITEMS} ~ {(len(review_item_eles)*100/int(shop_n_comments)):.2f} % items loaded")
                else:
                    break
                n_tries = 1
            except Exception as e:
                logger.error(str(e))
                if n_tries > self.MAX_RETRIES:
                    break
                n_tries += 1
                continue
        driver.quit()
        return comments

    def get_comment_info(self, review_item_eles: WebElement, shop_name: str, shop_url: str, shop_rating: str, shop_n_comments: str) -> List[Comment]:
        def process(review_item_ele: WebElement) -> Comment:
            commentor_ele: WebElement = review_item_ele.find_element_by_class_name("ru-username")
            commentor: str = commentor_ele.text
            content_ele: WebElement = review_item_ele.find_element_by_class_name("rd-des")
            content_ele = content_ele.find_element_by_tag_name("span")
            content: str = content_ele.text
            rating_ele: WebElement = review_item_ele.find_element_by_class_name("review-points")
            rating: str = rating_ele.text
            updated_at: str = CommonUtils.get_date_time()
            comment_info = Comment(commentor=commentor, content=content, rating=rating, updated_at=updated_at, shop_name=shop_name, shop_url=shop_url, shop_rating=shop_rating, shop_n_comments=shop_n_comments)
            return comment_info
        comments: List[Comment] = CommonUtils.process_list(inputs=review_item_eles, func=process, desc="Getting comment info", method='multi')
        return comments

    def go_get_comments(self):
        driver = self.create_driver()
        driver.get(self.HOMEPAGE_URL)
        # login
        self.login(driver)
        food_shops: List[FoodShop] = self.read_food_shops()
        all_comments: List[dict] = []
        results: List[List[Comment]] = CommonUtils.process_list(inputs=food_shops, func=self.get_comments_from_one_food_shop, desc="Getting comments", method='multi')
        for r in results:
            all_comments.extend([e.__dict__ for e in r])
        df = pd.DataFrame.from_dict(all_comments)
        df.to_csv('results/comments.csv', index=False)
        driver.quit()

    def test(self):
        food_shops: List[FoodShop] = self.read_food_shops()
        def process(food_shop: FoodShop) -> dict:
            url:str = food_shop.url
            index = url.find("https://www.foody.vn/https://www.foody.vn/")
            url = "https://www.foody.vn/" + url[index+len("https://www.foody.vn/https://www.foody.vn/"):]
            return FoodShop(name=food_shop.name, url=url, updated_at=food_shop.updated_at).to_dict()
        results: List[dict] = CommonUtils.process_list(inputs=food_shops, func=process, desc="Getting food shops", method='single')
        df = pd.DataFrame.from_dict(results)
        df.to_csv("food_shops.csv", index=False)


if __name__ == "__main__":
    crawler = FoodyCommentCrawler()
    crawler.go_get_comments()