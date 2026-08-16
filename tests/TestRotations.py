import unittest

from src.axis.SequenceRunner import build_sequence_steps
from src.axis.rotations import build_macro_chart, builtin_axes
from src.axis.rotations.AiDaQian import AXIS, LOOP, OPENER


class TestRotations(unittest.TestCase):
    def test_aidaqian_opener_and_loop_are_fully_carved(self):
        self.assertEqual(len(AXIS.chart.steps), len(OPENER) + len(LOOP))
        self.assertEqual(AXIS.chart.steps[0].move_id, "macro_f")
        self.assertEqual(AXIS.chart.steps[1].move_id, "switch_2")
        # 循环从启动轴之后的第一步开始。
        self.assertEqual(AXIS.loop_start, len(OPENER))
        self.assertEqual(AXIS.chart.steps[AXIS.loop_start].move_id, "macro_e")

    def test_opener_ends_with_e_until_cd_bridge(self):
        opener_steps = AXIS.chart.steps[: AXIS.loop_start]
        self.assertEqual(opener_steps[-1].move_id, "macro_e_until_cd")
        self.assertEqual(opener_steps[-1].duration_ms, 4000.0)

    def test_loop_contains_jump_and_finisher_sequence(self):
        loop_steps = AXIS.chart.steps[AXIS.loop_start:]
        move_ids = [step.move_id for step in loop_steps]
        self.assertIn("macro_space", move_ids)
        self.assertEqual(AXIS.mappings["macro_space"].config_text, "space")
        # 循环末尾的衔接：R、E、条件处决、普攻至 E 高亮、E、重击、开大。
        self.assertEqual(
            move_ids[-7:],
            [
                "macro_r",
                "macro_e",
                "macro_f_break",
                "macro_attack_until_e",
                "macro_e",
                "macro_heavy",
                "macro_r",
            ],
        )

    def test_team_is_confirmed(self):
        self.assertEqual(AXIS.team, "爱弥斯 / 达妮娅 / 千咲")

    def test_macro_timing_is_cumulative(self):
        # 第一步 F 按住 50 等待 450，第二步应从 500 毫秒开始。
        self.assertEqual(AXIS.chart.steps[0].start_ms, 0.0)
        self.assertEqual(AXIS.chart.steps[1].start_ms, 500.0)

    def test_long_left_click_is_heavy_attack(self):
        heavy = [step for step in AXIS.chart.steps if step.move_id == "macro_heavy"]
        # 启动轴一处 950 毫秒重击，循环收尾一处。
        self.assertEqual(len(heavy), 2)
        self.assertEqual(heavy[0].duration_ms, 950.0)
        self.assertEqual(AXIS.mappings["macro_heavy"].config_text, "mouse:left:hold")

    def test_short_and_long_key_presses_map_separately(self):
        self.assertEqual(AXIS.mappings["macro_e"].config_text, "e")
        self.assertEqual(AXIS.mappings["macro_e_hold"].config_text, "e:hold")
        self.assertEqual(AXIS.mappings["switch_3"].config_text, "3")

    def test_macro_chart_feeds_sequence_runner(self):
        steps = build_sequence_steps(AXIS.chart, AXIS.mappings)

        self.assertEqual(len(steps), len(OPENER) + len(LOOP))
        # R 大招后的动画等待必须保留宏原值（按住 50 + 等待 4500）。
        liberation_gaps = [step.gap_ms for step in steps if step.move_id == "macro_r"]
        self.assertIn(4550.0, liberation_gaps)

    def test_loop_start_points_to_loop_section(self):
        opener = (("a", 50, 100), ("e", 50, 200))
        loop = (("a", 50, 100), ("r", 50, 3000))

        chart, mappings, loop_start = build_macro_chart("dummy", "测试轴", opener, loop)

        self.assertEqual(loop_start, 2)
        self.assertEqual(len(chart.steps), 4)
        self.assertIn("macro_r", mappings)

    def test_registry_lists_builtin_axes(self):
        axes = builtin_axes()

        self.assertTrue(any(axis.key == "aidaqian" for axis in axes))
        for axis in axes:
            self.assertTrue(axis.chart.steps)
            self.assertTrue(axis.mappings)

    def test_unsupported_key_raises(self):
        with self.assertRaises(ValueError):
            build_macro_chart("bad", "坏轴", (("x", 50, 100),), ())


if __name__ == "__main__":
    unittest.main()
