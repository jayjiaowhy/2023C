import pandas as pd
import re

# 读取Excel文件
file_path = 'D:\\ObsidianLearning\\数模\\2023C\\daily_sku_sales_by_name.xlsx'
df = pd.read_excel(file_path)

# 1. 将“销售日期”列转换为标准的日期时间格式
df['销售日期'] = pd.to_datetime(df['销售日期'], errors='coerce')

# 2. 清理“单品名称”列
def clean_sku_name(name):
    if isinstance(name, str):
        return re.sub(r'[\(（].*?[\)）]', '', name).strip()
    return name

df['单品名称'] = df['单品名称'].apply(clean_sku_name)

# 3. 填充“销量(千克)”字段的空值和负数
# 首先用0填充NaN值
df['销量(千克)'] = df['销量(千克)'].fillna(0)
# 然后将负数替换为0
df.loc[df['销量(千克)'] < 0, '销量(千克)'] = 0

# 可选：按日期和清理后的单品名称合并，并加总销量
# 如果需要合并相同单品在同一天的销量，可以取消下面的代码注释
# df = df.groupby(['销售日期', '单品名称'])['销量(千克)'].sum().reset_index()


# 保存清理后的数据到新文件
output_path = 'cleaned_daily_sku_sales.xlsx'
df.to_excel(output_path, index=False)

print(f"数据清洗完成，已保存至 {output_path}")