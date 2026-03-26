import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

# =========================
# Load ENV
# =========================
load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

FAQ_URL_STC = os.getenv("FAQ_URL_STC")
FAQ_URL_WE = os.getenv("FAQ_URL_WE")

# =========================
# Initialize Firecrawl
# =========================
app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

# =========================
# Output folder
# =========================
OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# Helper function
# =========================

#fo ther to know scrape srtucture code https://docs.firecrawl.dev/features/scrape

def scrape_and_save(url, name):
    print(f"\n🚀 Scraping: {name}")

    try:
        response = app.scrape(
            url=url,
            formats= ["markdown"]
        
        )

        '''
        os.path.join() is a Python function that intelligently joins one or more path components into a single path string, 
        automatically using the correct directory separator for the operating system (e.g., / for Linux/macOS and \ for Windows).
        '''

        file_path = os.path.join(OUTPUT_DIR, f"{name}.md")  #os.path.join 


        with open(file_path, "w", encoding="utf-8") as f: 
            f.write(response.markdown)

        print(f"✅ Saved → {file_path}")

    except Exception as e:
        print(f"❌ Error scraping {name}: {e}")


# =========================
# Run scraping
# =========================
if FAQ_URL_STC:
    scrape_and_save(FAQ_URL_STC, "faq_stc")

if FAQ_URL_WE:
    scrape_and_save(FAQ_URL_WE, "faq_we")

print("\n🎯 Scraping completed.")


# =========================
# monitoring API firecrawl usag
# =========================

#go to this link to check usage https://www.firecrawl.dev/app