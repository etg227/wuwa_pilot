"""爱达千轴（角色逻辑版）：动作序列来自宏，技能释放学原脚本。

普攻与切人保留宏节奏；E/Q 按到确认放出；R 的大招演出由画面检测
判定结束（不再固定等待 3~5 秒），演出后统一留 0.4 秒恢复。
识别不可用时每个动作自动退化为宏式单按，节奏兜底。
"""

from src.axis.rotations.logic import RotationHost


def opener(h: RotationHost) -> None:
    h.press("f", 0.45)
    h.switch(2, 0.05)
    h.skill(0.1)
    h.liberation()
    h.attack(0.3)
    h.attack(0.15)

    h.switch(3, 0.1)
    h.skill(0.05)
    h.liberation()
    h.attack(0.05)
    h.switch(2, 0.1)
    h.attack(0.75)

    h.attack(0.1)
    h.switch(3, 0.1)
    h.echo(0.0)
    h.attack(0.25)
    h.attack(0.5)
    h.switch(2, 0.1)

    h.attack(0.25)
    h.attack(0.25)
    # 双 E 多段形态：保持宏原样，避免首段被误确认。
    h.press("e", 0.7)
    h.hold_key("e", 0.2, 0.05)
    h.echo(0.0)
    h.liberation()

    h.switch(3, 0.85)
    h.skill(0.05)
    h.switch(1, 0.25)
    h.heavy(0.95, 0.05)
    h.switch(3, 0.1)
    h.attack(0.95)

    h.attack(0.0)
    h.switch(1, 0.1)
    h.attack(0.75)
    h.attack(0.05)
    h.switch(3, 0.1)
    h.attack(0.2)

    h.switch(1, 1.25)
    h.attack(0.35)
    h.echo(0.0)
    h.liberation()
    # 启动宏结束后连按 E 直到进入 CD，确认放出后进入正式循环。
    h.e_until_cd(4.0, 0.1)


def loop_cycle(h: RotationHost) -> None:
    h.skill(0.05)
    h.switch(2, 0.75)
    h.attack(0.05)
    h.switch(3, 0.1)
    h.skill(0.35)
    h.attack(0.05)

    h.switch(1, 0.1)
    h.attack(0.55)
    h.attack(0.25)
    h.switch(3, 0.1)
    h.attack(0.05)
    h.switch(2, 0.1)

    h.attack(0.35)
    h.attack(0.2)
    h.switch(1, 0.1)
    h.attack(0.8)
    h.skill(0.0)
    h.switch(3, 0.1)

    h.attack(0.25)
    h.jump(0.15)
    h.attack(0.5)
    h.switch(1, 0.1)
    h.attack(0.45)
    h.attack(0.4)

    # 双 E 多段形态：首段保持宏时序，末段跟宏动画等待。
    h.press("e", 0.2)
    h.press("e", 2.5)
    h.attack(0.05)
    h.switch(2, 0.1)
    h.skill(0.1)
    h.liberation()

    h.attack(0.25)
    h.attack(0.05)
    h.switch(1, 0.1)
    h.attack(0.25)
    h.skill(0.0)
    h.switch(3, 0.1)

    h.echo(0.0)
    h.liberation()
    h.skill(0.0)
    h.switch(2, 0.1)
    h.attack(0.7)
    h.attack(0.1)

    h.switch(3, 0.1)
    h.attack(1.0)
    h.attack(0.0)
    h.switch(1, 0.1)
    h.attack(0.55)
    h.attack(0.2)

    h.skill(0.0)
    h.switch(3, 0.1)
    h.attack(0.2)
    h.switch(1, 1.25)
    h.attack(0.725)
    h.attack(0.0)

    h.switch(2, 0.1)
    h.press("e", 0.7)
    h.hold_key("e", 0.2, 0.05)
    h.echo(0.0)
    h.liberation()
    h.switch(1, 0.15)

    # 循环宏结束后的衔接：R、E、处决（若出现）、普攻至 E 高亮、E、重击、开大。
    h.liberation()
    h.skill(0.6)
    h.f_if_break(0.3)
    h.attack_until_e_ready(10.0)
    h.skill(0.5)
    h.heavy(0.95, 0.3)
    h.liberation()
