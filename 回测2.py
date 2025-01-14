import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 示例：读取历史数据
def load_data(file_path):
    """
    读取历史数据，假设数据包含日期、开盘价、收盘价、最高价、最低价、成交量等。
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件未找到: {file_path}")
    data = pd.read_csv(file_path, parse_dates=['Date'])
    data.set_index('Date', inplace=True)
    return data

# 示例策略逻辑
def simple_strategy(data, short_window=2, long_window=5):
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    data['Signal'] = 0
    data.loc[data['Short_MA'] > data['Long_MA'], 'Signal'] = 1  # 买入信号
    data.loc[data['Short_MA'] <= data['Long_MA'], 'Signal'] = -1  # 卖出信号
    return data

# 模拟回测
def backtest(data, initial_balance=1000000, risk_per_trade=0.5):
    balance = initial_balance
    positions = 0
    equity_curve = []
    risk_curve = []

    for i in range(len(data)):
        if i == 0:
            equity_curve.append(balance)
            risk_curve.append(0)
            continue

        signal = data['Signal'].iloc[i]
        price = data['Close'].iloc[i]

        if signal == 1 and positions == 0:
            risk_amount = balance * risk_per_trade
            positions = risk_amount // price
            balance -= positions * price

        elif signal == -1 and positions > 0:
            balance += positions * price
            positions = 0

        current_equity = balance + positions * price
        current_risk = (positions * price) / current_equity if current_equity > 0 else 0

        equity_curve.append(current_equity)
        risk_curve.append(current_risk)

    data['Equity'] = equity_curve
    data['Risk'] = risk_curve
    return data

# 计算回测指标
def calculate_metrics(data):
    equity = data['Equity']
    returns = equity.pct_change().dropna()
    rolling_max = equity.cummax()
    drawdown = (equity - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
    return {
        "Final Equity": equity.iloc[-1],
        "Max Drawdown": max_drawdown,
        "Sharpe Ratio": sharpe_ratio
    }

# 可视化结果
def plot_results(data):
    plt.figure(figsize=(14, 7))
    plt.plot(data['Equity'], label='Equity Curve')
    plt.title('Equity Curve')
    plt.xlabel('Date')
    plt.ylabel('Equity')
    plt.legend()
    plt.grid()
    plt.show()

# 主程序
if __name__ == '__main__':
    file_path = r'D:\resilio sync\品种数据库\historical_data.csv'  # 替换为你的实际路径
    data = load_data(file_path)
    data = simple_strategy(data)
    data = backtest(data)
    metrics = calculate_metrics(data)
    print("回测指标：")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    plot_results(data)