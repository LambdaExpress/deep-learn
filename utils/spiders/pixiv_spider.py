import sys
import requests
from tqdm import tqdm
import re
import os
import threading
import concurrent.futures
from spider import Spider
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath('..'))
import pid_extractor as pe
import date_generator as dg

class PixivSpider(Spider):
    def __init__(self, pid_list : list):
        super().__init__()
        self.pid_set = set(pid_list)

    def parse_json(self, json):
        illust_id_list = [img['illust_id'] for img in json['contents'] 
                          if not self.in_saved_files(str(img['illust_id']))]
        return illust_id_list
    def __process_artwork(self, artwork : str, img_url_list : list, lock : threading.Lock, pbar : tqdm):
        img_url = self.get(artwork).text
        for url in re.findall(r'original":"(.*?)"', img_url):
            with lock:
                img_url_list.append(url)
        pbar.update(1)
    def thread_pool_get_imgurl(self, illust_id_list):
        img_url_list = []
        lock = threading.Lock()

        total_artworks = len(illust_id_list)
        with tqdm(total=total_artworks, desc="Getting img url", leave=False) as pbar:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for artwork in illust_id_list:
                    future = executor.submit(self.__process_artwork, artwork, img_url_list , lock, pbar)
                    futures.append(future)

                for future in concurrent.futures.as_completed(futures):
                    future.result()
        return img_url_list
    def in_saved_files(self, pid):
        if pid in self.pid_set:
            return True
        self.pid_set.add(pid)
        return False
    def get_page_byuser(self, user_id: str, include_manga=False):
        result = []
        url = f'https://www.pixiv.net/ajax/user/{user_id}/profile/all'
        response = self.get(url)
        page_urls = response.json()['body']
        result.extend(list(page_urls['illusts'].keys()))
        
        if include_manga:
            result.extend(list(page_urls['manga'].keys()))
        
        return result
    def get_imgurl_bypage(self, page_url : list):
        img_urls = []
        response = self.get(f'https://www.pixiv.net/ajax/illust/{page_url}/pages')
        body = response.json()['body']
        for item in body:
            url = item['urls']['original']
            ProcessLookupError
            img_urls.append(url)
        return img_urls
    def thread_pool_imgurls_bypage(self, page_urls):
        total_img_urls = []
        total_pages = len(page_urls)
        with tqdm(total=total_pages, desc="Getting img url", leave=False) as pbar:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for page_url in page_urls:
                    future = executor.submit(self.get_imgurl_bypage, page_url)
                    futures.append(future)

                for future in concurrent.futures.as_completed(futures):
                    img_urls = future.result()
                    list_len = len(img_urls)
                    if list_len > 1:
                        pbar.total += list_len - 1
                    pbar.update(list_len)
                    total_img_urls.extend(img_urls)
        return total_img_urls
def main():
    root_dir = 'pixiv'
    user_id = '59269150'
    include_manga = False
    output_dir = os.path.join(root_dir, user_id)
    os.makedirs(output_dir, exist_ok=True)

    pid_list = pe.PidExtractor([output_dir, 'dataset']).get_pid_list()
    spider = PixivSpider(pid_list)
    date_generator = dg.DateGenerator([2020, 1, 1], [2020, 12, 31])
    date_generator.shuffle()
    page_urls = spider.get_page_byuser(user_id, include_manga)
    img_urls = spider.thread_pool_imgurls_bypage(page_urls)
    pbar = tqdm(total=len(img_urls), desc="Downloading")
    spider.thread_pool_download(img_urls, output_dir, pbar=pbar)
    # while True:
    #     try:
    #         rank_date = date_generator.get_date()
    #         desc = f"Date: {rank_date}"
    #         for page_num in tqdm(range(1, 11), desc=desc, leave=False):
    #             rank_url = f"https://www.pixiv.net/ranking.php?mode=monthly&content=illust&date={rank_date}&p={page_num}&format=json"
    #             work_url_head = r"https://www.pixiv.net/artworks/"
    #             rank_json = spider.get(rank_url).json()
    #             illust_id_list = spider.parse_json(rank_json)
    #             illust_id_list = [work_url_head + str(illust_id) for illust_id in illust_id_list]
    #             artworks = spider.thread_pool_get_imgurl(illust_id_list)
    #             spider.thread_pool_download(artworks, output_dir)
    #     except Exception as e:
    #         pass
    #     finally:
    #         date_generator.next()
if __name__ == '__main__':
    main()