import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体,以正确显示图表中的中文标签
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def create_output_folder(folder_name="花叶类ACF_PACF分析"):
    """创建输出文件夹"""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"已创建文件夹: {folder_name}")
    return folder_name

def calculate_acf(data, max_lags=40):
    """
    手动计算自相关函数(ACF)
    """
    n = len(data)
    data = np.array(data)
    
    # 去中心化
    mean_val = np.mean(data)
    data_centered = data - mean_val
    
    # 计算自相关
    acf_result = []
    
    for lag in range(max_lags + 1):
        if lag == 0:
            acf_result.append(1.0)
        else:
            if lag >= n:
                acf_result.append(0.0)
            else:
                # 计算滞后lag的自相关
                numerator = np.sum(data_centered[:-lag] * data_centered[lag:])
                denominator = np.sum(data_centered ** 2)
                
                if denominator != 0:
                    acf_val = numerator / denominator
                else:
                    acf_val = 0.0
                
                acf_result.append(acf_val)
    
    return np.array(acf_result)

def calculate_pacf(data, max_lags=40):
    """
    手动计算偏自相关函数(PACF)
    使用Yule-Walker方程求解
    """
    n = len(data)
    data = np.array(data)
    
    # 去中心化
    mean_val = np.mean(data)
    data_centered = data - mean_val
    
    # 先计算ACF
    acf_vals = calculate_acf(data, max_lags)
    
    pacf_result = [1.0]  # PACF在lag=0时总是1
    
    for k in range(1, min(max_lags + 1, n)):
        if k == 1:
            # 第一阶偏自相关就是一阶自相关
            pacf_result.append(acf_vals[1])
        else:
            # 使用Yule-Walker方程
            # 构建自相关矩阵
            R = np.zeros((k, k))
            for i in range(k):
                for j in range(k):
                    R[i, j] = acf_vals[abs(i - j)]
            
            # 右侧向量
            r = acf_vals[1:k+1]
            
            try:
                # 求解线性方程组
                phi = np.linalg.solve(R, r)
                pacf_result.append(phi[-1])  # 最后一个系数就是k阶偏自相关
            except np.linalg.LinAlgError:
                pacf_result.append(0.0)
    
    return np.array(pacf_result)

def calculate_confidence_bounds(n, alpha=0.05):
    """
    计算置信区间
    """
    # 对于大样本，95%置信区间约为 ±1.96/√n
    bound = 1.96 / np.sqrt(n)
    return bound

def plot_acf_manual(data, max_lags=40, title="自相关函数 (ACF)", ax=None):
    """
    手动绘制ACF图
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # 计算ACF
    acf_vals = calculate_acf(data, max_lags)
    lags = np.arange(len(acf_vals))
    
    # 计算置信区间
    n = len(data)
    conf_bound = calculate_confidence_bounds(n)
    
    # 绘制ACF
    ax.stem(lags, acf_vals, basefmt=" ")
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax.axhline(y=conf_bound, color='red', linestyle='--', alpha=0.7, label=f'95% 置信区间')
    ax.axhline(y=-conf_bound, color='red', linestyle='--', alpha=0.7)
    
    ax.set_title(title, fontweight='bold')
    ax.set_xlabel('滞后期')
    ax.set_ylabel('自相关系数')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    return acf_vals

def plot_pacf_manual(data, max_lags=40, title="偏自相关函数 (PACF)", ax=None):
    """
    手动绘制PACF图
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # 计算PACF
    pacf_vals = calculate_pacf(data, max_lags)
    lags = np.arange(len(pacf_vals))
    
    # 计算置信区间
    n = len(data)
    conf_bound = calculate_confidence_bounds(n)
    
    # 绘制PACF
    ax.stem(lags, pacf_vals, basefmt=" ")
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax.axhline(y=conf_bound, color='red', linestyle='--', alpha=0.7, label=f'95% 置信区间')
    ax.axhline(y=-conf_bound, color='red', linestyle='--', alpha=0.7)
    
    ax.set_title(title, fontweight='bold')
    ax.set_xlabel('滞后期')
    ax.set_ylabel('偏自相关系数')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    return pacf_vals

def load_and_prepare_data(file_path):
    """
    加载并准备时间序列数据
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        print(f"成功读取文件: {file_path}")
        print(f"数据形状: {df.shape}")
        print(f"列名: {list(df.columns)}")
        print("\n前5行数据:")
        print(df.head())
        
        # 检查列名并统一格式
        if '销售日期' in df.columns:
            date_col = '销售日期'
        elif '日期' in df.columns:
            date_col = '日期'
        else:
            print("错误: 找不到日期列")
            return None
            
        if '销量(千克)' in df.columns:
            sales_col = '销量(千克)'
        elif '销量（千克）' in df.columns:
            sales_col = '销量（千克）'
        elif '销量' in df.columns:
            sales_col = '销量'
        else:
            print("错误: 找不到销量列")
            return None
        
        # 转换日期格式
        df[date_col] = pd.to_datetime(df[date_col])
        
        # 按日期排序
        df = df.sort_values(date_col)
        
        # 设置日期为索引
        df.set_index(date_col, inplace=True)
        
        # 提取销量数据
        sales_data = df[sales_col].dropna()
        
        print(f"\n数据基本信息:")
        print(f"数据期间: {sales_data.index.min()} 到 {sales_data.index.max()}")
        print(f"总天数: {len(sales_data)} 天")
        print(f"销量统计:")
        print(sales_data.describe())
        
        return sales_data
        
    except Exception as e:
        print(f"数据加载错误: {e}")
        return None

def plot_time_series(sales_data, output_folder):
    """
    绘制原始时间序列图
    """
    plt.figure(figsize=(15, 6))
    
    plt.plot(sales_data.index, sales_data.values, 
             linewidth=2, color='#2E86AB', alpha=0.8, marker='o', markersize=3)
    
    plt.title('花叶类销量时间序列', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('销售日期', fontsize=12)
    plt.ylabel('销量(千克)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # 添加移动平均线
    if len(sales_data) >= 7:
        ma_7 = sales_data.rolling(window=7, center=True).mean()
        plt.plot(sales_data.index, ma_7, 
                color='red', linewidth=2, alpha=0.8, label='7日移动平均')
        plt.legend()
    
    plt.tight_layout()
    
    # 保存图片
    filename = "花叶类销量时间序列.png"
    filepath = os.path.join(output_folder, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"已保存: {filepath}")
    
    plt.show()

def analyze_acf_pacf_comprehensive(sales_data, output_folder):
    """
    综合ACF/PACF分析 - 观察不同周期
    """
    # 定义不同的分析周期
    analysis_periods = {
        '短期周期 (2周)': 14,      # 观察周循环
        '中期周期 (2个月)': 60,     # 观察月度模式  
        '长期周期 (1季度)': 90,     # 观察季度模式
        '年度周期': min(180, len(sales_data)//3)  # 观察年度模式，但不超过数据长度的1/3
    }
    
    fig, axes = plt.subplots(4, 2, figsize=(16, 20))
    fig.suptitle('花叶类销量 ACF/PACF 周期性分析', fontsize=18, fontweight='bold', y=0.98)
    
    for i, (period_name, lags) in enumerate(analysis_periods.items()):
        if lags >= len(sales_data):
            lags = len(sales_data) - 1
            
        # 绘制ACF
        acf_vals = plot_acf_manual(sales_data.values, max_lags=lags, 
                                  title=f'{period_name} - 自相关函数 (ACF)', ax=axes[i, 0])
        
        # 标记重要的周期点
        if lags >= 7:
            axes[i, 0].axvline(x=7, color='orange', linestyle=':', alpha=0.8, linewidth=2, label='周循环(7天)')
        if lags >= 30:
            axes[i, 0].axvline(x=30, color='green', linestyle=':', alpha=0.8, linewidth=2, label='月循环(30天)')
        if lags >= 90:
            axes[i, 0].axvline(x=90, color='purple', linestyle=':', alpha=0.8, linewidth=2, label='季度循环(90天)')
        
        axes[i, 0].legend()
        
        # 绘制PACF
        pacf_vals = plot_pacf_manual(sales_data.values, max_lags=lags, 
                                    title=f'{period_name} - 偏自相关函数 (PACF)', ax=axes[i, 1])
        
        # 标记重要的周期点
        if lags >= 7:
            axes[i, 1].axvline(x=7, color='orange', linestyle=':', alpha=0.8, linewidth=2, label='周循环(7天)')
        if lags >= 30:
            axes[i, 1].axvline(x=30, color='green', linestyle=':', alpha=0.8, linewidth=2, label='月循环(30天)')
        if lags >= 90:
            axes[i, 1].axvline(x=90, color='purple', linestyle=':', alpha=0.8, linewidth=2, label='季度循环(90天)')
            
        axes[i, 1].legend()
    
    plt.tight_layout()
    
    # 保存图片
    filename = "花叶类ACF_PACF综合分析.png"
    filepath = os.path.join(output_folder, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"已保存: {filepath}")
    
    plt.show()

def analyze_weekly_patterns(sales_data, output_folder):
    """
    专门分析周期性模式
    """
    # 添加时间特征
    df_analysis = pd.DataFrame(index=sales_data.index)
    df_analysis['销量'] = sales_data.values
    df_analysis['星期几'] = sales_data.index.dayofweek  # 0=周一, 6=周日
    df_analysis['月份'] = sales_data.index.month
    df_analysis['日期'] = sales_data.index.day
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('花叶类销量周期性模式分析', fontsize=16, fontweight='bold')
    
    # 1. 按星期几的销量分布
    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekly_avg = df_analysis.groupby('星期几')['销量'].agg(['mean', 'std']).reset_index()
    weekly_avg['星期名称'] = [weekday_names[i] for i in weekly_avg['星期几']]
    
    axes[0, 0].bar(weekly_avg['星期名称'], weekly_avg['mean'], 
                   yerr=weekly_avg['std'], capsize=5, color='skyblue', alpha=0.8)
    axes[0, 0].set_title('各星期平均销量分布', fontweight='bold')
    axes[0, 0].set_ylabel('平均销量(千克)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. 按月份的销量分布
    monthly_avg = df_analysis.groupby('月份')['销量'].agg(['mean', 'std']).reset_index()
    
    axes[0, 1].bar(monthly_avg['月份'], monthly_avg['mean'], 
                   yerr=monthly_avg['std'], capsize=5, color='lightcoral', alpha=0.8)
    axes[0, 1].set_title('各月份平均销量分布', fontweight='bold')
    axes[0, 1].set_xlabel('月份')
    axes[0, 1].set_ylabel('平均销量(千克)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. 热力图 - 星期vs月份
    pivot_table = df_analysis.pivot_table(values='销量', index='星期几', columns='月份', aggfunc='mean')
    pivot_table.index = weekday_names
    
    sns.heatmap(pivot_table, annot=True, fmt='.1f', cmap='RdYlBu_r', ax=axes[1, 0])
    axes[1, 0].set_title('星期-月份销量热力图', fontweight='bold')
    axes[1, 0].set_xlabel('月份')
    axes[1, 0].set_ylabel('星期')
    
    # 4. ACF图 - 专注于周循环
    acf_vals = plot_acf_manual(sales_data.values, max_lags=21, 
                              title='短期ACF图 (专注周循环)', ax=axes[1, 1])
    axes[1, 1].axvline(x=7, color='red', linestyle='--', alpha=0.8, label='7天周期')
    axes[1, 1].axvline(x=14, color='red', linestyle='--', alpha=0.6, label='14天周期')
    axes[1, 1].legend()
    
    plt.tight_layout()
    
    # 保存图片
    filename = "花叶类周期性模式分析.png"
    filepath = os.path.join(output_folder, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"已保存: {filepath}")
    
    plt.show()

def numerical_acf_pacf_analysis(sales_data):
    """
    数值化的ACF/PACF分析，输出关键统计信息
    """
    print("\n" + "="*60)
    print("数值化 ACF/PACF 分析结果")
    print("="*60)
    
    # 计算ACF和PACF值
    max_lags = min(30, len(sales_data)//4)
    acf_values = calculate_acf(sales_data.values, max_lags)
    pacf_values = calculate_pacf(sales_data.values, max_lags)
    
    # 计算置信区间
    n = len(sales_data)
    conf_bound = calculate_confidence_bounds(n)
    
    # 寻找显著的滞后期
    significant_lags_acf = []
    significant_lags_pacf = []
    
    for i in range(1, len(acf_values)):
        if abs(acf_values[i]) > conf_bound:
            significant_lags_acf.append((i, acf_values[i]))
    
    for i in range(1, len(pacf_values)):
        if abs(pacf_values[i]) > conf_bound:
            significant_lags_pacf.append((i, pacf_values[i]))
    
    # 输出分析结果
    print(f"\n【置信区间】95%置信区间: ±{conf_bound:.4f}")
    
    print(f"\n【ACF分析结果】")
    print(f"显著的ACF滞后期数量: {len(significant_lags_acf)}")
    if significant_lags_acf:
        print("前10个显著滞后期:")
        for lag, value in significant_lags_acf[:10]:
            cycle_type = ""
            if lag == 7:
                cycle_type = " (周循环) ⭐"
            elif lag in [30, 31]:
                cycle_type = " (月循环) ⭐"
            elif lag in [90, 91]:
                cycle_type = " (季度循环) ⭐"
            print(f"  滞后{lag}天: {value:.4f}{cycle_type}")
    
    print(f"\n【PACF分析结果】")
    print(f"显著的PACF滞后期数量: {len(significant_lags_pacf)}")
    if significant_lags_pacf:
        print("前10个显著滞后期:")
        for lag, value in significant_lags_pacf[:10]:
            cycle_type = ""
            if lag == 7:
                cycle_type = " (周循环) ⭐"
            elif lag in [30, 31]:
                cycle_type = " (月循环) ⭐"
            elif lag in [90, 91]:
                cycle_type = " (季度循环) ⭐"
            print(f"  滞后{lag}天: {value:.4f}{cycle_type}")
    
    # 检查特定周期的相关性
    print(f"\n【特定周期分析】")
    specific_lags = [1, 3, 7, 14, 30, 60, 90]
    
    for lag in specific_lags:
        if lag < len(acf_values):
            correlation = acf_values[lag]
            significance = "显著⭐" if abs(correlation) > conf_bound else "不显著"
            print(f"  滞后{lag}天ACF: {correlation:.4f} ({significance})")

def main():
    """
    主函数：执行完整的ACF/PACF分析
    """
    print("开始花叶类销量ACF/PACF周期性分析...")
    print("="*60)
    
    # 创建输出文件夹
    output_folder = create_output_folder()
    
    # 文件路径
    file_path = "花叶类.xlsx"  # 请确保文件在当前目录下
    
    # 1. 加载和准备数据
    sales_data = load_and_prepare_data(file_path)
    
    if sales_data is None:
        print("数据加载失败，分析终止。")
        return None
    
    # 2. 绘制原始时间序列
    print("\n1. 绘制原始时间序列图...")
    plot_time_series(sales_data, output_folder)
    
    # 3. 综合ACF/PACF分析
    print("\n2. 执行综合ACF/PACF分析...")
    analyze_acf_pacf_comprehensive(sales_data, output_folder)
    
    # 4. 周期性模式分析
    print("\n3. 执行周期性模式分析...")
    analyze_weekly_patterns(sales_data, output_folder)
    
    # 5. 数值化分析
    print("\n4. 执行数值化ACF/PACF分析...")
    numerical_acf_pacf_analysis(sales_data)
    
    print(f"\n分析完成！所有图表已保存到文件夹: {output_folder}")
    print("\n" + "="*60)
    print("📊 ACF/PACF 图表解读指南:")
    print("="*60)
    print("🔸 ACF图显示:")
    print("  - 在滞后7天处的峰值 → 表明存在周循环")
    print("  - 在滞后30天处的峰值 → 表明存在月循环")
    print("  - 缓慢衰减的ACF → 表明数据有趋势性")
    print("\n🔸 PACF图显示:")
    print("  - 滞后1天的显著值 → 短期依赖性")
    print("  - 滞后7天的显著值 → 周期性影响")
    print("  - 快速衰减到零 → 适合AR模型")
    print("\n🔸 置信区间:")
    print("  - 红色虚线为95%置信区间")
    print("  - 超出置信区间的值表示显著相关性")
    print("  - ⭐标记表示重要的周期性发现")
    
    return sales_data

# 运行分析
if __name__ == "__main__":
    sales_data = main()