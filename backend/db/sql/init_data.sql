-- 初始化管理员账户
INSERT INTO users (username, password, email, role, status) VALUES ('admin', 'c3284d0f94606de1fd2af172aba15bf3', 'admin@example.com', '管理员', '正常');

-- 初始化菜单数据
-- 一级菜单
INSERT INTO menu (name, icon, path, parent_id, `order`, status) VALUES 
('新闻汇总', 'summary', '/news-summary', 0, 1, 1),
('新闻管理', 'news', NULL, 0, 2, 1),
('用户管理', 'users', NULL, 0, 3, 1),
('系统设置', 'settings', NULL, 0, 4, 1);

-- 二级菜单 - 新闻管理
INSERT INTO menu (name, icon, path, parent_id, `order`, status) VALUES 
('新闻分类', 'category', NULL, 2, 1, 1),
('新闻发布', 'edit', NULL, 2, 2, 1);

-- 二级菜单 - 用户管理
INSERT INTO menu (name, icon, path, parent_id, `order`, status) VALUES 
('用户列表', 'user', '/users', 3, 1, 1);

-- 二级菜单 - 系统设置
INSERT INTO menu (name, icon, path, parent_id, `order`, status) VALUES 
('基本设置', 'pin', '/settings', 4, 1, 1),
('菜单管理', 'menu', '/menu', 4, 2, 1);

-- 三级菜单 - 新闻分类
INSERT INTO menu (name, icon, path, parent_id, `order`, status) VALUES 
('分类管理', 'archive', '/categories', 5, 0, 1),
('国内新闻', 'china', '/news?type=domestic', 5, 1, 1),
('国际新闻', 'world', '/news?type=international', 5, 2, 1),
('新闻API', 'api', '/news?type=api', 5, 3, 1),
('大语言模型', 'llm', '/news?type=llm', 5, 4, 1),
('网页爬取', 'web', '/news?type=web', 5, 5, 1);

-- 三级菜单 - 新闻发布
INSERT INTO menu (name, icon, path, parent_id, `order`, status) VALUES 
('新闻采集', 'spider', '/news-collector', 6, 1, 1),
('撰写新闻', 'write', '/write-news', 6, 2, 1),
('草稿箱', 'folder', '/draft-box', 6, 3, 1),
('已发布', 'published', '/published-news', 6, 4, 1);

-- 初始化新闻分类数据
INSERT INTO news_categories (name, icon, code, description, sort_order, status) VALUES 
('国内新闻', 'china', 'domestic', '国内热点新闻', 1, 'active'),
('国际新闻', 'world', 'international', '国际热点新闻', 2, 'active'),
('新闻API', 'api', 'api', '新闻API采集', 3, 'active'),
('大语言模型', 'llm', 'llm', '大语言模型生成', 4, 'active'),
('网页爬取', 'web', 'web', '网页爬取采集', 5, 'active');

-- 初始化新闻数据
INSERT INTO news (title, content, category, source, status, create_time, dt) VALUES 
('习近平主持召开全面深化改革委员会会议', '会议强调要进一步推进重点领域改革，激发市场活力和社会创造力。', 'domestic', '系统', 1, NOW(), NOW()),
('一季度经济运行总体平稳', 'GDP同比增长5.3%，经济回升向好态势持续巩固。', 'domestic', '系统', 1, NOW(), NOW()),
('科技创新取得新突破', '国产大飞机C919实现商业首航，新能源汽车产量创新高。', 'domestic', '系统', 1, NOW(), NOW()),
('乡村振兴全面推进', '各地春耕生产有序展开，现代农业发展取得新成效。', 'domestic', '系统', 1, NOW(), NOW()),
('文化事业繁荣发展', '文化遗产保护利用工作加强，公共文化服务体系持续完善。', 'domestic', '系统', 1, NOW(), NOW()),
('全球经济复苏面临新挑战', '国际货币基金组织下调全球经济增长预期，呼吁加强宏观政策协调。', 'international', '系统', 1, NOW(), NOW()),
('人工智能技术持续发展', '多国加快AI技术研发和应用，数字经济成为全球竞争新焦点。', 'international', '系统', 1, NOW(), NOW()),
('气候变化应对紧迫性加剧', '联合国报告呼吁各国加大减排力度，推动绿色低碳转型。', 'international', '系统', 1, NOW(), NOW()),
('国际贸易格局深刻调整', '区域全面经济伙伴关系协定(RCEP)深入实施，亚太经贸合作持续深化。', 'international', '系统', 1, NOW(), NOW()),
('科技创新国际合作加强', '全球科研人员联合攻关重大科学问题，国际科技交流日益频繁。', 'international', '系统', 1, NOW(), NOW());

-- 初始化系统配置数据
INSERT INTO system_config (config_key, config_value, description) VALUES 
('app_icon', 'news', '左上角图标名称'),
('app_name', 'AI-新闻系统', '系统名称'),
('login_background', 'login-bg.jpg', '登录页背景图片文件名'),
('llm_api_key', '', 'LLM API Key（兼容OpenAI格式）'),
('llm_base_url', '', 'LLM API Base URL（如：https://api.openai.com/v1）'),
('llm_model', 'gpt-3.5-turbo', 'LLM 模型名称');
