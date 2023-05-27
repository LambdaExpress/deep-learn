import sys
from tqdm import tqdm
import os
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
    def in_saved_files(self, pid):
        if pid in self.pid_set:
            return True
        self.pid_set.add(pid)
        return False
    def get_page_byuser(self, user_id: str, include_manga=False):
        result = []
        url = f'https://www.pixiv.net/ajax/user/{user_id}/profile/all'
        response = self.get(url)
        response.raise_for_status()
        page_urls = response.json()['body']
        result.extend(list(page_urls['illusts'].keys()))
        
        if include_manga:
            result.extend(list(page_urls['manga'].keys()))
        
        return result
    def get_imgurl_bypage(self, page_url : str, only_p0):
        img_urls = []
        response = self.get(f'https://www.pixiv.net/ajax/illust/{page_url}/pages')
        body = response.json()['body']
        for i, item in enumerate(body):
            if i > 0 and only_p0:
                continue
            url = item['urls']['original']
            img_urls.append(url)
        return img_urls
    def thread_pool_imgurls_bypage(self, page_urls: list, only_p0: bool):
        total_img_urls = []
        total_pages = len(page_urls)
        with tqdm(total=total_pages, desc="Getting img url", leave=False) as pbar, \
                concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.get_imgurl_bypage, page_url, only_p0) for page_url in page_urls]
            for future in concurrent.futures.as_completed(futures):
                img_urls = future.result()
                list_len = len(img_urls)
                if list_len > 1:
                    pbar.total += list_len - 1
                pbar.update(list_len)
                total_img_urls.extend(img_urls)
        return total_img_urls
    def get_page_byrank(self, rank_date, page_num):
        rank_url = f"https://www.pixiv.net/ranking.php?mode=monthly&content=illust&date={rank_date}&p={page_num}&format=json"
        rank_json = self.get(rank_url).json()
        return rank_json
    def get_page_bybookmark(self, user_id : int, offset : int, limit : int, pbar : tqdm):
        url = f'https://www.pixiv.net/ajax/user/{user_id}/illusts/bookmarks?tag=&offset={offset}&limit={limit}&rest=show'
        page_list = []
        bookmark = self.get(url).json()['body']['works']
        alive = True if len(bookmark) > 0 else False
        for item in bookmark:
            if item['url'] == "https://s.pximg.net/common/images/limit_unknown_360.png":
                if pbar is not None:
                    pbar.total -= 1
                    pbar.refresh()
                continue
            page_list.append(item['id'])
        return page_list, alive
    def get_total_pagenum_bybookmark(self, user_id, include_private : bool) -> int:
        total_num = 0
        url = f'https://www.pixiv.net/ajax/user/{user_id}/illusts/bookmark/tags'
        body = self.get(url).json()['body']
        public = body['public']
        for item in public:
            total_num += item['cnt']
        if include_private:
            for item in body['private']:
                total_num += item['cnt']
        return total_num
def main_download_bybookmark():
    root_dir = 'pixiv'
    user_id = '76021323'
    bookmark_name = f'bookmark_{user_id}'
    offset = 0
    limit = 100

    output_dir = os.path.join(root_dir, bookmark_name)
    os.makedirs(output_dir, exist_ok=True)

    spider = PixivSpider([])
    total_num = spider.get_total_pagenum_bybookmark(user_id, False)
    pbar = tqdm(total=total_num, desc='Downloading')
    while True:
        page_list, alive = spider.get_page_bybookmark(user_id, offset, limit, pbar)
        if not alive:
            break
        illust_id_list = spider.thread_pool_imgurls_bypage(page_list, False)
        pbar.total += len(illust_id_list) - len(page_list)
        pbar.refresh()
        spider.thread_pool_download(illust_id_list, output_dir, pbar=pbar)
        offset += limit
def main_download_byuser():
    try:
        root_dir = 'pixiv' 
        user_id = '27517'
        include_manga = False
        output_dir = os.path.join(root_dir, user_id)
        os.makedirs(output_dir, exist_ok=True)

        spider = PixivSpider([])
        page_urls = spider.get_page_byuser(user_id, include_manga)
        img_urls = spider.thread_pool_imgurls_bypage(page_urls, False)
        with tqdm(total=len(img_urls), desc="Downloading") as pbar:
            spider.thread_pool_download(img_urls, output_dir, pbar=pbar)

        # os.system(f'python C:\\Users\\LambdaExpress\\Desktop\\image\\deepbooru_txt.py --path "{os.path.abspath(output_dir)}"')
        # os.system('cls')
    finally:
        os.startfile(output_dir)
def main_download_byrank():
    output_dir = 'input'
    os.makedirs(output_dir, exist_ok=True)

    pid_list = pe.PidExtractor([output_dir, 'dataset']).get_pid_list()
    spider = PixivSpider(pid_list)
    date_generator = dg.DateGenerator([2020, 1, 1], [2020, 12, 31])
    date_generator.shuffle()
    while True:
        try:
            rank_date = date_generator.get_date()
            desc = f"Date: {rank_date}"
            for page_num in tqdm(range(1, 11), desc=desc, leave=False):
                rank_json = spider.get_page_byrank(rank_date, page_num)
                page_list = spider.parse_json(rank_json)
                illust_id_list = spider.thread_pool_imgurls_bypage(page_list, True)
                with tqdm(total=len(illust_id_list), desc='Downloading', leave=False) as pbar:
                    spider.thread_pool_download(illust_id_list, output_dir, pbar=pbar)
        except Exception as e:
            pass
        finally:
            date_generator.next()
if __name__ == '__main__':
    # main_download_byrank()
    main_download_byuser()
    # main_download_bybookmark()
    pass