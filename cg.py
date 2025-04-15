import os
import requests
import re
import subprocess
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service


def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    return webdriver.Chrome(service=Service(), options=options)


def is_valid_m3u8(url):
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200
    except:
        return False

def verificar_episodios_existentes():
    arquivos = [f for f in os.listdir() if re.match(r"episodio_(\d{2})\.mp4", f)]
    numeros = [int(re.search(r"(\d{2})", f).group(1)) for f in arquivos]
    return sorted(numeros)


def perguntar_sobrescrita():
    existentes = verificar_episodios_existentes()
    if existentes:
        print(f"\n⚠️ Foram encontrados {len(existentes)} episódios já baixados.")
        print("Opções:")
        print("  (c) Continuar de onde parou")
        print("  (r) Reinstalar tudo do início (deletar episódios)")
        print("  (s) Sair")

        while True:
            escolha = input("O que deseja fazer? [c/r/s]: ").strip().lower()
            if escolha == 'r':
                for f in [f for f in os.listdir() if re.match(r"episodio_\d{2}\.mp4", f)]:
                    os.remove(f)
                print("🧹 Episódios antigos removidos.\n")
                return 'reinstalar', 0
            elif escolha == 'c':
                return 'continuar', max(existentes)
            elif escolha == 's':
                print("❌ Operação cancelada pelo usuário.")
                exit()
            else:
                print("Opção inválida. Digite 'c', 'r' ou 's'.")
    else:
        return 'novo', 0


def web_scraper(url_web):
    modo, ultimo_ep_baixado = perguntar_sobrescrita()
    driver = setup_driver()
    driver.get(url_web)
    time.sleep(5)

    elementos = driver.find_elements(By.TAG_NAME, "a")
    raw_links = [
        a.get_attribute("href") for a in elementos
        if a.get_attribute("href") and "episodio" in a.get_attribute("href").lower()
    ]

    ep_links = sorted(set(raw_links))
    print(f"\n🔎 Verificando {len(ep_links)} links para episódios...")


    episodios_validos = []
    for link_ep in ep_links:
        print(f"⏳ Verificando link: {link_ep}")
        driver.get(link_ep)
        time.sleep(2)

        logs = driver.get_log("performance")
        m3u8_url = None
        for entry in logs:
            msg = entry.get("message", "")
            if ".m3u8" in msg:
                match = re.search(r'https?://[^\s\'"]+\.m3u8', msg)
                if match:
                    temp_url = match.group(0)
                    if is_valid_m3u8(temp_url):
                        m3u8_url = temp_url
                        break

        if m3u8_url:
            episodios_validos.append((link_ep, m3u8_url))
            print("✅ Link válido encontrado.")
        else:
            print("🚫 Nenhum .m3u8 válido nesse link.")

    total_encontrados = len(episodios_validos)
    print(f"\n🎯 Total de episódios válidos com .m3u8: {total_encontrados}")

    total_baixados = 0
    for numero_ep, (link_ep, m3u8_url) in enumerate(episodios_validos, start=1):
        if numero_ep <= ultimo_ep_baixado:
            continue  

        output_path = f"episodio_{numero_ep:02d}.mp4"
        print(f"\n🎬 Baixando Episódio {numero_ep:02d}: {link_ep}")
        print(f"🔗 Link .m3u8: {m3u8_url}")
        download_video_from_m3u8(m3u8_url, output_path)
        total_baixados += 1

    driver.quit()
    print(f"\n✅ Concluído! Total de novos episódios baixados: {total_baixados}")


def download_video_from_m3u8(m3u8_url, output_path):
    try:
        subprocess.run(['ffmpeg', '-i', m3u8_url, '-c', 'copy', output_path], check=True)
        print(f'📥 Vídeo baixado com sucesso: {output_path}')
    except subprocess.CalledProcessError as e:
        print(f'❌ Erro ao baixar o vídeo: {e}')


if __name__ == "__main__":
    url_web = input("Insira a URL do anime do BetterAnime: ").strip()
    web_scraper(url_web)
