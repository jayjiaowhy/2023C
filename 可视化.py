import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import numpy as np

def generate_sales_heatmaps():
    """
    从 daily_category_sales.xlsx 数据生成各品类销量热力图。
    热力图展示了不同月份和星期几的平均日销量。
    """
    # --- 1. 数据加载和准备 ---
    file_path = 'daily_category_sales.xlsx'
    if not os.path.exists(file_path):
        print(f"错误：找不到文件 '{file_path}'。请确保文件在当前目录中。")
        return

    df = pd.read_excel(file_path)

    # --- 2. 数据预处理 ---
    # 将销售日期列转换为日期时间格式
    df['销售日期'] = pd.to_datetime(df['销售日期'])
    # 提取月份 (1-12)
    df['月份'] = df['销售日期'].dt.month
    # 提取星期几 (0=星期一, 6=星期日)
    df['星期几'] = df['销售日期'].dt.dayofweek

    # --- 3. 设置可视化环境 ---
    # 配置字体以支持中文显示
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

    # 获取所有独特的分类名称
    categories = df['分类名称'].unique()

    # --- 4. 为每个分类生成并保存热力图 ---
    for category in categories:
        print(f"正在为品类 '{category}' 生成热力图...")

        # 筛选特定品类的数据
        df_category = df[df['分类名称'] == category]

        # 创建数据透视表：索引为月份，列为星期几，值为日销量的平均值
        try:
            pivot_table = df_category.pivot_table(
                values='销量(千克)',
                index='月份',
                columns='星期几',
                aggfunc='mean'
            )
            # 确保星期几的顺序是从0到6
            pivot_table = pivot_table.reindex(columns=range(7))
        except Exception as e:
            print(f"为品类 '{category}' 创建数据透视表时出错: {e}")
            continue

        # --- 5. 可视化 ---
        plt.figure(figsize=(12, 8))
        
        # 计算数据的动态范围以优化色阶
        # 使用 np.nanmin 和 np.nanmax 来处理可能的NaN值
        vmin = np.nanmin(pivot_table.values)
        vmax = np.nanmax(pivot_table.values)

        # 使用seaborn创建热力图
        ax = sns.heatmap(
            pivot_table,
            annot=True,          # 在单元格上标注数值
            fmt=".1f",           # 数值格式，保留一位小数
            linewidths=.5,       # 单元格之间的分隔线宽度
            cmap='coolwarm',     # 使用'coolwarm'色阶
            vmin=vmin,           # 设置色阶的最小值
            vmax=vmax,           # 设置色阶的最大值
            cbar_kws={'label': '平均销量 (千克)'} # 色阶条标签
        )

        # 设置标题和坐标轴标签
        ax.set_title(f'{category} 月份与星期几日销量热力图', fontsize=18)
        ax.set_xlabel('星期几', fontsize=12)
        ax.set_ylabel('月份', fontsize=12)

        # 自定义坐标轴刻度标签
        ax.set_xticklabels(['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'], rotation=0)
        # 获取存在的月份并生成标签
        y_labels = [f'{month}月' for month in pivot_table.index]
        ax.set_yticklabels(y_labels, rotation=0)

        # --- 6. 输出 ---
        # 定义输出文件名并保存为高质量PNG
        output_filename = f'{category}_热力图.png'
        try:
            plt.savefig(output_filename, dpi=300, bbox_inches='tight')
            print(f"已成功保存热力图: {output_filename}")
        except Exception as e:
            print(f"保存文件 '{output_filename}' 时出错: {e}")
        
        plt.close() # 关闭当前图表以释放内存

    print("\n所有品类的热力图已生成完毕。")

if __name__ == '__main__':
    generate_sales_heatmaps()