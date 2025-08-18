import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def remove_outliers_by_group(df, group_col, value_col):
    """
    一个简便的函数，用于按分组去除数据中的异常值。
    它会为每个组（如每个品类或每个单品）计算IQR边界，
    并移除超出边界的数据点。

    参数:
    df (pd.DataFrame): 包含数据的DataFrame。
    group_col (str): 用于分组的列名 (例如 '分类名称' 或 '单品名称')。
    value_col (str): 需要检测异常值的数值列名 (例如 '销量(千克)')。

    返回:
    pd.DataFrame: 一个已经剔除了异常值的新DataFrame。
    """
    print(f"开始处理文件中的 '{group_col}'...")
    print(f"原始数据行数: {len(df)}")
    
    Q1 = df.groupby(group_col)[value_col].transform('quantile', 0.25)
    Q3 = df.groupby(group_col)[value_col].transform('quantile', 0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    is_inlier = df[value_col].between(lower_bound, upper_bound)
    df_cleaned = df[is_inlier]

    print(f"处理后数据行数: {len(df_cleaned)}")
    print(f"剔除了 {len(df) - len(df_cleaned)} 个异常值。\n")

    return df_cleaned

# --- 第二步：读取并处理文件 ---

# 导入库
import pandas as pd

# 读取文件
try:
    df_sku = pd.read_excel('cleaned_daily_sku_sales.xlsx')
    df_category = pd.read_excel('daily_category_sales.xlsx')
    
    # 确保日期列是datetime类型
    df_sku['销售日期'] = pd.to_datetime(df_sku['销售日期'])
    df_category['销售日期'] = pd.to_datetime(df_category['销售日期'])

    # 应用函数
    df_category_cleaned = remove_outliers_by_group(df_category, '分类名称', '销量(千克)')
    df_sku_cleaned = remove_outliers_by_group(df_sku, '单品名称', '销量(千克)')

    # 保存结果
    df_category_cleaned.to_excel('daily_category_sales_cleaned.xlsx', index=False)
    df_sku_cleaned.to_excel('cleaned_daily_sku_sales_cleaned.xlsx', index=False)

    print("处理完成，两个清洗后的文件已保存至脚本所在目录。")

    # --- 可视化部分 ---

    # 找出总销量最大的品类
    total_sales_category = df_category.groupby('分类名称')['销量(千克)'].sum().idxmax()
    print(f"总销量最大的品类是: {total_sales_category}")

    # 找出总销量最大的单品
    total_sales_sku = df_sku.groupby('单品名称')['销量(千克)'].sum().idxmax()
    print(f"总销量最大的单品是: {total_sales_sku}")

    # 筛选最大品类和单品的数据
    df_max_category_orig = df_category[df_category['分类名称'] == total_sales_category]
    df_max_category_cleaned = df_category_cleaned[df_category_cleaned['分类名称'] == total_sales_category]
    
    df_max_sku_orig = df_sku[df_sku['单品名称'] == total_sales_sku]
    df_max_sku_cleaned = df_sku_cleaned[df_sku_cleaned['单品名称'] == total_sales_sku]

    # --- 为最大品类生成图表 ---

    # 1. 品类 - 处理前日销量箱线图
    plt.figure(figsize=(10, 6))
    plt.boxplot(df_max_category_orig['销量(千克)'])
    plt.title(f'品类 "{total_sales_category}" 处理前日销量箱线图')
    plt.ylabel('销量(千克)')
    plt.xticks([1], [total_sales_category])
    plt.grid(True)
    plt.savefig(f'{total_sales_category}_before_boxplot.png')
    plt.show()
    print(f'图表 "{total_sales_category}_before_boxplot.png" 已保存。')

    # 2. 品类 - 数据预处理前后周销量时间序列对比图
    weekly_sales_category_orig = df_max_category_orig.set_index('销售日期').resample('W')['销量(千克)'].sum()
    weekly_sales_category_cleaned = df_max_category_cleaned.set_index('销售日期').resample('W')['销量(千克)'].sum()

    plt.figure(figsize=(15, 7))
    plt.plot(weekly_sales_category_orig.index, weekly_sales_category_orig.values, marker='o', linestyle='-', label='处理前')
    plt.plot(weekly_sales_category_cleaned.index, weekly_sales_category_cleaned.values, marker='x', linestyle='--', label='处理后')
    plt.title(f'品类 "{total_sales_category}" 数据预处理前后周销量对比')
    plt.xlabel('日期')
    plt.ylabel('周销量(千克)')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'{total_sales_category}_weekly_sales_comparison.png')
    plt.show()
    print(f'图表 "{total_sales_category}_weekly_sales_comparison.png" 已保存。')

    # --- 为最大单品生成图表 ---

    # 3. 单品 - 处理前日销量箱线图
    plt.figure(figsize=(10, 6))
    plt.boxplot(df_max_sku_orig['销量(千克)'])
    plt.title(f'单品 "{total_sales_sku}" 处理前日销量箱线图')
    plt.ylabel('销量(千克)')
    plt.xticks([1], [total_sales_sku])
    plt.grid(True)
    plt.savefig(f'{total_sales_sku}_before_boxplot.png')
    plt.show()
    print(f'图表 "{total_sales_sku}_before_boxplot.png" 已保存。')

    # 4. 单品 - 数据预处理前后周销量时间序列对比图
    weekly_sales_sku_orig = df_max_sku_orig.set_index('销售日期').resample('W')['销量(千克)'].sum()
    weekly_sales_sku_cleaned = df_max_sku_cleaned.set_index('销售日期').resample('W')['销量(千克)'].sum()

    plt.figure(figsize=(15, 7))
    plt.plot(weekly_sales_sku_orig.index, weekly_sales_sku_orig.values, marker='o', linestyle='-', label='处理前')
    plt.plot(weekly_sales_sku_cleaned.index, weekly_sales_sku_cleaned.values, marker='x', linestyle='--', label='处理后')
    plt.title(f'单品 "{total_sales_sku}" 数据预处理前后周销量对比')
    plt.xlabel('日期')
    plt.ylabel('周销量(千克)')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'{total_sales_sku}_weekly_sales_comparison.png')
    plt.show()
    print(f'图表 "{total_sales_sku}_weekly_sales_comparison.png" 已保存。')


except FileNotFoundError as e:
    print(f"错误: {e}。请确保文件路径正确并且文件存在于当前目录。")
