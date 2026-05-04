from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def create_presentation():
    # Create presentation
    prs = Presentation()
    
    # Define slide layouts
    title_slide_layout = prs.slide_layouts[0]
    bullet_slide_layout = prs.slide_layouts[1]
    
    # ---------------------------------------------------
    # Slide 1: Title
    # ---------------------------------------------------
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]
    
    title.text = "Intelligent AI Sourcing Bot"
    subtitle.text = "Technical Architecture & Implementation Review\nBuilt for Zero-Cost, Automated LinkedIn Recruiting"
    
    # ---------------------------------------------------
    # Slide 2: Problem Statement & Constraints
    # ---------------------------------------------------
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "Problem Statement & Constraints"
    tf = body_shape.text_frame
    
    tf.text = "Objective: Build an automated candidate sourcing tool that inputs raw Job Descriptions and outputs candidate profiles."
    
    p = tf.add_paragraph()
    p.text = "Strict Technical Constraints:"
    p.level = 0
    
    p = tf.add_paragraph()
    p.text = "Zero Cost: No paid APIs (LinkedIn Recruiter API, Google Search API, etc.)"
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Anti-Ban Requirements: Must respect LinkedIn's strict anti-bot measures."
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Non-Technical UX: Must be easy to use via a ChatGPT-style interface."
    p.level = 1
    
    # ---------------------------------------------------
    # Slide 3: High-Level Architecture
    # ---------------------------------------------------
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "High-Level Architecture"
    tf = body_shape.text_frame
    
    tf.text = "The solution is divided into four main technological pillars:"
    
    p = tf.add_paragraph()
    p.text = "Frontend: Streamlit (Python Web UI)"
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Discovery Engine: Custom Yahoo Web Scraper via Playwright"
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Data Extraction: Playwright Chromium Browser Automation"
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Database / Storage: SQLite with SQLAlchemy ORM"
    p.level = 1

    # ---------------------------------------------------
    # Slide 4: NLP & Keyword Extraction
    # ---------------------------------------------------
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "1. Natural Language Processing"
    tf = body_shape.text_frame
    
    tf.text = "Challenge: Converting unstructured, multi-paragraph Job Descriptions into actionable search queries."
    
    p = tf.add_paragraph()
    p.text = "Implementation:"
    p.level = 0
    
    p = tf.add_paragraph()
    p.text = "Tokenization & Cleaning: Stripping punctuation and enforcing minimum word lengths using Regex."
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Stop-Word Filtration: A custom, lightweight dictionary removes common words ('and', 'the', 'company') without bloated external dependencies."
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Frequency Analysis: Utilizes Python's collections.Counter to mathematically derive the top 5 most relevant semantic keywords."
    p.level = 1

    # ---------------------------------------------------
    # Slide 5: The Discovery Engine
    # ---------------------------------------------------
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "2. Search & Discovery Engine"
    tf = body_shape.text_frame
    
    tf.text = "Challenge: Search engines aggressively block automated web scrapers."
    
    p = tf.add_paragraph()
    p.text = "DuckDuckGo API: Frequently broke or returned 0 results."
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Google Search: Blocked headless browsers with CAPTCHA walls."
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Solution: Migrated to Yahoo Search using Playwright."
    p.level = 0
    
    p = tf.add_paragraph()
    p.text = "Yahoo allows automated browsing more leniently."
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Technical complexity: Reverse-engineered and decoded Yahoo's encrypted URL wrapping to extract clean linkedin.com URLs."
    p.level = 1

    # ---------------------------------------------------
    # Slide 6: Scraping & Anti-Ban Strategy
    # ---------------------------------------------------
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "3. Safe Data Extraction"
    tf = body_shape.text_frame
    
    tf.text = "Challenge: Scraping LinkedIn directly without getting the user's account banned."
    
    p = tf.add_paragraph()
    p.text = "Playwright Automation: Drives a real Chromium instance, executing JS exactly like a human to bypass basic scraping filters."
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Persistent Sessions: User profile cookies are saved locally. Prevents repeated logins which flag security algorithms."
    p.level = 1
    
    p = tf.add_paragraph()
    p.text = "Strict Rate Limiting: Enforces a randomized 30-35 second delay between visits, perfectly mirroring the requested '10 profiles per 5 mins' constraint."
    p.level = 1

    # ---------------------------------------------------
    # Slide 7: Database & Web UI
    # ---------------------------------------------------
    slide = prs.slides.add_slide(bullet_slide_layout)
    shapes = slide.shapes
    title_shape = shapes.title
    body_shape = shapes.placeholders[1]
    
    title_shape.text = "4. Database & Web Frontend"
    tf = body_shape.text_frame
    
    tf.text = "Data Persistence: Relational SQLite database using SQLAlchemy ensures candidate data is never lost and allows for direct CSV export."
    
    p = tf.add_paragraph()
    p.text = "Streamlit Frontend: Migrated from terminal CLI to a dynamic web UI."
    p.level = 0
    
    p = tf.add_paragraph()
    p.text = "Technical Hurdles Overcome: Resolved deep Windows/Python threading conflicts by explicitly setting WindowsProactorEventLoopPolicy and enforcing synchronous Playwright execution."
    p.level = 1
    
    # Save presentation
    prs.save("Technical_Overview.pptx")
    print("Presentation saved as Technical_Overview.pptx")

if __name__ == "__main__":
    create_presentation()
