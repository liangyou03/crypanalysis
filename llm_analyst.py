# llm_analyst.py
import json
import numpy as np # 需要 import numpy
from config import llm_client, LLM_MODEL
from datetime import datetime

# --- 核心修复：自定义 JSON 编码器 ---
class NumpyEncoder(json.JSONEncoder):
    """
    这个类专门用来处理 numpy 数据类型报错
    它可以把 numpy.bool_, numpy.float32 等自动转成 python 原生类型
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

def generate_execution_plan(dashboard, setups, news):
    print("🧠 AI 正在进行深度推演...")
    
    system_prompt = """
    Role: You are a **Senior Crypto Prop Trader** analyzing the market for a high-net-worth client (Biostats PhD).
    
    Style: 
    - **Analytical**: Show your work. Explain WHY you see a setup.
    - **Direct**: Give bold, unambiguous commands.
    - **Risk-Averse**: If the setup is bad, say "Skip".

    INPUT DATA:
    1. **Dashboard**: Overall market health (EMA structure, MACD momentum).
    2. **Setups**: Coins with detailed metrics (RSI, ADX, Volume Spike).
    3. **News**: Narrative context.

    TASK:
    Generate a **Daily Trading Strategy Report** in Chinese (Simplified).

    OUTPUT FORMAT (Markdown):

    # 📟 市场全景雷达 [Date]

    ## 1. 信号灯 (Signal Light)
    [Visual Bar of Market Score] 
    > **状态**: {signal_light} | **评分**: {score}/100
    
    * **深度解构**:
      - 均线形态: {ema_structure} (解释这对趋势意味着什么)
      - 动能状态: {macd_status}
      - **直白建议**: 基于当前 ADX ({adx})，**[简短建议，例如：全仓出击 / 仅限现货 / 空仓休息]**

    ## 2. 叙事逻辑 (Narrative)
    - 用一句话概括当前新闻情绪，并判断它是否支持上述技术面。

    ## 3. 精选交易推演 (Top Setups)
    *只分析逻辑最清晰的 4-5 个币种，不要罗列数据。*

    ### 🪙 {Ticker} ({Change}) - {Pattern}
    
    * **🔍 分析推演 (The Logic)**:
        * 引用数据证明观点。例如："RSI 目前为 **{rsi}**，显示并未超买，且成交量放大了 **{vol_spike}**，说明主力资金正在..."
        * 结合均线距离："{dist_to_ema25}"...
        * *Tell the story of the chart.*

    * **⚡️ 交易指令 (The Action)**:
        * **方向**: **[做多 Long / 做空 Short]**
        * **进场**: **[具体价格 或 "市价进场"]**
        * **止损**: **[价格]** (必须严格基于 ATR 计算: Price +/- atr_stop)
        * **止盈**: **[价格]** (建议设在进场价 + 3*ATR 或 阻力位)
        * **杠杆**: **[建议倍数，例如 3x-5x]** (参考 max_lev)

    ## 4. 风险提示
    - 一句话总结今日最大的风险点（如数据发布或流动性枯竭）。

    Do not use generic disclaimers. Be a trader.
    """
    
    data_packet = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "dashboard": dashboard,
        "candidates": setups,
        "news": news
    }
    
    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            # 修复点：在这里指定 cls=NumpyEncoder，自动处理所有 numpy 类型
            {"role": "user", "content": json.dumps(data_packet, cls=NumpyEncoder)}
        ],
        temperature=1.0 
    )
    return response.choices[0].message.content