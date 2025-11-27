from flask import Flask, render_template, request
import subprocess
import os
import json

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        n = request.form.get('n', '')
        try:
            n = int(n)
            # 验证是否为完全平方数
            sqrt_n = int(n ** 0.5)
            if sqrt_n * sqrt_n != n:
                raise ValueError("n必须是完全平方数")
                
            # 调用test.py
            result = subprocess.run(
                ['python', 'test.py', str(n)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                try:
                    error_data = json.loads(result.stderr)
                    return render_template('index.html', error=error_data.get('error', '未知错误'))
                except:
                    return render_template('index.html', error=result.stderr)
                
            # 解析JSON输出并转换为模板所需格式
            try:
                data = json.loads(result.stdout)
                if not isinstance(data, dict):
                    raise ValueError("无效的JSON格式")
                
                if 'puzzle' not in data or 'solution' not in data:
                    raise ValueError("JSON数据缺少必要的字段")
                
                # 验证puzzle和solution是否为二维数组
                if (not isinstance(data['puzzle'], list) or 
                    not all(isinstance(row, list) for row in data['puzzle']) or
                    not isinstance(data['solution'], list) or 
                    not all(isinstance(row, list) for row in data['solution'])):
                    raise ValueError("puzzle和solution必须是二维数组")
                
                # 将数字转换为字符串以便模板处理
                puzzle = [[str(cell) for cell in row] for row in data['puzzle']]
                solution = [[str(cell) for cell in row] for row in data['solution']]
                
                return render_template('index.html',
                                    n=data['n'],
                                    puzzle=puzzle,
                                    solution=solution)
                
            except json.JSONDecodeError as e:
                return render_template('index.html', error=f"JSON解析错误: {str(e)}")
            except ValueError as e:
                return render_template('index.html', error=f"数据格式错误: {str(e)}")
            except Exception as e:
                return render_template('index.html', error=f"解析结果出错: {str(e)}")
            
        except ValueError as e:
            return render_template('index.html', error=str(e))
        except Exception as e:
            return render_template('index.html', error=f"发生错误: {str(e)}")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
