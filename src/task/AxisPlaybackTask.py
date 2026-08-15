import threading

from PySide6.QtCore import QObject, Signal

from src.axis.AxisChart import AxisChart, OutputBinding
from src.axis.AxisRunner import AxisEvent, AxisOutput, AxisRunner, build_axis_events
from src.axis.VisualSync import wait_for_switch_sync
from src.task.BaseWWTask import BaseWWTask


class AxisPlaybackSignals(QObject):
    status_changed = Signal(str)
    action_changed = Signal(int, str, str)
    progress_changed = Signal(int)
    timing_changed = Signal(float, float, float)
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
    """由“椰果启动器”页面配置并加入统一任务队列的隐藏任务。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "椰果启动器"
        self.description = "按 WWCOMBO 时间线启动角色连段"
        self.visible = False
        self.signals = AxisPlaybackSignals()
        self._settings_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._playback_settings = None
        self._visual_sync = False
        self._sync_timeout = 1.5
        self._last_timing = None

    def configure_playback(
        self,
        chart: AxisChart,
        mappings: dict[str, OutputBinding | None],
        speed: float,
        countdown: int,
        repeat_interval_ms: int,
        include_start_trigger: bool,
        visual_sync: bool = False,
        sync_timeout: float = 1.5,
    ) -> None:
        if self.running or self.enabled:
            raise RuntimeError("已有椰果启动器任务正在执行或等待执行")
        events = build_axis_events(chart, mappings, repeat_interval_ms, include_start_trigger)
        if not events:
            raise ValueError("这个轴没有可执行的已识别动作")
        with self._settings_lock:
            self._playback_settings = (chart, events, float(speed), int(countdown))
            self._visual_sync = bool(visual_sync)
            self._sync_timeout = max(0.2, float(sync_timeout))
        self._stop_event.clear()
        self._last_timing = None

    def request_stop(self) -> None:
        self._stop_event.set()
        if self.enabled and not self.running:
            self.disable()
            self.signals.playback_finished.emit(True, "已从任务队列移除")

    def run(self):
        with self._settings_lock:
            settings = self._playback_settings
        if settings is None:
            raise RuntimeError("尚未配置椰果启动器")
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
                sync_callback=self._sync_after_switch if self._visual_sync else None,
                timing_callback=self._on_timing,
            )
            message = "已停止并释放全部按键" if cancelled else "椰果启动器执行完成"
            if self._last_timing is not None:
                _, average_ms, max_ms = self._last_timing
                message += f"｜平均偏差 {average_ms:.1f} ms，最大 {max_ms:.1f} ms"
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

    def _on_timing(self, _event: AxisEvent, current_ms: float, average_ms: float, max_ms: float) -> None:
        self._last_timing = (current_ms, average_ms, max_ms)
        self.signals.timing_changed.emit(current_ms, average_ms, max_ms)

    def _sync_after_switch(self, event: AxisEvent) -> bool:
        if event.operation != "tap" or event.move_id not in {"switch_1", "switch_2", "switch_3"}:
            return False

        expected_slot = int(event.move_id[-1]) - 1
        synced = wait_for_switch_sync(
            self.next_frame,
            self.in_team,
            expected_slot,
            self._stop_event,
            self._sync_timeout,
        )

        if not synced and not self._stop_event.is_set():
            self.signals.status_changed.emit(
                f"切人视觉同步超时：{event.move_id}，继续按时间轴执行"
            )
        # 这个事件仍然是同步点；把等待时间计入时间轴，避免后续动作集中补发。
        return True
