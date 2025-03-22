from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re

def extract_days(posted_date):
    match = re.match(r'(\d+)\s+days?\s+ago',posted_date)
    if match:
        return int(match.group(1))
    return None


html_text = requests.get("https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords=python&txtLocation=").text
job_found = False

soup = BeautifulSoup(html_text,"lxml")
jobs = soup.find_all('li', class_ = 'clearfix job-bx wht-shd-bx')

for job in jobs:
    posted_date = job.find('span',class_ = 'sim-posted').text.strip()

    if posted_date:
        days_ago = extract_days(posted_date)

        if days_ago is not None:
            today = datetime.now()

            if days_ago<4:
                job_found = True

                company_name = job.find('h3', class_='joblist-comp-name').text.strip()
                company_name = ' '.join(company_name.split())

                skills = job.find('a', class_='posoverlay_srp')

                onclick_text = skills.get('onclick','')
                match = re.search(r"logViewUSBT\('view','\d+','([^']+)','", onclick_text)

                skills_str = match.group(1)
                skills = [skill.strip() for skill in skills_str.split(',')]

                link_tag = job.find('a',attrs = {'href':re.compile('https://')})
                if link_tag:
                    link = link_tag.get('href')
                
                print(f"Company Name: {company_name}")
                print(f"Required Skills: {skills}")
                print(f"Date posted: {posted_date}")
                print(f"Link to the post: {link}")
                print(f"-"*100)

if not job_found:
    print("No job found based on the criteria..")