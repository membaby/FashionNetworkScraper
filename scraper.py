import requests
from bs4 import BeautifulSoup
from rich import print
import concurrent.futures
from pipeline import Pipeline
import time

class FashionNetworkScraper:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Fetch-Mode': 'navigate',
        'Host': 'us.fashionnetwork.com',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
        'Connection': 'keep-alive'
    }
    
    def getResults(self, tags, page):
        url = f"https://us.fashionnetwork.com/tags/news/{tags},{page}.html"
        for trial in range(10):
            try:
                response = requests.request("GET", url, headers=self.headers)
                if response.status_code == 200:
                    break
            except Exception as err:
                if trial == 9: return None
                time.sleep(5)

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find('div', class_='container-fluid').find_all('div', class_='home__item-card')
        results = []
        for article in articles:
            if tags not in article.text: continue
            link = article.find('a')['href']
            results.append(link)
        if not articles: return None
        print(f'[+] Found {len(results)} articles for {tags} on page {page}')
        return results

    def getArticle(self, keyword, link):
        for trial in range(10):
            try:
                response = requests.request("GET", link, headers=self.headers)
                if response.status_code == 200:
                    break
                elif response.status_code == 404:
                    return None
            except Exception as err:
                if trial == 9: return None
                time.sleep(5)
        soup = BeautifulSoup(response.text, 'html.parser')
        article = {
            'Article URL': link,
            'Article Image URL': soup.find('img', class_='news-image')['src'] if soup.find('img', class_='news-image') else soup.find('center').find('img')['src'] if soup.find('center') and soup.find('center').find('img') else None,
            'Article Title': soup.find('h1', class_='newsTitle').text if soup.find('h1', class_='newsTitle') else None,
            'Keyword': keyword,
            'Article Details': str(soup.find('p', class_='article-content--texte')) if soup.find('p', class_='article-content--texte') else None,
            'Date of Article': soup.find('div', class_='newsPublishedAt').find('span').text.replace('today', '').strip() if soup.find('div', class_='newsPublishedAt') else None,
            'author': soup.find('a', itemprop="name")['title'] if soup.find('a', itemprop="name") else None,
            'reading_time': soup.find('div', class_='newsReadingTime').find('span').text.replace('access_time', '').strip() if soup.find('div', class_='newsReadingTime') else None,
            'sub_title': soup.find('p', class_='article-content').text.strip() if soup.find('p', class_='article-content') else None,
            'section': soup.find_all('a', class_='fg-breadcrumb__link')[-1].text.strip()
        }
        if not article['Article Title']:
            return self.getArticle(keyword, link)
        if article['Article Details'] == None or article['Article Details'] == '':
            article_content = soup.find('div', class_='newsContent')
            if article_content:
                article['Article Details'] = article_content.text.strip()
        return article

if __name__ == '__main__':
    scraper = FashionNetworkScraper()
    pipeline = Pipeline()
    keywords = [x.strip() for x in open('keywords.txt', 'r').readlines()]

    for keyword in keywords:
        page = 1
        article_links = []
        while True:
            results = scraper.getResults(keyword, page)
            if results is None: break
            page += 1
            if results:
                for result in results:
                    if not pipeline.article_exists(result):
                        article_links.append(result)
            else:
                break

        print(f'[{keyword}] Found {len(article_links)} new articles for {keyword}')
        
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=32)
        futures = []
        for link in article_links:
            futures.append(executor.submit(scraper.getArticle, keyword, link))
        
        for future in concurrent.futures.as_completed(futures):
            article = future.result()
            if article:
                pipeline.insert_article(article)
        executor.shutdown(wait=True)