import sys, os, requests, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# 🛑 1. FACEBOOK KEYS (දැන් ගන්නේ GitHub Secrets වලින්) 🛑
# ==========================================
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN")
PAGE_ID = os.environ.get("PAGE_ID")
# ==========================================

# ==========================================

HASHTAGS = "\n\n#jobsearch #JobOpportunity #SriLankaJobs #srilanka #jobs"
DB_FILE = "seen_jobs.txt"

def load_seen_jobs():
    if not os.path.exists(DB_FILE): return []
    try:
        with open(DB_FILE, "r", encoding='utf-8') as f:
            return [line.strip() for line in f.read().splitlines() if line.strip()]
    except: return []

def save_new_job(job_id):
    with open(DB_FILE, "a", encoding='utf-8') as f:
        f.write(job_id + "\n")

def get_chrome_driver():
    options = Options()
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def is_post_safe(job_title, job_link):
    print(f"🔍 FB Policy පරීක්ෂා කරමින්: {job_title[:30]}...")
    title_lower = job_title.lower()
    fb_restricted_keywords = [
        "crypto", "bitcoin", "forex", "trading", "investment", "binary", "stock",
        "loan", "credit", "payday", "cash advance", "debt", "interest rate",
        "earn money", "make money", "quick cash", "easy income", "be your own boss",
        "work from home", "wfh", "data entry", "part time income", "no experience needed",
        "mlm", "network marketing", "pyramid", "direct selling", "distributor wanted",
        "casino", "betting", "gambling", "lottery", "adult", "massage", "dating", "escort"
    ]
    for word in fb_restricted_keywords:
        if word in title_lower:
            print(f"🛑 FB Policy Alert: '{word}' අඩංගු නිසා පෝස්ට් කිරීම ප්‍රතික්ෂේප විය!")
            return False 
    return True

def get_job_flyer(driver, job_link):
    try:
        driver.get(job_link)
        time.sleep(3)
        
        # 🔴 අලුත් කෑල්ල: "Full Details" ලින්ක් එකක් තිබ්බොත් ඒකට යනවා!
        try:
            details_links = driver.find_elements(By.TAG_NAME, "a")
            for d_link in details_links:
                d_text = str(d_link.text).lower()
                d_href = str(d_link.get_attribute("href")).lower()
                # "full details" කියලා තිබ්බොත් හරි houzzideas සයිට් එකට යවනව නම් හරි...
                if "full details" in d_text or "houzzideas.com" in d_href:
                    driver.get(d_href) # ඒ පිටුවට යනවා
                    time.sleep(4)      # ඒක ලෝඩ් වෙනකම් ඉන්නවා
                    break              # එකක් හම්බුණාම ඇති
        except:
            pass # මොකුත් නැත්නම් සාමාන්‍ය විදිහට පල්ලෙහාට යනවා
        # -------------------------------------------------------------

        driver.execute_script("window.scrollTo(0, 700);")
        time.sleep(3)
        
        imgs = driver.find_elements(By.CSS_SELECTOR, ".post-body img")
        if not imgs:
            imgs = driver.find_elements(By.TAG_NAME, "img")
            
        best_img = None
        max_area = 0
        bad_keywords = ["banner", "whatsapp", "sponsored", "footer", "header", "icon", "avatar", "profile", "svg", "promo", "campaign", "related", "slider", "slide", "default", "placeholder", "logo", "advertise", "square", "megaphone", "ad-here"]
        
        for img in imgs:
            src = img.get_attribute("src") or img.get_attribute("data-src")
            if not src: continue
            
            src_lower = src.lower()
            is_bad = False
            for bad_word in bad_keywords:
                if bad_word in src_lower:
                    if bad_word == "logo" and "topjobs" in job_link.lower():
                        continue
                    is_bad = True
                    break
            if is_bad: continue
                
            try:
                w = int(img.get_attribute("naturalWidth") or 0)
                h = int(img.get_attribute("naturalHeight") or 0)
                if w == 800 and h == 800: continue
                if w > 300 and h > 300: 
                    if w > (h * 1.5): continue
                    area = w * h
                    if area > max_area: 
                        max_area = area
                        best_img = src
            except: continue
        return best_img
    except: return None

# --- FACEBOOK POSTING ---
def post_to_facebook(message, image_url=None):
    if not FB_PAGE_TOKEN or not PAGE_ID: return False
    if image_url:
        url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/photos"
        payload = {'url': image_url, 'message': message, 'access_token': FB_PAGE_TOKEN}
    else:
        url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/feed"
        payload = {'message': message, 'access_token': FB_PAGE_TOKEN}
    try:
        r = requests.post(url, data=payload)
        return r.status_code == 200
    except: return False

# --- MAIN POSTING LOGIC (FB Only) ---
def process_and_post(job, flyer_url):
    msg = f"📢 අලුත්ම රැකියා අවස්ථාවක්! \n\n📌 තනතුර: {job['title']}\n🔗 වැඩි විස්තර: {job['link']}{HASHTAGS}"
    
    # Facebook එකට විතරක් දානවා
    if post_to_facebook(msg, flyer_url):
        print(f"🎯 FB පෝස්ට් එක සාර්ථකයි: {job['title']}")
        save_new_job(job['link'])
        seen_jobs_global.append(job['link'])
        time.sleep(5)

# ගෝලීය මතකය
seen_jobs_global = []

def run_job_scraper():
    print(f"\n🚀 බොට් වැඩ පටන් ගත්තා! වෙලාව: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    global seen_jobs_global
    seen_jobs_global = load_seen_jobs()
    
    # 1. TOPJOBS
    print("\n🔍 TopJobs පරීක්ෂා කරයි...")
    driver = None
    try:
        driver = get_chrome_driver()
        driver.get("http://topjobs.lk/applicant/vacancybyfunctionalarea.jsp?FA=ALL")
        time.sleep(8)
        found_topjobs = []
        rows = driver.find_elements(By.XPATH, "//tr[contains(@onclick, 'createAlert')]")
        for row in rows:
            try:
                onclick_text = row.get_attribute("onclick")
                params_str = onclick_text.split("createAlert(")[1].split(")")[0]
                params = [p.strip().strip("'").strip('"') for p in params_str.split(',')]
                if len(params) >= 4:
                    job_link = f"http://topjobs.lk/employer/JobAdvertismentServlet?rid={params[0]}&ac={params[1]}&jc={params[2]}&ec={params[3]}"
                    title = row.find_element(By.TAG_NAME, "h2").text.strip()
                    if len(title) > 5 and job_link not in seen_jobs_global:
                        if job_link not in [j['link'] for j in found_topjobs]:
                            found_topjobs.append({'title': title, 'link': job_link})
            except: continue
        for job in found_topjobs[:2]:
            if is_post_safe(job['title'], job['link']):
                process_and_post(job, get_job_flyer(driver, job['link']))
    except Exception as e: print(f"TopJobs දෝෂයකි: {e}")
    finally:
        if driver: driver.quit()

    # ==========================================
    # 2. XPRESSJOBS (අලුත් ලින්ක් රටාවට හැදුවා)
    # ==========================================
    print("\n🔍 XpressJobs පරීක්ෂා කරයි...")
    driver = None
    try:
        driver = get_chrome_driver()
        driver.get("https://xpress.jobs/jobs")
        time.sleep(5)
        found_xpress = []
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            try:
                href = str(link.get_attribute("href"))
                title = link.text.strip()
                
                # XpressJobs අලුත් ලින්ක් වල /view/ නෑ. ඒක /jobs/12345/title විදිහට තියෙන්නේ.
                if "xpress.jobs/jobs/" in href and href != "https://xpress.jobs/jobs":
                    
                    # සමහරවිට title එක හිස් නම් ලින්ක් එකෙන් title එක හදාගන්නවා
                    if not title or len(title) < 5:
                        # ලින්ක් එකේ අග තියෙන 'graphic-designer' වගේ කෑල්ල අරන් ලස්සන කරනවා
                        title = href.split('/')[-1].replace('-', ' ').title()
                        
                    if len(title) > 5 and href not in seen_jobs_global:
                        if href not in [j['link'] for j in found_xpress]:
                            found_xpress.append({'title': title, 'link': href})
            except: continue
            
        for job in found_xpress[:2]:
            if is_post_safe(job['title'], job['link']):
                process_and_post(job, get_job_flyer(driver, job['link']))
    except Exception as e: print(f"XpressJobs දෝෂයකි: {e}")
    finally:
        if driver: driver.quit()

    # 3. COLOMBOJOBS.LK 
    print("\n🔍 ColomboJobs පරීක්ෂා කරයි...")
    driver = None
    try:
        driver = get_chrome_driver()
        driver.get("https://www.colombojobs.lk/")
        time.sleep(5)
        found_colombo = []
        links = driver.find_elements(By.TAG_NAME, "a")
        bad_colombo_links = ["category", "categories", "guidance", "employer", "about", "contact", "pricing", "/p/"]
        for link in links:
            try:
                href = str(link.get_attribute("href"))
                title = link.text.strip()
                if href and len(title) > 10 and href not in seen_jobs_global:
                    if "colombojobs.lk" in href and href != "https://www.colombojobs.lk/":
                        href_lower = href.lower()
                        if not any(bad_word in href_lower for bad_word in bad_colombo_links):
                            if ".html" in href_lower:
                                if href not in [j['link'] for j in found_colombo]:
                                    found_colombo.append({'title': title, 'link': href})
            except: continue
        for job in found_colombo[:2]:
            if is_post_safe(job['title'], job['link']):
                process_and_post(job, get_job_flyer(driver, job['link']))
    except Exception as e: print(f"ColomboJobs දෝෂයකි: {e}")
    finally:
        if driver: driver.quit()

   # ==========================================
    # 4, 5 & 6. BLOGGER SITES (අලුත්ම මාසේ ෆිල්ටරය සමඟ)
    # ==========================================
    def scrape_blogspot(url, site_name, domain):
        print(f"\n🔍 {site_name} පරීක්ෂා කරයි...")
        driver = None
        try:
            driver = get_chrome_driver()
            driver.get(url)
            time.sleep(5)
            found_blog = []
            links = driver.find_elements(By.TAG_NAME, "a")
            bad_blog_links = ["terms", "privacy", "contact", "about", "policy", "disclaimer", "author"]
            
            # 🔴 අද දවසට අදාළ මාසය සහ අවුරුද්ද ලින්ක් එකට ගැලපෙනවද බලන්න හදනවා (උදා: /2026/09/)
            import datetime
            current_month_url = datetime.datetime.now().strftime("/%Y/%m/")
            
            for link in links:
                try:
                    href = str(link.get_attribute("href"))
                    title = link.text.strip()
                    if href and len(title) > 15 and href not in seen_jobs_global:
                        # 🔴 current_month_url එකත් අනිවාර්යයෙන්ම ලින්ක් එකේ තියෙන්නම ඕනේ! (පරණ ඒවා අයින් වෙයි)
                        if ".html" in href and domain in href and current_month_url in href:
                            href_lower = href.lower()
                            if not any(bad_word in href_lower for bad_word in bad_blog_links):
                                if href not in [j['link'] for j in found_blog]:
                                    found_blog.append({'title': title, 'link': href})
                except: continue
                
            for job in found_blog[:2]:
                if is_post_safe(job['title'], job['link']):
                    process_and_post(job, get_job_flyer(driver, job['link']))
        except Exception as e: print(f"{site_name} දෝෂයකි: {e}")
        finally:
            if driver: driver.quit()

    scrape_blogspot("https://jobvacanciesinsl.blogspot.com/search/label/Private%20Jobs?&max-results=5", "JobVacanciesInSL Private", "jobvacanciesinsl.blogspot.com")
    scrape_blogspot("https://jobvacanciesinsl.blogspot.com/search/label/government%20job?&max-results=5", "JobVacanciesInSL Government", "jobvacanciesinsl.blogspot.com")
    scrape_blogspot("https://www.plusinfo.lk/search/label/Private%20Jobs?&max-results=5", "PlusInfo Private Jobs", "plusinfo.lk")
    scrape_blogspot("https://www.plusinfo.lk/search/label/Government%20Jobs?&max-results=5", "PlusInfo Government Jobs", "plusinfo.lk")
    scrape_blogspot("https://www.rajayejobs.com/search/label/Private%20Jobs?&max-results=5", "RajayeJobs Private", "rajayejobs.com")
    scrape_blogspot("https://www.rajayejobs.com/search/label/Government%20Jobs?&max-results=5", "RajayeJobs Government", "rajayejobs.com")

    print("\n🏁 මේ වෙලාවේ සියලුම සයිට් පරීක්ෂාව අවසන්! ඊළඟ වෙලාව එනකම් බොට් නිදාගනී... 😴")

# ==========================================
# ⏰ SCHEDULER
# ==========================================
# ==========================================
# ⏰ SCHEDULER (GitHub Actions වලින් රන් වන නිසා ලූප් අවශ්‍ය නැත)
# ==========================================
if __name__ == "__main__":
    print("⏳ Lanka Career Hub Bot GitHub හරහා ක්‍රියාත්මකයි...")
    run_job_scraper()