# check_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ 未找到 GOOGLE_API_KEY，请检查 .env 文件")
    exit()

genai.configure(api_key=api_key)

print(f"🔍 正在查询可用模型列表 (Key: {api_key[:5]}...)...")

try:
    count = 0
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            count += 1
    
    if count == 0:
        print("⚠️ 未找到任何支持 generateContent 的模型。可能原因：")
        print("1. API Key 无效或未开通 Google AI Studio 服务。")
        print("2. 所在地区不支持 (建议使用 US 节点 VPN)。")
    else:
        print(f"\n✅ 共找到 {count} 个可用模型。")
        print("👉 请在 macro_analyst.py 中使用上面列表里的名称 (去掉 'models/' 前缀)。")

except Exception as e:
    print(f"❌ 查询失败: {e}")