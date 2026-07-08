# 验证科目失分排名与科目->失分项两级下钻逻辑。
import unittest

import pandas as pd

from boeing_eval.analysis import filter_data, subject_loss_ranking, top_subject_item_loss


def _sample_deductions() -> pd.DataFrame:
    rows = [
        {"所属单位": "A航", "科目名称": "起飞", "评分项目": "P1", "扣分标准": "S1", "扣分项": "起飞-项A", "失分": 10},
        {"所属单位": "A航", "科目名称": "起飞", "评分项目": "P1", "扣分标准": "S1", "扣分项": "起飞-项B", "失分": 6},
        {"所属单位": "B航", "科目名称": "起飞", "评分项目": "P1", "扣分标准": "S1", "扣分项": "起飞-项A", "失分": 4},
        {"所属单位": "A航", "科目名称": "降落", "评分项目": "P2", "扣分标准": "S2", "扣分项": "降落-项A", "失分": 20},
        {"所属单位": "B航", "科目名称": "降落", "评分项目": "P2", "扣分标准": "S2", "扣分项": "降落-项B", "失分": 5},
        {"所属单位": "A航", "科目名称": "巡航", "评分项目": "P3", "扣分标准": "S3", "扣分项": "巡航-项A", "失分": 1},
        {"所属单位": "B航", "科目名称": "巡航", "评分项目": "P3", "扣分标准": "S3", "扣分项": "巡航-项B", "失分": 1},
    ]
    return pd.DataFrame(rows)


class SubjectRankingTest(unittest.TestCase):
    def test_subject_loss_ranking_orders_by_total_loss(self):
        ranking = subject_loss_ranking(_sample_deductions())
        self.assertEqual(ranking["科目名称"].tolist(), ["降落", "起飞", "巡航"])
        self.assertEqual(ranking.iloc[0]["总失分"], 25)

    def test_subject_loss_ranking_top_n_truncates(self):
        ranking = subject_loss_ranking(_sample_deductions(), top_n=2)
        self.assertEqual(len(ranking), 2)
        self.assertEqual(ranking["科目名称"].tolist(), ["降落", "起飞"])

    def test_top_subject_item_loss_scopes_to_top_subjects(self):
        result = top_subject_item_loss(_sample_deductions(), subject_top_n=2, item_top_n=1)
        # 只应包含失分最多的两个科目：降落、起飞，不含巡航
        self.assertEqual(set(result["科目名称"].astype(str)), {"降落", "起飞"})
        # 每个科目只取失分最多的 1 个失分项
        self.assertEqual(len(result), 2)
        top_takeoff = result[result["科目名称"] == "起飞"].iloc[0]
        self.assertEqual(top_takeoff["扣分项"], "起飞-项A")


class MultiCompanyFilterTest(unittest.TestCase):
    def test_filter_data_accepts_company_list(self):
        pilots = pd.DataFrame(
            {
                "人员ID": ["1", "2", "3"],
                "所属单位": ["A航", "B航", "C航"],
                "模板类型": ["双盲测试表", "双盲测试表", "双盲测试表"],
            }
        )
        deductions = _sample_deductions()
        deductions["模板类型"] = "双盲测试表"
        filtered_pilots, filtered_deductions = filter_data(pilots, deductions, "全部", ["A航", "B航"])
        self.assertEqual(set(filtered_pilots["所属单位"]), {"A航", "B航"})
        self.assertEqual(set(filtered_deductions["所属单位"]), {"A航", "B航"})

    def test_filter_data_still_supports_single_company_string(self):
        pilots = pd.DataFrame({"人员ID": ["1", "2"], "所属单位": ["A航", "B航"], "模板类型": ["双盲测试表", "双盲测试表"]})
        deductions = _sample_deductions()
        deductions["模板类型"] = "双盲测试表"
        filtered_pilots, _ = filter_data(pilots, deductions, "全部", "A航")
        self.assertEqual(filtered_pilots["所属单位"].tolist(), ["A航"])


if __name__ == "__main__":
    unittest.main()
