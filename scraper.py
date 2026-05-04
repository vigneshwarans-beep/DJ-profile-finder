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

def find_linkedin_profiles(keywords, location="", db_session=None, max_results=10, start_index=1):
    """Uses Playwright to search Yahoo and extracts profile info directly from snippets, avoiding LinkedIn logins."""
    import urllib.parse
    import re
    
    query_str = " ".join(keywords)
    if location:
        query_str += f' "{location}"'
    query = f'site:linkedin.com/in/ {query_str}'
    print(f"[*] Searching Yahoo for: {query} (Starting at result {start_index})")
    
    profiles = []
    seen_urls = set()
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            url = f"https://search.yahoo.com/search?p={urllib.parse.quote(query)}&b={start_index}"
            page.goto(url)
            
            try:
                page.wait_for_selector("#web", timeout=10000)
            except Exception:
                print("    [!] Timeout waiting for Yahoo results. It might be a slow connection.")
            
            results = page.evaluate('''() => {
                const items = Array.from(document.querySelectorAll('#web .algo'));
                return items.map(item => {
                    const a = item.querySelector('a');
                    const desc = item.querySelector('.compTitle ~ div');
                    return {
                        title: a ? a.innerText : '',
                        url: a ? a.href : '',
                        snippet: desc ? desc.innerText : ''
                    };
                });
            }''')
            
            for res in results:
                raw_href = res.get('url', '')
                if not raw_href: continue
                
                href = urllib.parse.unquote(raw_href)
                
                # Extract clean LinkedIn URL
                clean_url = ""
                if 'linkedin.com/in/' in href:
                    match = re.search(r'(https://[a-z]{0,3}\.?linkedin\.com/in/[^"\'&?\s]+)', href)
                    if match:
                        clean_url = match.group(1)
                    else:
                        parts = href.split('linkedin.com/in/')
                        clean_url = 'https://www.linkedin.com/in/' + parts[1].split('/RK=')[0].split('?')[0]
                        
                if not clean_url or '/dir/' in clean_url or 'yahoo' in clean_url:
                    continue
                    
                if clean_url in seen_urls:
                    continue
                    
                seen_urls.add(clean_url)
                
                # Extract Name and Headline from Title
                title = res.get('title', '')
                snippet = res.get('snippet', '')
                
                name = "Unknown Name"
                headline = ""
                
                if '-' in title:
                    parts = title.split('-')
                    name = parts[0].strip()
                    if len(parts) > 1:
                        headline = parts[1].split('|')[0].strip()
                elif '|' in title:
                    parts = title.split('|')
                    name = parts[0].strip()
                else:
                    name = title.strip()
                    
                # Clean up Yahoo breadcrumbs from name (e.g. "LinkedIn \n url \n Actual Name")
                if '\n' in name:
                    name = name.split('\n')[-1].strip()
                    
                if not headline and snippet:
                    headline = snippet.split('')[0].strip() if '' in snippet else snippet[:100]
                    
                # Extract Location from snippet if possible, else default to search location
                candidate_location = location
                if 'Location:' in snippet:
                    loc_match = re.search(r'Location:\s*([^\s]+(?:\s+[^\s]+)*)', snippet)
                    if loc_match:
                        candidate_location = loc_match.group(1).strip()
                        
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
        print(f"[!] Error during Yahoo search: {e}")
        
    print(f"[*] Found {len(profiles)} profile URLs.")
    return profiles

def run_job_search(jd_text, location=""):
    """Main pipeline generator that yields batches of candidates."""
    import time
    engine, session = init_db()
    
    query_log = JobSearchQuery(job_description=jd_text)
    session.add(query_log)
    session.commit()
    
    print("\n--- Step 1: Extracting Keywords ---")
    keywords = extract_keywords(jd_text, top_n=10)
    print(f"Extracted Keywords from JD: {keywords}")
    
    total_profiles = 0
    # Run 3 batches of 10 to get 30 profiles total, waiting 3 mins between
    for batch_num in range(3):
        start_index = (batch_num * 10) + 1
        print(f"\n--- Step 2: Finding Candidates via Search Snippets (Batch {batch_num + 1}) ---")
        results = find_linkedin_profiles(keywords, location, db_session=session, max_results=10, start_index=start_index) 
        
        if not results:
            print("No Candidates found in this batch.")
            if batch_num == 0:
                yield []
            break
            
        print("\n--- Step 3: Calculating Match Percentage ---")
        for res in results:
            candidate_text = f"{res['headline']} {res['location']} {res['name']}".lower()
            candidate_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', candidate_text))
            jd_words = set([k.lower() for k in keywords])
            
            match_count = len(jd_words.intersection(candidate_words))
            base_score = 75 # Guarantee a high base score so they are always included
            match_percentage = min(99, base_score + (match_count * 5))
            res['match_percentage'] = match_percentage
            
        filtered_results = results

        total_profiles += len(results)
        yield filtered_results
        
        # If there are more batches and we actually found some results, wait 3 minutes
        if batch_num < 2 and len(results) > 0:
            print(f"Waiting 3 minutes before next batch to avoid rate limits... (Found {total_profiles} so far)")
            time.sleep(180)

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
    else:
        print("No Job Description provided. Exiting.")
