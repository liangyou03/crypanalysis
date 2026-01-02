# config.py
import os
import ccxt
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

# 1. 初始化 DeepSeek/OpenAI 客户端
try:
    llm_client = OpenAI(
        api_key=os.getenv("LLM_API_KEY"), 
        base_url=os.getenv("LLM_BASE_URL")
    )
    LLM_MODEL = os.getenv("LLM_MODEL")
except Exception as e:
    print(f"❌ LLM 客户端初始化失败: {e}")
    exit()

# 2. 初始化 OKX 客户端
try:
    exchange = ccxt.okx({
        'timeout': 30000, 
        'enableRateLimit': True
    })
except Exception as e:
    print(f"❌ OKX 客户端初始化失败: {e}")
    exit()

print("✅ 系统配置加载完成")