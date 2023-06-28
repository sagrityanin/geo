import requests
from bs4 import BeautifulSoup, SoupStrainer
from time import sleep, time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

COUNT_PAGE = 5


class Staff:
    company_url = "http://botgard.uran.ru/labs/"

    def __init__(self) -> None:
        self.employers = []

    def get_laboratory(self, url):
        self.laboratories = []
        html = requests.get(url)
        soup = BeautifulSoup(html.content, "lxml")
        laboratory_bloks = soup.find_all(
            "div", class_="align-self-center container-sm p-5 mt-4 rounded text_container news_content")
        for item in laboratory_bloks:
            name_string = item.get_text().strip().replace("\n", " ")
            lab_url = (item["onclick"].split('=')[1]).replace("'", "").replace(";", "")
            lab = {"name": " ".join(name_string.split()),
                   "url": f"http://botgard.uran.ru{lab_url}"}
            self.laboratories.append(lab)
        return self.laboratories

    def get_employers(self):
        for lab in self.laboratories:
            print(f"Get staff from {lab['name']}")
            html = requests.get(lab["url"])
            soup = BeautifulSoup(html.content, "lxml")
            marks = soup.find("h3", class_="align-self-center")

            if marks is not None and "Лаборатория состоит" in [item.text for item in marks]:
                pass
            else:
                empoloyers = []
                emploters_block = soup.find_all(
                    "div", class_="align-self-center container-sm p-5 mt-4 rounded text_container")
                if len(emploters_block) >= 6:
                    empoloyers_list = emploters_block[2].find_all("h5")
                else:
                    empoloyers_list = emploters_block[0].find_all("h5")
                for item in empoloyers_list:
                    employer = {"surname": item.text.split()[0], "full_name": item.text.split()}
                    empoloyers.append(employer)
                    self.employers.append(item.text.split()[0])
                lab["employers"] = empoloyers


class Publish(Staff):

    def __init__(self):
        options = Options()
        options.add_argument("-profile")
        # Для vscode
        options.add_argument("parser/user")
        # Для pyCharm
        # options.add_argument("user")
        self.driver = webdriver.Firefox(options=options)
        self.org_url = "https://elibrary.ru/org_items.asp?orgsid=182"
        self.publish_dict = {}

    def set_employer_dict(self, employers):
        for item in employers:
            self.publish_dict[item] = 0

    def get_page(self):
        publish_table = self.driver.find_element(By.ID, "restab")
        publishes = publish_table.find_elements(By.TAG_NAME, 'i')
        for paper in publishes:
            print(paper.text)
            self.set_publish(paper.text)

    def get_next_page(self):
        self.driver.get(self.org_url)
        sleep(120)
        self.get_page()
        for i in range(1, COUNT_PAGE):
            print(f"Get {i + 1} page")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@title="Следующая страница"]')))
            self.driver.find_element(By.XPATH, '//a[@title="Следующая страница"]').click()
            sleep(2)
            self.get_page()
        self.driver.close()

    def set_publish(self, author_list):
        for employer in self.publish_dict:
            if employer in author_list:
                self.publish_dict[employer] += 1


def main():
    bot_garden = Staff()
    bot_garden.get_laboratory(Staff.company_url)
    bot_garden.get_employers()
    publish = Publish()
    publish.set_employer_dict(bot_garden.employers)
    publish.get_next_page()
    print(publish.publish_dict)
    return publish.publish_dict


if __name__ == "__main__":
    main()