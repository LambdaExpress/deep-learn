import sys
import requests
from tqdm import tqdm
import os
import concurrent.futures

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Callable


class Spider(object):
    def __init__(self, headers=None):
        self.session = requests.Session()
        self.proxies = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        }
        if headers != None:
            self.headers = headers
        else:
            self.headers = {
                'cookie' : r'first_visit_datetime_pc=2022-10-23+17:59:29; p_ab_id=6; p_ab_id_2=5; p_ab_d_id=1731174387; yuid_b=JggyFjg; __utmz=235335808.1666515621.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); PHPSESSID=76021323_cvgP187nl5LBUJijLjBb7L8LSS4Tb7Aw; privacy_policy_agreement=5; _ga_MZ1NL4PHH0=GS1.1.1666515625.1.1.1666515637.0.0.0; c_type=20; privacy_policy_notification=0; a_type=0; b_type=1; adr_id=zmV13byg2dIFkS1Qkov3IDGU7OQsO0n2M9DGzCT0aCj2ZWln; pt_60er4xix=uid=4ZMv74xrstxjYPgtekWekw&nid=1&vid=u1bs626RShp29PkbekObyg&vn=1&pvn=1&sact=1671033827102&to_flag=0&pl=IZoRf4OCSv6aouL5bhDEAg*pt*1671033827102; _fbp=fb.1.1672979969946.2091952342; _im_vid=01GRZYG5YQBTCGN5W2YEZM6FE5; login_ever=yes; __utmv=235335808.|2=login ever=yes=1^3=plan=normal=1^5=gender=male=1^6=user_id=76021323=1^9=p_ab_id=6=1^10=p_ab_id_2=5=1^11=lang=zh=1; stacc_mode=unify; __utma=235335808.729001087.1666515621.1679073478.1681033285.10; _im_uid.3929=b.2450e3841ba7dbb7; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; _gcl_au=1.1.578591107.1684040458; tag_view_ranking=liM64qjhwQ~VV3Uu--0IH~uGQeWvelyQ~qqtSkaj9zg~MjipLdRIMT~RTJMXD26Ak~OZbzcrhaSe~Lt-oEicbBr~MI2kUkwUjZ~_hSAdpN9rx~eVxus64GZU~aKhT3n4RHZ~tIxXnxOP_e~VqqXyMy80A~BtXd1-LPRH~0xsDLqCEW6~PwF-JByMnN~h95BJDIOJ9~CkDjyRo6Vc~75zhzbk0bS~kGYw4gQ11Z~zIv0cf5VVk~ujS7cIBGO-~BFjqWz2NRg~xck9-YDGlT~z6i8Mevt17~b_rY80S-DW~KkXUHnIeIl~cmh2pduhtP~G21pet8li6~q3eUobDMJW~ZnTuRjwMxS~4igsAj4V73~CmIov8_f5j~66pgV3BU1a~LJo91uBPz4~LX3_ayvQX4~TV3I2h_Vd8~_vzBwsdzth~pnCQRVigpy~azESOjmQSV~qWFESUmfEs~184M6VPfBv~PwDMGzD6xn~fou0EcjjpJ~ENAXmnb9Rd~pvP44gGKdO~wKJzzRvQS3~kP7msdIeEU~gzY20gtW1F~jH0uD88V6F~qpeZSmEVVP~HLWLeyYOUF~t6fkfIQnjP~wKl4cqK7Gl~0qYEzzmUCZ~GOuKuI1rXg~sYhl4SsLi1~iFcW6hPGPU~K8esoIs2eW~oSou9dlsDv~Y04kSN8Q7d~OHeMHS0-NU~rQTnmliYQM~ykDUPR1jwm~RTV3VbNJzf~cwLG8ks7Vj~-k4xbUv_zd~qHQdncSkNX~w0A5rVRfvZ~MwHZukeY9-~j4YdkYQPMe~ykNnpw2uh5~4ZEPYJhfGu~HY55MqmzzQ~7WfWkHyQ76~D0nMcn6oGk~7fg3D60F6v~Uhg1g_SJrF~6lAZFEHdIG~oJAJo4VO5E~MzyhgX0YIu~JwOnNobdvo~yqhVAkZ_Lh~gVfGX_rH_Y~Bd2L9ZBE8q~MM6RXH_rlN~rLSi6fjJKm~qpHbTQdj1t~g46N4P5qOY~Wi1mGeJ7fz~lH5YZxnbfC~OritT7bldw~CgxrM0PVjB~UxQkMlt9TY~lIKfIoyEqh~id7JJp5-iN~Zlq7Xuh20J~3fccVtAHTt~N9mnt2nQQq; _ga=GA1.1.729001087.1666515621; _ga_75BBYNYN9J=GS1.1.1684575576.39.0.1684575576.0.0.0; __cf_bm=R_.7bp_Jgw2rgwejpyaeHEXGXxZ1JVZ61YWEYphPaP8-1684575569-0-AQ6wVGN6OB1I6IMuZUMxZnkqZe1QrE1VibYm2Mjd9o/c43HgIyQHVAAoJJ+AhC6zhdmj4aHYSpxGW3D7ojEdU05Rk8+lQBe85qzxav7Hy+84o+eL7mir1CtY4vl5ITbkAxMK4soWYfmQWshXcrzUKTcuJfw14QDmRGCZurdBB2YF; cto_bundle=echA1185TXRMY0VQWmx3WnE4TmlJMGVCNXpuMWdJVkRKbVg5emhjZVpwVllseWlkbE1aV2lmUlR5UTdiZTFsbDZQNWZtZnQlMkJQRUNCRFF3MDRLS1hhdE1lU1BVdWRPN1d2dHhVWnFJTVNPZmJ5Q0pHNElDb1NFZUFVNlolMkZlZXd6TUJIa2JhMjYydzdGVTdVaVJzUGdUTEdFVUNRJTNEJTNE',
                "referer": "https://www.pixiv.net/ranking.php",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48",
            }
    def get(self, url : str, timeout = 30) -> requests.Response:
        response = self.session.get(url, headers=self.headers, proxies=self.proxies, timeout=timeout)
        return response
    def post(self, url : str, data : dict, timeout = 30) -> requests.Response:
        response = self.session.post(url, data=data, headers=self.headers, proxies=self.proxies, timeout=timeout)
        return response
    def download(self, url: str, file_path: str, block_size: int, timeout : int, max_call_limit : int) -> None:
        assert max_call_limit > 0, 'Max call limit reached'
        try:
            response = requests.get(url, stream=True, proxies=self.proxies, headers=self.headers, timeout=timeout)
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            with open(file_path, 'wb') as file, \
                tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, leave=False, desc=f"Downloading : {os.path.split(file_path)[-1]}") as progress_bar:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
                if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                    raise requests.HTTPError(f'Download failed due to network error')
        except Exception:
            self.download(url, file_path, block_size, timeout, max_call_limit - 1)

    def thread_pool_download(
            self, 
            urls: list, 
            output_dir: str, 
            *, 
            fn_filename : Callable[[str], str] =lambda url: url.split("/")[-1], 
            max_workers: int = None, 
            pbar: tqdm = None, 
            block_size: int = 1024 * 16, 
            timeout = 15, 
            max_call_limit=5
        ) -> None:
        
        os.makedirs(output_dir, exist_ok=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.download, url, os.path.join(output_dir, fn_filename(url)), block_size, timeout, max_call_limit) 
                       for url in urls]
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(e)
                finally:
                    if pbar is not None:
                        pbar.update(1)