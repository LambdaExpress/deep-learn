import requests
from tqdm import tqdm
import re
import os
import pid_extractor as pe
import date_generator as dg
import threading

class Spider(object):
    def __init__(self, session : requests.Session, pid_list : list):
        self.pid_list = set(pid_list)
        self.session = session
        self.proxies = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        }
        self.headers = {
            "accept": "application/json, text/javascript, /; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            'cookie' : r'first_visit_datetime_pc=2021-07-02+15%3A40%3A32; p_ab_id=9; p_ab_id_2=2; p_ab_d_id=546313176; yuid_b=IXMlgmA; privacy_policy_notification=0; a_type=0; b_type=1; login_ever=yes; first_visit_datetime=2022-02-13+01%3A28%3A26; PHPSESSID=16981004_N0l7gAuyGHJOW00lsyY2y4SOG2UcW8kY; _ga_692MXKN5XF=GS1.1.1666422380.1.0.1666422523.0.0.0; pt_60er4xix=uid=BhyiTejl873JxXk-Q52ycQ&nid=1&vid=tuxor64LLf/bICkObbgbrw&vn=1&pvn=1&sact=1672499202357&to_flag=0&pl=IZoRf4OCSv6aouL5bhDEAg*pt*1672499078403; c_type=28; cf_clearance=Nc238qywDPwQ0xAxiVQJqEU9nRib0ruO4xqUqiTMIHk-1680346660-0-1-62b095bb.dc39bd81.35b1ca5b-250; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=male=1^6=user_id=16981004=1^9=p_ab_id=9=1^10=p_ab_id_2=2=1^11=lang=zh=1^20=webp_available=yes=1; _ga_MZ1NL4PHH0=GS1.1.1680504369.5.0.1680504383.0.0.0; privacy_policy_agreement=5; __utmz=235335808.1681217316.395.56.utmcsr=web.telegram.org|utmccn=(referral)|utmcmd=referral|utmcct=/; _gcl_au=1.1.493398084.1682066403; __utmc=235335808; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; _gid=GA1.2.943066473.1682344225; __utmt=1; __utma=235335808.689511952.1625208038.1682395858.1682395858.410; __cf_bm=dHhviq9CIQRRLZj4XvbTplL2A6fJRhAkOfMG_UOPSV4-1682398898-0-AZeomvHJv0hknCyvT1cNsUkXvNekzFNl0WNJJ0gE3azh1jm6bphvtfYTzskfu8fpTIs2THT65yWCIEkVJvoi4OFvYwDS7V9aJ12m3/Yx26lwGNrNPqdNgkrq5wPSLENmpCD3T83BWOac5lcT2SZiPXLrOzRjLIw5MLb9jjHpakVj; _ga=GA1.1.689511952.1625208038; tag_view_ranking=Lt-oEicbBr~aKhT3n4RHZ~eVxus64GZU~7WfWkHyQ76~RTJMXD26Ak~BtXd1-LPRH~75zhzbk0bS~oJAJo4VO5E~0xsDLqCEW6~CkDjyRo6Vc~8GYVuLJRQ8~LJo91uBPz4~-98s6o2-Rp~4QveACRzn3~D0nMcn6oGk~uusOs0ipBx~PwDMGzD6xn~gCB7z_XWkp~L7-FiupSjg~EZQqoW9r8g~Ltq1hgLZe3~Ed_W9RQRe_~UJG1lu-V13~8p2ehmu0sL~nnWu---KFy~lH5YZxnbfC~YCJduqB2Ci~K8esoIs2eW~SqVgDNdq49~kGYw4gQ11Z~HLWLeyYOUF~SoxapNkN85~jhuUT0OJva~9ODMAZ0ebV~azESOjmQSV~HY55MqmzzQ~dUhrZMpRPB~KMpT0re7Sq~JXmGXDx4tL~p27QC63XHD~kqC0Pkkf7Z~zyKU3Q5L4C~8-iylRZUWo~M9JrSEAUyN~_14KFV6H2t~gmUDHkRx4v~psh8GRVyBc~IWEldpNAgD~tlXeaI4KBb~jH0uD88V6F~3SAZKPd9Ah~tgP8r-gOe_~6fP0r2UE2S~KOnmT1ndWG~k3AcsamkCa~Bd2L9ZBE8q~HBlflqJjBZ~qkC-JF_MXY~pTcJWiADGA~vFVsobz-jF~NF9UWEqUcf~9aCtrIRNdF~v3nOtgG77A~xPzNjdEfl2~iszjNkquhZ~Hm8YFGRD7n~lUM3Y7NGaw~BSkdEJ73Ii~Cr3jSW1VoH~HffPWSkEm-~9yQxu4p_gf~nIjJS15KLN~J0YmpUa4nW~I8PKmJXPGb~_hSAdpN9rx~KvAGITxIxH~_Jc3XITZqL~qtVr8SCFs5~GFExx0uFgX~-StjcwdYwv~ay54Q_G6oX~VN7cgWyMmg~Ie2c51_4Sp~ziiAzr_h04~_EOd7bsGyl~CiSfl_AE0h~faHcYIP1U0~QaiOjmwQnI~jk9IzfjZ6n~1LN8nwTqf_~Xs-7j6fVPs~T40wdiG5yy~2EpPrOnc5S~CrFcrMFJzz~pzzjRSV6ZO~nInT2dTMR6~7kHMYSX6tr~yCfY27ds4z~_2R62Coh8C~_DAzWnMkmG; _ga_75BBYNYN9J=GS1.1.1682398886.417.1.1682399051.0.0.0; __utmb=235335808.8.10.1682395858',
            "referer": "https://www.pixiv.net/ranking.php",
            "sec-ch-ua": '"Chromium";v="112", "Microsoft Edge";v="112", "Not:A-Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48",
            "x-requested-with": "XMLHttpRequest"
        }
    def get_web(self, url):
        html = self.session.get(url, headers=self.headers, proxies=self.proxies)
        return html

    def parse_json(self, json):
        illust_id_list = [img['illust_id'] for img in json['contents'] 
                          if not self.in_saved_files(str(img['illust_id']))]
        return illust_id_list
    def get_imgurl(self, illust_id_list):
        img_url_list = []
        for artwork in tqdm(illust_id_list, desc="Getting img url", leave=False):
            img_url = self.get_web(artwork).text
            for o in re.findall(r'original":"(.*?)"', img_url):
                img_url_list.append(o)
        return img_url_list
    def thread_get_imgurl(self, illust_id_list):
        img_url_list = []
        lock = threading.Lock()

        def process_artwork(artwork):
            img_url = self.get_web(artwork).text
            for url in re.findall(r'original":"(.*?)"', img_url):
                with lock:
                    img_url_list.append(url)
            pbar.update(1)

        total_artworks = len(illust_id_list)
        with tqdm(total=total_artworks, desc="Getting img url", leave=False) as pbar:
            threads = []
            for artwork in illust_id_list:
                t = threading.Thread(target=process_artwork, args=(artwork,))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

        return img_url_list
    def in_saved_files(self, pid):
        if pid in self.pid_list:
            return True
        self.pid_list.add(pid)
        return False
    def download(self, url, filename):

        response = requests.get(url, stream=True, proxies=self.proxies, headers=self.headers)

        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size_in_bytes, 
                            unit='iB', 
                            unit_scale=True, 
                            leave=False, 
                            desc=f"Progress file: {os.path.split(filename)[-1]}")

        with open(filename, 'wb') as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            raise Exception("Download incomplete!")

if __name__ == '__main__':
    input_dir = 'input'
    os.makedirs(input_dir, exist_ok=True)

    pid_list = pe.PidExtractor([input_dir, 'dataset']).get_pid_list()
    spider = Spider(requests.Session(), pid_list=pid_list)
    date_generator = dg.DateGenerator([2020, 1, 1], [2020, 12, 31])
    date_generator.shuffle()
    while True:
        try:
            rank_date = date_generator.get_date()
            desc = f"Date: {rank_date}"
            for page_num in tqdm(range(1, 11), desc=desc, leave=False):
                rank_url = f"https://www.pixiv.net/ranking.php?mode=monthly&content=illust&date={rank_date}&p={page_num}&format=json"
                work_url_head = r"https://www.pixiv.net/artworks/"
                rank_json = spider.get_web(rank_url).json()
                illust_id_list = spider.parse_json(rank_json)
                illust_id_list = [work_url_head + str(illust_id) for illust_id in illust_id_list]
                artworks = spider.thread_get_imgurl(illust_id_list)
                threads = []
                for artwork_url in artworks:
                    filename = os.path.join(input_dir, artwork_url.split("/")[-1])
                    thread = threading.Thread(target=spider.download, args=(artwork_url, filename))
                    threads.append(thread)
                    thread.start()
                for thread in threads:
                    thread.join()
        except Exception as e:
            pass
        finally:
            date_generator.next()