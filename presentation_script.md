# 🎙️ Presentation Speaker Script: DJ Profile Finder

*(This script is designed to be read while presenting `Technical_Overview.pdf` or `Technical_Overview.pptx`. It takes approximately 5-7 minutes to present.)*

---

## Slide 1: Title Slide (Intelligent AI Sourcing Bot)
**Speaker:**
"Hello everyone. Today I'm excited to walk you through a project I've been building called the DJ Profile Finder. 

It is an intelligent, fully automated AI sourcing bot designed to completely streamline how we find candidates. Instead of manually digging through LinkedIn or paying thousands of dollars for expensive enterprise tools like LinkedIn Recruiter or API subscriptions, I set out to build a zero-cost, automated solution that does the heavy lifting for us."

---

## Slide 2: Problem Statement & Constraints
**Speaker:**
"Before diving into the code, let's talk about the problem we were solving. 

The goal was simple: take a raw, unstructured Job Description, and output a clean list of highly qualified candidate profiles. 

But I had three very strict constraints:
1. **Zero Cost:** I refused to use paid APIs. No Google Search APIs, no paid scraping services.
2. **Anti-Ban Security:** LinkedIn is notoriously aggressive at banning automated bots. The tool had to be completely undetectable to protect our accounts.
3. **Non-Technical UX:** It had to be as easy to use as ChatGPT. I wanted a recruiter to just paste a JD into a chat window and let the system do the rest."

---

## Slide 3: High-Level Architecture
**Speaker:**
"To achieve this, I broke the system down into four main architectural pillars.

First, the **Frontend**, which is a custom Python Web UI built on Streamlit that mimics the clean, light-mode interface of ChatGPT. 

Second, the **Discovery Engine**, a custom web scraper that utilizes Yahoo Search to bypass CAPTCHA walls.

Third, the **Data Extraction Engine**, powered by Playwright Chromium, which actually drives a headless browser to read LinkedIn profiles.

And finally, the **Database Layer**, using SQLite and SQLAlchemy, to persistently store candidate data and resumes locally so nothing is ever lost."

---

## Slide 4: 1. Natural Language Processing (NLP)
**Speaker:**
"Let's look at the first step in the pipeline: Natural Language Processing. 

When a user pastes a massive, multi-paragraph Job Description into the chat, the bot needs to know what to search for. Instead of importing heavy, bloated machine learning models, I wrote a custom, lightweight tokenization algorithm. 

It strips out punctuation, enforces minimum word lengths, and filters out common 'stop-words' like 'company' or 'requirements' using an in-memory dictionary. It then runs a mathematical frequency analysis to derive the top 4 or 5 most important semantic keywords for that specific role. Those keywords become our search query."

---

## Slide 5: 2. Search & Discovery Engine
**Speaker:**
"Now, here is where we hit our first major technical hurdle. Search engines aggressively block automated bots. 

Initially, I tried using the DuckDuckGo API, but it frequently failed or returned zero results due to strict bot detection. I then tried Google Search, but they immediately blocked our headless browsers with unsolvable CAPTCHA walls.

The solution? I pivoted the Discovery Engine to use Yahoo Search via Playwright. Yahoo is significantly more lenient with automated browsing. However, Yahoo encrypts their outbound links to track clicks. To solve this, I wrote a custom decoding algorithm to reverse-engineer Yahoo's URL wrapping in real-time, allowing us to extract clean, direct 'linkedin.com/in/' URLs."

---

## Slide 6: 3. Safe Data Extraction
**Speaker:**
"Once we have the URLs, we have to actually scrape the LinkedIn profiles. This is dangerous because LinkedIn will ban accounts that scrape too fast.

To bypass this, I utilized Playwright to drive a *real* Chromium browser. It executes JavaScript exactly like a human user. More importantly, I implemented Persistent Sessions—meaning the browser saves your local cookies. It doesn't need to log in every single time, which is a massive red flag for security algorithms.

Finally, I hardcoded a strict, randomized rate limit. The bot waits exactly 30 to 35 seconds between every profile visit. This perfectly mimics human behavior and strictly enforces a '10 profiles per 5 minutes' speed limit, keeping the account 100% safe."

---

## Slide 7: 4. Database & Web Frontend
**Speaker:**
"Finally, the user experience.

All of this complex background scraping is hidden behind a beautiful, ChatGPT-style web interface. Building this in Streamlit presented a major challenge: deep threading conflicts between Windows and Python's asynchronous event loops, which caused the browser to crash in the background.

I solved this by explicitly injecting a `WindowsProactorEventLoopPolicy` and forcing synchronous Playwright execution within the Streamlit threads. 

The result is a seamless UI where a recruiter can chat with the bot, view their search history, upload resumes to a local database, and instantly access a saved database of candidates—all completely free, and completely automated.

Thank you. I'd be happy to answer any questions or give a live demo!"
