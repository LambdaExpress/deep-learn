import os
from bs4 import BeautifulSoup
from tqdm import tqdm
from spider import Spider
import re
import concurrent.futures
from PIL import Image
class XifolioSpider(Spider):
    def __init__(self, headers=None):
        super().__init__(headers)
    def get_page(self, user_name, page):
        url = f'https://xfolio.jp/zh-CHS/portfolio/{user_name}/works?page={page}'
        result = re.findall('<a href="(.*?)" class="postItem__link" wovn-enable="">', self.get(url).text)
        return result
    def get_imgurl_from_page(self, page_url):
        html = self.get(page_url).text
        soup = BeautifulSoup(html, 'html.parser')
        article_wrap_img = soup.find('div', {'class': 'article__wrap_img'}).find('img')['src']
        return str(article_wrap_img)
    def convert_to_png(self, file_path : str):
        with Image.open(file_path) as file:
            file.save(f'{file_path.split(".")[0]}.png', 'PNG')
        os.remove(file_path)
    def convert_to_png_all(self, file_dir : str):
        files_path = os.listdir(file_dir)
        files_path = [os.path.join(file_dir, file_path) 
                      for file_path in files_path 
                      if os.path.split(file_path)[-1].split('.')[-1] == 'webp']
        for file_path in files_path:
            self.convert_to_png(file_path)
if __name__ == '__main__':

    output_dir = 'xifolio'
    user_name = 'psychelo'
    page_of_nums = 3
    headers = {
        'cookie' : r'WAPID=vShfw6UHFbe2va1oXMsToo1IJ21ZejV1ESn; wap_last_event=showWidgetPage; xfolio_session=9h3fq08a2oi127rou8op89ub5d; _gid=GA1.2.69026018.1686139408; _gat_UA-219308834-1=1; wovn_selected_lang=zh-CHS; _ga=GA1.2.1123408128.1684918553; _ga_PX1Q0L9M31=GS1.1.1686139408.2.1.1686139452.16.0.0',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.37',
        'Referer':'https://xfolio.jp/',
    }
    spider = XifolioSpider(headers=headers)
    with concurrent.futures.ThreadPoolExecutor() as executor, \
    tqdm(total=0, desc='Getting', leave=False) as pbar:
        page_urls_list = []
        futures = [executor.submit(spider.get_page, 'psychelo', i) for i in range(1, page_of_nums + 1)]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            page_urls_list.extend(result)
            pbar.update(len(result))
        img_urls = []
        futures = [executor.submit(spider.get_imgurl_from_page, page) for page in page_urls_list]
        for future in concurrent.futures.as_completed(futures):
            img_urls.append(future.result())
        with tqdm(img_urls, desc='Downloading', leave=False) as pbar:
            spider.thread_pool_download(
                img_urls, 
                output_dir, 
                pbar = pbar, 
                fn_filename= lambda url : url.split('?')[0].split('/')[-1],
                stream=False,
                )
    spider.convert_to_png_all(output_dir)
