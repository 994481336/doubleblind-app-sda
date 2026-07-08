# 系统修改与部署手册

这份文档面向后续接手的开发者或 AI，目标是让你可以直接在这台电脑上修改、验证并部署这个 Streamlit 应用。

## 1. 项目定位

这是一个基于 Streamlit 的飞行员双盲测试/复飞专项评估分析平台。

它的工作方式是：

1. 上传 Excel 数据。
2. 解析固定格式台账。
3. 聚合人员得分、扣分项、单位统计、简报素材。
4. 在当前会话内导出 HTML、Word、CSV、Excel 报告。

它不保存上传文件或分析历史。

## 2. 关键文件

- [eastchina_doubleblindtestA.py](/Users/seok/Desktop/doubleblindtest/eastchina_doubleblindtestA.py): 启动入口，只负责把 `app_parts/part_*.pyfrag` 拼接后执行。
- [app_parts/part_00.pyfrag](/Users/seok/Desktop/doubleblindtest/app_parts/part_00.pyfrag): 主题样式、公共函数、图表组件、部分回退逻辑。
- [app_parts/part_03.pyfrag](/Users/seok/Desktop/doubleblindtest/app_parts/part_03.pyfrag): 质量检查、图表渲染、通用展示组件。
- [app_parts/part_04.pyfrag](/Users/seok/Desktop/doubleblindtest/app_parts/part_04.pyfrag): 上传、筛选、总览和数据预处理。
- [app_parts/part_05.pyfrag](/Users/seok/Desktop/doubleblindtest/app_parts/part_05.pyfrag): 扣分项、个人明细、报告输出、简报素材页。
- [boeing_eval/parsers.py](/Users/seok/Desktop/doubleblindtest/boeing_eval/parsers.py): Excel 解析逻辑。
- [boeing_eval/analysis.py](/Users/seok/Desktop/doubleblindtest/boeing_eval/analysis.py): 统计聚合逻辑。
- [boeing_eval/reports.py](/Users/seok/Desktop/doubleblindtest/boeing_eval/reports.py): HTML 和 Word 报告生成。
- [docs/APP_REQUIREMENTS.md](/Users/seok/Desktop/doubleblindtest/docs/APP_REQUIREMENTS.md): 当前需求、兼容口径和验收基线。
- [README.md](/Users/seok/Desktop/doubleblindtest/README.md): 项目入口说明。

## 3. 本机环境

工作目录：

```bash
cd /Users/seok/Desktop/doubleblindtest
```

推荐直接使用仓库里的虚拟环境：

```bash
.venv/bin/python --version
```

如果 `.venv` 不可用，再重新安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. 本地运行

启动 Streamlit：

```bash
streamlit run eastchina_doubleblindtestA.py
```

如果要用仓库虚拟环境：

```bash
.venv/bin/streamlit run eastchina_doubleblindtestA.py
```

默认会从 `app_parts/part_*.pyfrag` 拼接出页面。

## 5. 修改代码的方式

优先遵循下面的顺序：

1. 先改 `boeing_eval/` 中的解析和分析逻辑。
2. 再改 `app_parts/` 里的页面展示和交互。
3. 最后同步更新 `README.md` 和 `docs/APP_REQUIREMENTS.md`。

常见修改点：

- 改解析规则，看 [boeing_eval/parsers.py](/Users/seok/Desktop/doubleblindtest/boeing_eval/parsers.py)。
- 改统计口径，看 [boeing_eval/analysis.py](/Users/seok/Desktop/doubleblindtest/boeing_eval/analysis.py)。
- 改页面布局或图表，看 [app_parts/part_03.pyfrag](/Users/seok/Desktop/doubleblindtest/app_parts/part_03.pyfrag) 到 [app_parts/part_05.pyfrag](/Users/seok/Desktop/doubleblindtest/app_parts/part_05.pyfrag)。
- 改主题样式，看 [app_parts/part_00.pyfrag](/Users/seok/Desktop/doubleblindtest/app_parts/part_00.pyfrag)。

### 页面拼接机制

入口文件会把 `app_parts/part_00.pyfrag` 到 `app_parts/part_05.pyfrag` 按文件名排序后直接拼接执行。

这意味着：

- 不要假设这些文件是独立模块。
- 不要在某个 part 里依赖“后面才定义”的变量，除非当前拼接顺序已经保证。
- 如果新加页面代码，优先放到现有 part 文件中，并保持命名连续。

## 6. 改完怎么验证

至少跑这三个检查：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 - <<'PY'
from pathlib import Path
parts = Path('app_parts')
source = ''.join((parts / f'part_{idx:02d}.pyfrag').read_text() for idx in range(6))
compile(source, str(parts / 'eastchina_doubleblindtestA.py'), 'exec')
print('compile ok')
PY
```

如果环境里装了完整依赖，再补一轮：

```bash
.venv/bin/python eastchina_doubleblindtestA.py
```

这个命令在无界面模式下只要不报真正的 Python 异常，就说明入口可以启动。

## 7. 数据和隐私

公开仓库和 public app 不要提交这些内容：

- `files/`
- `.env`
- `.streamlit/secrets.toml`
- 真实 Excel、Word、PDF 报告
- 人员数据和敏感账号信息

仓库已经通过 [`.gitignore`](/Users/seok/Desktop/doubleblindtest/.gitignore) 排除了这些内容。

## 8. 部署到 Streamlit Cloud

当前做法是把代码推到 GitHub，Streamlit Cloud 自动从主分支拉取并部署。

### 推送流程

```bash
git status
git add <changed files>
git commit -m "your message"
git push origin <branch>:main
```

### 部署检查

1. 确认 GitHub 仓库是 public app 对应的公开仓库。
2. 确认 `requirements.txt` 里列出了运行所需依赖。
3. 确认没有把 `files/`、密钥或私有数据提交进去。
4. 等 Streamlit Cloud 自动重建。
5. 打开线上地址做一次人工验证。

## 9. 常见问题

### 入口报 `KeyError`

通常是某个页面直接取了一个不存在的列。

处理方式：

- 在 `app_parts/part_04.pyfrag` 里确认解析后是否补齐了列。
- 在 `app_parts/part_05.pyfrag` 里把直接 `df[columns]` 改成 `safe_columns(...)`。
- 如果是聚合结果为空表，先给结果补默认列，再用于展示。

### 图表报错

优先检查：

- `make_bar`
- `make_horizontal_bar`
- `make_pie`
- `make_line_bar`

如果输入表没有相应字段，图表函数应该直接返回 `None`，而不是抛异常。

### 页面样式异常

浅色主题和全局 CSS 在 [app_parts/part_00.pyfrag](/Users/seok/Desktop/doubleblindtest/app_parts/part_00.pyfrag) 和 [`.streamlit/config.toml`](/Users/seok/Desktop/doubleblindtest/.streamlit/config.toml)。

如果暗色模式、字体颜色或卡片背景出问题，先看这两个位置。

## 10. 推荐工作方式

1. 先改代码。
2. 跑测试和启动检查。
3. 看 `git diff`，确认没有误改样表或无关文件。
4. 推送到 GitHub。
5. 让 Streamlit Cloud 自动部署。
6. 用真实样表回归验证。

