from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests

def fetch_case_hc(case_type, case_no, year):
    url = "https://hcservices.ecourts.gov.in/hcservices/main.php"  # landing page
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=30000)
        # TODO: adapt selectors based on actual page; example:
        page.fill("#caseNoInput", str(case_no))
        page.select_option("#caseTypeSelect", case_type)
        page.fill("#yearInput", str(year))
        page.click("#searchBtn")
        page.wait_for_selector(".result-row", timeout=20000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    # parse party names, dates and status - selectors are placeholders
    party = soup.select_one(".party-names").get_text(strip=True) if soup.select_one(".party-names") else None
    filing_date = soup.select_one(".filing-date").get_text(strip=True) if soup.select_one(".filing-date") else None
    next_hearing = soup.select_one(".next-hearing").get_text(strip=True) if soup.select_one(".next-hearing") else None
    status = soup.select_one(".status").get_text(strip=True) if soup.select_one(".status") else None

    # find PDF links (example)
    pdf_urls = []
    for a in soup.select("a"):
        href = a.get("href","")
        if href.endswith(".pdf"):
            pdf_urls.append(href)

    # download PDFs
    saved_files = []
    for i, pdf in enumerate(pdf_urls):
        pdf_response = requests.get(pdf, timeout=30)
        fname = f"downloads/{case_type}_{case_no}_{i}.pdf"
        with open(fname, "wb") as f:
            f.write(pdf_response.content)
        saved_files.append(fname)

    return {
        "party": party,
        "filing_date": filing_date,
        "next_hearing": next_hearing,
        "status": status,
        "pdfs": saved_files,
        "raw_html": str(soup)
    }
