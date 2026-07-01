from __future__ import annotations

import pandas as pd


def build_pilot_scores(ratings: pd.DataFrame, summary_scores: pd.DataFrame) -> pd.DataFrame:
    if ratings.empty:
        return pd.DataFrame()

    grouped = (
        ratings.groupby("人员ID", dropna=False)
        .agg(
            姓名=("姓名", "first"),
            所属单位=("所属单位", "first"),
            技术等级=("技术等级", "first"),
            模板类型=("模板类型", "first"),
            来源文件=("来源文件", "first"),
            评分人数=("评估员", "count"),
            评分员平均分=("计算得分", "mean"),
            平均扣分项数量=("扣分项数量", "mean"),
        )
        .reset_index()
    )

    if not summary_scores.empty and "模板得分" in summary_scores.columns:
        summary = (
            summary_scores.dropna(subset=["模板得分"])
            .groupby("人员ID", dropna=False)["模板得分"]
            .mean()
            .reset_index()
            .rename(columns={"模板得分": "模板平均/合计得分"})
        )
        grouped = grouped.merge(summary, on="人员ID", how="left")
    else:
        grouped["模板平均/合计得分"] = pd.NA

    grouped["最终得分"] = grouped["模板平均/合计得分"].combine_first(grouped["评分员平均分"])
    grouped["平均失分"] = 100 - grouped["最终得分"]
    grouped["最终得分"] = grouped["最终得分"].round(2)
    grouped["平均失分"] = grouped["平均失分"].round(2)
    grouped["平均扣分项数量"] = grouped["平均扣分项数量"].round(2)
    return grouped


def company_stats(pilot_scores: pd.DataFrame) -> pd.DataFrame:
    if pilot_scores.empty:
        return pd.DataFrame()
    return (
        pilot_scores.groupby(["所属单位", "模板类型"], dropna=False)
        .agg(
            参评人数=("人员ID", "count"),
            平均分=("最终得分", "mean"),
            最高分=("最终得分", "max"),
            最低分=("最终得分", "min"),
            机长人数=("技术等级", lambda s: (s == "机长").sum()),
            副驾驶人数=("技术等级", lambda s: (s == "副驾驶").sum()),
        )
        .reset_index()
        .round({"平均分": 2, "最高分": 2, "最低分": 2})
        .sort_values(["模板类型", "平均分"], ascending=[True, False])
    )


def loss_by_item(deductions: pd.DataFrame, group_cols: list[str], top_n: int | None = None) -> pd.DataFrame:
    if deductions.empty:
        return pd.DataFrame()
    result = (
        deductions.groupby(group_cols, dropna=False)
        .agg(扣分次数=("失分", "count"), 总失分=("失分", "sum"), 平均失分=("失分", "mean"))
        .reset_index()
        .sort_values(["总失分", "扣分次数"], ascending=False)
        .round({"总失分": 2, "平均失分": 2})
    )
    if top_n:
        result = result.head(top_n)
    return result


def company_role_counts(pilot_scores: pd.DataFrame) -> pd.DataFrame:
    if pilot_scores.empty:
        return pd.DataFrame()
    return (
        pilot_scores.groupby(["所属单位", "技术等级"], dropna=False)
        .agg(参评人数=("人员ID", "count"))
        .reset_index()
        .sort_values(["所属单位", "技术等级"])
    )


def company_role_scores(pilot_scores: pd.DataFrame) -> pd.DataFrame:
    if pilot_scores.empty:
        return pd.DataFrame()
    return (
        pilot_scores.groupby(["所属单位", "技术等级"], dropna=False)
        .agg(平均分=("最终得分", "mean"), 参评人数=("人员ID", "count"))
        .reset_index()
        .round({"平均分": 2})
        .sort_values(["所属单位", "技术等级"])
    )


def score_distribution(pilot_scores: pd.DataFrame) -> pd.DataFrame:
    if pilot_scores.empty:
        return pd.DataFrame()
    bins = [0, 60, 70, 80, 90, 100.01]
    labels = ["60以下", "60-69", "70-79", "80-89", "90以上"]
    data = pilot_scores.copy()
    data["分数区间"] = pd.cut(data["最终得分"], bins=bins, labels=labels, right=False, include_lowest=True)
    return (
        data.groupby("分数区间", observed=False)
        .agg(人数=("人员ID", "count"))
        .reset_index()
    )


def role_score_distribution(pilot_scores: pd.DataFrame) -> pd.DataFrame:
    if pilot_scores.empty:
        return pd.DataFrame()
    bins = [0, 60, 70, 80, 90, 100.01]
    labels = ["60以下", "60-69", "70-79", "80-89", "90以上"]
    data = pilot_scores.copy()
    data["分数区间"] = pd.cut(data["最终得分"], bins=bins, labels=labels, right=False, include_lowest=True)
    return (
        data.groupby(["技术等级", "分数区间"], observed=False, dropna=False)
        .agg(人数=("人员ID", "count"))
        .reset_index()
    )


def subject_company_loss(deductions: pd.DataFrame, pilot_scores: pd.DataFrame) -> pd.DataFrame:
    if deductions.empty or pilot_scores.empty:
        return pd.DataFrame()
    people_count = pilot_scores.groupby("所属单位", dropna=False)["人员ID"].nunique().reset_index(name="参评人数")
    stats = (
        deductions.groupby(["所属单位", "科目名称"], dropna=False)
        .agg(总失分=("失分", "sum"), 扣分次数=("失分", "count"))
        .reset_index()
        .merge(people_count, on="所属单位", how="left")
    )
    stats["人均失分"] = stats["总失分"] / stats["参评人数"].replace(0, pd.NA)
    return stats.round({"总失分": 2, "人均失分": 2}).sort_values(["所属单位", "科目名称"])


def subject_top_items(deductions: pd.DataFrame, top_n: int = 3) -> pd.DataFrame:
    if deductions.empty:
        return pd.DataFrame()
    grouped = loss_by_item(deductions, ["科目名称", "评分项目", "扣分标准"], top_n=None)
    if grouped.empty:
        return grouped
    return grouped.groupby("科目名称", group_keys=False).head(top_n).reset_index(drop=True)


def subject_item_loss(deductions: pd.DataFrame, subject: str | None = None) -> pd.DataFrame:
    if deductions.empty:
        return pd.DataFrame()
    data = deductions if subject is None else deductions[deductions["科目名称"] == subject]
    return loss_by_item(data, ["科目名称", "评分项目", "扣分标准"], top_n=None)


def subject_role_loss(deductions: pd.DataFrame, subject: str | None = None) -> pd.DataFrame:
    if deductions.empty:
        return pd.DataFrame()
    data = deductions if subject is None else deductions[deductions["科目名称"] == subject]
    return loss_by_item(data, ["技术等级", "评分项目", "扣分标准"], top_n=None)


def subject_company_item_loss(deductions: pd.DataFrame, subject: str | None = None) -> pd.DataFrame:
    if deductions.empty:
        return pd.DataFrame()
    data = deductions if subject is None else deductions[deductions["科目名称"] == subject]
    return loss_by_item(data, ["所属单位", "评分项目", "扣分标准"], top_n=None)


def risk_index(deductions: pd.DataFrame, ratings: pd.DataFrame | None = None) -> pd.DataFrame:
    if deductions.empty:
        return pd.DataFrame()
    denominator = len(ratings) if ratings is not None and not ratings.empty else deductions["人员ID"].nunique()
    denominator = max(int(denominator or 1), 1)
    grouped = (
        deductions.groupby(["科目名称", "评分项目", "扣分标准"], dropna=False)
        .agg(
            扣分次数=("失分", "count"),
            总失分=("失分", "sum"),
            平均失分=("失分", "mean"),
            标准分值=("标准分值", "first"),
        )
        .reset_index()
    )
    grouped["触发率"] = grouped["扣分次数"] / denominator
    grouped["风险指数"] = grouped["触发率"] * grouped["平均失分"].fillna(0)
    return (
        grouped.round({"总失分": 2, "平均失分": 2, "触发率": 4, "风险指数": 4})
        .sort_values(["风险指数", "总失分"], ascending=False)
        .reset_index(drop=True)
    )


def comprehensive_loss(deductions: pd.DataFrame) -> pd.DataFrame:
    if deductions.empty:
        return pd.DataFrame()
    mask = deductions["科目名称"].astype(str).str.contains("综合", na=False)
    data = deductions[mask]
    if data.empty:
        return pd.DataFrame()
    return loss_by_item(data, ["评分项目", "扣分标准"], top_n=None)


def template_quality(summaries: pd.DataFrame, pilot_scores: pd.DataFrame) -> pd.DataFrame:
    if summaries.empty:
        return pd.DataFrame()
    quality = summaries.copy()
    missing_scores = (
        pilot_scores[pilot_scores["最终得分"].isna()]
        .groupby("来源文件")["人员ID"]
        .count()
        .to_dict()
        if not pilot_scores.empty
        else {}
    )
    quality["缺失得分人数"] = quality["文件名"].map(missing_scores).fillna(0).astype(int)
    quality["状态"] = quality.apply(
        lambda row: "需检查" if row.get("警告") or row.get("缺失得分人数", 0) else "正常",
        axis=1,
    )
    return quality


def filter_data(
    pilot_scores: pd.DataFrame,
    deductions: pd.DataFrame,
    template: str,
    company: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pilots = pilot_scores.copy()
    ded = deductions.copy()
    if template != "全部":
        pilots = pilots[pilots["模板类型"] == template]
        if not ded.empty:
            ded = ded[ded["模板类型"] == template]
    if company != "全部":
        pilots = pilots[pilots["所属单位"] == company]
        if not ded.empty:
            ded = ded[ded["所属单位"] == company]
    return pilots, ded
