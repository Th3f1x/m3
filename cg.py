from tqdm import tqdm
import os
import requests
import ffmpeg

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def dwl_m3u8(m3u8_url, output_file):
    response = requests.get(m3u8_url)
    m3u8_content = response.text

    # Extract url in m3u8
    segments = [line for line in m3u8_content.split('\n') if line and not line.startswith('#')]

    # Create list url
    segment_urls = [f"{m3u8_url.rsplit('/', 1)[0]}/{segment}" for segment in segments]

    # Download segments
    temp_files = []

    bar = tqdm(total=len(segment_urls), desc='Download Progress', unit='segment')
    clear_console()
    
    for i,segment_url in enumerate(segment_urls):
        temp_file = f"temp_segment_{i}.ts"
        temp_files.append(temp_file)
        response = requests.get(segment_url,stream=True)

        with open(temp_file, 'wb') as f :
            for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        bar.update(1)
        clear_console()
    bar.close()

    #ffmpeg for compact file in a mp4 file
    input_args = []
    for temp_file in temp_files:
        input_args.extend(['-i', temp_file])

    (
        ffmpeg
        .input(*input_args, v=1, a=1)
        .output(output_file)
        .run()
    )

    for temp_file in temp_files:
        os.remove(temp_file)

if __name__ == "__main__":

    m3u8_url = input("Put you m3u8 link here: ")
    output_file = "video.mp4"

    dwl_m3u8(m3u8_url, output_file)

