import re

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# implement caching
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # 5 minutes timeout
cache = Cache(app)


def extract_days(posted_date):
    """Helper function to extract number of days from the posted date."""
    match = re.match(r"(\d+)\s+days?\s+ago", posted_date)
    return int(match.group(1)) if match else None


def scrape_jobs(page=1, per_page=6):
    """Function to scrape jobs with pagination support."""
    url = f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&txtKeywords=python&page={
        page}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    jobs = soup.find_all("li", class_="clearfix job-bx wht-shd-bx")

    job_list = []
    for job in jobs:
        posted_date = job.find("span", class_="sim-posted").text.strip()
        days_ago = extract_days(posted_date)

        if days_ago is not None and days_ago < 7:
            company_name = " ".join(
                job.find("h3", class_="joblist-comp-name").text.strip().split()
            )

            skills_tag = job.find("a", class_="posoverlay_srp")
            skills_str = re.search(
                r"logViewUSBT\('view','\d+','([^']+)','", skills_tag.get("onclick", "")
            )
            skills = (
                [skill.strip() for skill in skills_str.group(1).split(",")]
                if skills_str
                else []
            )

            link_tag = job.find("a", attrs={"href": re.compile("https://")})
            link = link_tag.get("href") if link_tag else "#"

            job_list.append(
                {
                    "company_name": company_name,
                    "skills": skills,
                    "posted_date": posted_date,
                    "link": link,
                }
            )

    # Implement pagination: return only a slice of the job_list
    start = (page - 1) * per_page
    end = start + per_page
    return job_list[start:end]


@app.route("/api/jobs", methods=["GET"])
@cache.cached(query_string=True)
def get_jobs():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 6))

    jobs = scrape_jobs(page, per_page)
    return jsonify(jobs)


if __name__ == "__main__":
    app.run(debug=True)
