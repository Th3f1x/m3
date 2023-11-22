import requests
import sys
import os
from urllib.parse import urlparse
from progress.bar import Bar

def config():
    argv = sys.argv
    if len(argv) <= 1:
        print('Usage: python3', argv[0], '[your_m3u8_url] [save_dir]')
        return None
    return (argv[1])

def host(url):
    urls = urlparse(url)
    return urls.scheme + '://' + urls.hostname

def m3u8(url):
    print('m3u8 file:', url)
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=10)
    session.mount('http://', adapter)
    session.mount('https://',adapter)
    x = session.get(url, timeout=10)
    return r.text

def list1(host, body):
    lines = body.split('\n')
    f_url_list = []
    for line in lines:
        if not line.startswith('#') and line != '':
                if line.lower().startswith('http'):
                    f_url_list.append(line)
                else:
                     f_url_list.append('%s/%s' % (host, line))

    return f_url_list

def dw_ts(f_url_list,dw_dir):
    t_path = []
    i = 0
    for x_url in reversed(f_url_list):
        i += 1
        fl_name = x_url[x_url.rfind('/'):]
        act_path = '%s%s' % (dw_dir, fl_name)
        t_path.append(act_path)
        if os.path.isfile(act_path):
            print('File Exists')
            continue
        x = requests.get(x_url)
     
        with open(act_path, 'wb') as f:
            f.write(x.content)
    return t_path

def chk_dir(path):
    if os.path.exists(path):
        return
    os.makedirs(path)

def get_dw_l(host,m3_url, url_list=[]):
    body = m3u8(m3_url)
    url_list = list1(host,body)
    for url in url_list:
        if url.lower().endwith('.m3u8'):
            url_list = get_dw_l(host, url, url_list)
        else:
            url_list.append(url)
    return url_list


def dw_ts(m3_url,save):
    check_dir(save)
    host = get_host(m3_url)
    f_url_list
    
def download_ts(m3u8_url, save_dir):
	check_dir(save_dir)
	host = get_host(m3u8_url)
	ts_url_list = get_download_url_list(host, m3u8_url)
	print(ts_url_list)
	print('total file count:', len(ts_url_list))
	ts_path_list = download_ts_file(ts_url_list, save_dir)

def main():
	save_dir = '/Users/huzhenjie/Downloads/m3u8_sample_dir'
	m3u8_url = 'http://hls.cntv.lxdns.com/asp/hls/main/0303000a/3/default/978a64ddd3a1caa85ae70a23414e6540/main.m3u8'
	download_ts(m3u8_url, save_dir)


if __name__ == '__main__':
	# main()
	config = get_cfg()
	if config:
		download_ts(config[0], config[1])


