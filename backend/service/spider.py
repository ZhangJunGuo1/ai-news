import logging
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, List

logger = logging.getLogger(__name__)

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class SpiderService:
    """
    网页爬虫服务
    支持爬取主流新闻网站的文章内容
    推荐测试网站：https://www.chinanews.com.cn/ (中国新闻网)
    """
    
    # 主流新闻网站列表（支持静态HTML渲染）
    SUPPORTED_NEWS_SITES = {
        'chinanews': {
            'name': '中国新闻网',
            'url': 'https://www.chinanews.com.cn/',
            'description': '中国知名新闻门户，提供国内外热点新闻'
        },
        'people': {
            'name': '人民网',
            'url': 'http://www.people.com.cn/',
            'description': '人民日报社主办的新闻网站'
        },
        'xinhua': {
            'name': '新华网',
            'url': 'http://www.news.cn/',
            'description': '新华社主办的权威新闻门户'
        }
    }
    
    @staticmethod
    def fetch_page(url: str) -> requests.Response:
        """
        获取网页内容
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        logger.debug(f"开始爬取网页: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        
        logger.debug(f"网页响应状态码: {response.status_code}, 内容长度: {len(response.content)} 字节")
        return response
    
    @staticmethod
    async def fetch_page_with_playwright(url: str) -> str:
        """
        使用Playwright获取渲染后的HTML（支持JavaScript动态加载）
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception('Playwright未安装，请运行: pip install playwright && playwright install chromium')
        
        logger.debug(f"使用Playwright渲染页面: {url}")
        
        p = await async_playwright().start()
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        
        html = await page.content()
        await browser.close()
        
        logger.debug(f"Playwright渲染完成，内容长度: {len(html)} 字节")
        return html
    
    @staticmethod
    def parse_html(html_content: bytes, encoding: str = 'utf-8') -> BeautifulSoup:
        """
        解析HTML内容
        """
        soup = BeautifulSoup(html_content, 'lxml')
        return soup
    
    @staticmethod
    def extract_title(soup: BeautifulSoup) -> str:
        """
        提取网页标题
        """
        title = None
        for selector in ['h1.article-title', 'h1.news-title', 'h1.title', 'article h1', '.article-header h1', '.news-header h1', 'h1']:
            title = soup.select_one(selector)
            if title:
                break
        
        if not title:
            title = soup.find('h1') or soup.find('h2') or soup.find('title')
        
        title_text = title.get_text(strip=True) if title else '未知标题'
        logger.debug(f"提取到标题: {title_text}")
        return title_text
    
    @staticmethod
    def extract_content(soup: BeautifulSoup) -> str:
        """
        提取网页正文内容，使用多种策略
        """
        content = ''
        
        # 策略1: 查找文章主体区域
        content_selectors = [
            {'tag': ['article', 'div'], 'class': ['article-content', 'article-body', 'news-content', 'content', 'post-content', 'entry-content', 'article_content', 'detail-content', 'text', 'main-content']},
            {'tag': ['div'], 'class': ['TRS_Editor', 'article', 'news_article', 'main-article']},
            {'tag': ['div'], 'id': ['content', 'main', 'articleContent', 'newsContent']}
        ]
        
        for selector in content_selectors:
            content_tags = soup.find_all(selector['tag'], class_=selector.get('class'), id=selector.get('id'))
            if content_tags:
                logger.debug(f"策略1: 找到 {len(content_tags)} 个内容区域")
                for tag in content_tags:
                    for p in tag.find_all('p'):
                        text = p.get_text(strip=True)
                        if len(text) > 20 and not any(kw in text.lower() for kw in ['copyright', '版权所有', '未经授权', '免责声明', '广告', '声明', '来源：', '责任编辑', '编辑：', '作者：']):
                            content += text + '\n\n'
                if content and len(content) >= 100:
                    break
        
        # 策略2: 如果策略1失败，尝试查找所有段落
        if not content or len(content) < 100:
            logger.debug("策略1失败，尝试策略2")
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 30 and not any(kw in text.lower() for kw in ['copyright', '版权所有', '未经授权', '免责声明', '广告', '声明', '来源：', '责任编辑', '编辑：', '作者：', '扫描', '二维码', '客户端', '搜索']):
                    content += text + '\n\n'
        
        # 策略3: 如果策略2也失败，尝试提取main或content区域的长文本
        if not content or len(content) < 100:
            logger.debug("策略2失败，尝试策略3")
            main_content = soup.find('main') or soup.find(id='content') or soup.find(id='main')
            if main_content:
                text_content = main_content.get_text(separator='\n', strip=True)
                lines = [line for line in text_content.split('\n') if len(line) > 50]
                content = '\n\n'.join(lines)
        
        # 清理内容
        while '\n\n\n' in content:
            content = content.replace('\n\n\n', '\n\n')
        content = content.strip()
        
        logger.debug(f"最终提取内容长度: {len(content)} 字符")
        return content
    
    @staticmethod
    def clean_soup(soup: BeautifulSoup) -> BeautifulSoup:
        """
        清理HTML，移除不需要的标签
        """
        # 移除不需要的标签
        for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript', 'form']):
            tag.decompose()

        # 移除广告、导航等无关内容
        remove_classes = ['ad', 'ads', 'advert', 'nav', 'menu', 'sidebar', 'footer', 'header', 'toolbar', 'share', 'social', 'comment', 'related', 'recommend', 'qrcode', 'code', 'copyright', 'source', 'author', 'time', 'tag']
        for cls in remove_classes:
            for tag in soup.find_all(class_=lambda x: x and cls in x.lower()):
                tag.decompose()
        
        return soup
    
    @staticmethod
    async def crawl_news(url: str) -> dict:
        """
        爬取新闻文章
        返回: {'title': str, 'content': str}
        """
        try:
            html_content = None
            use_playwright = False
            
            # 先尝试静态获取
            try:
                response = SpiderService.fetch_page(url)
                html_content = response.content
            except Exception as e:
                logger.warning(f"静态获取失败: {str(e)}")
            
            # 解析HTML
            soup = SpiderService.parse_html(html_content)
            
            # 输出调试信息
            page_title = soup.find('title')
            logger.debug(f"页面title: {page_title.get_text(strip=True) if page_title else '无'}")
            
            headings = soup.find_all(['h1', 'h2', 'h3'])
            logger.debug(f"页面包含 {len(headings)} 个标题标签")
            for h in headings[:5]:
                logger.debug(f"  - {h.name}: {h.get_text(strip=True)[:100]}")
            
            p_tags = soup.find_all('p')
            logger.debug(f"页面包含 {len(p_tags)} 个段落标签")
            
            # 清理HTML
            soup = SpiderService.clean_soup(soup)
            
            # 提取标题和内容
            title = SpiderService.extract_title(soup)
            content = SpiderService.extract_content(soup)
            
            # 如果静态提取失败，尝试Playwright动态渲染
            if (not content or len(content) < 100) and PLAYWRIGHT_AVAILABLE:
                logger.debug(f"静态内容提取失败，尝试使用Playwright动态渲染...")
                try:
                    html_content = await SpiderService.fetch_page_with_playwright(url)
                    soup = SpiderService.parse_html(html_content.encode('utf-8'))
                    
                    page_title = soup.find('title')
                    logger.debug(f"[Playwright] 页面title: {page_title.get_text(strip=True) if page_title else '无'}")
                    
                    headings = soup.find_all(['h1', 'h2', 'h3'])
                    logger.debug(f"[Playwright] 页面包含 {len(headings)} 个标题标签")
                    
                    p_tags = soup.find_all('p')
                    logger.debug(f"[Playwright] 页面包含 {len(p_tags)} 个段落标签")
                    
                    soup = SpiderService.clean_soup(soup)
                    title = SpiderService.extract_title(soup)
                    content = SpiderService.extract_content(soup)
                    use_playwright = True
                except Exception as e:
                    logger.error(f"Playwright渲染失败: {str(e)}")
            
            if not content or len(content) < 100:
                error_msg = '无法提取有效的新闻内容。可能原因：1) 该页面使用JavaScript动态加载内容；2) 该页面是新闻聚合页而非单篇文章；3) 网站有反爬虫保护。建议：尝试具体的新闻文章URL（如 xxx.com/article/123.html），而非新闻首页。'
                logger.warning(f"内容提取失败，标题: {title}, 内容长度: {len(content)}")
                raise Exception(error_msg)
            
            return {
                'title': title,
                'content': content
            }
            
        except requests.RequestException as e:
            logger.error(f"网页爬取失败: {str(e)}")
            raise Exception(f'网页爬取失败: {str(e)}')
        except Exception as e:
            logger.error(f"采集新闻失败: {str(e)}")
            raise Exception(f'采集失败: {str(e)}')

    @staticmethod
    def fetch_60s_news() -> List[dict]:
        """
        通过60s API获取每日新闻速览（免费，无需注册）
        返回: [{'title': str, 'content': str}, ...]
        """
        try:
            url = "https://60s.viki.moe/v2/60s"
            
            logger.info(f"获取60秒新闻: {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') != 200:
                logger.warning(f"60秒新闻API返回异常: {data}")
                return []
            
            news_data = data.get('data', {})
            news_list_raw = news_data.get('news', [])
            
            news_list = []
            for i, news_item in enumerate(news_list_raw, 1):
                news_list.append({
                    'title': f"今日新闻 {i}",
                    'content': news_item
                })
            
            logger.info(f"获取到 {len(news_list)} 条60秒新闻")
            return news_list
            
        except Exception as e:
            logger.error(f"获取60秒新闻失败: {str(e)}")
            return []

    @staticmethod
    def fetch_baidu_hotsearch() -> List[dict]:
        """
        通过百度热搜官方公开接口获取实时热搜榜单（免费，无需注册）
        返回: [{'title': str, 'content': str, 'url': str}, ...]
        """
        try:
            url = "https://top.baidu.com/api/board?platform=wise&tab=realtime"
            
            logger.info(f"获取百度热搜: {url}")
            response = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            data = response.json()
            
            if not data.get('success'):
                logger.warning(f"百度热搜API返回异常: {data}")
                return []
            
            cards = data.get('data', {}).get('cards', [])
            news_list = []
            if cards:
                items = cards[0].get('content', [])[0].get('content', [])
                for item in items:
                    news_list.append({
                        'title': item.get('word', ''),
                        'content': item.get('url', '') or f"https://www.baidu.com/s?wd={item.get('word', '')}",
                    })
            
            logger.info(f"获取到 {len(news_list)} 条百度热搜")
            return news_list
            
        except Exception as e:
            logger.error(f"获取百度热搜失败: {str(e)}")
            return []

    @staticmethod
    def fetch_cctv_news() -> List[dict]:
        """
        通过CCTV官方RSS获取最新国内新闻（免费）
        返回: [{'title': str, 'content': str, 'url': str, 'published': str}, ...]
        """
        try:
            rss_url = "http://www.cctv.com/program/rss/02/01/index.xml"
            
            logger.info(f"获取CCTV新闻RSS: {rss_url}")
            response = requests.get(rss_url, timeout=15)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                logger.warning("CCTV RSS未返回任何条目")
                return []
            
            news_list = []
            for entry in feed.entries:
                published = entry.get('published', '') or entry.get('updated', '')
                if published:
                    try:
                        published_dt = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z')
                        published = published_dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                summary = entry.get('summary', '') or entry.get('description', '')
                
                news_list.append({
                    'title': entry.get('title', ''),
                    'content': summary,
                    'url': entry.get('link', ''),
                    'published': published
                })
            
            logger.info(f"获取到 {len(news_list)} 条CCTV新闻")
            return news_list
            
        except Exception as e:
            logger.error(f"获取CCTV新闻失败: {str(e)}")
            return []

    @staticmethod
    def fetch_sina_news() -> List[dict]:
        """
        通过新浪新闻API获取国内新闻（免费，无需注册）
        返回: [{'title': str, 'content': str, 'url': str, 'published': str}, ...]
        """
        try:
            url = "https://feed.mix.sina.com.cn/api/roll/get"
            params = {
                "pageid": "153",
                "lid": "2509",
                "num": "50",
                "page": "1",
                "r": "0.5"
            }
            
            logger.info(f"获取新浪新闻: {url}")
            response = requests.get(url, params=params, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            data = response.json()
            
            result = data.get('result', {})
            status = result.get('status', {})
            if str(status.get('code')) != '0':
                logger.warning(f"新浪新闻API返回异常: {data}")
                return []
            
            news_list = []
            items = result.get('data', [])
            for item in items:
                ctime = item.get('ctime', '')
                if ctime:
                    try:
                        ctime = datetime.fromtimestamp(int(ctime)).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                news_list.append({
                    'title': item.get('title', ''),
                    'content': item.get('intro', '') or item.get('summary', ''),
                    'url': item.get('url', ''),
                    'published': ctime
                })
            
            logger.info(f"获取到 {len(news_list)} 条新浪新闻")
            return news_list
            
        except Exception as e:
            logger.error(f"获取新浪新闻失败: {str(e)}")
            return []

    @staticmethod
    def parse_llm_news(content: str) -> List[dict]:
        """
        解析大模型生成的新闻内容
        格式：
        1. 分类标题：新闻主题
         - 要点1
         - 要点2
         - 要点3
        
        2. 分类标题：新闻主题
         - 要点1
         - 要点2
         - 要点3
        """
        import re
        
        news_list = []
        
        pattern = r'(\d+)\.\s*([^\n：]+)：([^\n]+)\n((?:\s*-\s*[^\n]+\n?)+)'
        matches = re.findall(pattern, content)
        
        for match in matches:
            num, category, topic, points_text = match
            
            points = []
            for line in points_text.strip().split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    points.append(line[1:].strip())
            
            title = f"{category}：{topic.strip()}"
            content_text = '\n'.join([f"• {point}" for point in points])
            
            news_list.append({
                'title': title,
                'content': content_text,
                'category': category.strip()
            })
        
        logger.info(f"解析LLM新闻，共 {len(news_list)} 条")
        return news_list

    @staticmethod
    async def fetch_news_from_api(source: str, **kwargs) -> List[dict]:
        """
        统一新闻采集入口
        支持的source: '60s', 'cctv', 'sina', 'baidu', 'web'
        """
        if source == '60s':
            return SpiderService.fetch_60s_news()
        elif source == 'cctv':
            return SpiderService.fetch_cctv_news()
        elif source == 'sina':
            return SpiderService.fetch_sina_news()
        elif source == 'baidu':
            return SpiderService.fetch_baidu_hotsearch()
        elif source == 'web':
            url = kwargs.get('url')
            if not url:
                raise Exception('网页采集需要提供url参数')
            result = await SpiderService.crawl_news(url)
            return [result]
        else:
            raise Exception(f'不支持的新闻源: {source}')
