import socket
import requests.packages.urllib3.util.connection as urllib3_cn
import requests
from bs4 import BeautifulSoup
from urllib import request as u_r
from multiprocessing import Pool
import time
    
def allowed_gai_family():
    """
     https://github.com/shazow/urllib3/blob/master/urllib3/util/connection.py
    """
    return socket.AF_INET

urllib3_cn.allowed_gai_family = allowed_gai_family

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'}

def get_page(l):
    passed = 0
    while passed == 0:
        try:
            page = requests.get(l, headers=headers)
            #print(page)
            if page.status_code == 429:
                print("retrying after ", int(page.headers["Retry-After"]))
                time.sleep(int(page.headers["Retry-After"]))
            else:
                passed = 1
        except:
            passed = 0
            print("trying to download ", l)
            time.sleep(5)
            
    return page