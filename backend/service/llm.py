import logging
import os
import requests
from typing import List, Optional

logger = logging.getLogger(__name__)

def load_system_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'system_prompt.md')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        logger.warning(f"加载提示词文件失败: {str(e)}，使用默认提示词")
        return "你是一名专业的新闻编辑，请根据用户需求提供新闻相关服务。"

SYSTEM_PROMPT = load_system_prompt()

class LLMService:
    """
    大语言模型服务
    兼容 OpenAI API 格式
    """
    
    @staticmethod
    def chat(messages: List[dict], api_key: str, base_url: str, model: str = 'gpt-3.5-turbo') -> dict:
        """
        调用大模型聊天接口
        """
        try:
            url = f"{base_url.rstrip('/')}/chat/completions"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            payload = {
                'model': model,
                'messages': [
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    *messages
                ],
                'temperature': 0.7,
                'max_tokens': 2000
            }
            
            logger.info(f"调用大模型: {url}, 模型: {model}")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            logger.info(f"大模型回复成功，内容长度: {len(content)}")
            return {
                'success': True,
                'content': content
            }
            
        except requests.RequestException as e:
            logger.error(f"大模型请求失败: {str(e)}")
            return {
                'success': False,
                'message': f'大模型请求失败: {str(e)}'
            }
        except Exception as e:
            logger.error(f"大模型调用异常: {str(e)}")
            return {
                'success': False,
                'message': f'大模型调用异常: {str(e)}'
            }
