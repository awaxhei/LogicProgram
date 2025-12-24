# 前端美化配置
FRONTEND_CONFIG = {
    # 背景图片配置
    'background_image': {
        'enabled': True,
        'path': '/static/images/MyGo_background.png',  # 默认在线背景图片
        'overlay': {
            'enabled': True,
            'color': 'white',
            'opacity': 0.5  # 60% 不透明度
        }
    },
    
    # 颜色主题配置
    'theme': {
        'primary_color': '#1e88e5',  # 主色调 - 蓝色
        'secondary_color': '#f5f5f5',  # 辅助色 - 浅白色
        'accent_color': '#1976d2',  # 强调色 - 深蓝色
        'text_color': '#333333',  # 文字颜色
        'success_color': '#4caf50',  # 成功颜色
        'error_color': '#f44336'  # 错误颜色
    },
    
    # 动画配置
    'animations': {
        'cell_animation': {
            'enabled': True,
            'duration': '0.3s',
            'effect': 'pulse'
        },
        'message_animation': {
            'enabled': True,
            'duration': '0.5s',
            'effect': 'slideDown'
        }
    },
    
    # 弹出消息配置
    'messages': {
        'position': 'top-right',
        'duration': 3000,  # 显示时间（毫秒）
        'animation': 'fade'
    }
}

# AI提示配置
AI_CONFIG = {
    'enabled': True,  # 是否启用AI提示功能
    'api_url': 'https://api.deepseek.com/v1/chat/completions',  # AI API地址
    'api_key': 'YOUR_API_KEY_HERE',  # 请替换为你的API密钥
    'model': 'deepseek-chat',  # 使用的模型
    'prompt_template': '请为这个数独提供一些解题提示：\n数独阶数：{n}\n当前状态：{current_state}\n请给出简洁的第一人称以建议的口吻的一句话的解题思路和下一步建议。',
    'max_tokens': 200
}