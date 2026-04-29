import logging
from db.utils import execute_query, execute_query_one, execute_update

logger = logging.getLogger(__name__)

class ConfigService:
    @staticmethod
    def get_config(key: str = None):
        try:
            if key:
                query = 'SELECT config_key, config_value, description FROM system_config WHERE config_key = %s'
                config = execute_query_one(query, (key,))
                if config:
                    return {
                        'success': True,
                        'config': {
                            'key': config[0],
                            'value': config[1],
                            'description': config[2]
                        }
                    }
                return {'success': False, 'message': '配置不存在'}
            else:
                query = 'SELECT config_key, config_value, description FROM system_config ORDER BY id'
                configs = execute_query(query)
                config_dict = {}
                for config in configs:
                    config_dict[config[0]] = {
                        'key': config[0],
                        'value': config[1],
                        'description': config[2]
                    }
                return {'success': True, 'configs': config_dict}
        except Exception as e:
            logger.error(f"获取配置失败: {str(e)}")
            raise Exception(f'获取配置失败: {str(e)}')

    @staticmethod
    def update_config(key: str, value: str):
        try:
            query = 'UPDATE system_config SET config_value = %s WHERE config_key = %s'
            params = (value, key)
            rowcount = execute_update(query, params)

            if rowcount > 0:
                return {'success': True, 'message': '配置更新成功'}
            else:
                raise Exception('配置不存在')
        except Exception as e:
            logger.error(f"更新配置失败: {str(e)}")
            raise Exception(f'更新配置失败: {str(e)}')

    @staticmethod
    def batch_update_configs(configs: dict):
        try:
            for key, value in configs.items():
                query = 'UPDATE system_config SET config_value = %s WHERE config_key = %s'
                params = (value, key)
                execute_update(query, params)
            return {'success': True, 'message': '配置更新成功'}
        except Exception as e:
            logger.error(f"批量更新配置失败: {str(e)}")
            raise Exception(f'批量更新配置失败: {str(e)}')
