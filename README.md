# LegalExtract

湖北法律文书内容格式化提取

## 环境配置

```python
# flashtext 大规模文本搜索
from flashtext import KeywordProcessor
```

## 主函数/get_content
提取结果:
```
l_num: 鄂武昌民速字第00030号
l_court_name: 湖北武汉市武昌区人民法院
l_court_type: 民事判决书
l_date: 2015年9月21日
l_dispute: 借款合同纠纷
l_accuser: 原告(张三)
l_accused: 被告(老王)
l_content: 一、冻结或者查封被告黄冈商业步行街****有限公司银行存款***元或者相等
价值的其他财产。二、冻结担保人***名下位于黄州区西湖二路与青砖湖路交界处鼎立
华庭商铺幢*层*号商铺（权证号：黄冈市房预黄州区字第Y038194）
```