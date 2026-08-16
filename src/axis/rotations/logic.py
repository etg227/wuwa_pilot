"""角色逻辑执行宿主：用原脚本的角色原语执行内置轴。

与宏播放的区别：技能与大招通过 BaseChar 的 click_resonance /
click_liberation 释放——按到确认放出为止，大招演出结束由画面检测
（角色 UI 消失→重现）判定，不再依赖固定等待；普攻与切人保留宏节奏。
"""

import threading
from collections.abc import Callable


class StopPlayback(Exception):
    """用户停止播放。"""


class RotationHost:
    """轴代码的执行环境；slot 从 1 开始，与队伍位一致。"""

    LIBERATION_RECOVER_S = 0.4

    def __init__(
        self,
        task,
        stop_event: threading.Event,
        status_callback: Callable[[str], None] | None = None,
    ):
        self.task = task
        self.stop_event = stop_event
        self.status_callback = status_callback
        self.slot = 1

    # ---- 基础动作（宏节奏） ----

    def wait(self, seconds: float) -> None:
        if seconds > 0 and self.stop_event.wait(seconds):
            raise StopPlayback
        if self.stop_event.is_set():
            raise StopPlayback

    def press(self, key: str, after: float = 0.0, down: float = 0.02) -> None:
        self._interaction().send_key(key, down)
        self.wait(after)

    def hold_key(self, key: str, hold: float, after: float = 0.0) -> None:
        interaction = self._interaction()
        interaction.send_key_down(key)
        try:
            self.wait(hold)
        finally:
            interaction.send_key_up(key)
        self.wait(after)

    def attack(self, after: float = 0.0) -> None:
        self._interaction().click(-1, -1, move=False, down_time=0.015, key="left")
        self.wait(after)

    def heavy(self, hold: float, after: float = 0.0) -> None:
        interaction = self._interaction()
        interaction.mouse_down(-1, -1, key="left")
        try:
            self.wait(hold)
        finally:
            interaction.mouse_up(key="left")
        self.wait(after)

    def jump(self, after: float = 0.0) -> None:
        self.press("space", after)

    def switch(self, slot: int, after: float = 0.1) -> None:
        """切人立即衔接；只有明确看到停在错误槽位才补按一次。"""
        self.press(str(slot))
        self.slot = slot
        self.wait(after)
        try:
            self.task.next_frame()
            in_team, current, _ = self.task.in_team()
        except Exception:
            return
        if in_team and current is not None and current != slot - 1:
            self.status(f"切人 {slot} 未成功，补按一次")
            self.press(str(slot))
            self.wait(0.05)

    # ---- 角色原语（状态驱动，学自原脚本） ----

    def char(self):
        chars = getattr(self.task, "chars", None)
        if chars and len(chars) >= self.slot and chars[self.slot - 1] is not None:
            return chars[self.slot - 1]
        return None

    def skill(self, after: float = 0.0) -> None:
        """共鸣技能：按到确认放出（原脚本 click_resonance），失败退化为单按。"""
        self._checked_cast(lambda char: char.click_resonance(), "e")
        self.wait(after)

    def liberation(self, after: float = LIBERATION_RECOVER_S) -> None:
        """共鸣解放：演出结束由画面检测判定（原脚本 click_liberation）。

        识别不可用时退化为单按 R + 固定等待，保证宏节奏兜底。
        """
        fallback_wait = 3.5

        def cast(char):
            return char.click_liberation(wait_if_cd_ready=2.0)

        if not self._checked_cast(cast, "r"):
            self.wait(fallback_wait)
        self.wait(after)

    def echo(self, after: float = 0.0) -> None:
        self._checked_cast(lambda char: char.click_echo(time_out=1), "q")
        self.wait(after)

    def f_if_break(self, after: float = 0.0) -> None:
        try:
            self.task.next_frame()
            if self.task.check_f_break():
                self.press("f")
        except Exception:
            pass
        self.wait(after)

    def attack_until_e_ready(self, timeout: float = 10.0, interval: float = 0.45) -> None:
        import time

        deadline = time.monotonic() + timeout
        while True:
            self.attack()
            try:
                self.task.next_frame()
                char = self.char()
                if char is not None and char.resonance_available():
                    return
            except Exception:
                pass
            if time.monotonic() >= deadline:
                return
            self.wait(interval)

    def e_until_cd(self, timeout: float = 4.0, after: float = 0.0) -> None:
        import time

        deadline = time.monotonic() + timeout
        while True:
            self.press("e")
            try:
                self.task.next_frame()
                char = self.char()
                if char is not None and char.has_cd("resonance"):
                    break
            except Exception:
                pass
            if time.monotonic() >= deadline:
                break
            self.wait(0.4)
        self.wait(after)

    # ---- 内部 ----

    def status(self, message: str) -> None:
        if self.status_callback:
            try:
                self.status_callback(message)
            except Exception:
                pass

    def _interaction(self):
        if self.stop_event.is_set():
            raise StopPlayback
        interaction = self.task.executor.interaction
        if interaction is None:
            raise StopPlayback
        return interaction

    def _checked_cast(self, action, fallback_key: str) -> bool:
        """用角色原语释放技能；角色不可用或原语异常时退化为单按。"""
        from src.task.BaseCombatTask import NotInCombatException

        char = self.char()
        if char is not None:
            try:
                action(char)
                return True
            except StopPlayback:
                raise
            except NotInCombatException:
                self.status("战斗状态变化，继续执行")
                return True
            except Exception:
                pass
        if self.stop_event.is_set():
            raise StopPlayback
        self.press(fallback_key)
        return False
