from z3 import *
import sys
import random
import json

def generate_sudoku(n, max_retries=10, retry_count=0):
    """
    生成n阶唯一解数独及其解
    :param n: 数独阶数，必须是完全平方数
    :param max_retries: 最大重试次数
    :param retry_count: 当前重试次数
    :return: (题目, 解)
    """
    try:
        # 验证n是否为完全平方数
        sqrt_n = int(n ** 0.5)
        if sqrt_n * sqrt_n != n:
            raise ValueError("n必须是完全平方数")
        
        # 检查递归深度
        if retry_count >= max_retries:
            raise ValueError("达到最大重试次数，无法生成唯一解数独")
        
        # 创建z3求解器
        solver = Solver()
        
        # 创建n×n的整数变量矩阵
        cells = [[Int(f'cell_{i}_{j}') for j in range(n)] for i in range(n)]
        
        # 添加基本约束
        for i in range(n):
            for j in range(n):
                # 每个单元格的值在1到n之间
                solver.add(cells[i][j] >= 1, cells[i][j] <= n)
            
            # 每行数字不重复
            solver.add(Distinct(cells[i]))
            
            # 每列数字不重复
            solver.add(Distinct([cells[j][i] for j in range(n)]))
        
        # 每个小宫格数字不重复
        box_size = int(n ** 0.5)
        for box_i in range(box_size):
            for box_j in range(box_size):
                box_cells = []
                for i in range(box_i*box_size, (box_i+1)*box_size):
                    for j in range(box_j*box_size, (box_j+1)*box_size):
                        box_cells.append(cells[i][j])
                solver.add(Distinct(box_cells))
        
        # 求解完整数独
        if solver.check() != sat:
            raise ValueError("无法生成数独")
        
        model = solver.model()
        solution = [[model.evaluate(cells[i][j]).as_long() for j in range(n)] for i in range(n)]
        
        # 随机挖空部分单元格生成题目
        puzzle = [row.copy() for row in solution]
        empty_cells = random.sample(range(n*n), k=int(n*n*0.6))  # 挖空约60%的单元格
        for pos in empty_cells:
            i, j = divmod(pos, n)
            puzzle[i][j] = 0
        
        # 验证题目是否有唯一解
        temp_solver = Solver()
        # 添加题目已知数字的约束
        for i in range(n):
            for j in range(n):
                if puzzle[i][j] != 0:
                    temp_solver.add(cells[i][j] == puzzle[i][j])
        
        # 检查是否有解
        if temp_solver.check() != sat:
            return generate_sudoku(n, max_retries, retry_count + 1)  # 递归重试
        
        # 检查是否唯一解
        temp_model = temp_solver.model()
        temp_solver.add(Or([cells[i][j] != temp_model.evaluate(cells[i][j]) 
                          for i in range(n) for j in range(n) if puzzle[i][j] == 0]))
        if temp_solver.check() == sat:
            return generate_sudoku(n, max_retries, retry_count + 1)  # 不唯一解，递归重试
        
        # 返回生成的数独题目和解
        return puzzle, solution
        
    except ImportError:
        print(json.dumps({"error": "未安装z3-solver库，请先运行 'pip install z3-solver'"}))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"error": "用法: python test.py n", "example": "python test.py 9"}))
        sys.exit(1)
    
    try:
        n = int(sys.argv[1])
        puzzle, solution = generate_sudoku(n)
        
        result = {
            "n": n,
            "puzzle": puzzle,
            "solution": solution
        }
        print(json.dumps(result))
        
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
