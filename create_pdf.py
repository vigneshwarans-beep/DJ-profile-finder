from fpdf import FPDF

class PresentationPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'LinkedIn Sourcing Bot - Technical Overview', border=False, align='R')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def add_slide(self, title, content):
        self.add_page()
        # Title
        self.set_font('helvetica', 'B', 24)
        self.set_text_color(10, 102, 194)  # LinkedIn Blue
        self.multi_cell(0, 15, title, align='L')
        self.ln(10)
        
        # Content
        self.set_text_color(0, 0, 0)
        for item in content:
            if item.startswith('- '):
                self.set_font('helvetica', '', 14)
                # Render bullet point
                self.cell(10, 10, chr(149), ln=False)
                self.multi_cell(0, 10, item[2:])
                self.ln(2)
            elif item.startswith('  - '):
                self.set_font('helvetica', '', 12)
                # Render sub-bullet point
                self.cell(20)
                self.cell(10, 8, '-', ln=False)
                self.multi_cell(0, 8, item[4:])
                self.ln(2)
            else:
                self.set_font('helvetica', 'B', 16)
                self.multi_cell(0, 12, item)
                self.ln(4)

def create_pdf():
    pdf = PresentationPDF(orientation='L', unit='mm', format='A4') # Landscape format for slides
    pdf.set_auto_page_break(auto=True, margin=15)

    # Slide 1
    pdf.add_page()
    pdf.set_y(80)
    pdf.set_font('helvetica', 'B', 36)
    pdf.set_text_color(10, 102, 194)
    pdf.cell(0, 20, 'Intelligent AI Sourcing Bot', align='C', ln=True)
    pdf.set_font('helvetica', '', 18)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, 'Technical Architecture & Implementation Review', align='C', ln=True)
    pdf.cell(0, 10, 'Built for Zero-Cost, Automated LinkedIn Recruiting', align='C', ln=True)

    # Slide 2
    pdf.add_slide("Problem Statement & Constraints", [
        "Objective:",
        "- Build an automated candidate sourcing tool that inputs raw Job Descriptions and outputs candidate profiles.",
        "Strict Technical Constraints:",
        "- Zero Cost: No paid APIs (LinkedIn Recruiter API, Google Search API, etc.)",
        "- Anti-Ban Requirements: Must respect LinkedIn's strict anti-bot measures.",
        "- Non-Technical UX: Must be easy to use via a ChatGPT-style interface."
    ])

    # Slide 3
    pdf.add_slide("High-Level Architecture", [
        "The solution is divided into four main technological pillars:",
        "- Frontend: Streamlit (Python Web UI)",
        "- Discovery Engine: Custom Yahoo Web Scraper via Playwright",
        "- Data Extraction: Playwright Chromium Browser Automation",
        "- Database / Storage: SQLite with SQLAlchemy ORM"
    ])

    # Slide 4
    pdf.add_slide("1. Natural Language Processing", [
        "Challenge: Converting unstructured, multi-paragraph Job Descriptions into actionable search queries.",
        "Implementation:",
        "- Tokenization & Cleaning: Stripping punctuation and enforcing minimum word lengths using Regex.",
        "- Stop-Word Filtration: A custom, lightweight dictionary removes common words ('and', 'the', 'company') without bloated external dependencies.",
        "- Frequency Analysis: Utilizes Python's collections.Counter to mathematically derive the top 5 most relevant semantic keywords."
    ])

    # Slide 5
    pdf.add_slide("2. Search & Discovery Engine", [
        "Challenge: Search engines aggressively block automated web scrapers.",
        "- DuckDuckGo API: Frequently broke or returned 0 results.",
        "- Google Search: Blocked headless browsers with CAPTCHA walls.",
        "Solution: Migrated to Yahoo Search using Playwright.",
        "- Yahoo allows automated browsing more leniently.",
        "- Technical complexity: Reverse-engineered and decoded Yahoo's encrypted URL wrapping to extract clean linkedin.com URLs."
    ])

    # Slide 6
    pdf.add_slide("3. Safe Data Extraction", [
        "Challenge: Scraping LinkedIn directly without getting the user's account banned.",
        "- Playwright Automation: Drives a real Chromium instance, executing JS exactly like a human to bypass basic scraping filters.",
        "- Persistent Sessions: User profile cookies are saved locally. Prevents repeated logins which flag security algorithms.",
        "- Strict Rate Limiting: Enforces a randomized 30-35 second delay between visits, perfectly mirroring the requested '10 profiles per 5 mins' constraint."
    ])

    # Slide 7
    pdf.add_slide("4. Database & Web Frontend", [
        "Data Persistence:",
        "- Relational SQLite database using SQLAlchemy ensures candidate data is never lost and allows for direct CSV export.",
        "Streamlit Frontend:",
        "- Migrated from terminal CLI to a dynamic web UI.",
        "- Technical Hurdles Overcome: Resolved deep Windows/Python threading conflicts by explicitly setting WindowsProactorEventLoopPolicy and enforcing synchronous Playwright execution."
    ])

    pdf.output("Technical_Overview.pdf")
    print("PDF saved as Technical_Overview.pdf")

if __name__ == "__main__":
    create_pdf()
