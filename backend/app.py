from flask import Flask, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

def extract_days(posted_date):
    match = re.match(r'(\d+)\s+days?\s+ago', posted_date)
    return int(match.group(1)) if match else None

def scrape_jobs():
    url = "https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=python"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')

    job_list = []
    for job in jobs:
        posted_date = job.find('span', class_='sim-posted').text.strip()
        days_ago = extract_days(posted_date)

        if days_ago is not None and days_ago < 7:  
            company_name = ' '.join(job.find('h3', class_='joblist-comp-name').text.strip().split())

            skills_tag = job.find('a', class_='posoverlay_srp')
            skills_str = re.search(r"logViewUSBT\('view','\d+','([^']+)','", skills_tag.get('onclick', ''))
            skills = [skill.strip() for skill in skills_str.group(1).split(',')] if skills_str else []

            link_tag = job.find('a', attrs={'href': re.compile('https://')})
            link = link_tag.get('href') if link_tag else "#"

            job_list.append({
                "company_name": company_name,
                "skills": skills,
                "posted_date": posted_date,
                "link": link
            })

    return job_list

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    jobs = scrape_jobs()
    return jsonify(jobs)

if __name__ == '__main__':
    app.run(debug=True)
