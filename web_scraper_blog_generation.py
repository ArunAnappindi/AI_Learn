import autogen
from playwright.sync_api import sync_playwright
import openai

import configparser

config = configparser.ConfigParser()
config.read("config/config.ini")

API_KEY = config["API"]["API_KEY"]


# Web Scraper Agent
class WebScraper:
    def __init__(self):
        self.urls = []

    def search_and_scrape(self, query):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            page.goto(search_url)

            links = page.locator("a").all()
            for link in links:
                href = link.get_attribute("href")
                if href and "http" in href:
                    self.urls.append(href)

            browser.close()

        return self.urls[:5]  # Limit to 5 sources

# Blog Writer Agent using AutoGen
blog_writer = autogen.AssistantAgent(name="blog_writer", llm_config={"model": "gpt-4", "api_key": ("%s" % API_KEY)})

# Instantiate Web Scraper
scraper = WebScraper()
topic = "AI in Cybersecurity"
sources = scraper.search_and_scrape(topic)

# Compile sources into a research summary
research_summary = f"Sources on {topic}:\n" + "\n".join(sources)

# Blog Generation
prompt = f"Write a detailed blog on {topic} using insights from these sources:\n{research_summary}"
blog_content = blog_writer.generate_reply(messages=[{"role": "user", "content": prompt}])

print("Generated Blog:\n", blog_content)
