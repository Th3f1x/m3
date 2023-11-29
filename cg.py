import os
import requests
import subprocess 
from ffmpeg import input as ffmpeg_input
from tqdm import tqdm

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def download_and_convert_m3u8_to_mp4(m3u8_url, output_file):
    response = requests.get(m3u8_url)
    m3u8_content = response.text

    
    segments = [line for line in m3u8_content.split('\n') if line and not line.startswith('#')]

    # Create a list of complete URLs for the segments
    segment_urls = [f"{m3u8_url.rsplit('/', 1)[0]}/{segment}" for segment in segments]

    # Create a progress bar
    progress_bar = tqdm(total=len(segment_urls), desc='Download Progress', unit='segment')

    # Download each segment and save it to a temporary file
    temp_files = []
    for i, segment_url in enumerate(segment_urls):
        temp_file = f"temp_segment_{i}.ts"
        temp_files.append(temp_file)
        response = requests.get(segment_url, stream=True)
        with open(temp_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        progress_bar.update(1)
        clear_console()

    progress_bar.close()

    # Concatenate the downloaded segments into a single mp4 file using ffmpeg
    input_files = "|".join(temp_files)
    ffmpeg_cmd = f"ffmpeg -i 'concat:{input_files}' -c copy {output_file}"
    
    try:
        # Use subprocess to run the ffmpeg command
        subprocess.run(ffmpeg_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("ffmpeg stderr:", e.stderr.decode())
    finally:
        # Remove the temporary files
        for temp_file in temp_files:
            os.remove(temp_file)

if __name__ == "__main__":
    m3u8_url = input("Digite a URL do seu arquivo m3u8 aqui: ")
    output_file = "video.mp4"

    download_and_convert_m3u8_to_mp4(m3u8_url, output_file)
