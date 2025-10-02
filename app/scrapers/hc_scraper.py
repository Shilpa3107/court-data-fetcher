from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urljoin

def fetch_case_hc(case_type, case_no, year):
    base_url = "https://hcservices.ecourts.gov.in/hcservices/main.php"  # landing page
    downloads_dir = "downloads"
    os.makedirs(downloads_dir, exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Go to site
            page.goto(base_url, timeout=30000)

            # ---- Fill form (update selectors after inspecting the real page) ----
            page.fill("#caseNoInput", str(case_no))
            page.select_option("#caseTypeSelect", case_type)
            page.fill("#yearInput", str(year))

            # Submit search
            page.click("#searchBtn")

            # Wait for result table/list
            try:
                page.wait_for_selector(".result-row", timeout=20000)
            except PlaywrightTimeoutError:
                print("No results found or page took too long to load.")
                return None

            html = page.content()
            browser.close()

        # ---- Parse results ----
        soup = BeautifulSoup(html, "html.parser")

        # Extract info (update selectors based on actual HTML)
        party = soup.select_one(".party-names").get_text(strip=True) if soup.select_one(".party-names") else None
        filing_date = soup.select_one(".filing-date").get_text(strip=True) if soup.select_one(".filing-date") else None
        next_hearing = soup.select_one(".next-hearing").get_text(strip=True) if soup.select_one(".next-hearing") else None
        status = soup.select_one(".status").get_text(strip=True) if soup.select_one(".status") else None

        # ---- Find PDF links ----
        pdf_urls = []
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if href.endswith(".pdf"):
                pdf_urls.append(urljoin(base_url, href))

        # ---- Download PDFs ----
        saved_files = []
        for i, pdf_url in enumerate(pdf_urls):
            try:
                pdf_response = requests.get(pdf_url, timeout=30)
                pdf_response.raise_for_status()
                fname = os.path.join(downloads_dir, f"{case_type}_{case_no}_{i}.pdf")
                with open(fname, "wb") as f:
                    f.write(pdf_response.content)
                saved_files.append(fname)
            except Exception as e:
                print(f"Failed to download PDF {pdf_url}: {e}")

        return {
            "party": party,
            "filing_date": filing_date,
            "next_hearing": next_hearing,
            "status": status,
            "pdfs": saved_files,
            "raw_html": str(soup)
        }

    except Exception as e:
        print(f"Error occurred: {e}")
        return None


# Example usage
if __name__ == "__main__":
    result = fetch_case_hc("CIVIL", 1234, 2023)
    if result:
        print("Case Info:", result)
    else:
        print("No data retrieved.")

