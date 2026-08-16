"""内置阵容轴：把成熟的宏轴刻录为程序内置数据，按推进模式执行。

每条内置轴由启动轴和循环轴两段宏组成，宏步骤为（按键, 按住毫秒, 松开后等待毫秒），
按键 a 表示鼠标左键。载入后走椰果启动器现有的推进模式与循环机制执行。
"""

from dataclasses import dataclass

from src.axis.AxisChart import AxisChart, AxisStep, OutputBinding

MacroStep = tuple[str, int, int]

_KEY_LABELS = {"f": "挑战/处决", "e": "共鸣技能", "q": "声骸", "r": "共鸣解放", "space": "跳跃"}
# 按住不低于该时长视为长按；鼠标左键长按即重击。
_HOLD_THRESHOLD_MS = 150
_HEAVY_THRESHOLD_MS = 300


@dataclass(frozen=True)
class BuiltinAxis:
    key: str
    name: str
    team: str
    chart: AxisChart
    mappings: dict[str, OutputBinding]
    loop_start: int | None


def _step_meta(key: str, hold_ms: int) -> tuple[str, str, OutputBinding]:
    if key == "f?":
        # 条件步：画面上出现处决提示才按 F，否则跳过。
        return "macro_f_break", "处决（若出现）", OutputBinding("key", "f")
    if key == "a>e":
        # 条件步：连点普攻直到 E 技能高亮（hold_ms 为超时预算毫秒）。
        return "macro_attack_until_e", "普攻至 E 高亮", OutputBinding("mouse", "left")
    if key == "e!cd":
        # 条件步：连按 E 直到进入 CD，确认技能真的放出（hold_ms 为超时预算毫秒）。
        return "macro_e_until_cd", "E（确认放出）", OutputBinding("key", "e")
    if key == "r!cd":
        return "macro_r_until_cd", "共鸣解放（确认放出）", OutputBinding("key", "r")
    if key == "q!cd":
        return "macro_q_until_cd", "声骸（确认放出）", OutputBinding("key", "q")
    if key in {"1", "2", "3"}:
        return f"switch_{key}", f"切人 {key}", OutputBinding("key", key)
    if key == "a":
        if hold_ms >= _HEAVY_THRESHOLD_MS:
            return "macro_heavy", "重击", OutputBinding("mouse", "left", "hold")
        return "macro_attack", "普攻", OutputBinding("mouse", "left")
    if key not in _KEY_LABELS:
        raise ValueError(f"内置轴不支持按键：{key}")
    if hold_ms >= _HOLD_THRESHOLD_MS:
        return f"macro_{key}_hold", f"{_KEY_LABELS[key]}（长按）", OutputBinding("key", key, "hold")
    return f"macro_{key}", _KEY_LABELS[key], OutputBinding("key", key)


def build_macro_chart(
    key_name: str,
    title: str,
    opener: tuple[MacroStep, ...],
    loop: tuple[MacroStep, ...],
) -> tuple[AxisChart, dict[str, OutputBinding], int | None]:
    steps: list[AxisStep] = []
    mappings: dict[str, OutputBinding] = {}
    move_labels: dict[str, str] = {}
    clock_ms = 0.0

    def append(sequence: tuple[MacroStep, ...]) -> None:
        nonlocal clock_ms
        for key, hold_ms, wait_ms in sequence:
            move_id, label, binding = _step_meta(key, hold_ms)
            mappings.setdefault(move_id, binding)
            move_labels[move_id] = label
            steps.append(
                AxisStep(
                    step_id=f"{key_name}_{len(steps)}",
                    move_id=move_id,
                    label=label,
                    start_ms=clock_ms,
                    duration_ms=float(hold_ms),
                )
            )
            clock_ms += max(hold_ms, 1) + max(wait_ms, 0)

    append(opener)
    loop_start = len(steps) if loop else None
    append(loop)
    if not steps:
        raise ValueError(f"内置轴 {key_name} 没有任何步骤")

    chart = AxisChart(
        chart_id=f"builtin_{key_name}",
        title=title,
        version=3,
        steps=tuple(steps),
        move_labels=move_labels,
        binding_codes={},
    )
    return chart, mappings, loop_start


def builtin_axes() -> tuple[BuiltinAxis, ...]:
    from src.axis.rotations.AiDaQian import AXIS as aidaqian

    return (aidaqian,)
