# Wuwa Pilot 贡献指南

感谢你愿意改进 Wuwa Pilot。提交代码前请先搜索现有 Issue，确认没有重复工作；较大的功能或行为变更建议先开 Issue 说明目标和范围。

## 开发环境

推荐使用 Windows 10/11 和 Python 3.12：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

运行全部测试：

```powershell
.\run_tests.ps1
```

## 提交要求

- 每个提交只处理一个清晰主题，不混入日志、缓存、截图或个人配置。
- 涉及识别、输入、任务流程或界面的修改，需要说明验证环境和结果。
- 新增功能应补充测试；修复问题应尽可能补充能复现旧行为的回归测试。
- 用户可见文案优先维护简体中文，并同步必要的翻译键。
- 提交前确认程序可以启动，并运行与改动相关的测试。

## Pull Request

PR 中请说明修改目的、实现范围、测试结果和已知限制。界面或识别结果发生变化时，请附截图或短录屏。提交代码即表示你同意按本项目的 AGPL-3.0 许可证发布贡献。
