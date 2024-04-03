import os
import requests
import subprocess
from tqdm import tqdm

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def dw_m3(url, output_path):
    with requests.get(url, stream=True) as response, open(output_path, 'wb') as out_file:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading', leave=False) as pbar:
            for data in response.iter_content(block_size):
                pbar.update(len(data))
                out_file.write(data)

def conv(m3u8_url, output_file):
    response = requests.get(m3u8_url)
    m3u8_content = response.text

    segments = [line for line in m3u8_content.split('\n') if line and not line.startswith('#')]
    
    segment_urls = [f"{m3u8_url.rsplit('/', 1)[0]}/{segment}" for segment in segments]

    progress_bar = tqdm(total=len(segment_urls), desc='Progresso do Download (☞ﾟヮﾟ)☞', unit='segment')

    temp_files = []

    clear_console()
    for i, segment_url in enumerate(segment_urls):
        temp_file = f"temp_segment_{i}.ts"
        temp_files.append(temp_file)

        dw_m3(segment_url, temp_file)

        progress_bar.update(1)
    progress_bar.close()

    with open(output_file, 'wb') as output:
        for temp_file in temp_files:
            with open(temp_file, 'rb') as temp_input:
                output.write(temp_input.read())

    for temp_file in temp_files:
        os.remove(temp_file)

def dw_mpeg(m3u8_url, output_file):
    try:
        subprocess.run(['ffmpeg', '-i', m3u8_url, '-c', 'copy', output_file], check=True)
        print(f'Vídeo baixado em: {output_file}')
    except subprocess.CalledProcessError as e:
        print(f'Erro, descrição: {e}')
    


if __name__ == "__main__":

    m3u8_url = input(f'Insira m3u8 url: ')
    output_file = input(f'Insira o caminho e o nome do arquivo: ')
    dw_opt = input(f'Utilizar metodo ffmpeg para download?(y/n)')

    if dw_opt == 'y' or 'Y':
        try:
            dw_mpeg(m3u8_url,output_file)
        except subprocess.CalledProcessError:
            print('Este metodo falhou, trocando por um mais estável...')
            conv(m3u8_url,output_file)

    elif dw_opt == 'n' or 'N':
        try:
            conv(m3u8_url, output_file)
        except subprocess.CalledProcessError:
            print('Este metodo falhou, trocando para um mais estável...')
            dw_mpeg(m3u8_url,output_file)

    #try:
    #   clear_console()
    #   dw_mpeg(m3u8_url, output_file)
    #except subprocess.CalledProcessError:
    #   conv(m3u8_url, output_file)



clear_console()
print(f'Seu vídeo foi baixado em: {output_file}')
