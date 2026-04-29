import logging
from db.utils import execute_query, execute_query_one, execute_insert, execute_update, execute_delete
from db.utils import execute_query_one_with_conn, execute_insert_with_conn, execute_update_with_conn, execute_delete_with_conn
from db.conf.init import get_db_connection
from service.menu import MenuService

logger = logging.getLogger(__name__)

class CategoryService:
    NEWS_CATEGORY_PARENT_ID = None

    @classmethod
    def _get_news_category_parent_id(cls, conn=None):
        if cls.NEWS_CATEGORY_PARENT_ID is None:
            query = "SELECT id FROM menu WHERE name = '新闻分类' AND parent_id = (SELECT id FROM menu WHERE name = '新闻管理' AND parent_id = 0) LIMIT 1"
            if conn:
                result = execute_query_one_with_conn(conn, query)
            else:
                result = execute_query_one(query)
            if result:
                cls.NEWS_CATEGORY_PARENT_ID = result[0]
        return cls.NEWS_CATEGORY_PARENT_ID

    @classmethod
    def _create_category_menu_with_conn(cls, conn, name, icon, code, sort_order, status):
        parent_id = cls._get_news_category_parent_id(conn)
        if not parent_id:
            logger.warning("未找到新闻分类父菜单，跳过创建子菜单")
            return
        try:
            MenuService.create_menu_with_conn(conn, {
                'name': name,
                'icon': icon,
                'path': f'/news?type={code}',
                'parent_id': parent_id,
                'order': sort_order,
                'status': status
            })
        except Exception as e:
            logger.error(f"创建分类菜单失败: {str(e)}")
            raise

    @classmethod
    def _create_category_menu(cls, name, icon, code, sort_order, status):
        parent_id = cls._get_news_category_parent_id()
        if not parent_id:
            logger.warning("未找到新闻分类父菜单，跳过创建子菜单")
            return
        try:
            MenuService.create_menu({
                'name': name,
                'icon': icon,
                'path': f'/news?type={code}',
                'parent_id': parent_id,
                'order': sort_order,
                'status': status
            })
        except Exception as e:
            logger.error(f"创建分类菜单失败: {str(e)}")

    @classmethod
    def _delete_category_menu_with_conn(cls, conn, code):
        try:
            parent_id = cls._get_news_category_parent_id(conn)
            query = "SELECT id FROM menu WHERE path LIKE %s AND parent_id = %s"
            result = execute_query_one_with_conn(conn, query, (f'/news?type={code}', parent_id))
            if result:
                MenuService.delete_menu_with_conn(conn, result[0])
        except Exception as e:
            logger.error(f"删除分类菜单失败: {str(e)}")
            raise

    @classmethod
    def _delete_category_menu(cls, code):
        try:
            parent_id = cls._get_news_category_parent_id()
            query = "SELECT id FROM menu WHERE path LIKE %s AND parent_id = %s"
            result = execute_query_one(query, (f'/news?type={code}', parent_id))
            if result:
                MenuService.delete_menu(result[0])
        except Exception as e:
            logger.error(f"删除分类菜单失败: {str(e)}")

    @classmethod
    def _update_category_menu_with_conn(cls, conn, old_name, name, icon, code, sort_order, status):
        try:
            parent_id = cls._get_news_category_parent_id(conn)
            query = "SELECT id FROM menu WHERE name = %s AND parent_id = %s"
            result = execute_query_one_with_conn(conn, query, (old_name, parent_id))
            if result:
                MenuService.update_menu_with_conn(conn, result[0], {
                    'name': name,
                    'icon': icon,
                    'path': f'/news?type={code}',
                    'parent_id': parent_id,
                    'order': sort_order,
                    'status': 1 if status == 'active' else 0
                })
        except Exception as e:
            logger.error(f"更新分类菜单失败: {str(e)}")
            raise

    @classmethod
    def _update_category_menu(cls, old_name, name, icon, code, sort_order, status):
        try:
            parent_id = cls._get_news_category_parent_id()
            query = "SELECT id FROM menu WHERE name = %s AND parent_id = %s"
            result = execute_query_one(query, (old_name, parent_id))
            if result:
                MenuService.update_menu(result[0], {
                    'name': name,
                    'icon': icon,
                    'path': f'/news?type={code}',
                    'parent_id': parent_id,
                    'order': sort_order,
                    'status': 1 if status == 'active' else 0
                })
        except Exception as e:
            logger.error(f"更新分类菜单失败: {str(e)}")

    @staticmethod
    def get_categories():
        try:
            query = '''
                SELECT id, name, icon, code, description, sort_order, status, create_time
                FROM news_categories
                ORDER BY sort_order, id
            '''
            categories = execute_query(query)
            category_list = []
            for category in categories:
                category_list.append({
                    'id': category[0],
                    'name': category[1],
                    'icon': category[2],
                    'code': category[3],
                    'description': category[4],
                    'sort_order': category[5],
                    'status': category[6],
                    'create_time': str(category[7])
                })
            return {'success': True, 'categories': category_list}
        except Exception as e:
            logger.error(f"获取分类列表失败: {str(e)}")
            raise Exception(f'获取分类列表失败: {str(e)}')

    @staticmethod
    def get_category_by_id(category_id: int):
        try:
            query = '''
                SELECT id, name, icon, code, description, sort_order, status, create_time
                FROM news_categories
                WHERE id = %s
            '''
            category = execute_query_one(query, (category_id,))
            if category:
                return {
                    'id': category[0],
                    'name': category[1],
                    'icon': category[2],
                    'code': category[3],
                    'description': category[4],
                    'sort_order': category[5],
                    'status': category[6],
                    'create_time': str(category[7])
                }
            return None
        except Exception as e:
            logger.error(f"获取分类失败: {str(e)}")
            raise Exception(f'获取分类失败: {str(e)}')

    @classmethod
    def create_category(cls, category_data):
        conn = get_db_connection()
        try:
            query = '''
                INSERT INTO news_categories (name, icon, code, description, sort_order, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            '''
            params = (
                category_data['name'],
                category_data.get('icon', ''),
                category_data['code'],
                category_data.get('description', ''),
                category_data.get('sort_order', 0),
                category_data.get('status', 'active')
            )
            category_id = execute_insert_with_conn(conn, query, params)

            cls._create_category_menu_with_conn(
                conn,
                category_data['name'],
                category_data.get('icon', ''),
                category_data['code'],
                category_data.get('sort_order', 0),
                1 if category_data.get('status') == 'active' else 0
            )

            conn.commit()
            return {'success': True, 'category_id': category_id, 'message': '分类创建成功'}
        except Exception as e:
            conn.rollback()
            logger.error(f"创建分类失败: {str(e)}")
            raise Exception(f'创建分类失败: {str(e)}')
        finally:
            conn.close()

    @classmethod
    def update_category(cls, category_id: int, category_data):
        conn = get_db_connection()
        try:
            query = "SELECT name FROM news_categories WHERE id = %s"
            old_name_row = execute_query_one_with_conn(conn, query, (category_id,))
            old_name = old_name_row[0] if old_name_row else category_data['name']

            query = '''
                UPDATE news_categories
                SET name = %s, icon = %s, code = %s, description = %s, sort_order = %s, status = %s
                WHERE id = %s
            '''
            params = (
                category_data['name'],
                category_data.get('icon', ''),
                category_data['code'],
                category_data.get('description', ''),
                category_data.get('sort_order', 0),
                category_data.get('status', 'active'),
                category_id
            )
            rowcount = execute_update_with_conn(conn, query, params)

            if rowcount > 0:
                cls._update_category_menu_with_conn(
                    conn,
                    old_name,
                    category_data['name'],
                    category_data.get('icon', ''),
                    category_data['code'],
                    category_data.get('sort_order', 0),
                    category_data.get('status', 'active')
                )
                conn.commit()
                return {'success': True, 'message': '分类更新成功'}
            else:
                raise Exception('分类不存在')
        except Exception as e:
            conn.rollback()
            logger.error(f"更新分类失败: {str(e)}")
            raise Exception(f'更新分类失败: {str(e)}')
        finally:
            conn.close()

    @classmethod
    def delete_category(cls, category_id: int):
        conn = get_db_connection()
        try:
            query = "SELECT code FROM news_categories WHERE id = %s"
            row = execute_query_one_with_conn(conn, query, (category_id,))
            code = row[0] if row else None

            query = 'DELETE FROM news_categories WHERE id = %s'
            params = (category_id,)
            rowcount = execute_delete_with_conn(conn, query, params)

            if rowcount > 0:
                if code:
                    cls._delete_category_menu_with_conn(conn, code)
                conn.commit()
                return {'success': True, 'message': '分类删除成功'}
            else:
                raise Exception('分类不存在')
        except Exception as e:
            conn.rollback()
            logger.error(f"删除分类失败: {str(e)}")
            raise Exception(f'删除分类失败: {str(e)}')
        finally:
            conn.close()
