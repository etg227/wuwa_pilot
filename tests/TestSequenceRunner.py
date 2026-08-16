import threading
import unittest

from src.axis.AxisChart import OutputBinding, build_default_output_mapping
from src.axis.SequenceRunner import SequenceRunner, SequenceStep, build_sequence_steps
from src.axis.TextAxis import parse_text_axis
from tests.TestAxisRunner import FakeOutput


def make_step(move_id, binding, duration_ms=0.0, gap_ms=100.0, step_index=0, label="动作"):
    return SequenceStep(step_index, move_id, label, binding, duration_ms, gap_ms)


class AdvancingStopEvent:
    def __init__(self, now):
        self.now = now

    def wait(self, seconds):
        self.now[0] += seconds
        return False

    @staticmethod
    def is_set():
        return False


class TestSequenceRunner(unittest.TestCase):
    def test_build_steps_skips_unmapped_and_keeps_noop_waits(self):
        chart, _ = parse_text_axis("a2 e w0.5 q")
        mappings = {
            "basic_attack": OutputBinding("mouse", "left"),
            "echo": OutputBinding("key", "q"),
            "noop": None,
        }

        steps = build_sequence_steps(chart, mappings)

        self.assertEqual([step.move_id for step in steps], ["basic_attack", "basic_attack", "noop", "echo"])
        self.assertIsNone(steps[2].binding)
        self.assertEqual(steps[2].duration_ms, 500.0)

    def test_basic_attacks_use_configured_interval(self):
        now = [0.0]
        binding = OutputBinding("key", "a")
        steps = tuple(
            make_step("basic_attack", binding, gap_ms=100.0, step_index=i) for i in range(3)
        )

        class TimedOutput(FakeOutput):
            def tap(self, _binding):
                self.actions.append(("tap", now[0]))

        output = TimedOutput()
        cancelled, loops = SequenceRunner(clock=lambda: now[0]).run(
            steps, output, AdvancingStopEvent(now), basic_interval_ms=450
        )

        self.assertFalse(cancelled)
        self.assertEqual(loops, 1)
        self.assertAlmostEqual(output.actions[0][1], 0.0)
        self.assertAlmostEqual(output.actions[1][1], 0.45)
        self.assertAlmostEqual(output.actions[2][1], 0.9)

    def test_hold_step_presses_full_duration_then_releases(self):
        now = [0.0]
        hold = OutputBinding("mouse", "left", "hold")
        steps = (make_step("heavy_attack", hold, duration_ms=600.0, gap_ms=800.0),)
        output = FakeOutput()

        cancelled, _ = SequenceRunner(clock=lambda: now[0]).run(
            steps, output, AdvancingStopEvent(now)
        )

        self.assertFalse(cancelled)
        self.assertEqual(output.actions, [("down", "mouse:left:hold"), ("up", "mouse:left:hold")])
        self.assertGreaterEqual(now[0], 0.8)

    def test_switch_retries_once_when_confirm_fails(self):
        binding = OutputBinding("key", "2")
        steps = (make_step("switch_2", binding, label="切人"),)
        confirms = []

        def confirm(_step):
            confirms.append(True)
            return len(confirms) > 1

        output = FakeOutput()
        cancelled, _ = SequenceRunner().run(
            steps, output, threading.Event(), switch_confirm=confirm
        )

        self.assertFalse(cancelled)
        self.assertEqual(len([a for a in output.actions if a[0] == "tap"]), 2)
        self.assertEqual(len(confirms), 2)

    def test_loop_repeats_from_entry_until_continue_returns_false(self):
        binding = OutputBinding("key", "e")
        steps = (
            make_step("skill", binding, gap_ms=1.0, step_index=0),
            make_step("skill", binding, gap_ms=1.0, step_index=1),
        )
        continues = [True, False]

        output = FakeOutput()
        cancelled, loops = SequenceRunner().run(
            steps,
            output,
            threading.Event(),
            loop=True,
            loop_start_step=1,
            should_continue_loop=lambda: continues.pop(0),
        )

        self.assertFalse(cancelled)
        self.assertEqual(loops, 2)
        # 第一轮 2 步 + 第二轮从循环起点开始 1 步。
        self.assertEqual(len(output.actions), 3)

    def test_stop_during_hold_releases_key(self):
        stop_event = threading.Event()
        hold = OutputBinding("key", "lshift", "hold")

        class StoppingOutput(FakeOutput):
            def press(self, binding):
                super().press(binding)
                stop_event.set()

        steps = (make_step("dodge_hold", hold, duration_ms=500.0),)
        output = StoppingOutput()

        cancelled, _ = SequenceRunner().run(steps, output, stop_event)

        self.assertTrue(cancelled)
        self.assertEqual(output.actions, [("down", "lshift:hold"), ("up", "lshift:hold")])

    def test_gate_blocks_step_until_allowed(self):
        binding = OutputBinding("key", "e")
        steps = (make_step("skill", binding, gap_ms=1.0),)
        gate_calls = []

        def gate(_step):
            gate_calls.append(True)
            return len(gate_calls) > 2

        output = FakeOutput()
        cancelled, _ = SequenceRunner().run(
            steps, output, threading.Event(), gate_callback=gate
        )

        self.assertFalse(cancelled)
        self.assertEqual(len(output.actions), 1)
        self.assertEqual(len(gate_calls), 3)

    def test_default_mapping_repeat_basic_attack_respects_interval(self):
        now = [0.0]
        chart, _ = parse_text_axis("a2")
        mappings = build_default_output_mapping(chart)
        steps = build_sequence_steps(chart, mappings)

        class TimedOutput(FakeOutput):
            def tap(self, _binding):
                self.actions.append(("tap", now[0]))

        output = TimedOutput()
        cancelled, _ = SequenceRunner(clock=lambda: now[0]).run(
            steps, output, AdvancingStopEvent(now), basic_interval_ms=450
        )

        self.assertFalse(cancelled)
        # 连点映射的单次普攻步也必须遵守出手间隔，不能 60 毫秒连发。
        self.assertGreaterEqual(output.actions[-1][1] - output.actions[0][1], 0.35)


if __name__ == "__main__":
    unittest.main()
