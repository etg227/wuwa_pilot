import threading

from PySide6.QtCore import QObject, Signal

from src.axis.AxisChart import AxisChart, OutputBinding
from src.axis.AxisRunner import AxisEvent, AxisOutput, AxisRunner, build_axis_events
from src.task.BaseWWTask import BaseWWTask


class AxisPlaybackSignals(QObject):
    status_changed = Signal(str)
    action_changed = Signal(int, str, str)
    progress_changed = Signal(int)
    playback_finished = Signal(bool, str)


class InteractionAxisOutput(AxisOutput):
    """直接使用 OK-Script 输入后端，确保停止清理不受任务状态影响。"""

    def __init__(self, interaction):
        self.interaction = interaction

    def tap(self, binding: OutputBinding) -> None:
        if binding.kind == "mouse":
            self.interaction.click(-1, -1, move=False, down_time=0.015, key=binding.code)
        else:
            self.interaction.send_key(binding.code, 0.02)

    def press(self, binding: OutputBinding) -> None:
        if binding.kind == "mouse":
            self.interaction.mouse_down(-1, -1, key=binding.code)
        else:
            self.interaction.send_key_down(binding.code)

    def release(self, binding: OutputBinding) -> None:
        if binding.kind == "mouse":
            self.interaction.mouse_up(key=binding.code)
        else:
            self.interaction.send_key_up(binding.code)


class AxisPlaybackTask(BaseWWTask):
    """由“连段轴”页面配置并加入统一任务队列的隐藏任务。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "连段轴播放"
        self.description = "按 wwcombo 时间线执行角色连段"
        self.visible = False
        self.signals = AxisPlaybackSignals()
        self._settings_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._playback_settings = None

    def configure_playback(
        self,
        chart: AxisChart,
        mappings: dict[str, OutputBinding | None],
        speed: float,
        countdown: int,
        repeat_interval_ms: int,
        include_start_trigger: bool,
    ) -> None:
        if self.running or self.enabled:
            raise RuntimeError("已有连段轴正在执行或等待执行")
        events = build_axis_events(chart, mappings, repeat_interval_ms, include_start_trigger)
        if not events:
            raise ValueError("这个轴没有可执行的已识别动作")
        with self._settings_lock:
            self._playback_settings = (chart, events, float(speed), int(countdown))
        self._stop_event.clear()

    def request_stop(self) -> None:
        self._stop_event.set()
        if self.enabled and not self.running:
            self.disable()
            self.signals.playback_finished.emit(True, "已从任务队列移除")

    def run(self):
        with self._settings_lock:
            settings = self._playback_settings
        if settings is None:
            raise RuntimeError("尚未配置连段轴")
        chart, events, speed, countdown = settings

        try:
            for remaining in range(countdown, 0, -1):
                self.signals.status_changed.emit(f"{remaining} 秒后开始，请切回游戏")
                if self._stop_event.wait(1):
                    self.signals.playback_finished.emit(True, "已停止")
                    return

            interaction = self.executor.interaction
            if interaction is None:
                raise RuntimeError("游戏输入设备尚未连接")
            interaction.on_run()
            self.signals.status_changed.emit(f"正在执行：{chart.title}")
            runner = AxisRunner()
            cancelled = runner.run(
                events,
                InteractionAxisOutput(interaction),
                self._stop_event,
                speed=speed,
                action_callback=self._on_action,
                progress_callback=lambda value: self.signals.progress_changed.emit(round(value)),
            )
            message = "已停止并释放全部按键" if cancelled else "连段轴执行完成"
            self.signals.playback_finished.emit(cancelled, message)
        except Exception as error:
            self.signals.playback_finished.emit(True, f"执行失败：{error}")
            raise
        finally:
            with self._settings_lock:
                self._playback_settings = None

    def on_destroy(self):
        self._stop_event.set()

    def _on_action(self, event: AxisEvent) -> None:
        self.signals.action_changed.emit(event.step_index, event.label, event.binding.display_text)
