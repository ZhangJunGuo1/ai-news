-- 添加 LLM 配置项（如果不存在）
INSERT IGNORE INTO system_config (config_key, config_value, description) VALUES 
('llm_api_key', '', 'LLM API Key（兼容OpenAI格式）'),
('llm_base_url', '', 'LLM API Base URL（如：https://api.openai.com/v1）'),
('llm_model', 'gpt-3.5-turbo', 'LLM 模型名称');
