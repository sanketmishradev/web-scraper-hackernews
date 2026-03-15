import urllib.request
import urllib.parse
import html
import re
import csv
import os
from datetime import datetime

# ─────────────────────────────────────────
#  Web Scraper — Hacker News Top Stories
#  Tech: Python (urllib, csv, re — no external libs)
# ─────────────────────────────────────────

BASE_URL = "https://news.ycombinator.com/"

def fetch_html(url):
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; PythonScraper/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        print(f"  ⚠️  Could not fetch URL: {e}")
        return None

def parse_stories(html_content):
    stories = []

    # Extract title rows
    title_pattern = re.compile(
        r'<span class="rank">(\d+)\.</span>.*?'
        r'<span class="titleline"><a href="([^"]+)"[^>]*>([^<]+)</a>.*?'
        r'<span class="sitestr">([^<]+)</span>',
        re.DOTALL
    )

    # Extract score/meta rows
    score_pattern = re.compile(
        r'<span class="score"[^>]*>(\d+ points?)</span>.*?'
        r'<a[^>]+>\s*(\d+)\s+(?:comment|comments|discuss)',
        re.DOTALL
    )

    titles   = title_pattern.findall(html_content)
    metadata = score_pattern.findall(html_content)

    for i, (rank, url, title, site) in enumerate(titles):
        title   = html.unescape(title.strip())
        url     = html.unescape(url.strip())
        score   = metadata[i][0] if i < len(metadata) else "N/A"
        comments= metadata[i][1] if i < len(metadata) else "0"

        # Make relative URLs absolute
        if url.startswith("item?"):
            url = BASE_URL + url

        stories.append({
            "rank":     rank,
            "title":    title,
            "url":      url,
            "site":     site,
            "score":    score,
            "comments": comments,
        })

    return stories

def display_stories(stories, limit=10):
    print("\n" + "═" * 70)
    print("   🔥  HACKER NEWS — TOP STORIES")
    print("═" * 70)
    for s in stories[:limit]:
        print(f"\n  [{s['rank']:>2}]  {s['title']}")
        print(f"        🌐 {s['site']:<30} ⭐ {s['score']:<15} 💬 {s['comments']} comments")
        print(f"        🔗 {s['url'][:65]}{'...' if len(s['url']) > 65 else ''}")
    print("\n" + "═" * 70)

def save_to_csv(stories, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"hackernews_{timestamp}.csv"

    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rank", "title", "url", "site", "score", "comments"])
        writer.writeheader()
        writer.writerows(stories)

    print(f"\n  ✅ Saved {len(stories)} stories to → {filename}")
    return filepath

def filter_stories(stories, keyword):
    keyword = keyword.lower()
    filtered = [s for s in stories if keyword in s["title"].lower()]
    print(f"\n  🔍 Found {len(filtered)} stories matching '{keyword}'")
    return filtered

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("\n╔══════════════════════════════════════╗")
    print("║   🕷️  Hacker News Web Scraper         ║")
    print("╚══════════════════════════════════════╝\n")

    print("  Fetching top stories from Hacker News...")
    html_content = fetch_html(BASE_URL)

    if not html_content:
        print("  ❌ Failed to fetch data. Check your internet connection.")
        return

    stories = parse_stories(html_content)

    if not stories:
        print("  ❌ Could not parse stories. The site structure may have changed.")
        return

    print(f"  ✅ Scraped {len(stories)} stories!\n")

    while True:
        print("\n  ┌─ MENU ──────────────────────────────┐")
        print("  │  [1] Show top 10 stories            │")
        print("  │  [2] Show top 20 stories            │")
        print("  │  [3] Search stories by keyword      │")
        print("  │  [4] Save all stories to CSV        │")
        print("  │  [5] Exit                           │")
        print("  └─────────────────────────────────────┘")
        choice = input("\n  Choose option: ").strip()

        if choice == "1":
            display_stories(stories, 10)
        elif choice == "2":
            display_stories(stories, 20)
        elif choice == "3":
            keyword = input("  Enter keyword to search: ").strip()
            if keyword:
                results = filter_stories(stories, keyword)
                display_stories(results, len(results))
            else:
                print("  ⚠️  Please enter a keyword.")
        elif choice == "4":
            save_to_csv(stories)
        elif choice == "5":
            print("\n  👋 Goodbye!\n")
            break
        else:
            print("  ⚠️  Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
