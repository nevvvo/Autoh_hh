from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from urls import urls
from excluded_words import excluded_words
import time
import random


class HHScraper():
    def __init__(self, urls: list[str], excluded_words: list[str]):
        self.urls = urls
        self.excluded_words = excluded_words
        self.all_vacancies  = []
        self.seen = set()
        self.driver = self.init_driver()
        self.wait = WebDriverWait(self.driver, 15)
    
    def init_driver(self):
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        return webdriver.Chrome(options=options)


    def is_valid_vacancy(self, title, employer):
        for word in self.excluded_words:
            if word.lower() in title.lower() or word.lower() in employer.lower():
                return False
        return True
        

    def update_url_with_page(self, url, page_number):
        self.parsed_url = urlparse(url)
        self.query_params = parse_qs(self.parsed_url.query)
        self.query_params["page"] = [str(page_number)]
        self.new_query = urlencode(self.query_params, doseq=True)
        return urlunparse(self.parsed_url._replace(query=self.new_query))
    
    def parse_url(self, base_url):
        print(f"\n🌐 Парсим URL: {base_url}")
        page = 0

        while True:
            url = self.update_url_with_page(base_url, page)
            self.driver.get(url)
            print(f"\n🔄 Страница {page + 1}: {url}")

            try:
                self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//span[@data-qa='serp-item__title-text']")))
                time.sleep(random.uniform(1.2, 2.5))

                titles = self.driver.find_elements(By.XPATH, "//span[@data-qa='serp-item__title-text']")
                links = self.driver.find_elements(By.XPATH, "//a[@data-qa='serp-item__title']")
                companies = self.driver.find_elements(By.XPATH, "//span[@data-qa='vacancy-serp__vacancy-employer-text']")

                if not titles:
                    print("📭 Вакансии закончились. Останавливаемся.")
                    break

                for title, link, company in zip(titles, links, companies):
                    name = title.text.strip()
                    href = link.get_attribute("href")
                    employer = company.text.strip()

                    if self.is_valid_vacancy(name, employer):
                        key = (name, employer, href)
                        if key not in self.seen:
                            self.seen.add(key)
                            self.all_vacancies.append({
                                "title": name,
                                "employer": employer,
                                "link": href
                            })
                            print(f"✅ Найдена вакансия: {name} | {employer}")
                    else:
                        print(f"❌ Исключена: {name} | {employer}")

                page += 1
                time.sleep(random.uniform(1.5, 3.0))

            except Exception as e:
                print(f"⚠️ Ошибка на странице: {e}")
                break
    
    
    def run(self):
        for url in self.urls:
            self.parse_url(url)
            time.sleep(random.uniform(2.0, 4.0))  # между URL — отдых
        
        self.driver.quit()
        self.save_vacansies()

    
    def save_vacansies(self):
        self.driver.quit()
        return self.all_vacancies


class HHResponder(HHScraper):
    def __init__(self, vacansies : list[dict]):
        self.response_text = "Здравствуйте, мой гитхаб: https://github.com/nevvvo"
        self.vacansies = vacansies
        self.driver = self.init_driver()
        self.wait = WebDriverWait(self.driver, 15)

    def start(self):
        self.driver.get("https://hh.ru")
        input("Залогиньтесь и нажмиете Enter")


    def _click_first_button(self):
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Откликнуться']")))
        button.click()
        print("✅ Первая кнопка нажата")
        time.sleep(2)

    def _fill_response_text(self):
        try:
            textarea = self.wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@data-qa='vacancy-response-popup-form-letter-input']")))
            textarea.send_keys(self.response_text)  # Вставляем текст в textarea
            print("✅ Текст отклика вставлен в поле.")
        except Exception as e:
            print(f"⚠️ Textarea не найден")

    def _click_sumbit_button(self):
        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @form='RESPONSE_MODAL_FORM_ID']")))
            button.click()
            print("🎯 Кнопка нажата")
            self.wait.until(EC.invisibility_of_element_located((By.XPATH, "//button[@type='submit' and @form='RESPONSE_MODAL_FORM_ID']")))
            print("✅ Отклик успешно отправлен.")
        except:
            print("⚠️ Вторая кнопка не нажалась.")

    def _has_textarea(self):
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//textarea[@data-qa='vacancy-response-popup-form-letter-input']")))
            return True
        except:
            return False

    def respond_to_all(self):
        for vacancy in self.vacansies:
            try:
                print(f"\n➡️ Открываем вакансию: {vacancy['title']} | {vacancy['employer']}")
                self.driver.get(vacancy['link'])
                time.sleep(2)

                self._click_first_button()

                # Проверяем, есть ли поле textarea
                if self._has_textarea():
                    print("📝 Обнаружено поле для ввода текста.")
                    self._fill_response_text()
                    self._click_sumbit_button()
                else:
                    print("📭 Поле для текста не найдено. Будет отправлен простой отклик.")

                time.sleep(2)

            except Exception as e:
                print(f"⚠️ Ошибка при отклике: {e}")
                continue

    def quit(self):
        self.driver.quit()

if __name__ == "__main__":
    scraper = HHScraper(urls=urls, excluded_words=excluded_words)
    scraper.run()
    vacansies = scraper.save_vacansies()
    responder = HHResponder(vacansies=vacansies)
    responder.start()
    responder.respond_to_all()
    responder.quit()