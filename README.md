<div align="center">
  <h1>Wuwa Pilot</h1>
  <p>面向《鸣潮》的图像识别自动化工具，新增社区连段轴识别与自动执行。</p>

  [![版本](https://img.shields.io/badge/version-beta1.0-orange)](https://github.com/etg227/wuwa_pilot/releases)
  [![平台](https://img.shields.io/badge/platform-Windows-blue)](#运行要求)
  [![许可证](https://img.shields.io/badge/license-AGPL--3.0-green)](LICENSE.txt)
</div>

> [!WARNING]
> 本项目会模拟键盘和鼠标操作，属于第三方自动化工具，可能违反游戏规则并导致账号处罚。请先阅读本文的风险说明，并只在能够承担风险的账号与场景中使用。

## 下载

前往 [GitHub Releases](https://github.com/etg227/wuwa_pilot/releases) 下载最新版本。

- 当前测试版：`beta1.0`
- Windows 用户优先下载文件名包含 `setup.exe` 的安装包。
- 不熟悉源码运行的用户不要下载 GitHub 自动生成的 `Source code` 压缩包。
- 测试版未使用原项目的商业签名密钥，Windows 可能显示未知发布者提示；请只从本仓库 Releases 下载。

## beta1.0 新功能：连段轴

Wuwa Pilot 可以读取 [WWCOMBO 社区](https://nova.fb520.site/) 发布的 `.wwcombo.json` 连段轴，将其中的动作、时间点、持续时间和按键绑定转换成实际游戏输入。

支持的核心能力：

- 从社区轴 ID、详情链接、下载链接或本地文件导入。
- 自动识别普攻、重击、共鸣技能、声骸、共鸣解放、闪避、跳跃和 1/2/3 切人。
- 自动采用 Wuwa Pilot“游戏热键”中的本机按键设置，未知动作可在映射表中手动指定。
- 普攻动作块按设定间隔连点；重击和长按闪避会按轴记录的持续时间按住后释放。
- 按单调时钟执行重叠动作，避免把可并行动作错误地串行播放。
- 实时显示玩家当前按住的键和程序正在输出的动作。
- 点击“停止并释放按键”或按 `F10`，会立即停止并释放所有仍按住的键。

### 使用方法

1. 启动 Wuwa Pilot 并连接《鸣潮》游戏窗口。
2. 在左侧菜单打开“连段轴”。
3. 粘贴社区轴的 `wwc_...` ID/链接，或选择本地 `.wwcombo.json` 文件。
4. 检查“动作映射”。如果游戏内改过键位，请确认“实际输出”与游戏设置一致。
5. 根据需要调整播放速度、倒计时和普攻连点间隔。
6. 点击“执行连段轴”。任务会进入 Wuwa Pilot 的统一任务队列，倒计时结束后开始输出。
7. 发现画面、站位或时间不对时，立即按 `F10` 停止。

映射表接受以下格式：

| 格式 | 含义 |
|---|---|
| `e` | 轻触 E |
| `lshift:hold` | 长按左 Shift |
| `mouse:left` | 单击鼠标左键 |
| `mouse:left:repeat` | 在动作持续时间内连续点击鼠标左键 |
| `mouse:right:hold` | 长按鼠标右键 |

目前兼容 WWCOMBO v1～v3，并兼容早期社区文件中的 `MouseRightHoid` 历史拼写。

## 原有功能

本项目保留 OK-WW 的主要自动化能力，包括：

- 图像识别驱动的自动战斗与角色识别。
- 日常、声骸、无音区、模拟领域等任务。
- 16:9 多分辨率支持，最低 1280×720。
- 支持后台窗口交互，具体能力取决于所选输入方式。
- 自定义角色代码与游戏热键设置。

## 运行要求

- Windows 10/11 64 位。
- 《鸣潮》PC 客户端。
- 建议游戏稳定运行在 60 FPS；轴的实际效果会受到帧率、延迟、角色配置、敌人位置和网络状态影响。
- 建议使用 16:9 分辨率，最低 1280×720。
- 游戏内修改过的热键应同步到 Wuwa Pilot 设置。
- 实时按键监听或前台输入模式可能需要管理员权限。

## 常见问题

### 导入后提示动作无法识别

社区轴可能使用了自定义动作或鼠标侧键。请在“动作映射”的“实际输出”列填写 Wuwa Pilot 支持的按键格式。

### 执行节奏与视频不同

先确认游戏能稳定在 60 FPS，并把播放速度保持在 `1.0×`。网络延迟、角色共鸣链、武器、声骸和站位都可能改变动作时长；必要时小幅调整播放速度或重新选择更适合当前配置的轴。

### 停止后角色仍在移动或按键未释放

先按 `F10`，再松开实体键盘上的对应按键。如果输入后端或游戏进程失去响应，请切回游戏窗口手动轻触一次该键。执行器会在正常停止和异常路径中主动释放它管理的全部长按输入。

### 杀毒软件或 SmartScreen 报警

自动化程序需要模拟输入，测试版又没有原项目的数字签名，可能触发安全软件提示。请核对下载地址必须位于 `github.com/etg227/wuwa_pilot/releases`；无法确认来源时不要运行。

## 从源码运行

推荐使用 Python 3.12：

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

运行连段轴测试：

```bash
python -m unittest tests.TestAxisChart tests.TestAxisRunner -v
```

## 项目关系与致谢

Wuwa Pilot 基于 [ok-oldking/ok-wuthering-waves](https://github.com/ok-oldking/ok-wuthering-waves) 二次开发，自动化框架来自 [ok-script](https://ok-script.com)。连段轴文件格式与社区内容来自 [WWCOMBO 社区](https://nova.fb520.site/)。

感谢原项目作者、OK-Script、WWCOMBO 工具与所有社区轴作者。社区轴归各自作者所有，本项目只解析用户主动导入的文件。

## 许可证与风险说明

本项目沿用 [AGPL-3.0](LICENSE.txt) 许可证，免费开源，禁止冒充官方或对免费软件进行欺诈性收费。

本软件不读取游戏内存、不修改游戏文件，但会模拟玩家输入。游戏运营方可能将自动战斗、宏脚本或其他第三方自动化认定为违规行为。使用者应自行了解并遵守游戏规则；因使用本软件造成的账号、数据或设备损失，由使用者自行承担。