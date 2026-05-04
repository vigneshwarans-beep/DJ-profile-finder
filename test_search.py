from scraper import find_linkedin_urls

def main():
    urls = find_linkedin_urls(["software", "engineer"], max_results=5)
    print(f"\nFINAL OUTPUT: {urls}")

if __name__ == "__main__":
    main()
