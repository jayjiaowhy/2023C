import pandas as pd
import re
import os

def clean_item_name(name):
    """
    清洗单品名称，去除括号及括号内的内容
    处理中英文括号：()（）
    """
    if pd.isna(name):
        return name
    # 转换为字符串并去除各种括号及其内容
    cleaned = re.sub(r'[\(（][^)）]*[\)）]', '', str(name))
    # 去除首尾空格
    return cleaned.strip()

def get_representative_samples():
    """
    完整的代表性样本筛选流程
    """
    # 文件路径
    merged_file = r"D:\ObsidianLearning\数模\2023C\merged_data.xlsx"
    original_file = r"D:\ObsidianLearning\数模\2023C\cleaned_daily_sku_sales_cleaned.xlsx"
    
    print("="*60)
    print("开始蔬菜销售代表性样本筛选分析")
    print("="*60)
    
    # =====================
    # 第一步：读取数据并进行分组聚合
    # =====================
    print("\n【第一步】读取数据并进行分组聚合...")
    
    try:
        # 读取合并后的数据
        df_merged = pd.read_excel(merged_file)
        print(f"成功读取文件: {merged_file}")
        print(f"原始数据形状: {df_merged.shape}")
        print(f"原始列名: {df_merged.columns.tolist()}")
        
        # 显示原始数据的前几行
        print("\n原始数据示例（前5行）:")
        print(df_merged.head())
        
    except Exception as e:
        print(f"读取文件出错: {e}")
        return None
    
    # 清洗单品名称
    print("\n清洗单品名称（去除括号及内容）...")
    df_merged['单品名称_清洗后'] = df_merged['单品名称'].apply(clean_item_name)
    
    # 显示清洗效果示例
    print("\n单品名称清洗示例:")
    sample_items = df_merged[df_merged['单品名称'].str.contains(r'[\(（]', na=False)].head(10)
    if not sample_items.empty:
        for _, row in sample_items.iterrows():
            print(f"  原始: {row['单品名称']} -> 清洗后: {row['单品名称_清洗后']}")
    
    # 按分类名称和清洗后的单品名称分组，对销量求和
    print("\n进行分组聚合...")
    grouped_sales = df_merged.groupby(['分类名称', '单品名称_清洗后'])['销量(千克)'].sum().reset_index()
    grouped_sales.rename(columns={'销量(千克)': '累计总销量(千克)'}, inplace=True)
    
    print(f"聚合后数据形状: {grouped_sales.shape}")
    print("\n聚合后数据示例（前10行）:")
    print(grouped_sales.head(10))
    
    # =====================
    # 第二步：在每个品类内部按总销量降序排序
    # =====================
    print("\n【第二步】在每个品类内部按总销量降序排序...")
    
    # 先按分类名称升序，再按累计总销量降序
    sorted_sales = grouped_sales.sort_values(
        by=['分类名称', '累计总销量(千克)'], 
        ascending=[True, False]
    )
    
    # 显示每个品类的销量分布
    print("\n各品类销量统计:")
    category_stats = sorted_sales.groupby('分类名称')['累计总销量(千克)'].agg([
        ('单品数量', 'count'),
        ('总销量', 'sum'),
        ('平均销量', 'mean'),
        ('最大销量', 'max'),
        ('最小销量', 'min')
    ]).round(2)
    print(category_stats)
    
    # =====================
    # 第三步：从每个品类中选出前3名（但题目要求每个品类2个，共12个）
    # =====================
    print("\n【第三步】从每个品类中选出销量前2名...")
    
    # 根据题目要求，选择每个品类的前2名（6个品类 × 2个单品 = 12个）
    top_n_per_category = 2
    representative_samples = sorted_sales.groupby('分类名称').head(top_n_per_category)
    
    print(f"\n代表性样本池（每个品类前{top_n_per_category}名）:")
    print("="*60)
    
    # 按品类显示代表性样本
    for category in representative_samples['分类名称'].unique():
        category_samples = representative_samples[representative_samples['分类名称'] == category]
        print(f"\n{category}:")
        for idx, row in category_samples.iterrows():
            print(f"  {row['单品名称_清洗后']}: {row['累计总销量(千克)']:.2f} 千克")
    
    # 保存代表性样本列表
    representative_items = representative_samples['单品名称_清洗后'].tolist()
    print(f"\n共选出 {len(representative_items)} 个代表性单品")
    
    # 保存中间结果
    representative_samples.to_excel(
        r"D:\ObsidianLearning\数模\2023C\representative_samples_summary.xlsx", 
        index=False
    )
    print("\n代表性样本汇总已保存至: representative_samples_summary.xlsx")
    
    # =====================
    # 第四步：从原始日销售数据中筛选代表性样本
    # =====================
    print("\n【第四步】从原始日销售数据中筛选代表性样本...")
    
    try:
        # 读取原始日销售数据
        df_original = pd.read_excel(original_file)
        print(f"\n成功读取原始数据文件: {original_file}")
        print(f"原始日销售数据形状: {df_original.shape}")
        
        # 清洗原始数据中的单品名称
        df_original['单品名称_清洗后'] = df_original['单品名称'].apply(clean_item_name)
        
        # 筛选出代表性样本的数据
        print("\n筛选代表性样本数据...")
        final_data = df_original[df_original['单品名称_清洗后'].isin(representative_items)].copy()
        
        print(f"筛选后数据形状: {final_data.shape}")
        
        # 验证筛选结果
        print("\n筛选结果验证:")
        selected_items = final_data['单品名称_清洗后'].unique()
        print(f"实际筛选出的单品数: {len(selected_items)}")
        
        # 检查是否所有代表性单品都找到了数据
        missing_items = set(representative_items) - set(selected_items)
        if missing_items:
            print(f"警告：以下代表性单品在原始数据中未找到: {missing_items}")
        
        # 显示每个代表性单品的记录数
        print("\n每个代表性单品的记录数:")
        item_counts = final_data.groupby('单品名称_清洗后').size().sort_values(ascending=False)
        for item, count in item_counts.items():
            print(f"  {item}: {count} 条记录")
        
        # 保存最终结果
        output_file = r"D:\ObsidianLearning\数模\2023C\representative_daily_sales_final.xlsx"
        final_data.to_excel(output_file, index=False)
        print(f"\n最终数据已保存至: {output_file}")
        
        # 生成分析报告
        generate_analysis_report(final_data, representative_samples)
        
        return final_data
        
    except Exception as e:
        print(f"处理原始数据时出错: {e}")
        print("请检查原始数据文件路径是否正确")
        return None

def generate_analysis_report(final_data, representative_samples):
    """
    生成分析报告
    """
    print("\n" + "="*60)
    print("数据分析报告")
    print("="*60)
    
    # 时间范围
    if '销售日期' in final_data.columns:
        date_range = f"{final_data['销售日期'].min()} 至 {final_data['销售日期'].max()}"
        print(f"\n数据时间范围: {date_range}")
    
    # 数据概览
    print(f"\n数据概览:")
    print(f"  总记录数: {len(final_data)}")
    print(f"  代表性单品数: {final_data['单品名称_清洗后'].nunique()}")
    print(f"  涵盖品类数: {final_data['分类名称'].nunique()}")
    
    # 销量统计
    if '销量(千克)' in final_data.columns:
        total_sales = final_data['销量(千克)'].sum()
        avg_daily_sales = final_data['销量(千克)'].mean()
        print(f"\n销量统计:")
        print(f"  总销量: {total_sales:.2f} 千克")
        print(f"  日均销量: {avg_daily_sales:.2f} 千克")
    
    # 各品类代表性单品清单
    print("\n各品类代表性单品清单:")
    for category in representative_samples['分类名称'].unique():
        items = representative_samples[representative_samples['分类名称'] == category]['单品名称_清洗后'].tolist()
        print(f"  {category}: {', '.join(items)}")
    
    print("\n" + "="*60)
    print("分析完成！")
    print("="*60)

def check_files():
    """
    检查所需文件是否存在
    """
    files_to_check = [
        r"D:\ObsidianLearning\数模\2023C\merged_data.xlsx",
        r"D:\ObsidianLearning\数模\2023C\cleaned_daily_sku_sales_cleaned.xlsx"
    ]
    
    print("检查文件是否存在:")
    all_exist = True
    for file in files_to_check:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (文件不存在)")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    # 检查文件
    print("开始执行代表性样本筛选程序")
    print("-"*60)
    
    if check_files():
        print("\n所有文件检查通过，开始处理数据...\n")
        result = get_representative_samples()
        
        if result is not None:
            print("\n程序执行成功！")
            print("生成的文件:")
            print("  1. representative_samples_summary.xlsx - 代表性样本汇总")
            print("  2. representative_daily_sales_final.xlsx - 代表性样本的完整日销售数据")
    else:
        print("\n请确保所有必需文件都存在后再运行程序。")