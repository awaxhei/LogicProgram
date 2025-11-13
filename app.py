from flask import Flask, render_template, request
import subprocess
import os

app = Flask(__name__)

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
                return render_template('index.html', error=result.stderr)
                
            # 解析输出
            output = result.stdout.split('\n')
            puzzle = '\n'.join(output[1:output.index('数独的解:')])
            solution = '\n'.join(output[output.index('数独的解:')+1:])
            
            return render_template('index.html', 
                                n=n,
                                puzzle=puzzle,
                                solution=solution)
            
        except ValueError as e:
            return render_template('index.html', error=str(e))
        except Exception as e:
            return render_template('index.html', error=f"发生错误: {str(e)}")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
