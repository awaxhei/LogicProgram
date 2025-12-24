#!/usr/bin/env python3
"""
DeepSeek API测试程序
用于测试API连接和功能
"""

import requests
import json
import sys

def test_deepseek_api(api_key, api_url):
    """
    测试DeepSeek API连接
    
    Args:
        api_key (str): API密钥
        api_url (str): API端点URL
        
    Returns:
        dict: 测试结果
    """
    print("=" * 50)
    print("DeepSeek API 测试程序")
    print("=" * 50)
    
    # 检查API密钥
    if not api_key:
        return {
            'success': False,
            'error': 'API密钥为空，请检查配置'
        }
    
    # 构建请求头
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 构建测试请求数据
    test_payload = {
        'model': 'deepseek-chat',
        'messages': [
            {
                'role': 'user',
                'content': '请回复"测试成功"，这是一个API连接测试。'
            }
        ],
        'max_tokens': 50,
        'temperature': 0.7
    }
    
    try:
        print(f"测试API端点: {api_url}")
        print(f"使用模型: {test_payload['model']}")
        print("正在发送测试请求...")
        
        # 发送请求
        response = requests.post(
            api_url,
            headers=headers,
            json=test_payload,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 请求成功
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                message_content = result['choices'][0]['message']['content']
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'response': message_content,
                    'full_response': result
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': '响应格式异常',
                    'response_text': response.text
                }
        else:
            # 请求失败
            return {
                'success': False,
                'status_code': response.status_code,
                'error': f'API调用失败: {response.status_code}',
                'response_text': response.text
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': '请求超时，请检查网络连接'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': '连接错误，请检查API URL和网络连接'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'发生未知错误: {str(e)}'
        }

def main():
    """主函数"""
    # 从config.py导入配置
    try:
        from config import AI_CONFIG
        api_key = AI_CONFIG['api_key']
        api_url = AI_CONFIG['api_url']
    except ImportError:
        print("错误: 无法导入config.py")
        return
    except KeyError as e:
        print(f"错误: 配置文件中缺少必要的键: {e}")
        return
    
    # 运行测试
    result = test_deepseek_api(api_key, api_url)
    
    print("\n" + "=" * 50)
    print("测试结果")
    print("=" * 50)
    
    if result['success']:
        print("API测试成功!")
        print(f"响应内容: {result['response']}")
        print(f"状态码: {result['status_code']}")
    else:
        print("API测试失败!")
        print(f"错误信息: {result['error']}")
        if 'status_code' in result:
            print(f"状态码: {result['status_code']}")
        if 'response_text' in result:
            print(f"响应内容: {result['response_text'][:200]}...")  # 只显示前200字符
    
    print("\n调试信息:")
    print(f"API URL: {api_url}")
    print(f"API密钥: {'*' * 10 if api_key else '未设置'}")
    
    # 提供建议
    if not result['success']:
        print("\n建议:")
        if result.get('status_code') == 404:
            print("1. 检查API URL是否正确")
            print("2. 确保API端点存在")
        elif result.get('status_code') == 401:
            print("1. 检查API密钥是否正确")
            print("2. 确保API密钥未过期")
        elif result.get('status_code') == 403:
            print("1. 检查API密钥权限")
            print("2. 确保账户有足够的额度")
        else:
            print("1. 检查网络连接")
            print("2. 验证API配置")

if __name__ == "__main__":
    main()
