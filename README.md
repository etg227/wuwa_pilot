<div align="center">
  <h1>Wuwa Pilot</h1>
  <p>基于 OK-WW 的《鸣潮》图像识别自动化工具，新增 WWCOMBO 社区连段轴导入与执行。</p>

  [![版本](https://img.shields.io/badge/version-beta1.0-orange)](https://github.com/etg227/wuwa_pilot/releases)
  [![平台](https://img.shields.io/badge/platform-Windows-blue)](#运行要求)
  [![许可证](https://img.shields.io/badge/license-AGPL--3.0-green)](LICENSE.txt)
</div>

> [!WARNING]
> 本项目会模拟键盘和鼠标操作，属于第三方自动化工具，可能违反游戏规则并导致账号处罚。请自行判断并承担使用风险。

## 下载

前往 [GitHub Releases](https://github.com/etg227/wuwa_pilot/releases) 下载测试版。

- 当前版本：`beta1.0`
- Windows 用户优先下载文件名包含 `setup.exe` 的安装包。
- 不熟悉源码运行的用户不要下载 GitHub 自动生成的 `Source code` 压缩包。
- 测试版未使用原项目的商业签名，Windows 可能显示未知发布者提示。

## 连段轴

Wuwa Pilot 可以读取 [WWCOMBO 社区](https://nova.fb520.site/) 的 `.wwcombo.json` 文件，并按照时间轴转换为实际游戏输入。

主要功能：

- 支持社区轴 ID、链接和本地文件导入。
- 支持普攻、重击、共鸣技能、声骸、共鸣解放、闪避、跳跃和 1/2/3 切人。
- 自动使用 Wuwa Pilot 的游戏热键，也可以手动修改动作映射。
- 支持轻触、长按、连续点击和重叠动作。
- 使用单调时钟执行时间轴，减少长时间运行产生的累计偏差。
- 可选切人视觉同步，确认角色 UI 后再继续后续时间轴。
- 实时显示当前、平均和最大时间偏差，方便实机校准。
- 支持 `F10` 紧急停止，并在停止或异常时释放长按输入。

### 使用

1. 启动 Wuwa Pilot 并连接《鸣潮》窗口。
2. 打开左侧“连段轴”。
3. 粘贴 `wwc_...` ID/链接，或选择本地 `.wwcombo.json`。
4. 检查动作映射和实际按键。
5. 调整播放速度、倒计时、普攻连点间隔和视觉同步。
6. 点击“执行连段轴”。
7. 需要立即停止时按 `F10`。

动作映射示例：

| 格式 | 含义 |
|---|---|
| `e` | 轻触 E |
| `lshift:hold` | 长按左 Shift |
| `mouse:left` | 单击鼠标左键 |
| `mouse:left:repeat` | 连续点击鼠标左键 |
| `mouse:right:hold` | 长按鼠标右键 |

目前兼容 WWCOMBO v1～v3，并兼容早期文件中的 `MouseRightHoid` 历史拼写。视觉同步目前主要用于切人动作，其他技能和动画仍以轴时间为准。

## 原有功能

本项目保留 OK-WW 的主要能力：

- 图像识别自动战斗与角色识别。
- 日常、声骸、无音区、模拟领域等任务。
- 16:9 多分辨率支持，最低 1280×720。
- 后台窗口交互。
- 自定义角色代码与游戏热键。

## 运行要求

- Windows 10/11 64 位。
- 《鸣潮》PC 客户端。
- 建议稳定运行在 60 FPS。
- 建议使用 16:9 分辨率，最低 1280×720。
- 游戏内修改过的按键请同步到 Wuwa Pilot。

连段轴效果会受到帧率、延迟、角色配置、敌人位置、站位和网络状态影响。

## 从源码运行

推荐 Python 3.12：

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

调试模式：

```bash
python main_debug.py
```

连段轴测试：

```bash
python -m unittest tests.TestAxisChart tests.TestAxisRunner -v
```

## 项目说明

Wuwa Pilot 基于 [ok-oldking/ok-wuthering-waves](https://github.com/ok-oldking/ok-wuthering-waves) 二次开发，自动化框架来自 [OK-Script](https://ok-script.com)，连段轴格式与社区内容来自 [WWCOMBO 社区](https://nova.fb520.site/)。

本项目在功能设计、代码实现、重构、测试和文档整理过程中使用了 AI 辅助。AI 仅作为开发工具使用，最终代码、发布内容和维护决定由项目维护者审核并负责。

感谢原项目作者、OK-Script、WWCOMBO 工具及所有社区轴作者。社区轴内容归各自作者所有，本项目只解析用户主动导入的文件。

## 许可证与风险

本项目沿用 [AGPL-3.0](LICENSE.txt) 许可证，免费开源。

本软件不读取游戏内存、不修改游戏文件，但会模拟玩家输入。游戏运营方可能将自动战斗、宏脚本或其他第三方自动化认定为违规行为。使用者应自行了解并遵守游戏规则，并承担由此产生的账号、数据或设备风险。
