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
KEYWORD = 'the'
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
    headers = {'User-Agent': 'Mozilla/5.0'}

    for url in URLS:
        try:
            response = requests.get(url,headers=headers,timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')


            # Search all heading tags
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])

            for tag in headings:
                text = tag.get_text(strip=True)
                if KEYWORD.lower() in text.lower() and text not in seen_titles:
                    link_tag = tag.find('a')
                    if link_tag and link_tag.has_attr('href'):
                        link = urljoin(url, link_tag['href'])
                        matched.append((text, link)) 
                        new_titles.append(text)

        except Exception as e:
            print(f"⚠️ Failed to fetch from {url}: {e}")
            continue  # ✅ FIXED: do NOT return early, just skip failed site
        
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
                print(f"✅ Found {len(new_titles)} headlines containing '{KEYWORD}':")
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