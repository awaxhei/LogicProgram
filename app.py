from flask import Flask, render_template, request
import subprocess
import os
import config
import json
import threading
import time
from collections import deque
from queue import Queue

app = Flask(__name__)

# 创建配置字典
config_dict = {
    'FRONTEND_CONFIG': config.FRONTEND_CONFIG,
    'AI_CONFIG': config.AI_CONFIG
}

# 缓存配置
SUPPORTED_SIZES = [4, 9, 16]  # 支持的数独阶数
CACHE_SIZE = 3  # 每个阶数缓存的数量

# 缓存数据结构
sudoku_cache = {
    size: deque(maxlen=CACHE_SIZE) for size in SUPPORTED_SIZES
}

# 缓存状态管理
cache_status = {
    size: {
        'initializing': False,  # 是否正在初始化
        'generating': False,    # 是否正在后台生成
        'initialized': False,   # 是否已完成初始化
        'last_generation_time': 0  # 最后生成时间
    } for size in SUPPORTED_SIZES
}

# 后台生成队列
generation_queue = Queue()

def format_sudoku(grid, box_size):
    """格式化输出数独"""
    n = len(grid)
    result = []
    for i in range(n):
        if i % box_size == 0:
            result.append("+" + ("-" * (box_size * 2 + 1) + "+") * box_size)
        
        row = []
        for j in range(n):
            if j % box_size == 0:
                row.append("|")
            row.append(f" {grid[i][j] if grid[i][j] != 0 else '.'} ")
        row.append("|")
        result.append("".join(row))
    
    result.append("+" + ("-" * (box_size * 2 + 1) + "+") * box_size)
    return "\n".join(result)

def generate_sudoku_background(size):
    """后台生成数独"""
    try:
        result = subprocess.run(
            ['python', 'test.py', str(size)],
            capture_output=True,
            text=True,
            timeout=30  # 30秒超时
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if isinstance(data, dict) and 'puzzle' in data and 'solution' in data:
                # 添加到缓存
                with threading.Lock():
                    if len(sudoku_cache[size]) < CACHE_SIZE:
                        sudoku_cache[size].append({
                            'puzzle': data['puzzle'],
                            'solution': data['solution']
                        })
                        cache_status[size]['last_generation_time'] = time.time()
                        print(f"成功生成 {size} 阶数独，当前缓存数量: {len(sudoku_cache[size])}")
        else:
            print(f"生成 {size} 阶数独失败: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"生成 {size} 阶数独超时")
    except Exception as e:
        print(f"生成 {size} 阶数独时发生错误: {str(e)}")
    finally:
        cache_status[size]['generating'] = False

def initialize_cache():
    """初始化缓存 - 预填充所有支持的阶数"""
    print("开始初始化数独缓存...")
    
    for size in SUPPORTED_SIZES:
        cache_status[size]['initializing'] = True
        print(f"预填充 {size} 阶数独缓存...")
        
        # 为每个阶数启动多个生成线程
        threads = []
        for _ in range(CACHE_SIZE):
            thread = threading.Thread(target=generate_sudoku_background, args=(size,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=60)  # 最多等待60秒
        
        cache_status[size]['initializing'] = False
        cache_status[size]['initialized'] = True
        print(f"{size} 阶数独缓存初始化完成，当前数量: {len(sudoku_cache[size])}")
    
    print("所有数独缓存初始化完成")

def check_and_generate_background(size):
    """检查缓存数量，如果不足则后台生成"""
    with threading.Lock():
        if (len(sudoku_cache[size]) <= 1 and 
            not cache_status[size]['generating'] and
            time.time() - cache_status[size]['last_generation_time'] > 5):  # 避免频繁生成
            
            cache_status[size]['generating'] = True
            thread = threading.Thread(target=generate_sudoku_background, args=(size,))
            thread.daemon = True
            thread.start()
            print(f"启动后台生成 {size} 阶数独")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        n = request.form.get('n', '')
        try:
            n = int(n)
            
            # 验证是否为支持的阶数
            if n not in SUPPORTED_SIZES:
                # 验证是否为完全平方数
                sqrt_n = int(n ** 0.5)
                if sqrt_n * sqrt_n != n:
                    raise ValueError("n必须是完全平方数")
                else:
                    return render_template('index.html', error=f"暂不支持 {n} 阶数独，目前仅支持 {', '.join(map(str, SUPPORTED_SIZES))} 阶", config=config)
            
            # 检查缓存状态
            if cache_status[n]['initializing']:
                return render_template('index.html', error=f"{n}阶数独初始化中，请稍后再试", config=config)
            
            # 从缓存中获取数独（线程安全）
            with threading.Lock():
                # 检查缓存是否为空
                if len(sudoku_cache[n]) == 0:
                    if not cache_status[n]['generating']:
                        # 启动后台生成
                        cache_status[n]['generating'] = True
                        thread = threading.Thread(target=generate_sudoku_background, args=(n,))
                        thread.daemon = True
                        thread.start()
                    return render_template('index.html', error=f"{n}阶数独生成中，请稍后再试", config=config)
                
                # 安全地从缓存中获取数据 - 使用try-except防止竞态条件
                try:
                    cached_data = sudoku_cache[n].popleft()
                    
                    # 检查是否需要后台生成
                    check_and_generate_background(n)
                    
                    # 将数字转换为字符串以便模板处理
                    puzzle = [[str(cell) for cell in row] for row in cached_data['puzzle']]
                    solution = [[str(cell) for cell in row] for row in cached_data['solution']]
                    
                    return render_template('index.html',
                                        n=n,
                                        puzzle=puzzle,
                                        solution=solution,
                                        config=config)
                except IndexError:
                    # 如果缓存为空（竞态条件发生），返回错误信息
                    if not cache_status[n]['generating']:
                        cache_status[n]['generating'] = True
                        thread = threading.Thread(target=generate_sudoku_background, args=(n,))
                        thread.daemon = True
                        thread.start()
                    return render_template('index.html', error=f"{n}阶数独生成中，请稍后再试", config=config)
            
        except ValueError as e:
            return render_template('index.html', error=str(e), config=config)
        except Exception as e:
            return render_template('index.html', error=f"发生错误: {str(e)}", config=config)
    
    return render_template('index.html', config=config)

@app.route('/refresh', methods=['POST'])
def refresh_sudoku():
    """刷新数独，将当前数独重新放回缓存"""
    try:
        data = request.get_json()
        n = data.get('n')
        puzzle = data.get('puzzle')
        solution = data.get('solution')
        
        if not n or not puzzle or not solution:
            return {'success': False, 'error': '缺少必要参数'}
        
        n = int(n)
        
        # 验证是否为支持的阶数
        if n not in SUPPORTED_SIZES:
            return {'success': False, 'error': f'不支持的阶数: {n}'}
        
        # 将数独重新放回缓存（线程安全）
        with threading.Lock():
            # 将字符串转换回数字
            puzzle_numeric = [[int(cell) for cell in row] for row in puzzle]
            solution_numeric = [[int(cell) for cell in row] for row in solution]
            
            # 如果缓存已满，移除最旧的一个
            if len(sudoku_cache[n]) >= CACHE_SIZE:
                sudoku_cache[n].popleft()
            
            # 将当前数独添加到缓存
            sudoku_cache[n].append({
                'puzzle': puzzle_numeric,
                'solution': solution_numeric
            })
            
            print(f"数独已重新放回 {n} 阶缓存，当前缓存数量: {len(sudoku_cache[n])}")
        
        return {'success': True}
        
    except Exception as e:
        return {'success': False, 'error': f'刷新失败: {str(e)}'}

@app.route('/hint', methods=['POST'])
def get_hint():
    """获取AI提示"""
    try:
        # 检查AI功能是否启用
        if not config.AI_CONFIG['enabled']:
            return {'success': False, 'error': 'AI提示功能未启用'}
        
        data = request.get_json()
        n = data.get('n')
        current_state = data.get('current_state')
        
        if not n or not current_state:
            return {'success': False, 'error': '缺少必要参数'}
        
        # 检查API密钥
        api_key = config.AI_CONFIG['api_key']
        if not api_key:
            return {'success': False, 'error': '未配置AI API密钥'}
        
        # 构建提示词
        prompt = config.AI_CONFIG['prompt_template'].format(
            n=n,
            current_state=current_state
        )
        
        # 调用AI API
        import requests
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': config.AI_CONFIG['model'],
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': config.AI_CONFIG['max_tokens'],
            'temperature': 0.7
        }
        
        response = requests.post(config.AI_CONFIG['api_url'], 
                            headers=headers, 
                            json=payload,
                            timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            hint = result['choices'][0]['message']['content']
            return {'success': True, 'hint': hint}
        else:
            return {'success': False, 'error': f'AI API调用失败: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': f'获取提示失败: {str(e)}'}

# 服务器启动时立即初始化缓存
def start_cache_initialization():
    """启动缓存初始化"""
    print("服务器启动，开始预生成数独缓存...")
    init_thread = threading.Thread(target=initialize_cache)
    init_thread.daemon = True
    init_thread.start()

# 在第一次请求时检查缓存状态
@app.before_request
def check_cache_status():
    """检查缓存状态"""
    # 这里可以添加其他状态检查逻辑
    pass

if __name__ == '__main__':
    # 服务器启动时立即开始预生成
    start_cache_initialization()
    app.run(host='::', port=5000, debug=True)
