
from pandas import concat
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from shutil import which
from scrapy import Selector
import csv
from datetime import datetime
import requests
import html2text

h = html2text.HTML2Text()
h.ignore_links = True
h.ignore_images = True


startURL = "https://www.joberty.rs/IT-poslovi?page=1&pageSize=50"
fileName = "joberty.csv"
chromePath = "D:\Projects\chromedriver_97\chromedriver.exe"


def botInitialization():
    # Initialize the Bot
    chromeOptions = Options()
    # chromeOptions.add_argument("--headless")
    path = which(chromePath)
    driver = webdriver.Chrome(executable_path=path, options=chromeOptions)
    driver.maximize_window()
    # open a new tab
    driver.execute_script("window.open('','_blank');")
    return driver

driver = botInitialization()


with open(fileName, 'w', newline='', encoding="utf-8-sig") as csvfile:
    fieldnames = ['Title', 'Skills', 'Location', "Company", "Content", "URL"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    driver.get(startURL)
    # sleep(2)

    while True:
        sleep(15)
        responseMain = Selector(text=driver.page_source)
        jobURLs = responseMain.css("h4 > a::attr(href)").extract()

        driver.switch_to.window(driver.window_handles[1])
        for url in jobURLs:
            print("scraping: " + url)
            url = "https://www.joberty.rs" + url
            driver.get(url)
            count = 0
            while True:
                sleep(1)
                response = Selector(text=driver.page_source)                
                content = response.css("div.container-job-description").extract()
                if content:
                    break
                count += 1
                if count > 10:
                    break
            
            if count > 10:
                continue

            title = response.css("h4.header::text").extract_first()
            
            try:
                location = response.css("div.ui.container.mb-20 > span > span::text").extract()[-1]
            except:
                location = ""

            if location:
                location = location.strip()

            # try:
            #     date = response.css("p.uk-margin-remove-top.uk-text-bold::text").extract()[-1]
            # except:
            #     date = ""
            
            # if date:
            #     date = date.strip()
            
            company = response.css("div.ui.container.mb-20 > a::text").extract()
            if company:
                company = company[-1].strip()
            else:
                company = ""

            skills = response.css("div.label-technology::text").extract()
            skills = [skill.strip() for skill in skills]
            skills = ", ".join(skills)

            content = response.css("div.container-job-description").extract()[0]

            content = h.handle(content)

            content = content.replace("*", "")
            content = content.replace("#", "")
            content = content.replace("\n\n", "\n").strip()
            content = content.replace("\n\n", "\n").strip()

            # content = " ".join(content.split())

            writer.writerow({'Title': title, "Skills":skills, 'Location': location, 'Company': company, 'Content': content, 'URL': url})
            print({
                'Title': title,
                "Skills":skills,
                'Location': location,
                'Company': company,
                'Content': content,
                'URL': url
            })

        driver.switch_to.window(driver.window_handles[0])
        nextPage = driver.find_elements_by_css_selector("a.item.icon")
        clicked = False
        for page in nextPage:
            try:
                if "angle right icon" in page.find_element_by_css_selector("i").get_attribute("class"):
                    # click using js
                    driver.execute_script("arguments[0].click();", page)
                    print("Clicked")
                    clicked = True
                    break
            except:
                continue
        
        if not clicked:
            break

driver.close()
driver.quit()