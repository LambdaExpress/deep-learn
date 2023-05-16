import time
import requests
from spider import Spider
import re
import concurrent.futures
from tqdm import tqdm
import os


class GelbooruSpider(Spider):
    def __init__(self, headers, output_dir):
        self.headers = headers
        self.proxies = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        }
        self.imgids = self.get_allimgid(output_dir)
        super().__init__(headers=headers)

    def get_page(self, page, tags):
        assert tags != '' and tags is not None, 'tags can not be empty'
        page = (page - 1) * 42
        response = self.get(f'https://gelbooru.com/index.php?page=post&s=list&tags={tags}&pid={page}')
        response.raise_for_status()
        data_ids = re.findall('<a id="(.*?)"', response.text)
        return data_ids
    
    def get_img_url(self, id_url):
        text = self.get(id_url).text
        url = re.findall('<li><a href="https://(.*?)"', text)[0]
        url = 'https://' + url
        return url
    def get_img_urlid(self, id_url):
        url = self.get_img_url(id_url)
        return url, id_url.split('=')[-1]
    def thread_pool_urlids(self, id_urls):
        img_idurl_dict = {}
        with tqdm(total=len(id_urls), desc="Getting img idurl", leave=False) as pbar:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for id_url in id_urls:
                    future = executor.submit(self.get_img_urlid, id_url)
                    futures.append(future)
                for future in concurrent.futures.as_completed(futures):
                    pbar.update(1)
                    url, id = future.result()
                    img_idurl_dict[url] = id
        return img_idurl_dict 
    def thread_pool_urls(self, id_urls):
        img_url_list = []
        with tqdm(total=len(id_urls), desc="Getting img url", leave=False) as pbar:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for id_url in id_urls:
                    future = executor.submit(self.get_img_url, id_url)
                    futures.append(future)
                for future in concurrent.futures.as_completed(futures):
                    pbar.update(1)
                    img_url_list.append(future.result())
        return img_url_list
    def get_total_img_num(self, tags=None) -> int:
        response = self.get(f'https://gelbooru.com/index.php?page=post&s=list&tags={tags}&pid=0')
        response.raise_for_status()
        total_img_num = re.findall('pid=(.*?)"', response.text)[-1]
        return int(total_img_num)
    def parse_dataids(self, data_ids : list):
        return [f'https://gelbooru.com/index.php?page=post&s=view&id={data_id[1:]}' for data_id in data_ids]
    def get_allimgid(self, input_dir) -> set:
        img_ids = set()
        for _, _, files in os.walk(input_dir):
            for file in files:
                img_id = file.split('.')[0]
                img_ids.add(img_id)
        return img_ids
    def parse_id_url_dict(self, id_url_dict : dict):
        new_id_url_dict = {}
        for url, data_id in list(id_url_dict.items()):
            if data_id in self.imgids:
                continue
            self.imgids.add(data_id)
            new_id_url_dict[url] = data_id
        return new_id_url_dict
    @staticmethod
    def parse_tags(tags : str):
        return tags.replace(' ', '+').lower() if tags is not None else 'all'
def main() -> None:
    headers = {
        'cookie' : r'PHPSESSID=9fa1e741464257d74b86514ccb827a6a',
        "referer": "https://gelbooru.com/index.php?page=post&s=view&id=8541132",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
    }
    root_dir = 'gelbooru'
    tags = 'irokari'
    tags = GelbooruSpider.parse_tags(tags)
    output_dir = os.path.join(root_dir, tags)
    spider = GelbooruSpider(headers=headers, output_dir=output_dir)
    total_img_num = spider.get_total_img_num(tags=tags)
    pbar = tqdm(total=total_img_num, desc="Total Image Num", leave=False, smoothing=0.7)

    for i in range(1, int(total_img_num / 42) + 2):
        try:
            data_ids = spider.get_page(i, tags=tags)
            data_ids = spider.parse_dataids(data_ids)
            id_url_dict = spider.thread_pool_urlids(data_ids)
            id_url_dict = spider.parse_id_url_dict(id_url_dict)
            spider.thread_pool_download(list(id_url_dict.keys()), 
                                        output_dir, 
                                        fn_filename=lambda url: f'{id_url_dict[url]}.{url.split(".")[-1]}', 
                                        pbar=pbar)
        except Exception as e:
            print(str(e))
            for _ in tqdm(range(30), desc='Waiting', leave=False):
                time.sleep(0.1)
            os.system('cls')
        finally:
            pbar.n = len(os.listdir(output_dir))
            pbar.refresh()

if __name__ == '__main__':
    main()