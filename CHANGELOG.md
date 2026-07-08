# 修改记录

本文件记录由 AI 协助完成的功能修改，方便追踪改动来源和内容。

## 2026-07-08 [Kiro]

新增科目和公司维度的对比与排名能力，对应用户提出的四个功能确认问题：

1. **单位内部科目对比支持多选公司**（`app_parts/part_05.pyfrag` 扣分项页新增"单位与科目对比范围"筛选区）
   - 新增 `st.multiselect` 公司筛选（可留空表示全部，也可勾选一家或多家公司）。
   - "单位内部科目对比"图表随选择的公司范围联动，展示所选公司内部各科目的失分对比。

2. **科目跨单位对比支持多选科目**（同一筛选区）
   - 新增 `st.multiselect` 科目筛选（可留空表示全部，也可勾选一个或多个科目）。
   - "科目跨单位对比"图表随选择的科目范围联动，展示所选科目在各单位之间的失分对比。

3. **科目失分排名（失分最多的科目）**（`app_parts/part_05.pyfrag` 新增"科目失分排名"卡片）
   - 新增 `boeing_eval/analysis.py` 中的 `subject_loss_ranking()` 函数：按科目总失分排序，支持 `top_n` 截断。
   - 页面提供下拉选择显示前 3 / 5 / 10 个科目或全部，默认显示失分最多的前 3 个科目。

4. **失分最多科目内部的失分项下钻**（`app_parts/part_05.pyfrag` 新增"失分最多科目的失分项下钻"卡片）
   - 新增 `boeing_eval/analysis.py` 中的 `top_subject_item_loss()` 函数：先取失分最多的前 N 个科目，再在这些科目范围内取失分最多的前 M 个具体失分项。
   - 页面提供下拉选择科目数量（3/5）和每个科目显示的失分项数量（3/5），默认失分最多的 3 个科目、每个科目显示 3 个失分项。

### 涉及文件

- `boeing_eval/analysis.py`：新增 `subject_loss_ranking()`、`top_subject_item_loss()`；`filter_data()` 的 `company` 参数扩展为同时支持单个公司字符串和公司列表（多选）。
- `app_parts/part_00.pyfrag`：补充新函数的导入。
- `app_parts/part_05.pyfrag`：扣分项页新增公司/科目多选筛选区、科目失分排名卡片、科目失分项两级下钻卡片。
- `tests/test_analysis.py`：新增单元测试，覆盖科目排名排序、TopN 截断、两级下钻范围限定，以及 `filter_data` 对公司列表和单个公司字符串两种输入的兼容性。

### 验证方式

- `python3 -m unittest discover -s tests -p 'test_*.py'` 全部通过（含新增的 `test_analysis.py`）。
- `app_parts/part_*.pyfrag` 拼接后 `compile()` 检查通过。
- 使用 `streamlit.testing.v1.AppTest` 在无界面模式下加载真实样表（上航/东航/厦航 B737 + 江西航复飞专项检查表），验证新增的多选筛选、科目排名下拉、下钻下拉均可正常交互且不抛出异常。

### 已知范围

- 未修改解析层格式兼容口径，双盲测试表和复飞专项检查表的识别规则不受影响。
- 未改动报告导出（HTML/Word/CSV/Excel）内容结构。
