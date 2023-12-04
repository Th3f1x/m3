import subprocess

def download_video_from_m3u8(m3u8_url, output_path):
    try:
        # Use ffmpeg to download the video
        subprocess.run(['ffmpeg', '-i', m3u8_url, '-c', 'copy', output_path], check=True)
        print(f'Vídeo baixado com sucesso em: {output_path}')
    except subprocess.CalledProcessError as e:
        print(f'Erro ao baixar o vídeo: {e}')

if __name__ == "__main__":
    m3u8_url = input('Insira a URL do arquivo m3u8: ')
    output_path = input('Insira o caminho de saída do vídeo (ex: video.mp4): ')

    download_video_from_m3u8(m3u8_url, output_path)
