import time
from collections.abc import Callable
from dataclasses import dataclass

from src.axis.AxisChart import AxisChart, OutputBinding
from src.axis.AxisRunner import AxisOutput

SWITCH_MOVES = {"switch_1", "switch_2", "switch_3"}
MAX_SEQUENCE_LOOPS = 100
# 推进模式下各类动作出手后的最小间隔（毫秒）；录制间隔更长时取录制值。
AFTER_MIN_MS = {
    "skill": 500,
    "skill_hold": 500,
    "echo": 400,
    "liberation": 1200,
    "dodge": 300,
    "jump": 300,
}
DEFAULT_MIN_GAP_MS = 60


@dataclass(frozen=True)
class SequenceStep:
    """推进模式的一步：binding 为 None 表示纯等待（空招式）。"""

    step_index: int
    move_id: str
    label: str
    binding: OutputBinding | None
    duration_ms: float
    gap_ms: float


def build_sequence_steps(
    chart: AxisChart, mappings: dict[str, OutputBinding | None]
) -> tuple[SequenceStep, ...]:
    """把轴步骤编译成推进步骤；未映射动作跳过，空招式保留为等待。"""

    playable = []
    for index, step in enumerate(chart.steps):
        binding = mappings.get(step.move_id)
        if binding is None and not chart.is_noop_move(step.move_id):
            continue
        playable.append((index, step, binding))
    result = []
    for pos, (index, step, binding) in enumerate(playable):
        if pos + 1 < len(playable):
            gap = max(0.0, playable[pos + 1][1].start_ms - step.start_ms)
        else:
            gap = max(step.duration_ms, 0.0)
        result.append(
            SequenceStep(index, step.move_id, step.label, binding, step.duration_ms, gap)
        )
    return tuple(result)


class SequenceRunner:
    """按顺序推进执行：完成一步再进入下一步，不使用绝对时间戳。

    普攻按可配置的出手间隔逐次按满，切人经确认失败会重试一次，
    循环模式在每轮结束后根据回调决定是否继续，用于打到战斗结束。
    """

    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self.clock = clock

    def run(
        self,
        steps: tuple[SequenceStep, ...],
        output: AxisOutput,
        stop_event,
        *,
        basic_interval_ms: int = 450,
        repeat_interval_ms: int = 110,
        loop: bool = False,
        loop_start_step: int = 0,
        should_continue_loop: Callable[[], bool] | None = None,
        max_loops: int = MAX_SEQUENCE_LOOPS,
        gate_callback: Callable[[SequenceStep], bool] | None = None,
        switch_confirm: Callable[[SequenceStep], bool] | None = None,
        action_callback: Callable[[SequenceStep], None] | None = None,
        progress_callback: Callable[[float], None] | None = None,
        status_callback: Callable[[str], None] | None = None,
    ) -> tuple[bool, int]:
        if basic_interval_ms < 100 or basic_interval_ms > 2000:
            raise ValueError("普攻出手间隔必须在 100～2000 毫秒之间")
        if not steps:
            raise ValueError("推进模式没有可执行的步骤")

        entry = 0
        for pos, step in enumerate(steps):
            if step.step_index >= loop_start_step:
                entry = pos
                break

        cancelled = False
        loops_done = 0
        pos = 0
        total = len(steps)
        while True:
            if pos >= total:
                loops_done += 1
                if not loop or loops_done >= max_loops:
                    break
                if should_continue_loop is not None and not should_continue_loop():
                    if status_callback:
                        status_callback(f"战斗结束，共执行 {loops_done} 轮")
                    break
                pos = entry
                if status_callback:
                    status_callback(f"进入第 {loops_done + 1} 轮循环")
                continue
            if stop_event.is_set():
                cancelled = True
                break
            step = steps[pos]
            if gate_callback and not gate_callback(step):
                if stop_event.wait(0.05):
                    cancelled = True
                    break
                continue
            if action_callback:
                action_callback(step)
            if not self._execute_step(
                step, output, stop_event, basic_interval_ms, repeat_interval_ms, switch_confirm
            ):
                cancelled = True
                break
            if progress_callback:
                progress_callback(min(100.0, (pos + 1) / total * 100))
            pos += 1
        return cancelled, loops_done

    def _execute_step(
        self, step, output, stop_event, basic_interval_ms, repeat_interval_ms, switch_confirm
    ) -> bool:
        binding = step.binding
        if binding is None:
            # 空招式：只占位等待。
            return not stop_event.wait(max(step.duration_ms, 0.0) / 1000)

        if binding.mode == "hold":
            output.press(binding)
            try:
                if stop_event.wait(max(step.duration_ms, 40) / 1000):
                    return False
            finally:
                output.release(binding)
            return not stop_event.wait(
                self._after_wait_s(step, basic_interval_ms, consumed_ms=step.duration_ms)
            )

        if binding.mode == "repeat":
            end = self.clock() + max(step.duration_ms, 1) / 1000
            while True:
                output.tap(binding)
                remaining = end - self.clock()
                if remaining <= 0:
                    break
                if stop_event.wait(min(repeat_interval_ms / 1000, remaining)):
                    return False
            return not stop_event.wait(
                self._after_wait_s(step, basic_interval_ms, consumed_ms=step.duration_ms)
            )

        output.tap(binding)
        if step.move_id in SWITCH_MOVES and switch_confirm is not None:
            if not switch_confirm(step) and not stop_event.is_set():
                # 切人没有得到画面确认：重试一次，仍失败则继续推进。
                output.tap(binding)
                switch_confirm(step)
            if stop_event.is_set():
                return False
            return not stop_event.wait(DEFAULT_MIN_GAP_MS / 1000)

        return not stop_event.wait(self._after_wait_s(step, basic_interval_ms))

    @staticmethod
    def _after_wait_s(step, basic_interval_ms: int, consumed_ms: float = 0.0) -> float:
        """出手到下一步的总时长下限：普攻用出手间隔，其余用类型下限，再扣除已消耗时间。"""
        if step.move_id == "basic_attack":
            floor_ms = basic_interval_ms
        else:
            floor_ms = AFTER_MIN_MS.get(step.move_id, DEFAULT_MIN_GAP_MS)
        total_ms = max(step.gap_ms, floor_ms)
        return max((total_ms - consumed_ms) / 1000, DEFAULT_MIN_GAP_MS / 1000)
