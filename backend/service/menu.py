import logging
from db.utils import execute_query, execute_query_one, execute_insert, execute_update, execute_delete
from db.utils import execute_query_one_with_conn, execute_insert_with_conn, execute_update_with_conn, execute_delete_with_conn

logger = logging.getLogger(__name__)

class MenuService:
    @staticmethod
    def get_menus():
        try:
            query = '''
                SELECT m1.id, m1.name, m1.icon, m1.path, m1.parent_id, m1.`order`, m1.status, m2.name AS parent_name
                FROM menu m1
                LEFT JOIN menu m2 ON m1.parent_id = m2.id
                ORDER BY m1.parent_id, m1.`order`
            '''
            menus = execute_query(query)
            
            menu_list = []
            for menu in menus:
                menu_list.append({
                    'id': menu[0],
                    'name': menu[1],
                    'icon': menu[2],
                    'path': menu[3],
                    'parent_id': menu[4],
                    'order': menu[5],
                    'status': menu[6],
                    'parent_name': menu[7]
                })
        
            return {'success': True, 'menus': menu_list}
        except Exception as e:
            logger.error(f"获取菜单列表失败: {str(e)}")
            raise Exception(f'获取菜单列表失败: {str(e)}')
    
    @staticmethod
    def get_menu_by_id(menu_id):
        try:
            query = '''
                SELECT id, name, icon, path, parent_id, `order`
                FROM menu
                WHERE id = %s
            '''
            menu = execute_query_one(query, (menu_id,))
            
            if menu:
                return {
                    'id': menu[0],
                    'name': menu[1],
                    'icon': menu[2],
                    'path': menu[3],
                    'parent_id': menu[4],
                    'order': menu[5]
                }
            return None
        except Exception as e:
            logger.error(f"获取菜单失败: {str(e)}")
            raise Exception(f'获取菜单失败: {str(e)}')
    
    @staticmethod
    def create_menu(menu_data):
        try:
            query = '''
                INSERT INTO menu (name, icon, path, parent_id, `order`, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            '''
            params = (
                menu_data['name'],
                menu_data['icon'],
                menu_data['path'],
                menu_data['parent_id'],
                menu_data.get('order', 0),
                menu_data.get('status', 1)
            )
            menu_id = execute_insert(query, params)
        
            return {'success': True, 'menu_id': menu_id, 'message': '菜单创建成功'}
        except Exception as e:
            logger.error(f"创建菜单失败: {str(e)}")
            raise Exception(f'创建菜单失败: {str(e)}')
    
    @staticmethod
    def create_menu_with_conn(conn, menu_data):
        try:
            query = '''
                INSERT INTO menu (name, icon, path, parent_id, `order`, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            '''
            params = (
                menu_data['name'],
                menu_data['icon'],
                menu_data['path'],
                menu_data['parent_id'],
                menu_data.get('order', 0),
                menu_data.get('status', 1)
            )
            menu_id = execute_insert_with_conn(conn, query, params)
        
            return {'success': True, 'menu_id': menu_id, 'message': '菜单创建成功'}
        except Exception as e:
            logger.error(f"创建菜单失败: {str(e)}")
            raise
    
    @staticmethod
    def update_menu(menu_id, menu_data):
        try:
            query = '''
                UPDATE menu
                SET name = %s, icon = %s, path = %s, parent_id = %s, `order` = %s, status = %s
                WHERE id = %s
            '''
            params = (
                menu_data['name'],
                menu_data['icon'],
                menu_data['path'],
                menu_data['parent_id'],
                menu_data.get('order', 0),
                menu_data.get('status', 1),
                menu_id
            )
            execute_update(query, params)
            
            return {'success': True, 'message': '菜单更新成功'}
        except Exception as e:
            logger.error(f"更新菜单失败: {str(e)}")
            raise Exception(f'更新菜单失败: {str(e)}')
    
    @staticmethod
    def update_menu_with_conn(conn, menu_id, menu_data):
        try:
            query = '''
                UPDATE menu
                SET name = %s, icon = %s, path = %s, parent_id = %s, `order` = %s, status = %s
                WHERE id = %s
            '''
            params = (
                menu_data['name'],
                menu_data['icon'],
                menu_data['path'],
                menu_data['parent_id'],
                menu_data.get('order', 0),
                menu_data.get('status', 1),
                menu_id
            )
            execute_update_with_conn(conn, query, params)
            
            return {'success': True, 'message': '菜单更新成功'}
        except Exception as e:
            logger.error(f"更新菜单失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_menu(menu_id):
        try:
            check_query = 'SELECT COUNT(*) FROM menu WHERE parent_id = %s'
            child_count = execute_query_one(check_query, (menu_id,))[0]
            
            if child_count > 0:
                raise Exception('该菜单下有子菜单，无法删除')
            
            query = 'DELETE FROM menu WHERE id = %s'
            params = (menu_id,)
            rowcount = execute_delete(query, params)
            
            if rowcount > 0:
                return {'success': True, 'message': '菜单删除成功'}
            else:
                raise Exception('菜单不存在')
        except Exception as e:
            logger.error(f"删除菜单失败: {str(e)}")
            raise Exception(f'删除菜单失败: {str(e)}')
    
    @staticmethod
    def delete_menu_with_conn(conn, menu_id):
        try:
            check_query = 'SELECT COUNT(*) FROM menu WHERE parent_id = %s'
            child_count = execute_query_one_with_conn(conn, check_query, (menu_id,))[0]
            
            if child_count > 0:
                raise Exception('该菜单下有子菜单，无法删除')
            
            query = 'DELETE FROM menu WHERE id = %s'
            params = (menu_id,)
            rowcount = execute_delete_with_conn(conn, query, params)
            
            if rowcount > 0:
                return {'success': True, 'message': '菜单删除成功'}
            else:
                raise Exception('菜单不存在')
        except Exception as e:
            logger.error(f"删除菜单失败: {str(e)}")
            raise
