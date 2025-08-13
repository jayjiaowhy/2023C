# import pandas as pd
#
# # 假设你已经将附件1和附件2保存为XLSX文件，文件名分别为 '附件1.xlsx' 和 '附件2.xlsx'
# # 如果文件格式不同，请相应修改 pd.read_excel 等
#
# # 加载附件1（商品信息）和附件2（销售流水明细）的数据
# df_goods_info = pd.read_excel('附件1.xlsx')
# df_sales_details = pd.read_excel('附件2.xlsx')
#
# # 确保用于合并的列名在两个数据框中完全一致，这里是'单品编码'
# # 如果不一致，可以使用 df.rename(columns={'旧列名': '新列名'}, inplace=True) 进行修改
# # 这里假设列名已经一致
#
# # 将两个数据框基于'单品编码'列进行合并
# # how='left' 表示以df_sales_details为主，保留其所有记录，并匹配df_goods_info中的信息
# merged_df = pd.merge(df_sales_details, df_goods_info, on='单品编码', how='left')
#
# # 将合并后的数据保存到一个新的XLSX文件，例如 'merged_data.xlsx'
# # index=False 避免将数据框的索引写入文件
# merged_df.to_excel('merged_data.xlsx', index=False)
#
# print("数据合并完成，并已保存到 'merged_data.xlsx' 文件中。")

# import pandas as pd
#
# # 读取合并后的数据文件
# try:
#     df = pd.read_excel('merged_data.xlsx')
# except FileNotFoundError:
#     print("错误：文件 'merged_data.xlsx' 不存在。请确保该文件位于当前工作目录下。")
#     exit()
#
# # 确保“销售日期”列是日期格式，并提取出日期部分（不包含时间）
# df['销售日期'] = pd.to_datetime(df['销售日期']).dt.date
#
# # 确保“销量(千克)”列是数值类型
# df['销量(千克)'] = pd.to_numeric(df['销量(千克)'])
#
# # 按天汇总单品销量
# # 分组键为“销售日期”和“单品编码”
# daily_sku_sales = df.groupby(['销售日期', '单品编码'])['销量(千克)'].sum().reset_index()
# print("按天汇总的单品销量（部分）：")
# print(daily_sku_sales.head())
#
# # 将结果保存到新的 Excel 文件
# daily_sku_sales.to_excel('daily_sku_sales.xlsx', index=False)
# print("\n单品日销量数据已保存到 'daily_sku_sales.xlsx'。")
#
# # 按天汇总品类销量
# # 分组键为“销售日期”和“分类名称”
# daily_category_sales = df.groupby(['销售日期', '分类名称'])['销量(千克)'].sum().reset_index()
# print("\n按天汇总的品类销量（部分）：")
# print(daily_category_sales.head())
#
# # 将结果保存到新的 Excel 文件
# daily_category_sales.to_excel('daily_category_sales.xlsx', index=False)
# print("\n品类日销量数据已保存到 'daily_category_sales.xlsx'。")
#
# print("\n所有汇总操作已完成。")
import pandas as pd

# 读取合并后的数据文件
try:
    df = pd.read_excel('merged_data.xlsx')
except FileNotFoundError:
    print("错误：文件 'merged_data.xlsx' 不存在。请确保该文件位于当前工作目录下。")
    exit()

# 确保“销售日期”列是日期格式，并提取出日期部分（不包含时间）
df['销售日期'] = pd.to_datetime(df['销售日期']).dt.date

# 确保“销量(千克)”列是数值类型
df['销量(千克)'] = pd.to_numeric(df['销量(千克)'])

# 按天汇总单品销量，分组键为“销售日期”和“单品名称”
daily_sku_sales = df.groupby(['销售日期', '单品名称'])['销量(千克)'].sum().reset_index()

print("按天汇总的单品销量（部分）：")
print(daily_sku_sales.head())

# 将结果保存到新的 Excel 文件
daily_sku_sales.to_excel('daily_sku_sales_by_name.xlsx', index=False)
print("\n单品日销量数据（按单品名称）已保存到 'daily_sku_sales_by_name.xlsx'。")