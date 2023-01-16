from pyecharts import Bar

# 创建 Bar 实例
bar = Bar()

# 添加数据，x 轴为省份名称，y 轴为销售额（单位：万元）
bar.add("销售额", ["北京", "上海", "广州", "深圳", "成都", "杭州"], [55, 66, 77, 88, 99, 110])

# 渲染图表
bar.render()
