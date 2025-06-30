import requests
from bs4 import BeautifulSoup
from datetime import datetime
from deep_translator import GoogleTranslator
import time
from urllib.parse import urljoin 



# 可配置多个静态网站
URLS = [
    'https://www.abc.net.au/news',
    'https://www.bbc.com/news/world',
    'https://www.reuters.com/news/world',
    'https://www.theguardian.com/world',
    'https://www.aljazeera.com/news/',
    'https://www.npr.org/sections/world/',
]
KEYWORDS = ['trump','iran','australia','Amarica','China','Israel']
OUTPUT_FILE = 'fetch_titles.html'
SEEN_FILE = 'seen_titles.txt'  # ✅ ADDED: File to persist seen titles

# ✅ ADDED: Load seen titles from local file
def load_seen_titles(file=SEEN_FILE):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

# ✅ ADDED: Save new titles to local file
def save_seen_titles(titles, file=SEEN_FILE):
    with open(file, 'a', encoding='utf-8') as f:
        for title in titles:
            f.write(title + '\n')

# Fetch new titles that contain the keyword
def fetch_specific_titles(seen_titles):
    matched = []
    new_titles = [] 
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}
    

    for url in URLS:
        try:
            response = requests.get(url,headers=headers,timeout=10)
            print(f"📥 {url} status: {response.status_code}, size: {len(response.text)}")

            # Check response code
            if response.status_code != 200:
                print(f"❌ {url} blocked or redirected, status: {response.status_code}")
                continue

            # Check content size
            if len(response.text) < 500:
                print(f"⚠️ {url} returned unusually short response, likely blocked.")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')


            # Search all heading tags
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])

            print(f"🔎 Checking {len(headings)} headings from {url}")

            for tag in headings:
                text = tag.get_text(strip=True)
                print(f"👉 {text}")  # Print each heading
                if any(keyword.lower() in text.lower() for keyword in KEYWORDS) and text not in seen_titles:
                    link_tag = tag.find('a')
                    if link_tag and link_tag.has_attr('href'):
                        link = urljoin(url, link_tag['href'])
                        matched.append((text, link)) 
                        new_titles.append(text)

        except Exception as e:
            print(f"⚠️ Failed to fetch from {url}: {e}")
            continue  # ✅ FIXED: do NOT return early, just skip failed site
    
    # ✅ Add short delay between each request
    time.sleep(1)
        
    # ✅ Debug line: show how many matches after all sites checked
    print(f"🔍 Checked {len(URLS)} sites, matched {len(matched)} titles.")   
    return matched, new_titles

# Translate English title to Chinese
def translate_to_chinese(text):
    try:
        return GoogleTranslator(source='en', target='zh-CN').translate(text)
    except Exception as e:
        print(f"⚠️ Translation failed: {e}")
        return "[Translation error]"

# Append bilingual news to file
def append_to_file(titles_with_source):
    with open(OUTPUT_FILE, 'a') as f:
        for title,link in titles_with_source:   
            translation = translate_to_chinese(title)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            f.write('<div class="news-block">\n')
            f.write(f'  <div class="timestamp">🕒 {timestamp}</div>\n')
            f.write(f'  <div class="title"><a href="{link}" target="_blank">{title}</a></div>\n')
            f.write(f'  <div class="translation">{translation}</div>\n')
            f.write('</div>\n\n')

# Main loop
if __name__ == '__main__':
    print("🔄 Starting auto-refresh every 60 seconds. Watching for new specific headlines...\n")
    
    seen_titles = load_seen_titles()  # ✅ ADDED: Load previously seen titles

    try:
        while True:
            new_items, new_titles = fetch_specific_titles(seen_titles)  # 🔧 FIXED: Always define both variables
            if new_titles:
                print(f"✅ Found {len(new_titles)} headlines containing keywords: {', '.join(KEYWORDS)}")
                for t, link in new_items:
                    translation = translate_to_chinese(t)
                    print(f"- {t}\n  → {translation}\n   🔗 {link}\n")
                append_to_file(new_items)
                save_seen_titles(new_titles)         # ✅ ADDED: Save to file
                seen_titles.update(new_titles)       # ✅ ADDED: Update in-memory set
            else:
                print("⏳ No new headlines found.")

            time.sleep(60)  # Wait 60 seconds before next check

    except KeyboardInterrupt:
        print("\n👋 Script stopped by user.")
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write("</body>\n</html>\n") 