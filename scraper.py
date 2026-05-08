import time
import random
import re
from collections import Counter
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from database import init_db, Candidate, JobSearchQuery

# Minimal list of stop words to avoid external dependencies for NLP
STOP_WORDS = set([
    "the", "and", "to", "of", "a", "in", "for", "is", "on", "that", "by", "this", "with", "i", "you", "it", 
    "not", "or", "be", "are", "from", "at", "as", "your", "all", "have", "new", "more", "an", "was", "we",
    "will", "home", "can", "us", "about", "if", "page", "my", "has", "search", "free", "but", "our", "one",
    "other", "do", "no", "information", "time", "they", "site", "he", "up", "may", "what", "which", "their",
    "how", "were", "me", "some", "these", "click", "its", "like", "service", "than", "find", "date", "back", 
    "top", "people", "had", "list", "name", "just", "over", "state", "year", "day", "into", "email", "two",
    "world", "re", "next", "used", "go", "work", "last", "most", "make", "them", "should", "product", "system", 
    "post", "her", "city", "add", "policy", "number", "such", "please", "available", "support", "message", 
    "after", "best", "software", "then", "good", "well", "where", "info", "through", "each", "she", "years", 
    "very", "company", "read", "group", "need", "many", "user", "said", "does", "set", "under", "general", 
    "research", "full", "program", "life", "know", "way", "days", "management", "part", "could", "great", 
    "united", "real", "center", "must", "development", "report", "off", "member", "details", "line", "terms", 
    "before", "did", "send", "right", "type", "because", "local", "those", "using", "results", "office", 
    "education", "national", "design", "take", "posted", "internet", "address", "community", "within", "states", 
    "area", "want", "phone", "subject", "between", "family", "long", "based", "code", "show", "even", "check", 
    "special", "website", "much", "sign", "file", "link", "open", "today", "technology", "south", "case", 
    "project", "same", "pages", "version", "section", "own", "found", "related", "security", "both", "american", 
    "members", "power", "while", "care", "network", "down", "computer", "systems", "three", "total", "place", 
    "end", "following", "download", "him", "without", "per", "access", "think", "north", "resources", "current", 
    "big", "media", "law", "control", "history", "size", "art", "personal", "since", "including", "guide", 
    "board", "location", "change", "white", "text", "small", "rating", "rate", "government", "during", "usa", 
    "return", "students", "account", "times", "sites", "level", "digital", "profile", "previous", "form", 
    "events", "love", "old", "main", "call", "hours", "image", "department", "title", "description", "non", 
    "insurance", "another", "why", "shall", "property", "class", "still", "money", "quality", "every", "listing", 
    "content", "country", "private", "little", "visit", "save", "tools", "low", "reply", "customer", "compare", 
    "include", "college", "value", "article", "york", "man", "card", "jobs", "provide", "source", "author", 
    "different", "press", "learn", "sale", "around", "course", "job", "process", "training", "too", "credit", 
    "point", "join", "science", "men", "advanced", "west", "sales", "look", "english", "left", "team", "box", 
    "conditions", "select", "windows", "week", "category", "note", "live", "large", "table", "register", "however", 
    "market", "library", "really", "action", "start", "series", "model", "features", "industry", "plan", "human", 
    "provided", "yes", "required", "second", "cost", "better", "say", "questions", "going", "medical", "test", 
    "friend", "come", "server", "study", "application", "staff", "articles", "feedback", "again", "play", 
    "looking", "issues", "never", "users", "complete", "street", "topic", "comment", "financial", "things", 
    "working", "against", "standard", "person", "below", "mobile", "less", "got", "payment", "equipment", "login", 
    "student", "let", "programs", "offers", "options", "services", "looking", "candidate", "role", "requirements", 
    "experience", "strong", "skills", "ability", "knowledge", "working", "understanding", "preferred", "plus", 
    "equivalent", "degree", "years", "proven", "track", "record", "excellent", "written", "verbal", "communication",
    "responsibilities", "duties", "qualifications", "required", "minimum", "maximum", "including", "related",
    "field", "bachelor", "master", "phd", "equivalent", "position", "seeking", "hiring", "join", "team", "company"
])

def extract_keywords(jd_text, top_n=5):
    """Extracts top keywords from a Job Description ignoring stop words."""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', jd_text.lower())
    filtered_words = [w for w in words if w not in STOP_WORDS]
    most_common = [word for word, count in Counter(filtered_words).most_common(top_n)]
    return most_common

def find_linkedin_profiles(keywords, location="", db_session=None, max_results=10, start_page=1):
    """Uses Playwright to search LinkedIn directly with an authenticated session."""
    import urllib.parse
    import re
    import os
    import time
    import random
    
    query_str = " ".join(keywords)
    if location:
        query_str += f' "{location}"'
        
    print(f"[*] Searching LinkedIn directly for: {query_str} (Page {start_page})")
    
    profiles = []
    seen_urls = set()
    
    # We need the absolute path for playwright_profile
    profile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "playwright_profile"))
    
    try:
        with sync_playwright() as p:
            # We use headless=False so the user can log in if needed or solve CAPTCHAs
            browser = p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=False,
                viewport={"width": 1280, "height": 800}
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Go to LinkedIn
            page.goto("https://www.linkedin.com/")
            
            # Check if we are logged in by looking for the nav bar or login field
            time.sleep(random.uniform(2, 4))
            if page.locator("input#session_key").count() > 0 or page.locator("input#username").count() > 0:
                print("\n[!] IMPORTANT: You are not logged into LinkedIn.")
                print("[!] A browser window has opened. Please log in to your account.")
                print("[!] Waiting for you to log in... (I will automatically continue once logged in)")
                # Wait until the global nav search bar appears (meaning login successful)
                page.wait_for_selector("input.search-global-typeahead__input", timeout=600000) # 10 minutes max wait
                print("[*] Login detected! Proceeding with search...\n")
                time.sleep(random.uniform(2, 4))
            
            # Construct search URL
            url_encoded_query = urllib.parse.quote(query_str)
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={url_encoded_query}&page={start_page}"
            
            print(f"[*] Navigating to search page: {search_url}")
            page.goto(search_url)
            
            # Wait for results to load
            try:
                page.wait_for_selector("ul.reusable-search__entity-result-list", timeout=15000)
            except:
                print("    [!] Could not find search results. You might have hit a search limit or CAPTCHA.")
                print("    [!] Look at the browser window to resolve any issues.")
                try:
                    input("    [!] Press Enter here AFTER resolving the issue in the browser...")
                except EOFError:
                    pass
            
            # Scroll down slowly to load all results on the page
            for _ in range(4):
                page.mouse.wheel(0, 500)
                time.sleep(random.uniform(1, 2))
                
            # Extract results
            results = page.evaluate('''() => {
                const items = Array.from(document.querySelectorAll('li.reusable-search__result-container'));
                return items.map(item => {
                    const nameEl = item.querySelector('span[dir="ltr"] span[aria-hidden="true"]');
                    const linkEl = item.querySelector('a.app-aware-link');
                    const headlineEl = item.querySelector('.entity-result__primary-subtitle');
                    const locationEl = item.querySelector('.entity-result__secondary-subtitle');
                    
                    return {
                        name: nameEl ? nameEl.innerText.trim() : '',
                        url: linkEl ? linkEl.href.split('?')[0] : '', // Remove tracking parameters
                        headline: headlineEl ? headlineEl.innerText.trim() : '',
                        location: locationEl ? locationEl.innerText.trim() : ''
                    };
                });
            }''')
            
            for res in results:
                name = res.get('name', '')
                clean_url = res.get('url', '')
                headline = res.get('headline', '')
                candidate_location = res.get('location', '')
                
                if not name or not clean_url or 'linkedin.com/in/' not in clean_url:
                    continue
                    
                if clean_url in seen_urls or name == "LinkedIn Member":
                    continue
                    
                seen_urls.add(clean_url)
                
                print(f"    Found: {name}")
                print(f"    Headline: {headline}")
                print(f"    Location: {candidate_location}")
                
                # Save to database
                if db_session:
                    existing = db_session.query(Candidate).filter_by(linkedin_url=clean_url).first()
                    if not existing:
                        candidate = Candidate(
                            linkedin_url=clean_url,
                            name=name,
                            headline=headline,
                            location=candidate_location
                        )
                        db_session.add(candidate)
                        db_session.commit()
                
                profiles.append({
                    "name": name,
                    "headline": headline,
                    "location": candidate_location,
                    "url": clean_url
                })
                
                if len(profiles) >= max_results:
                    break
                    
            browser.close()
    except Exception as e:
        print(f"[!] Error during LinkedIn search: {e}")
        
    print(f"[*] Found {len(profiles)} profile URLs on this page.")
    return profiles

def run_job_search(jd_text, location=""):
    """Main pipeline generator that yields batches of candidates."""
    import time
    import random
    engine, session = init_db()
    
    query_log = JobSearchQuery(job_description=jd_text)
    session.add(query_log)
    session.commit()
    
    print("\n--- Step 1: Extracting Keywords ---")
    keywords = extract_keywords(jd_text, top_n=10)
    print(f"Extracted Keywords from JD: {keywords}")
    
    total_profiles = 0
    # Run 3 batches to get profiles, incrementing page number
    for batch_num in range(3):
        start_page = batch_num + 1
        print(f"\n--- Step 2: Finding Candidates directly on LinkedIn (Page {start_page}) ---")
        results = find_linkedin_profiles(keywords, location, db_session=session, max_results=10, start_page=start_page) 
        
        if not results:
            print("No Candidates found on this page.")
            if batch_num == 0:
                yield []
            break
            
        print("\n--- Step 3: Calculating Match Percentage & Generating Fit Justification ---")
        for res in results:
            candidate_text = f"{res['headline']} {res['location']} {res['name']}".lower()
            candidate_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', candidate_text))
            jd_words = set([k.lower() for k in keywords])
            
            matched_keywords = jd_words.intersection(candidate_words)
            match_count = len(matched_keywords)
            base_score = 75 
            match_percentage = min(99, base_score + (match_count * 5))
            res['match_percentage'] = match_percentage
            
            # Generate fit justification sentence
            if matched_keywords:
                matched_str = ", ".join(list(matched_keywords)[:3])
                res['fit_justification'] = f"This profile aligns with the role due to matching key terms like '{matched_str}' found in their headline/location."
            else:
                res['fit_justification'] = "This profile was returned by LinkedIn search as a potential fit for the required skills."
                
        filtered_results = results

        total_profiles += len(results)
        yield filtered_results
        
        # Human-like delay between pages
        if batch_num < 2 and len(results) > 0:
            delay = random.uniform(15, 30) # Wait 15-30 seconds between pages to mimic humans
            print(f"Waiting {delay:.1f} seconds before next page to avoid rate limits... (Found {total_profiles} so far)")
            time.sleep(delay)

if __name__ == "__main__":
    print("=================================================")
    print("  Free Local LinkedIn Recruiter Tool  ")
    print("=================================================")
    print("Paste your Job Description below.")
    print("When you are finished pasting, type the word DONE on a new line and press Enter:")
    print("-------------------------------------------------")
    
    jd_lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == 'DONE':
                break
            jd_lines.append(line)
        except EOFError:
            break
            
    jd_text = "\n".join(jd_lines)
    
    if jd_text.strip():
        # In CLI mode, just run without location
        for batch in run_job_search(jd_text, location=""):
            for res in batch:
                print(f" -> {res['name']} ({res.get('match_percentage', 0)}% Match) | {res['url']}")
                print(f"    Fit: {res.get('fit_justification', '')}")
    else:
        print("No Job Description provided. Exiting.")
