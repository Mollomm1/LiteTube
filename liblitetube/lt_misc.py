'''
this file contains random stuff
'''

import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'TE': 'Trailers',
}

cookies = {
    'CONSENT': 'YES+cb.20210328-17-p0.en-GB+FX+181',
}

def human_format(num):
    magnitude = 0
    try:
        num = int("".join([ele for ele in num if ele.isdigit()]))
        while abs(int(num)) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '%.2f%s' % (int(num), ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
    except Exception:
        return '?'

def get_canonical_link(channel_url):
    r = requests.get("https://www.youtube.com/"+channel_url, headers=headers, cookies=cookies)
    
    start_index = r.text.find('<link rel="canonical" href="') + len('<link rel="canonical" href="')
    end_index = r.text.find('"', start_index)
    if start_index != -1 and end_index != -1:
        return r.text[start_index:end_index]
    else:
        return None