import logging
from db.utils import execute_query, execute_query_one, execute_insert, execute_update, execute_delete
from db.enums import NewsStatus

logger = logging.getLogger(__name__)

class NewsService:
    @staticmethod
    def get_news(type: str = None):
        try:
            if type:
                query = 'SELECT id, title, content, category, source, status, create_time FROM news WHERE status = %s AND category = %s ORDER BY id ASC'
                params = (NewsStatus.PUBLISHED, type)
                news = execute_query(query, params)
                news_list = []
                for item in news:
                    news_list.append({
                        'id': item[0],
                        'title': item[1],
                        'summary': item[2][:200] if item[2] else '',
                        'category': item[3],
                        'source': item[4],
                        'status': NewsStatus.get_name(item[5]),
                        'create_time': str(item[6])
                    })
                
                category_query = 'SELECT code, name, icon, description FROM news_categories WHERE code = %s'
                category = execute_query_one(category_query, (type,))
                
                logger.debug(f"Category query result for type '{type}': {category}")
                
                if category:
                    return {
                        'news': news_list,
                        'category': {
                            'code': category[0],
                            'name': category[1],
                            'icon': category[2],
                            'description': category[3]
                        }
                    }
                return {'news': news_list}
            else:
                query = 'SELECT id, title, content, category, source, status, create_time FROM news WHERE status = %s ORDER BY id ASC'
                params = (NewsStatus.PUBLISHED,)
                news = execute_query(query, params)
                
                categories_query = 'SELECT code, name, icon, description FROM news_categories WHERE status = %s ORDER BY sort_order, id'
                categories = execute_query(categories_query, ('active',))
                
                category_map = {}
                for code, name, icon, description in categories:
                    category_map[code] = {'code': code, 'name': name, 'icon': icon, 'description': description, 'news': []}
                
                for item in news:
                    news_item = {
                        'id': item[0],
                        'title': item[1],
                        'summary': item[2][:200] if item[2] else '',
                        'category': item[3],
                        'source': item[4],
                        'status': NewsStatus.get_name(item[5]),
                        'create_time': str(item[6])
                    }
                    category_code = item[3]
                    if category_code in category_map:
                        category_map[category_code]['news'].append(news_item)
                    else:
                        if 'other' not in category_map:
                            category_map['other'] = {'code': 'other', 'name': '其他', 'news': []}
                        category_map['other']['news'].append(news_item)
                
                return {'categories': list(category_map.values())}
        except Exception as e:
            logger.error(f"获取新闻失败: {str(e)}")
            raise Exception(f'获取新闻失败: {str(e)}')

    @staticmethod
    def collect_news(title_text: str, content: str, category: str = '网页采集', source: str = '系统'):
        try:
            query = '''
                INSERT INTO news (title, content, category, source, status)
                VALUES (%s, %s, %s, %s, %s)
            '''
            params = (title_text, content, category, source, NewsStatus.DRAFT)
            news_id = execute_insert(query, params)

            query = 'SELECT id, title, content, category, source, status, create_time FROM news WHERE id = %s'
            news = execute_query_one(query, (news_id,))

            if news:
                return {
                    'success': True,
                    'data': {
                        'id': news[0],
                        'title': news[1],
                        'content': news[2],
                        'category': news[3],
                        'source': news[4],
                        'status': NewsStatus.get_name(news[5]),
                        'created_at': str(news[6])
                    }
                }
            else:
                raise Exception('新闻保存失败')
        except Exception as e:
            logger.error(f"采集新闻失败: {str(e)}")
            raise Exception(f'采集新闻失败: {str(e)}')

    @staticmethod
    def publish_news(news_id: int):
        try:
            query = 'UPDATE news SET status = %s WHERE id = %s'
            params = (NewsStatus.PUBLISHED, news_id)
            rowcount = execute_update(query, params)

            if rowcount > 0:
                return {'success': True, 'message': '发布成功'}
            else:
                raise Exception('新闻不存在')
        except Exception as e:
            logger.error(f"发布新闻失败: {str(e)}")
            raise Exception(f'发布新闻失败: {str(e)}')

    @staticmethod
    def save_news(title: str, content: str, category: str, source: str = '系统', status: int = NewsStatus.DRAFT):
        try:
            query = '''
                INSERT INTO news (title, content, category, source, status)
                VALUES (%s, %s, %s, %s, %s)
            '''
            params = (title, content, category, source, status)
            news_id = execute_insert(query, params)

            return {'success': True, 'news_id': news_id, 'message': '保存成功'}
        except Exception as e:
            logger.error(f"保存新闻失败: {str(e)}")
            raise Exception(f'保存新闻失败: {str(e)}')

    @staticmethod
    def _query_news(status: int, page: int = 1, page_size: int = 10, category: str = None, keyword: str = None, source: str = None):
        try:
            offset = (page - 1) * page_size
            
            where_conditions = ['n.status = %s']
            params = [status]
            
            if category:
                where_conditions.append('n.category = %s')
                params.append(category)
            
            if keyword:
                where_conditions.append('n.title LIKE %s')
                params.append(f'%{keyword}%')
            
            if source:
                where_conditions.append('n.source = %s')
                params.append(source)
            
            where_clause = ' AND '.join(where_conditions)
            
            query = f'''
                SELECT n.id, n.title, n.content, n.category, n.source, n.status, n.create_time, nc.name AS category_name
                FROM news n
                LEFT JOIN news_categories nc ON n.category = nc.code
                WHERE {where_clause}
                ORDER BY n.id ASC
                LIMIT %s OFFSET %s
            '''
            query_params = params + [page_size, offset]
            news_list = execute_query(query, tuple(query_params))
            
            count_query = f'SELECT COUNT(*) FROM news n WHERE {where_clause}'
            total = execute_query_one(count_query, tuple(params))[0]
            
            result_list = []
            for item in news_list:
                result_list.append({
                    'id': item[0],
                    'title': item[1],
                    'content': item[2],
                    'category': item[7] if item[7] else item[3],
                    'category_code': item[3],
                    'source': item[4],
                    'status': NewsStatus.get_name(item[5]),
                    'create_time': str(item[6])
                })
            
            return {
                'success': True,
                'data': result_list,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        except Exception as e:
            logger.error(f"查询新闻失败: {str(e)}")
            raise Exception(f'查询新闻失败: {str(e)}')

    @staticmethod
    def get_drafts(page: int = 1, page_size: int = 10, category: str = None, keyword: str = None, source: str = None):
        result = NewsService._query_news(
            status=NewsStatus.DRAFT,
            page=page,
            page_size=page_size,
            category=category,
            keyword=keyword,
            source=source
        )
        return {
            'success': result['success'],
            'drafts': result['data'],
            'total': result['total'],
            'page': result['page'],
            'page_size': result['page_size']
        }

    @staticmethod
    def update_draft(news_id: int, title: str, content: str):
        try:
            query = 'UPDATE news SET title = %s, content = %s WHERE id = %s AND status = %s'
            params = (title, content, news_id, NewsStatus.DRAFT)
            execute_update(query, params)
            return {'success': True, 'message': '保存成功'}
        except Exception as e:
            logger.error(f"更新草稿失败: {str(e)}")
            raise Exception(f'更新草稿失败: {str(e)}')

    @staticmethod
    def delete_draft(news_id: int):
        try:
            query = 'DELETE FROM news WHERE id = %s AND status = %s'
            params = (news_id, NewsStatus.DRAFT)
            rowcount = execute_delete(query, params)
            
            if rowcount > 0:
                return {'success': True, 'message': '删除成功'}
            else:
                raise Exception('草稿不存在或已发布')
        except Exception as e:
            logger.error(f"删除草稿失败: {str(e)}")
            raise Exception(f'删除草稿失败: {str(e)}')

    @staticmethod
    def batch_publish_news(news_ids: list):
        try:
            if not news_ids:
                raise Exception('请选择要发布的新闻')
            
            placeholders = ','.join(['%s'] * len(news_ids))
            query = f'UPDATE news SET status = %s WHERE id IN ({placeholders}) AND status = %s'
            params = [NewsStatus.PUBLISHED] + news_ids + [NewsStatus.DRAFT]
            rowcount = execute_update(query, tuple(params))
            
            if rowcount > 0:
                return {'success': True, 'message': f'成功发布{rowcount}条新闻'}
            else:
                raise Exception('没有可发布的草稿')
        except Exception as e:
            logger.error(f"批量发布新闻失败: {str(e)}")
            raise Exception(f'批量发布新闻失败: {str(e)}')

    @staticmethod
    def batch_delete_draft(news_ids: list):
        try:
            if not news_ids:
                raise Exception('请选择要删除的草稿')
            
            placeholders = ','.join(['%s'] * len(news_ids))
            query = f'DELETE FROM news WHERE id IN ({placeholders}) AND status = %s'
            params = news_ids + [NewsStatus.DRAFT]
            rowcount = execute_delete(query, tuple(params))
            
            if rowcount > 0:
                return {'success': True, 'message': f'成功删除{rowcount}条草稿'}
            else:
                raise Exception('没有可删除的草稿')
        except Exception as e:
            logger.error(f"批量删除草稿失败: {str(e)}")
            raise Exception(f'批量删除草稿失败: {str(e)}')

    @staticmethod
    def get_published_news(page: int = 1, page_size: int = 10, category: str = None, keyword: str = None, source: str = None):
        result = NewsService._query_news(
            status=NewsStatus.PUBLISHED,
            page=page,
            page_size=page_size,
            category=category,
            keyword=keyword,
            source=source
        )
        return {
            'success': result['success'],
            'news': result['data'],
            'total': result['total'],
            'page': result['page'],
            'page_size': result['page_size']
        }

    @staticmethod
    def unpublish_news(news_id: int):
        try:
            query = 'UPDATE news SET status = %s WHERE id = %s AND status = %s'
            params = (NewsStatus.DRAFT, news_id, NewsStatus.PUBLISHED)
            rowcount = execute_update(query, params)

            if rowcount > 0:
                return {'success': True, 'message': '撤销发布成功'}
            else:
                raise Exception('新闻不存在或不是已发布状态')
        except Exception as e:
            logger.error(f"撤销发布失败: {str(e)}")
            raise Exception(f'撤销发布失败: {str(e)}')

    @staticmethod
    def batch_unpublish_news(news_ids: list):
        try:
            if not news_ids:
                raise Exception('请选择要撤销发布的新闻')
            
            placeholders = ','.join(['%s'] * len(news_ids))
            query = f'UPDATE news SET status = %s WHERE id IN ({placeholders}) AND status = %s'
            params = [NewsStatus.DRAFT] + news_ids + [NewsStatus.PUBLISHED]
            rowcount = execute_update(query, tuple(params))
            
            if rowcount > 0:
                return {'success': True, 'message': f'成功撤销发布{rowcount}条新闻'}
            else:
                raise Exception('没有可撤销发布的新闻')
        except Exception as e:
            logger.error(f"批量撤销发布失败: {str(e)}")
            raise Exception(f'批量撤销发布失败: {str(e)}')
