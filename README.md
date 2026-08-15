<div align="center">
  <img src="icons/icon.png" alt="Wuwa Pilot Logo" width="220">
  <h1>Wuwa Pilot</h1>
  <p>《鸣潮》图像识别自动化工具，支持日常任务、自动战斗与 WWCOMBO 椰果启动器。</p>

  [![版本](https://img.shields.io/github/v/release/etg227/wuwa_pilot?include_prereleases&label=%E7%89%88%E6%9C%AC)](https://github.com/etg227/wuwa_pilot/releases)
  [![平台](https://img.shields.io/badge/platform-Windows-blue)](#运行要求)
  [![许可证](https://img.shields.io/badge/license-AGPL--3.0-green)](LICENSE.txt)
</div>

> [!WARNING]
> Wuwa Pilot 会模拟键盘和鼠标操作，属于第三方自动化工具，可能违反游戏规则并导致账号处罚。请在使用前了解相关规则，并自行承担账号、数据与设备风险。

## 下载与安装

前往 [GitHub Releases](https://github.com/etg227/wuwa_pilot/releases) 下载名称包含 `setup.exe` 的安装包。

- 不要下载 GitHub 自动生成的 `Source code` 压缩包或 `wuwa-win32.zip`。
- 安装包没有商业代码签名，Windows 可能显示“未知发布者”；请确认文件来自本仓库。
- 安装后的版本支持自动更新。
- 使用早期 `beta1.0`、`beta1.1` 安装包的用户，请重新下载安装最新版。

## 主要功能

- 图像识别自动战斗与角色识别。
- 日常、声骸、无音区和模拟领域等任务。
- 后台窗口交互。
- 自定义角色代码与游戏热键。
- 支持 16:9 多分辨率，最低 1280×720。
- 导入、预览并执行 WWCOMBO 社区轴。

## 椰果启动器

椰果启动器可以读取 [WWCOMBO 社区](https://nova.fb520.site/) 的 `.wwcombo.json` 文件，并将时间轴转换为实际游戏输入。

### 支持能力

- 通过社区轴 ID、链接或本地文件导入。
- 支持 WWCOMBO v1～v3。
- 支持普攻、重击、共鸣技能、声骸、共鸣解放、闪避、跳跃和 1/2/3 切人。
- 导入后可以检查并手动修改每个动作的实际输出映射。
- 支持轻触、长按、连续点击和重叠动作。
- 显示当前、平均与最大时间偏差。
- 切人后可通过角色 UI 进行视觉同步；识别失败或超时会自动继续时间轴。
- 支持 `F10` 紧急停止，并在停止或异常时释放全部长按输入。

### 使用方法

1. 启动 Wuwa Pilot 并连接《鸣潮》窗口。
2. 打开左侧“椰果启动器”。
3. 粘贴 `wwc_...` ID 或链接，也可以选择本地 `.wwcombo.json` 文件。
4. 检查动作映射与实际按键。
5. 设置播放速度、倒计时、普攻连点间隔和视觉同步。
6. 点击“启动椰果”。
7. 需要立即停止时按 `F10`。

### 动作映射

| 格式 | 含义 |
| --- | --- |
| `e` | 轻触 E |
| `lshift:hold` | 长按左 Shift |
| `mouse:left` | 单击鼠标左键 |
| `mouse:left:repeat` | 连续点击鼠标左键 |
| `mouse:right:hold` | 长按鼠标右键 |

视觉同步主要用于切人动作，其他技能和动画仍以轴时间为准。实际效果会受到帧率、延迟、角色配置、敌人位置、站位和网络状态影响。

## 运行要求

- Windows 10/11 64 位。
- 《鸣潮》PC 客户端。
- 建议使用 16:9 分辨率，最低 1280×720。
- 建议游戏稳定运行在 60 FPS。
- 游戏内修改过的按键需要同步到 Wuwa Pilot。

## 从源码运行

开发环境推荐 Python 3.12：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

启动调试模式：

```powershell
python main_debug.py
```

运行椰果启动器相关测试：

```powershell
python -m unittest tests.TestAxisPlaybackTask tests.TestAxisChart tests.TestAxisRunner -v
```

## 项目来源与致谢

Wuwa Pilot 基于 [ok-oldking/ok-wuthering-waves](https://github.com/ok-oldking/ok-wuthering-waves) 开发，自动化框架来自 [OK-Script](https://ok-script.com)，椰果启动器兼容 [WWCOMBO](https://nova.fb520.site/) 社区轴格式。

感谢 OK-WW、OK-Script、WWCOMBO 的开发者，以及所有分享社区轴的作者。社区轴内容归各自作者所有，Wuwa Pilot 只解析用户主动导入的文件。

## 使用过的开发工具与模型

本项目开发过程中使用了 AI 模型与开发工具进行辅助。

| AI 模型 |
| --- |
| ChatGPT |
| Claude |

## 许可证

本项目沿用 [GNU Affero General Public License v3.0](LICENSE.txt)。分发修改版本或通过网络提供其功能时，请遵守 AGPL-3.0 的相关要求。
