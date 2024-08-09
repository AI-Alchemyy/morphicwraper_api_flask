# scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


class MorphicScraper:

    def __init__(self):
        self.url = "https://morphic.sh"

    def get_response(self, user_input):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Set to headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)

        try:
            driver.get(self.url)

            # Wait for the input field and enter the question
            input_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "textarea[placeholder='Ask a question...']")))
            input_field.send_keys(user_input)
            input_field.send_keys(Keys.RETURN)

            # Wait for the initial response to be generated
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "div[class='prose-sm prose-neutral prose-a:text-subaccent']"
                )))

            # Wait for the "Related" section to appear
            try:
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//section[contains(@class, 'py-2')]//h2[text()='Related']"
                    )))
            except TimeoutException:
                print(
                    "Related section did not appear within the timeout period."
                )

            # Extract the entire response container
            response_container = driver.find_element(By.CSS_SELECTOR,
                                                     "div[data-state='open']")
            html_content = response_container.get_attribute(
                'innerHTML') if response_container else ""

        finally:
            driver.quit()

        return self.parse_response(html_content)

    def parse_response(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract the main response text
        response_element = soup.select_one(
            "div[class='prose-sm prose-neutral prose-a:text-subaccent']")
        response = response_element.get_text(
            strip=True) if response_element else "No response found"

        # Extract sources
        sources = []
        source_elements = soup.select("div.w-1\\/2.md\\:w-1\\/4.p-1 a")
        for source in source_elements:
            title_element = source.select_one("p.text-xs.text-foreground\\/70")
            title = title_element.get_text(
                strip=True) if title_element else "No title"
            url = source.get('href', '#')
            sources.append({"title": title, "url": url})

        # Extract related links
        related_links = []
        related_elements = soup.select("button[name='related_query']")
        for related in related_elements:
            related_links.append(related.get('value', ''))

        return {
            "response": response,
            "sources": sources,
            "related_links": related_links
        }


# Example usage
if __name__ == "__main__":
    scraper = MorphicScraper()
    result = scraper.get_response("What is the latest technology news?")
    print("Response:",
          result["response"][:100] + "...")  # Print first 100 characters
    print("\nSources:")
    for source in result["sources"]:
        print(f"- {source['title']}: {source['url']}")
    print("\nRelated Links:")
    for link in result["related_links"]:
        print(f"- {link}")
