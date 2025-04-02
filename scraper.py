from flask import Flask, request, jsonify, send_file
from playwright.sync_api import sync_playwright
import csv
import os
import uuid

app = Flask(__name__)

def extract_lot_links(page):
    page.wait_for_timeout(5000)
    return page.eval_on_selector_all("a[href*='/l/']", "elements => [...new Set(elements.map(e => e.href))]")

def extract_lot_data(page):
    title = page.title()
    url = page.url
    try:
        price_element = page.query_selector("span[class*='price'], div[class*='price'], span[data-test='lot-price']")
        price = price_element.inner_text().strip() if price_element else "N/A"
    except:
        price = "N/A"
    return {"title": title, "url": url, "price": price}

@app.route("/scrape", methods=["GET"])
def scrape():
    auction_url = request.args.get("url")
    if not auction_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(auction_url, timeout=60000)

            lot_links = extract_lot_links(page)
            if not lot_links:
                return jsonify({"error": "No lot links found"}), 404

            results = []
            for link in lot_links:
                try:
                    lot_page = context.new_page()
                    lot_page.goto(link, timeout=45000)
                    data = extract_lot_data(lot_page)
                    results.append(data)
                    lot_page.close()
                except Exception as e:
                    results.append({"url": link, "error": str(e)})

            browser.close()

        # Save to CSV
        filename = f"/tmp/{uuid.uuid4().hex}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "url", "price"])
            writer.writeheader()
            writer.writerows(results)

        return send_file(filename, as_attachment=True, download_name="catawiki_lots.csv")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)