# 修复 Python 3.13 兼容性问题
import sys
if sys.version_info >= (3, 13):
    import pydantic
    from pydantic.typing import ForwardRef
    
    # Monkey patch for ForwardRef compatibility
    def _evaluate_patched(self, globalns, localns, recursive_guard=frozenset()):
        return self._evaluate_original(globalns, localns, recursive_guard)
    
    if not hasattr(ForwardRef, '_evaluate_original'):
        ForwardRef._evaluate_original = ForwardRef._evaluate
        ForwardRef._evaluate = _evaluate_patched

import os
import uvicorn
import requests
import logging
import socket
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path
from typing import Dict, Any

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent.parent / "logs/app.log")
    ]
)
logger = logging.getLogger(__name__)

# 获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
logger.info(f"Project root: {PROJECT_ROOT}")

# 创建应用
app = FastAPI(title="AI Assistant", version="4.1")

# 设置模板和静态文件
frontend_dir = PROJECT_ROOT / 'frontend'
templates_dir = frontend_dir / 'templates'

# 确保目录存在
templates_dir.mkdir(parents=True, exist_ok=True)

# 初始化模板引擎
templates = Jinja2Templates(directory=str(templates_dir))

class QuestionRequest(BaseModel):
    question: str

# 获取公网IP
def get_public_ip() -> str:
    services = [
        'https://api.ipify.org',
        'https://ident.me',
        'https://ifconfig.me/ip'
    ]
    
    for service in services:
        try:
            response = requests.get(service, timeout=3)
            if response.status_code == 200:
                ip = response.text.strip()
                if ip.count('.') == 3:  # 简单验证IP格式
                    return ip
        except:
            continue
    
    return "unknown"

# 获取本地IP地址
def get_local_ip() -> str:
    try:
        # 方法1：获取所有网络接口的IP
        hostname = socket.gethostname()
        ip_list = socket.gethostbyname_ex(hostname)[2]
        
        # 优先选择非回环地址
        for ip in ip_list:
            if not ip.startswith('127.') and not ip.startswith('169.254.'):
                return ip
        
        # 如果没有找到，使用第一个非127的IP
        for ip in ip_list:
            if not ip.startswith('127.'):
                return ip
    except:
        pass
    
    try:
        # 方法2：使用UDP连接获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# 检查端口是否开放（更可靠的方法）
def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(2)
        try:
            s.connect((host, port))
            return True
        except:
            return False

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/public-ip")
async def get_public_ip_endpoint():
    return JSONResponse(content={"ip": get_public_ip()})

@app.get("/status")
async def service_status():
    try:
        response = requests.get("http://127.0.0.1:11435/api/tags", timeout=5)
        if response.status_code == 200:
            return JSONResponse(content={"status": "running"})
    except Exception as e:
        logger.error(f"Ollama状态检查失败: {str(e)}")
    return JSONResponse(content={"status": "down"}, status_code=503)

@app.get("/local-ip")
async def get_local_ip_endpoint():
    return JSONResponse(content={"ip": get_local_ip()})

@app.get("/port-status")
async def port_status():
    local_ip = get_local_ip()
    
    return JSONResponse(content={
        "port_8000": "open" if is_port_open(local_ip, 8000) else "closed",
        "port_11435": "open" if is_port_open(local_ip, 11435) else "closed",
        "local_ip": local_ip
    })

@app.post("/ask")
async def ask_question(request: Request, data: QuestionRequest):
    try:
        question = data.question.strip()
        if not question:
            return JSONResponse(content={"answer": "问题不能为空"}, status_code=400)
        
        # 调用Ollama API
        api_url = "http://127.0.0.1:11435/api/generate"
        payload = {
            "model": "deepseek-coder:1.3b",
            "prompt": question,
            "stream": False
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=120)
            response.raise_for_status()
            response_data = response.json()
            answer = response_data.get("response", "")
            
            # 记录问题和答案
            logger.info(f"问题: {question}")
            logger.info(f"答案: {answer[:200]}...")
            
            return JSONResponse(content={"answer": answer})
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API调用失败: {str(e)}")
            return JSONResponse(content={"answer": f"AI服务暂时不可用: {str(e)}"}, status_code=503)
        except ValueError as e:
            logger.error(f"Ollama响应解析失败: {str(e)}")
            return JSONResponse(content={"answer": "AI响应格式错误"}, status_code=500)
            
    except Exception as e:
        logger.exception("处理问题时发生意外错误")
        return JSONResponse(content={"answer": f"系统错误: {str(e)}"}, status_code=500)

if __name__ == "__main__":
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    logger.info(f"本地IP: {local_ip}")
    logger.info(f"公网IP: {public_ip}")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_config=None,
        access_log=False
    )
