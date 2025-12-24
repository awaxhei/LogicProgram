# 数独游戏项目 IPv6 部署指南

## 项目概述
这是一个基于Flask的数独游戏Web应用，支持多种阶数的数独生成和AI提示功能。

## IPv6 部署配置

### 1. 服务器配置修改
项目已经配置为支持IPv6访问。在 `app.py` 文件中，服务器启动配置已修改为：

```python
app.run(host='::', port=5000, debug=True)
```

- `host='::'`：监听所有IPv6地址（同时支持IPv4）
- `port=5000`：使用5000端口
- `debug=True`：开发模式（生产环境建议设为False）

### 2. 依赖安装
确保安装所有必要的依赖：

```bash
pip install -r requirements.txt
```

依赖包括：
- Flask==2.3.3
- z3-solver==4.12.2.0
- requests==2.31.0

### 3. 启动服务器

#### 方式一：直接运行
```bash
python app.py
```

#### 方式二：使用生产服务器（推荐）
```bash
# 安装生产服务器
pip install gunicorn

# 启动服务器（IPv6支持）
gunicorn -b [::]:5000 app:app
```

### 4. 访问应用

#### IPv6 访问
- 本地访问：`http://[::1]:5000`
- 局域网访问：`http://[你的IPv6地址]:5000`

#### IPv4 访问（兼容）
- 本地访问：`http://127.0.0.1:5000` 或 `http://localhost:5000`
- 局域网访问：`http://你的IPv4地址:5000`

### 5. 防火墙配置

确保防火墙允许5000端口的IPv6连接：

```bash
# Windows (管理员权限)
netsh advfirewall firewall add rule name="Sudoku IPv6" dir=in action=allow protocol=TCP localport=5000

# Linux
sudo ufw allow 5000/tcp
```

### 6. 生产环境建议

1. **关闭调试模式**：将 `debug=True` 改为 `debug=False`
2. **使用生产服务器**：推荐使用gunicorn或uWSGI
3. **配置反向代理**：使用nginx作为反向代理
4. **设置环境变量**：使用环境变量管理配置

### 7. 故障排除

#### 无法访问IPv6地址
- 检查网络是否支持IPv6：`ipconfig` (Windows) 或 `ifconfig` (Linux)
- 确认防火墙设置
- 检查路由器IPv6支持

#### 端口被占用
- 更改端口号：`app.run(host='::', port=8080)`
- 杀死占用进程

#### 依赖问题
- 重新安装依赖：`pip install -r requirements.txt`
- 检查Python版本兼容性

## 功能特性

- ✅ 支持4、9、16阶数独
- ✅ 智能缓存机制
- ✅ AI解题提示
- ✅ 响应式前端界面
- ✅ IPv6/IPv4双栈支持

## 注意事项

1. AI功能需要有效的API密钥
2. 首次启动会预生成数独缓存，可能需要一些时间
3. 生产环境建议关闭debug模式
4. 确保静态文件路径正确配置