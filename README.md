# 🚀 Lanka Career Hub - Automated Job Scraper & Publisher Bot

A fully automated, serverless Python bot designed to aggregate, filter, and publish job vacancies from top Sri Lankan career portals directly to a Facebook Page. 

Built as a real-world automation project, this bot eliminates manual data entry by programmatically scraping job listings, extracting relevant media, applying strict content policies, and interacting with the Facebook Graph API.

## ✨ Key Features

* **🌐 Multi-Source Data Aggregation:** Automatically scrapes multiple job boards including TopJobs, XpressJobs, ColomboJobs, and various Blogger-based government/private job sites.
* **🧠 Smart Image Extraction & Redirection Handling:** Bypasses generic advertisements (banners, logos) and dynamically navigates through hidden links or "Full Details" redirect pages to extract the precise high-quality job flyer.
* **🛡️ Strict Policy Filtering:** Implements a custom keyword-filtering algorithm to automatically detect and block MLMs, crypto scams, and unauthorized financial schemes, ensuring zero Facebook policy violations.
* **📅 Temporal URL Validation:** Dynamically parses URLs from Blogger-based sites to ensure only current-month job listings are processed, discarding outdated data.
* **⚡ Serverless Automation (CI/CD):** Fully deployed on **GitHub Actions**. The bot runs autonomously 3 times a day via CRON jobs, requiring zero manual intervention and zero hosting costs.

## 🛠️ Tech Stack

* **Language:** Python 3.10
* **Web Scraping:** Selenium WebDriver (Headless Chrome), Webdriver-Manager
* **API Integration:** Facebook Graph API v21.0, Python `requests`
* **Automation & CI/CD:** GitHub Actions, YAML
* **Data Management:** File-based local state tracking (`seen_jobs.txt`)

## ⚙️ How It Works

1. **Trigger:** GitHub Actions triggers the script based on a predefined CRON schedule.
2. **Scrape:** Selenium navigates through 6+ predefined job portals.
3. **Filter:** The `is_post_safe()` function checks titles against a scam-dictionary. Temporal filters drop old posts.
4. **Extract:** The script isolates the job flyer image, ignoring UI elements and ads.
5. **Publish:** The Facebook Graph API publishes the curated job post with custom hashtags.
6. **State Update:** The job link is appended to `seen_jobs.txt` to prevent duplicate posting in future runs.

## 👨‍💻 Developer Note

This project was developed to solve a real-world content curation problem while applying concepts learned in my Information and Communication Technology (ICT) undergraduate studies. It showcases practical implementations of web automation, DOM manipulation, RESTful APIs, and cloud-based CI/CD workflows.

---
*Developed by Nirmala Sandaruwan*
