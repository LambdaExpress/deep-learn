import asyncio
import sys
import time
import aiohttp
import requests
from tqdm import tqdm
import os
import concurrent.futures

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Any, Callable


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
                'cookie' : r'first_visit_datetime_pc=2021-07-02+15:40:32; p_ab_id=9; p_ab_id_2=2; p_ab_d_id=546313176; yuid_b=IXMlgmA; privacy_policy_notification=0; a_type=0; b_type=1; login_ever=yes; first_visit_datetime=2022-02-13+01:28:26; PHPSESSID=16981004_N0l7gAuyGHJOW00lsyY2y4SOG2UcW8kY; _ga_692MXKN5XF=GS1.1.1666422380.1.0.1666422523.0.0.0; pt_60er4xix=uid=BhyiTejl873JxXk-Q52ycQ&nid=1&vid=tuxor64LLf/bICkObbgbrw&vn=1&pvn=1&sact=1672499202357&to_flag=0&pl=IZoRf4OCSv6aouL5bhDEAg*pt*1672499078403; c_type=28; privacy_policy_agreement=5; _gcl_au=1.1.493398084.1682066403; _gid=GA1.2.1234678949.1683808570; _ga_ZPL8LPMDK3=GS1.1.1684729391.4.0.1684729395.0.0.0; _ga_MZ1NL4PHH0=GS1.1.1685066424.6.0.1685066439.0.0.0; __utmv=235335808.|2=login ever=yes=1^3=plan=normal=1^5=gender=male=1^6=user_id=16981004=1^9=p_ab_id=9=1^10=p_ab_id_2=2=1^11=lang=zh=1^20=webp_available=yes=1; cf_clearance=OGkXPQswS_1MF9nBV9D_7jOAgCRtYlBNWOUwcYf5OSg-1685093009-0-1-2249d4e1.21170058.75488b01-250; _ga_75BBYNYN9J=deleted; _ga_75BBYNYN9J=deleted; QSI_S_ZN_5hF4My7Ad6VNNAi=v:100:0; __utmz=235335808.1685532204.539.80.utmcsr=web.telegram.org|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=235335808.689511952.1625208038.1685543133.1685591257.542; __utmc=235335808; __utmt=1; __cf_bm=_._.70zobYwUvCJt1PSstmYbFkPWrLNv.Tu0YiDxldA-1685591258-0-ASfEFnrrEcANZtfjUBGSeU3Jb9Uu5D7bmK5Wdp6+w7iAljkne1OjDVrK8TWVYr1qgwNS5pYaZaNJaEZCvsfQBOfqLY6Zc1z6eB0ZH/VFTGXjsALE4tfMVzruAAqPiohaKaWj3b7LMDBZ2Jj+o2IVthpOL3MMqYSTScOcBAtJ9Kk+; tag_view_ranking=Lt-oEicbBr~4QveACRzn3~EQxf_UshiG~aKhT3n4RHZ~RTJMXD26Ak~qkC-JF_MXY~eVxus64GZU~0xsDLqCEW6~HY55MqmzzQ~azESOjmQSV~oJAJo4VO5E~-98s6o2-Rp~jk9IzfjZ6n~EZQqoW9r8g~nIjJS15KLN~6RcLf9BQ-w~BtXd1-LPRH~LJo91uBPz4~YCJduqB2Ci~PwDMGzD6xn~SIpXPnQ53M~7WfWkHyQ76~LX3_ayvQX4~5oPIfUbtd6~CkDjyRo6Vc~48UjH62K37~1G4QS71Nqp~D0nMcn6oGk~_EOd7bsGyl~pzzjRSV6ZO~-TeGk6mN86~QaiOjmwQnI~BN7FnIP06x~VN7cgWyMmg~GACl-vLazK~8e-OBkgs0n~2R7RYffVfj~RcahSSzeRf~9jijgHNOV4~WVrsHleeCL~D9BseuUB5Z~75zhzbk0bS~ahHegnNVxX~SoxapNkN85~oaVGtg6mpV~7ebIzNRkdM~CrFcrMFJzz~pnCQRVigpy~lRHALpj_iJ~3cT9FM3R6t~_SLlqsbxE_~SIBtn3ZiUT~DDa_BA6ZYS~qUh9-BBOW9~ETjPkL0e6r~5yfKLB9Nf0~Ed_W9RQRe_~SqVgDNdq49~PvCsalAgmW~zyKU3Q5L4C~8GYVuLJRQ8~y3RUmuZ1U0~ziiAzr_h04~ePN3h1AXKX~X_1kwTzaXt~RrFTD_HxHi~T2gKxTLD4U~MM6RXH_rlN~7fCik7KLYi~K8esoIs2eW~KOnmT1ndWG~uusOs0ipBx~qtVr8SCFs5~Bd2L9ZBE8q~9eL7npF2g4~UJG1lu-V13~aqjvQ1jk3G~Ie2c51_4Sp~NGpDowiVmM~4fhov5mA8J~ZEVqmDpghJ~2kSJBy_FeR~JL8rvDh62i~LtW-gO6CmS~VTeFUlRxgl~ruMzGK8KSy~7koc5h60k7~F8u6sord4r~hgM4Poq-Hh~q303ip6Ui5~MnGbHeuS94~qnGN-oHRQo~EF1ukwcqiy~6P3KMKP7kU~kZOrpQ0eOB~KN7uxuR89w~gpglyfLkWs~_hSAdpN9rx~U4mRkkC7gD~-KV9iGJAOP; _ga_75BBYNYN9J=GS1.1.1685591257.563.1.1685591439.0.0.0; _ga=GA1.1.689511952.1625208038; __utmb=235335808.11.10.1685591257',
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
    def download_nostream(self, url: str, file_path: str, timeout : int, max_call_limit : int) -> None:
        assert max_call_limit > 0
        while True:
            try:
                content = self.get(url, timeout=timeout).content
                with open(file_path, 'wb') as f:
                    f.write(content)
            except:
                continue
            else:
                break
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
            max_call_limit=5,
            stream=True,
        ) -> None:
        
        os.makedirs(output_dir, exist_ok=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            if stream:
                futures = [executor.submit(self.download, url, os.path.join(output_dir, fn_filename(url)), block_size, timeout, max_call_limit) 
                        for url in urls]
            else:
                futures = [executor.submit(self.download_nostream, url, os.path.join(output_dir, fn_filename(url)), timeout, max_call_limit) 
                        for url in urls]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(e)
                finally:
                    if pbar is not None:
                        pbar.update(1)
    async def download_nostream_async(self, url: str, file_path: str) -> None:
        while True:
            try:
                img_bytes = await self.get_async(url, lambda r : r.read())
                with open(file_path, 'wb') as f:
                    f.write(img_bytes)
            except:
                continue
            else:
                break

    async def download_async(self, url: str, file_path: str, block_size: int, max_call_limit : int) -> None:
        assert max_call_limit > 0
        try:
            timeout = aiohttp.ClientTimeout(connect=3)
            async with aiohttp.ClientSession(headers=self.headers, timeout=timeout) as session:
                async with session.get(url, proxy = self.proxies['http'], ssl= not self.proxies['https'].startswith('http'), proxy_auth=None) as response:
                    total_size = int(response.headers.get('content-length', 0))
                    with tqdm(total=total_size, unit='B', unit_scale=True, leave=False) as progress_bar, \
                        open(file_path, 'wb') as f:
                        progress_bar.set_description(f'Downloading : {os.path.split(file_path)[-1]}')
                        async for chunk in response.content.iter_chunked(block_size):
                            f.write(chunk)
                            progress_bar.update(len(chunk))
        except:
            await self.download_async(url, file_path, block_size, max_call_limit - 1)
    async def download_from_urls_async(            
            self, 
            urls: list, 
            output_dir: str, 
            *, 
            fn_filename : Callable[[str], str] =lambda url: url.split("/")[-1], 
            split_threshold: int = 100, 
            pbar: tqdm = None, 
            block_size: int = 1024, 
            max_call_limit=5,
            stream=False,
        ) -> None:
        os.makedirs(output_dir, exist_ok=True)
        if stream : 
            tasks = [self.download_async(url, os.path.join(output_dir, fn_filename(url)), block_size, max_call_limit) for url in urls]
        else:
            tasks = [self.download_nostream_async(url, os.path.join(output_dir, fn_filename(url))) for url in urls]
        new_list = [tasks[i : i + split_threshold] for i in range(0, len(tasks), split_threshold)]
        with tqdm(tasks, desc='Downloading', leave=False, mininterval=0) as pbar:
            for n in new_list:
                for future in asyncio.as_completed(n):
                    await future
                    pbar.update()
    async def get_async(
            self, 
            url, 
            fn_response : Callable[[aiohttp.ClientResponse], Any] = \
                lambda response : response.text(), 
        ):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url, proxy = self.proxies['http'], ssl= not self.proxies['https'].startswith('http'), proxy_auth=None) as response:
                return await fn_response(response)



async def main():
    spider = Spider()
    json_data = await spider.get_async('https://www.pixiv.net/ajax/illust/104541001/pages?lang=zh&version=3ee829105ad0a7e37194df46adcc36788c4cbdda',
                                       lambda r : r.json())
    urls = [url['urls']['original'] for url in json_data['body']] * 10
    start = time.time()
    await spider.download_from_urls_async(urls, 'ttt', split_threshold=1000)
    print(time.time() - start)

    start = time.time()
    with tqdm(urls, desc='Downloading', leave=False, mininterval=0) as pbar:
        spider.thread_pool_download(urls, '4212342', stream=False, pbar=pbar)
    print(time.time() - start)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())