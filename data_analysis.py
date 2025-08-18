import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# 设置中文字体,以正确显示图表中的中文标签
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建保存图片的文件夹
def create_output_folder(folder_name="销售数据分析图表"):
    """创建输出文件夹"""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"已创建文件夹: {folder_name}")
    return folder_name

# 定义高对比度颜色列表
HIGH_CONTRAST_COLORS = [
    '#FF0000',  # 红色
    '#0000FF',  # 蓝色  
    '#00FF00',  # 绿色
    '#FF00FF',  # 紫色
    '#FFA500',  # 橙色
    '#00FFFF',  # 青色
    '#800080',  # 深紫色
    '#008000',  # 深绿色
    '#800000',  # 深红色
    '#000080',  # 深蓝色
    '#808000',  # 橄榄色
    '#FF1493',  # 深粉色
    '#32CD32',  # 酸橙绿
    '#FFD700',  # 金色
    '#DC143C',  # 深红
    '#4169E1'   # 宝蓝色
]

def analyze_sales_data(file_path, group_by_column, value_column='销量(千克)', date_column='销售日期', output_folder="销售数据分析图表"):
    """
    加载销售数据,计算核心统计量,并绘制时间序列分布图。
     
    参数:
    - file_path (str): Excel文件的路径。
    - group_by_column (str): 用于分组的列名(例如 '分类名称' 或 '单品名称')。
    - value_column (str): 需要分析的数值列名。
    - date_column (str): 销售日期列名。
    - output_folder (str): 保存图片的文件夹名称。
    """
    # --- 1. 加载数据 ---
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        print(f"错误:文件未找到 -> {file_path}")
        return
    except Exception as e:
        print(f"错误:读取文件失败 -> {e}")
        return
 
    print(f"\n--- 正在分析文件: {file_path.split('/')[-1]} ---")
    print(f"数据按 '{group_by_column}' 分组进行分析。")
    print(f"数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
 
    # 检查必要的列是否存在
    if group_by_column not in df.columns:
        print(f"错误: 列 '{group_by_column}' 不存在于数据中")
        return
    if value_column not in df.columns:
        print(f"错误: 列 '{value_column}' 不存在于数据中")
        return
    if date_column not in df.columns:
        print(f"错误: 列 '{date_column}' 不存在于数据中")
        return
    
    # 转换销售日期列为datetime格式
    try:
        df[date_column] = pd.to_datetime(df[date_column])
    except Exception as e:
        print(f"销售日期转换错误: {e}")
        return
    
    # 按销售日期排序
    df = df.sort_values(date_column)
 
    # --- 2. 计算核心统计量 ---
    # 使用 agg 一次性计算均值、中位数和标准差
    core_stats = df.groupby(group_by_column)[value_column].agg(['mean', 'median', 'std']).round(2)
    
    # 重命名列以便更好地显示
    core_stats.columns = ['均值', '中位数', '标准差']
 
    print("\n核心统计量:")
    print("=" * 50)
    print(core_stats.to_string())
    print("=" * 50)
 
    # --- 3. 绘制时间序列分布图形 ---
    # 获取所有唯一的品类/单品名称
    unique_items = df[group_by_column].unique()
    num_items = len(unique_items)
 
    # 根据项目数量设置网格布局
    if num_items <= 0:
        print("没有数据可供绘制")
        return
    elif num_items == 1:
        rows, cols = 1, 1
    elif num_items <= 2:
        rows, cols = 1, 2
    elif num_items <= 3:
        rows, cols = 1, 3
    elif num_items <= 4:
        rows, cols = 2, 2
    elif num_items <= 6:
        rows, cols = 2, 3
    elif num_items <= 9:
        rows, cols = 3, 3
    elif num_items <= 12:
        rows, cols = 3, 4
    else:
        rows, cols = 4, 4  # 最多显示16个子图
        
    # 创建子图
    fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
    
    # 如果只有一个子图,确保axes是数组格式
    if num_items == 1:
        axes = [axes]
    elif rows == 1 or cols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    # 为每个品类/单品绘制时间序列图
    for i, item in enumerate(unique_items):
        if i >= len(axes):
            break
            
        # 筛选当前品类/单品的数据
        item_data = df[df[group_by_column] == item].copy()
        
        if len(item_data) == 0:
            axes[i].text(0.5, 0.5, '无数据', ha='center', va='center', transform=axes[i].transAxes)
            axes[i].set_title(f'{item}\n(无数据)')
            continue
        
        # 按日期分组，计算每日销量（如果同一天有多条记录）
        daily_sales = item_data.groupby(date_column)[value_column].sum().reset_index()
        
        # 使用高对比度颜色
        line_color = HIGH_CONTRAST_COLORS[i % len(HIGH_CONTRAST_COLORS)]
        
        # 绘制时间序列线图
        axes[i].plot(daily_sales[date_column], daily_sales[value_column], 
                    marker='o', markersize=3, linewidth=2, alpha=0.8, color=line_color)
        
        # 添加趋势线（移动平均）
        if len(daily_sales) >= 7:
            window_size = min(7, len(daily_sales)//3)  # 7天移动平均或数据量的1/3
            moving_avg = daily_sales[value_column].rolling(window=window_size, center=True).mean()
            axes[i].plot(daily_sales[date_column], moving_avg, 
                        color='black', linewidth=3, alpha=0.8, 
                        label=f'{window_size}日移动平均', linestyle='--')
            axes[i].legend()
        
        # 设置标题和标签
        mean_val = daily_sales[value_column].mean()
        std_val = daily_sales[value_column].std()
        axes[i].set_title(f'{item}\n均值: {mean_val:.2f}, 标准差: {std_val:.2f}', fontsize=10, fontweight='bold')
        axes[i].set_xlabel('销售日期')
        axes[i].set_ylabel(f'{value_column}')
        axes[i].grid(True, alpha=0.3)
        
        # 旋转x轴标签以避免重叠
        axes[i].tick_params(axis='x', rotation=45)
        
        # 设置y轴从0开始（如果所有值都是正数）
        if daily_sales[value_column].min() >= 0:
            axes[i].set_ylim(bottom=0)
    
    # 隐藏多余的子图
    for i in range(num_items, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    plt.suptitle(f'{file_path.split("/")[-1].split(".")[0]} - 销量时间序列分布', 
                 fontsize=16, y=1.02)
    
    # 保存个体时间序列图
    filename1 = f"{group_by_column}_个体时间序列图.png"
    filepath1 = os.path.join(output_folder, filename1)
    plt.savefig(filepath1, dpi=300, bbox_inches='tight')
    print(f"已保存: {filepath1}")
    
    plt.show()
    
    # --- 4. 绘制所有品类/单品的对比时间序列图 ---
    plt.figure(figsize=(15, 8))
    
    for i, item in enumerate(unique_items):
        item_data = df[df[group_by_column] == item].copy()
        if len(item_data) == 0:
            continue
            
        # 按日期分组，计算每日销量
        daily_sales = item_data.groupby(date_column)[value_column].sum().reset_index()
        
        # 使用高对比度颜色
        line_color = HIGH_CONTRAST_COLORS[i % len(HIGH_CONTRAST_COLORS)]
        
        # 绘制时间序列线图
        plt.plot(daily_sales[date_column], daily_sales[value_column], 
                marker='o', markersize=3, linewidth=2.5, alpha=0.8, 
                color=line_color, label=item)
    
    plt.title(f'所有{group_by_column}销量时间序列对比', fontsize=16, fontweight='bold')
    plt.xlabel('销售日期', fontsize=12)
    plt.ylabel(f'{value_column}', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 保存对比时间序列图
    filename2 = f"{group_by_column}_对比时间序列图.png"
    filepath2 = os.path.join(output_folder, filename2)
    plt.savefig(filepath2, dpi=300, bbox_inches='tight')
    print(f"已保存: {filepath2}")
    
    plt.show()
    
    return core_stats

def analyze_seasonal_patterns(df, group_by_column, value_column='销量(千克)', date_column='销售日期', output_folder="销售数据分析图表"):
    """
    分析季节性模式（按月份、星期几等）
    """
    print(f"\n--- 季节性模式分析 ---")
    
    # 确保销售日期列是datetime格式
    df[date_column] = pd.to_datetime(df[date_column])
    
    # 添加时间特征
    df['月份'] = df[date_column].dt.month
    df['星期几'] = df[date_column].dt.dayofweek  # 0=周一, 6=周日
    df['星期几名称'] = df[date_column].dt.day_name()
    
    # 按月份分析
    plt.figure(figsize=(16, 12))
    
    # 子图1: 按月份的销量分布
    plt.subplot(2, 2, 1)
    monthly_stats = df.groupby(['月份', group_by_column])[value_column].sum().unstack()
    
    # 使用高对比度颜色
    colors_for_plot = HIGH_CONTRAST_COLORS[:len(monthly_stats.columns)]
    monthly_stats.plot(kind='bar', ax=plt.gca(), color=colors_for_plot, width=0.8)
    plt.title('各月份销量分布', fontsize=14, fontweight='bold')
    plt.xlabel('月份')
    plt.ylabel(f'{value_column}')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=0)
    plt.grid(True, alpha=0.3)
    
    # 子图2: 按星期几的销量分布
    plt.subplot(2, 2, 2)
    weekly_stats = df.groupby(['星期几', group_by_column])[value_column].sum().unstack()
    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekly_stats.index = [weekday_names[i] for i in weekly_stats.index]
    weekly_stats.plot(kind='bar', ax=plt.gca(), color=colors_for_plot, width=0.8)
    plt.title('各星期销量分布', fontsize=14, fontweight='bold')
    plt.xlabel('星期')
    plt.ylabel(f'{value_column}')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 子图3: 热力图 - 月份vs品类
    plt.subplot(2, 2, 3)
    monthly_heatmap = df.groupby(['月份', group_by_column])[value_column].sum().unstack()
    sns.heatmap(monthly_heatmap.T, annot=True, fmt='.0f', cmap='RdYlBu_r', cbar_kws={'shrink': 0.8})
    plt.title('月份-品类销量热力图', fontsize=14, fontweight='bold')
    plt.ylabel(group_by_column)
    
    # 子图4: 热力图 - 星期vs品类
    plt.subplot(2, 2, 4)
    weekly_heatmap = df.groupby(['星期几', group_by_column])[value_column].sum().unstack()
    weekly_heatmap.index = [weekday_names[i] for i in weekly_heatmap.index]
    sns.heatmap(weekly_heatmap.T, annot=True, fmt='.0f', cmap='RdYlBu_r', cbar_kws={'shrink': 0.8})
    plt.title('星期-品类销量热力图', fontsize=14, fontweight='bold')
    plt.ylabel(group_by_column)
    
    plt.tight_layout()
    
    # 保存季节性分析图
    filename3 = f"{group_by_column}_季节性模式分析.png"
    filepath3 = os.path.join(output_folder, filename3)
    plt.savefig(filepath3, dpi=300, bbox_inches='tight')
    print(f"已保存: {filepath3}")
    
    plt.show()

def main():
    """
    主函数：分析两个Excel文件
    """
    print("开始销售数据时间序列分析...")
    print("=" * 60)
    
    # 创建输出文件夹
    output_folder = create_output_folder()
    
    # 文件路径
    file1_path = r"D:\ObsidianLearning\数模\2023C\daily_category_sales.xlsx"
    file2_path = r"D:\ObsidianLearning\数模\2023C\representative_daily_sales_final.xlsx"
    
    # 分析品类销售数据
    print("\n1. 分析品类销售数据")
    stats1 = analyze_sales_data(file1_path, '分类名称', '销量(千克)', output_folder=output_folder)
    
    # 如果第一个文件分析成功，进行季节性分析
    if stats1 is not None:
        try:
            df1 = pd.read_excel(file1_path)
            analyze_seasonal_patterns(df1, '分类名称', '销量(千克)', output_folder=output_folder)
        except Exception as e:
            print(f"季节性分析错误: {e}")
    
    # 分析代表性单品销售数据
    print("\n" + "="*60)
    print("\n2. 分析代表性单品销售数据")
    stats2 = analyze_sales_data(file2_path, '单品名称', '销量(千克)', output_folder=output_folder)
    
    # 如果第二个文件分析成功，进行季节性分析
    if stats2 is not None:
        try:
            df2 = pd.read_excel(file2_path)
            analyze_seasonal_patterns(df2, '单品名称', '销量(千克)', output_folder=output_folder)
        except Exception as e:
            print(f"季节性分析错误: {e}")
    
    print(f"\n分析完成！所有图表已保存到文件夹: {output_folder}")
    
    return stats1, stats2

# 如果直接运行此脚本，执行主函数
if __name__ == "__main__":
    category_stats, product_stats = main()