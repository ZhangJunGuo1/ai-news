import asyncio
import hashlib
import logging
import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db.conf.init import get_db
from service.menu import MenuService
from service.spider import SpiderService
from service.category import CategoryService
from service.news import NewsService
from service.config import ConfigService
from service.user import UserService
from service.llm import LLMService

load_dotenv()

log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO), format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

def md5(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

class CollectNewsRequest(BaseModel):
    source: str
    api_type: str = None
    url: str = None
    category: str = None
    title: str = None
    content: str = None

class LLMChatRequest(BaseModel):
    messages: list[dict]

@app.post('/api/llm-chat')
async def llm_chat(request: LLMChatRequest):
    try:
        config_result = ConfigService.get_config()
        if not config_result.get('success'):
            raise HTTPException(status_code=500, detail={'success': False, 'message': '获取配置失败'})
        
        configs = config_result.get('configs', {})
        api_key = configs.get('llm_api_key', {}).get('value', '')
        base_url = configs.get('llm_base_url', {}).get('value', '')
        model = configs.get('llm_model', {}).get('value', 'gpt-3.5-turbo')
        
        if not api_key or not base_url:
            raise HTTPException(status_code=400, detail={'success': False, 'message': '请先在设置中配置 LLM API Key 和 Base URL'})
        
        result = LLMService.chat(request.messages, api_key, base_url, model)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LLM 聊天失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'LLM 聊天失败: {str(e)}'})

class PublishNewsRequest(BaseModel):
    news_id: int

@app.post('/api/login')
async def login(login_data: LoginRequest):
    username = login_data.username
    password = md5(login_data.password)

    user = UserService.login(username, password)

    if user:
        return {'success': True, 'message': '登录成功'}
    else:
        raise HTTPException(status_code=401, detail={'success': False, 'message': '用户名或密码错误'})

@app.get('/api/users')
async def get_users():
    user_list = UserService.get_users()
    return {'users': user_list}

@app.get('/api/news')
async def get_news(type: str = None):
    try:
        return NewsService.get_news(type)
    except Exception as e:
        logger.error(f"获取新闻失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'error': str(e)})

@app.post('/api/collect-news')
async def collect_news(request: CollectNewsRequest):
    try:
        if request.source == 'api':
            if not request.api_type:
                raise HTTPException(status_code=400, detail={'success': False, 'message': '请选择新闻API'})
            
            api_source_map = {
                '60s': ('60秒新闻', SpiderService.fetch_60s_news),
                'cctv': ('CCTV新闻', SpiderService.fetch_cctv_news),
                'sina': ('新浪新闻', SpiderService.fetch_sina_news),
                'baidu': ('百度热搜', SpiderService.fetch_baidu_hotsearch)
            }
            
            if request.api_type not in api_source_map:
                raise HTTPException(status_code=400, detail={'success': False, 'message': f'不支持的API类型: {request.api_type}'})
            
            api_name, fetch_func = api_source_map[request.api_type]
            articles = fetch_func()
            
            if not articles:
                return {'success': False, 'message': '未获取到新闻'}
            
            count = 0
            for article in articles:
                try:
                    content = article.get('content', article.get('url', ''))
                    NewsService.collect_news(article['title'], content, request.source, api_name)
                    count += 1
                except:
                    pass
            return {'success': True, 'message': f'成功采集{count}条{api_name}'}
        elif request.source == 'llm':
            if not request.content:
                raise HTTPException(status_code=400, detail={'success': False, 'message': 'AI生成新闻需要提供content'})
            
            news_items = SpiderService.parse_llm_news(request.content)
            if not news_items:
                return {'success': False, 'message': '未能解析到有效的新闻内容，请确保内容格式正确'}
            
            count = 0
            for item in news_items:
                try:
                    NewsService.collect_news(item['title'], item['content'], request.source, 'AI助手')
                    count += 1
                except:
                    pass
            return {'success': True, 'message': f'成功采集{count}条AI生成新闻'}
        elif  request.source == 'web':
            if not request.url:
                raise HTTPException(status_code=400, detail={'success': False, 'message': '网页采集需要提供url'})
            result = await SpiderService.crawl_news(request.url)
            return NewsService.collect_news(result['title'], result['content'], request.source, request.url)
        else:
            raise HTTPException(status_code=400, detail={'success': False, 'message': f'不支持的新闻源: {request.source}'})

    except requests.RequestException as e:
        logger.error(f"网页爬取失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'网页爬取失败: {str(e)}'})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"采集新闻失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'采集失败: {str(e)}'})

@app.post('/api/publish-news')
async def publish_news(request: PublishNewsRequest):
    try:
        return NewsService.publish_news(request.news_id)
    except Exception as e:
        if '新闻不存在' in str(e):
            raise HTTPException(status_code=404, detail={'success': False, 'message': str(e)})
        logger.error(f"发布新闻失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'发布失败: {str(e)}'})

class DraftsRequest(BaseModel):
    page: int = 1
    page_size: int = 10

class DeleteDraftRequest(BaseModel):
    news_id: int

class BatchDraftsRequest(BaseModel):
    news_ids: list[int]

class DeleteMenuRequest(BaseModel):
    menu_id: int

class CreateMenuRequest(BaseModel):
    name: str
    icon: str
    path: str
    parent_id: int
    order: int = 0

class UpdateMenuRequest(BaseModel):
    name: str
    icon: str
    path: str
    parent_id: int
    order: int = 0
    status: int = 1

class CreateCategoryRequest(BaseModel):
    name: str
    icon: str = ''
    code: str
    description: str = ''
    sort_order: int = 0
    status: str = 'active'

class UpdateCategoryRequest(BaseModel):
    name: str
    icon: str = ''
    code: str
    description: str = ''
    sort_order: int = 0
    status: str = 'active'

class DeleteCategoryRequest(BaseModel):
    category_id: int

class UpdateConfigRequest(BaseModel):
    key: str
    value: str

class BatchUpdateConfigsRequest(BaseModel):
    configs: dict

@app.get('/api/configs')
async def get_configs():
    try:
        result = ConfigService.get_config()
        return result
    except Exception as e:
        logger.error(f"获取配置列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})

@app.put('/api/configs/{key}')
async def update_config(key: str, request: UpdateConfigRequest):
    try:
        result = ConfigService.update_config(key, request.value)
        return result
    except Exception as e:
        logger.error(f"更新配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})

@app.put('/api/configs')
async def batch_update_configs(request: BatchUpdateConfigsRequest):
    try:
        result = ConfigService.batch_update_configs(request.configs)
        return result
    except Exception as e:
        logger.error(f"批量更新配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})

class SaveNewsRequest(BaseModel):
    title: str
    category: str
    content: str
    source: str = '系统'
    status: int = 0

@app.post('/api/save-news')
async def save_news(request: SaveNewsRequest):
    try:
        return NewsService.save_news(request.title, request.content, request.category, request.source, request.status)
    except Exception as e:
        logger.error(f"保存新闻失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'保存失败: {str(e)}'})

@app.get('/api/drafts')
async def get_drafts(page: int = 1, page_size: int = 10, category: str = None, keyword: str = None, source: str = None):
    try:
        return NewsService.get_drafts(page, page_size, category, keyword, source)
    except Exception as e:
        logger.error(f"获取草稿列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'获取草稿列表失败: {str(e)}'})

class UpdateDraftRequest(BaseModel):
    news_id: int
    title: str
    content: str

@app.post('/api/update-draft')
async def update_draft(request: UpdateDraftRequest):
    try:
        return NewsService.update_draft(request.news_id, request.title, request.content)
    except Exception as e:
        if '草稿不存在' in str(e):
            raise HTTPException(status_code=404, detail={'success': False, 'message': str(e)})
        logger.error(f"更新草稿失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'更新失败: {str(e)}'})

@app.post('/api/delete-draft')
async def delete_draft(request: DeleteDraftRequest):
    try:
        return NewsService.delete_draft(request.news_id)
    except Exception as e:
        if '草稿不存在或已发布' in str(e):
            raise HTTPException(status_code=404, detail={'success': False, 'message': str(e)})
        logger.error(f"删除草稿失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'删除失败: {str(e)}'})

@app.post('/api/batch-publish-drafts')
async def batch_publish_drafts(request: BatchDraftsRequest):
    try:
        return NewsService.batch_publish_news(request.news_ids)
    except Exception as e:
        logger.error(f"批量发布草稿失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'批量发布失败: {str(e)}'})

@app.post('/api/batch-delete-drafts')
async def batch_delete_drafts(request: BatchDraftsRequest):
    try:
        return NewsService.batch_delete_draft(request.news_ids)
    except Exception as e:
        logger.error(f"批量删除草稿失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'批量删除失败: {str(e)}'})

@app.get('/api/published-news')
async def get_published_news(page: int = 1, page_size: int = 10, category: str = None, keyword: str = None, source: str = None):
    try:
        return NewsService.get_published_news(page, page_size, category, keyword, source)
    except Exception as e:
        logger.error(f"获取已发布新闻失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'获取已发布新闻失败: {str(e)}'})

@app.post('/api/unpublish-news')
async def unpublish_news(request: DeleteDraftRequest):
    try:
        return NewsService.unpublish_news(request.news_id)
    except Exception as e:
        logger.error(f"撤销发布失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'撤销发布失败: {str(e)}'})

@app.post('/api/batch-unpublish-news')
async def batch_unpublish_news(request: BatchDraftsRequest):
    try:
        return NewsService.batch_unpublish_news(request.news_ids)
    except Exception as e:
        logger.error(f"批量撤销发布失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': f'批量撤销发布失败: {str(e)}'})

@app.get('/api/menus')
async def get_menus():
    try:
        result = MenuService.get_menus()
        return result
    except Exception as e:
        logger.error(f"获取菜单列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})

@app.get('/api/menus/{menu_id}')
async def get_menu(menu_id: int):
    try:
        menu = MenuService.get_menu_by_id(menu_id)
        if menu:
            return {'success': True, 'menu': menu}
        else:
            raise HTTPException(status_code=404, detail={'success': False, 'message': '菜单不存在'})
    except Exception as e:
        logger.error(f"获取菜单失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})

@app.post('/api/menus')
async def create_menu(request: CreateMenuRequest):
    try:
        result = MenuService.create_menu(request.model_dump())
        return result
    except Exception as e:
        logger.error(f"创建菜单失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})

@app.put('/api/menus/{menu_id}')
async def update_menu(menu_id: int, request: UpdateMenuRequest):
    try:
        result = MenuService.update_menu(menu_id, request.model_dump())
        return result
    except Exception as e:
        if '菜单不存在' in str(e):
            raise HTTPException(status_code=404, detail={'success': False, 'message': str(e)})
        logger.error(f"更新菜单失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})

@app.post('/api/delete-menu')
async def delete_menu(request: DeleteMenuRequest):
    try:
        result = MenuService.delete_menu(request.menu_id)
        return result
    except Exception as e:
        if '该菜单下有子菜单，无法删除' in str(e):
            raise HTTPException(status_code=400, detail={'success': False, 'message': str(e)})
        if '菜单不存在' in str(e):
            raise HTTPException(status_code=404, detail={'success': False, 'message': str(e)})
        logger.error(f"删除菜单失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})

@app.get('/api/categories')
async def get_categories():
    try:
        result = CategoryService.get_categories()
        return result
    except Exception as e:
        logger.error(f"获取分类列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})

@app.get('/api/categories/{category_id}')
async def get_category(category_id: int):
    try:
        category = CategoryService.get_category_by_id(category_id)
        if category:
            return {'success': True, 'category': category}
        else:
            raise HTTPException(status_code=404, detail={'success': False, 'message': '分类不存在'})
    except Exception as e:
        logger.error(f"获取分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})

@app.post('/api/categories')
async def create_category(request: CreateCategoryRequest):
    try:
        result = CategoryService.create_category(request.model_dump())
        return result
    except Exception as e:
        logger.error(f"创建分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})

@app.put('/api/categories/{category_id}')
async def update_category(category_id: int, request: UpdateCategoryRequest):
    try:
        result = CategoryService.update_category(category_id, request.model_dump())
        return result
    except Exception as e:
        if '分类不存在' in str(e):
            raise HTTPException(status_code=404, detail={'success': False, 'message': str(e)})
        logger.error(f"更新分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})

@app.post('/api/delete-category')
async def delete_category(request: DeleteCategoryRequest):
    try:
        result = CategoryService.delete_category(request.category_id)
        return result
    except Exception as e:
        if '分类不存在' in str(e):
            raise HTTPException(status_code=404, detail={'success': False, 'message': str(e)})
        logger.error(f"删除分类失败: {str(e)}")
        raise HTTPException(status_code=500, detail={'success': False, 'message': str(e)})