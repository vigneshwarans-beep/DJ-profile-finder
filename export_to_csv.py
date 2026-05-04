import csv
from database import init_db, Candidate

def export_to_csv(csv_filename="candidates_export.csv"):
    """Reads candidates from the SQLite database and exports them to a CSV file."""
    print("[*] Connecting to database...")
    engine, session = init_db()
    
    # Fetch all scraped candidates
    candidates = session.query(Candidate).all()
    
    if not candidates:
        print("[-] No candidates found in the database. Make sure you run scraper.py first.")
        return
        
    print(f"[*] Found {len(candidates)} candidates. Exporting...")
    
    try:
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write column headers
            writer.writerow(["ID", "Name", "Headline", "Location", "LinkedIn URL", "Scraped At"])
            
            # Write row data
            for c in candidates:
                writer.writerow([
                    c.id,
                    c.name,
                    c.headline,
                    c.location,
                    c.linkedin_url,
                    c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else ""
                ])
                
        print(f"[+] Success! Exported to {csv_filename}")
        print("    You can now open this file in Excel, Google Sheets, or any spreadsheet software.")
    except Exception as e:
        print(f"[!] Error exporting to CSV: {e}")

if __name__ == "__main__":
    export_to_csv()
