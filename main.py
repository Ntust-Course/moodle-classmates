from argparse import ArgumentParser
from collections import Counter

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Moodle(object):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = webdriver.Chrome(chrome_options=options)

    def login(self, username, password) -> bool:
        """進入登入頁面"""
        self.driver.get('http://moodle.ntust.edu.tw/login/index.php')
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
        except TimeoutException:
            return False
        u = self.driver.find_element_by_xpath("//input [@id='username']")
        p = self.driver.find_element_by_xpath("//input [@id='password']")
        l = self.driver.find_element_by_xpath("//input [@id='loginbtn']")
        u.send_keys(username)
        p.send_keys(password)
        l.click()
        return True

    def home(self) -> bool:
        """進來囉 來走去我的頁面 //*[@id="essentialnavbar"]/div/div/div/div/div[1]/div[1]/ul/li/ul/li[1]/a/@href"""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'essentialnavbar'))
            )
        except TimeoutException:
            return False
        self.driver.get(self.driver.find_element_by_xpath(
            '//*[@id="essentialnavbar"]/div/div/div/div/div[1]/div[1]/ul/li/ul/li[1]/a').get_attribute('href'))
        self.driver.get(f'{self.driver.current_url}&showallcourses=1')
        return True

    def quit(self):
        self.driver.quit()

    def _get_classes(self):
        """別人是 section[1] 自己是 section[2]"""
        return self.driver.find_elements_by_xpath(
            '//*[@id="region-main"]/div/div/div/section[2]/ul/li/dl/dd/ul/li/a')

    def _get_classes_by_id(self, course_id):
        """link : https://moodle.ntust.edu.tw/user/index.php?id=16291&perpage=5000"""
        self.driver.get(
            f'https://moodle.ntust.edu.tw/user/index.php?id={course_id}&perpage=5000')
        # Wait until elements ready
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, 'participants'))
        )
        return self.driver.find_elements_by_xpath('//*[@id="participants"]/tbody/tr/td/strong/a')

    def _get_classes_links(self) -> list:
        return list(map(lambda c: c.get_attribute('href'), self._get_classes()))

    def get_classmates(self):
        for link in map(lambda link: link.split('course=')[1].split('&')[0], self._get_classes_links()):
            for text in map(lambda class_: class_.text, self._get_classes_by_id(link)):
                yield text

    def get_frequent_classmates(self):
        """
        return dict {name: count}
        """
        classmates_count = Counter(list(self.get_classmates()))
        return classmates_count.most_common()[1:]


def main(username, password):
    moodle = Moodle()
    if moodle.login(username, password) and moodle.home():
        for name, count in moodle.get_frequent_classmates():
            print(f'{name} {count}')
    moodle.quit()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('username', help='帳號')
    parser.add_argument('password', help='密碼')
    args = parser.parse_args()

    main(args.username, args.password)