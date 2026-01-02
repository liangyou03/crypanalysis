# main.py
import os
from datetime import datetime
from data_fetcher import get_market_dashboard, scan_setups, get_news_context
from llm_analyst import generate_execution_plan
from macro_analyst import generate_macro_report # 引入新的宏观分析师

def main():
    # 1. 获取数据
    dashboard = get_market_dashboard()
    setups = scan_setups()
    narrative = get_news_context()
    
    # 获取 BTC 价格用于宏观参照
    btc_price = dashboard.get('price', 0)
    
    # 2. 双核并行分析 (Dual Core Processing)
    
    # A. 左脑 (DeepSeek) - 专注技术执行
    technical_report = generate_execution_plan(dashboard, setups, narrative)
    
    macro_report = generate_macro_report(narrative, btc_price)
    
    # 3. 拼接报告
    final_report = f"""
{macro_report}

---
{technical_report}
    """
    
    # 4. 保存
    folder = "reports"
    if not os.path.exists(folder): os.makedirs(folder)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    fname = f"{folder}/{date_str}_Dual_View.md"
    
    with open(fname, "w", encoding='utf-8') as f:
        f.write(final_report)
        # 附录数据
        f.write("\n\n---\n### 🔢 QUANT DATA LOG\n")
        f.write(f"Score: {dashboard.get('score')}\n")
        for s in setups:
            max_lev = s['risk_data']['max_lev']
            f.write(f"- {s['ticker']}: {s['pattern']} (MaxLev: {max_lev}x)\n")

    print("\n" + "="*60)
    print("✅ 双份独立报告已生成！")
    print(f"📁 查看路径: {fname}")
    print("="*60)

if __name__ == "__main__":
    main()