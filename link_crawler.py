import urllib.robotparser
import urllib.parse
from downloader import Downloader
import re

def link_crawler(seed_url,link_regex=None,delay=5,max_depth=-1,max_urls=-1,user_agent='wswp',proxies=None,num_retries=1,scrape_callback=None,cache=None):
    """Crawl from the given seed URL following links matched by linl_regex
    """
    # the queue of URL's that still need to be crawled
    crawl_queue = [seed_url]
    # the URL's that have been seen and at what depth
    seen = {seed_url:0}
    # track how many URL's have been downloaded
    num_urls = 0
    rp = get_robots(seed_url)
    D = Downloader(delay=delay,user_agent=user_agent,proxies=proxies,num_retries=num_retries,cache=cache)

    while crawl_queue:
        url = crawl_queue.pop()
        depth = seen[url]
        # check url passes robots.txt restrictions
        if rp.can_fetch(user_agent,url):
            html = D(url)
            links = []
            if scrape_callback:
                links.extend(scrape_callback(url,html) or [])

            if depth != max_depth:
                #can still craw further
                if link_regex:
                    # filter for links matching our regular expression
                    links.extend(link for link in get_links(html) if re.match(link_regex,link))

            for link in links:
                normalize(seed_url,link)
                # check whether already crawled this link
                if link not in seen:
                    seen[link] = depth + 1
                    # check link is within sane domain
                    if same_domain(seed_url,link):
                        # success! and this new link to queue
                        crawl_queue.append(link)

            # check whether have reached downloaded maximum
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print('Blocked by robots.txt:',url)




def get_robots(url):
    """Initialize robots parser for this dimain
    """
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(urllib.parse.urljoin(url,'robots.txt'))
    rp.read()
    return rp

def get_links(html):
    """Return a list of links from html
    """
    # a regular expression to extract all links from the webpage
    web_regex = re.compile('<a[^>]+href=["\'](.*?)["\']',re.IGNORECASE)
    # list of all links from webpage
    return web_regex.findall(html.decode('utf-8'))

def normalize(seed_url,link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urllib.parse.urldefrag(link) # remove hash to avoid duplicates
    return  urllib.parse.urljoin(seed_url,link)

def same_domain(url1, url2):
    """Return True if both URL's belong to same domain
    """
    return urllib.parse.urlparse(url1).netloc == urllib.parse.urlparse(url2).netloc

if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, user_agent='BadCrawler')
    link_crawler('http://example.webscraping.com', '/(index|(places/default/view))', delay=0, num_retries=1, max_depth=1,user_agent='GoodCrawler')