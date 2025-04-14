import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import re
import subprocess

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=Service(), options=options)
    return driver

def is_valid_m3u8(url):
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

def web_scraper(url_web):
    driver = setup_driver()
    driver.get(url_web)
    time.sleep(5)

    elementos = driver.find_elements(By.TAG_NAME, "a")
    raw_links = [
        a.get_attribute("href") for a in elementos
        if a.get_attribute("href") and "episodio" in a.get_attribute("href").lower()
    ]

    ep_links = sorted(set(raw_links))
    print(f"🔎 Verificando {len(ep_links)} possíveis episódios...")

    ep_count = 0 

    for link_ep in ep_links:
        print(f"\nAcessando: {link_ep}")
        driver.get(link_ep)
        time.sleep(3)

        logs = driver.get_log("performance")
        m3u8_url = None
        for entry in logs:
            msg = entry.get("message", "")
            if ".m3u8" in msg:
                match = re.search(r'https?://[^\s\'"]+\.m3u8', msg)
                if match:
                    m3u8_url = match.group(0)
                    if is_valid_m3u8(m3u8_url):
                        break  
                    else:
                        print("⚠️ Link .m3u8 inválido ou inacessível. Ignorando...")
                        m3u8_url = None

        if m3u8_url:
            ep_count += 1
            print(f"🎯 Link .m3u8 válido encontrado: {m3u8_url}")
            output_path = f"episodio_{ep_count:02d}.mp4"
            download_video_from_m3u8(m3u8_url, output_path)
        else:
            print("🚫 Nenhum link .m3u8 válido encontrado nesse episódio.")

    driver.quit()
    print(f"\n✅ Download finalizado. Total de episódios válidos: {ep_count}")

def download_video_from_m3u8(m3u8_url, output_path):
    try:
        subprocess.run(['ffmpeg', '-i', m3u8_url, '-c', 'copy', output_path], check=True)
        print(f'📥 Vídeo baixado com sucesso: {output_path}')
    except subprocess.CalledProcessError as e:
        print(f'❌ Erro ao baixar o vídeo: {e}')

if __name__ == "__main__":
    url_web = input("Insira a URL do anime do BetterAnime: ")
    web_scraper(url_web)
