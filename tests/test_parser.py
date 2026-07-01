from pathlib import Path
import unittest

from boeing_eval.parsers import B737_TEMPLATE, GO_AROUND_TEMPLATE, parse_workbook


BASE = Path(__file__).resolve().parents[1] / "files"


EXPECTED = {
    "上航B737.xlsx": (B737_TEMPLATE, 3, 8, 16, 8, 93),
    "东航B737.xlsx": (B737_TEMPLATE, 3, 12, 36, 12, 93),
    "厦航B737.xlsx": (B737_TEMPLATE, 3, 24, 72, 24, 93),
    "山航B737.xlsx": (B737_TEMPLATE, 3, 20, 60, 20, 93),
    "复飞专项检查数据采集表(江西航).xlsx": (GO_AROUND_TEMPLATE, 5, 12, 24, 12, 149),
}


@unittest.skipUnless(BASE.exists(), "local sample files are not available")
class ParserRegressionTest(unittest.TestCase):
    def test_sample_baselines(self):
        for file_name, expected in EXPECTED.items():
            with self.subTest(file_name=file_name):
                path = BASE / file_name
                parsed = parse_workbook(path.read_bytes(), file_name)
                summary = parsed.summary
                self.assertEqual(summary["模板类型"], expected[0])
                self.assertEqual(summary["分值行"], expected[1])
                self.assertEqual(summary["人员数"], expected[2])
                self.assertEqual(summary["评分行数"], expected[3])
                self.assertEqual(summary["平均/合计行数"], expected[4])
                self.assertEqual(summary["扣分列数"], expected[5])
                self.assertIn("评估员", parsed.ratings.columns)
                self.assertIn("扣分项", parsed.deductions.columns)


if __name__ == "__main__":
    unittest.main()
