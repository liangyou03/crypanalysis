import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 初始化宏观分析师客户端
# 这是一个独立的 Client，可以配置与主交易员(DeepSeek)不同的模型
try:
    macro_client = OpenAI(
        api_key=os.getenv("MACRO_API_KEY"),
        base_url=os.getenv("MACRO_BASE_URL")
    )
    MACRO_MODEL = os.getenv("MACRO_MODEL")
except Exception as e:
    print(f"❌ 宏观模型配置失败: {e}")
    macro_client = None

def generate_macro_report(news_list, btc_price):
    if not macro_client: 
        return "⚠️ 宏观分析师离线 (请检查 .env 配置)"
    
    # 获取当前使用的模型名字，方便调试
    model_name = MACRO_MODEL if MACRO_MODEL else "Unknown Model"
    print(f"🌍 宏观分析师 ({model_name}) 正在研判全球局势...")

    prompt = f"""
    Role: You are a **Global Macro Strategist** for a Crypto Hedge Fund. 
    Unlike the technical traders, you DO NOT care about charts. 
    You care about **Liquidity, Narrative Cycles, and Geopolitics**.

    INPUT:
    1. **BTC Price**: ${btc_price}
    2. **Global Headlines**: 
    {json.dumps(news_list)}

    TASK:
    Write a **"Macro Narrative Outlook"** (Independent Report).

    OUTPUT FORMAT (Markdown, Chinese Simplified):

    # 🌍 宏观叙事简报 (Model: {model_name})

    ## 1. 全球风向 (The Meta)
    - **市场情绪**: (用一个词形容，如 "Risk-On", "PVP", "Fear")
    - **核心驱动力**: (What is the single biggest story moving money?)

    ## 2. 资金流向 (Sector Rotation)
    - Based on news, where is the smart money going? (AI? Meme? RWA? Major L1s?)
    - **关注币种**: Mention 1-2 specific tickers related to the narrative.
    
    ## 3. 机会与陷阱
    - **不对称机会**: (Where is the upside > downside?)
    - **陷阱**: (What is a "Sell the News" event?)

    ## 4. 战略建议 (Strategic Stance)
    - **Bold Advice**: **[Aggressive Long / Defensive / Cash is King]**
    - **Reasoning**: One sentence summary.
    
    Style: Insightful, Big-picture, Institutional tone.
    """

    try:
        response = macro_client.chat.completions.create(
            model=MACRO_MODEL,
            messages=[
                {"role": "system", "content": prompt},
            ],
            temperature=0.7 # 宏观分析不需要太发散，稍微收敛一点
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ 宏观分析失败: {e}"