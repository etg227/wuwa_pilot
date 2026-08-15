<div align="center">
  <h1>Wuwa Pilot</h1>
  <p>基于 OK-WW 的《鸣潮》图像识别自动化工具，增加 WWCOMBO 社区连段轴导入、预览与执行。</p>

  [![版本](https://img.shields.io/github/v/release/etg227/wuwa_pilot?include_prereleases&label=%E7%89%88%E6%9C%AC)](https://github.com/etg227/wuwa_pilot/releases)
  [![平台](https://img.shields.io/badge/platform-Windows-blue)](#运行要求)
  [![许可证](https://img.shields.io/badge/license-AGPL--3.0-green)](LICENSE.txt)
</div>

> [!WARNING]
> Wuwa Pilot 会模拟键盘和鼠标操作，属于第三方自动化工具，可能违反游戏规则并导致账号处罚。请在使用前了解相关规则，并自行承担账号、数据与设备风险。

## 下载

前往 [GitHub Releases](https://github.com/etg227/wuwa_pilot/releases) 下载名称包含 `setup.exe` 的在线安装包。

- 不要下载 GitHub 自动生成的 `Source code` 压缩包和 `wuwa-win32.zip`。
- 安装包没有商业代码签名，Windows 可能显示未知发布者提示；请只从本仓库下载。
- 早期的 `beta1.0`、`beta1.1` 安装包直接克隆完整开发仓库（含大量测试文件，体积大、下载易失败），已经废弃；装过的用户请重新下载新安装包。

## 发布流程

与上游 OK-WW 相同：

- 安装与自动更新走独立的更新仓库 [wuwa_pilot-update](https://github.com/etg227/wuwa_pilot-update)。打 tag 后 CI 跑全部测试，把 `deploy.txt` 列出的运行时文件同步过去，用户不需要克隆本开发仓库。
- 版本 tag 必须写成 `v主.次.补丁` 或 `v主.次.补丁-beta.N`，例如 `v1.0.0-beta.2`、`v1.0.0`。安装器只认这种格式；`beta1.0` 这类旧写法安装器无法识别为版本，已停用。
- 只有正式版 tag（不带 `-beta`）才构建安装包并发布 Release；beta tag 只同步更新仓库，供已安装用户升级。
- `config.py` 里的 `version` 固定为 `dev`，发布时由 CI 自动写入 tag。
- 不移动或覆盖已经发布的 tag。

## WWCOMBO 连段轴

Wuwa Pilot 可以读取 [WWCOMBO 社区](https://nova.fb520.site/) 的 `.wwcombo.json` 文件，并按照时间轴转换为实际游戏输入。

主要能力：

- 支持社区轴 ID、链接和本地文件导入。
- 支持 WWCOMBO v1～v3，并兼容早期文件中的 `MouseRightHoid` 历史拼写。
- 支持普攻、重击、共鸣技能、声骸、共鸣解放、闪避、跳跃和 1/2/3 切人。
- 自动读取 Wuwa Pilot 的游戏热键，也允许手动修改动作映射。
- 支持轻触、长按、连续点击和重叠动作。
- 使用单调时钟执行时间轴，显示当前、平均与最大 timing drift。
- 可选切人视觉同步：确认角色 UI 后再继续后续时间轴。
- 监听玩家输入和程序输出，方便实机检查动作。
- 支持 `F10` 紧急停止；停止或异常时会释放全部长按输入。

### 使用方法

1. 启动 Wuwa Pilot 并连接《鸣潮》窗口。
2. 打开左侧“连段轴”。
3. 粘贴 `wwc_...` ID/链接，或选择本地 `.wwcombo.json` 文件。
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

视觉同步目前主要用于切人动作，其他技能和动画仍以轴时间为准。轴的实际效果会受到帧率、延迟、角色配置、敌人位置、站位与网络状态影响。

## OK-WW 原有能力

Wuwa Pilot 保留 OK-WW 的主要能力，包括：

- 图像识别自动战斗与角色识别。
- 日常、声骸、无音区和模拟领域等任务。
- 16:9 多分辨率支持，最低 1280×720。
- 后台窗口交互。
- 自定义角色代码与游戏热键。

## 运行要求

- Windows 10/11 64 位。
- 《鸣潮》PC 客户端。
- 建议稳定运行在 60 FPS。
- 建议使用 16:9 分辨率，最低 1280×720。
- 游戏内修改过的按键必须同步到 Wuwa Pilot。

## 从源码运行

推荐 Python 3.12：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

调试模式：

```powershell
python main_debug.py
```

连段轴测试：

```powershell
python -m unittest tests.TestAxisChart tests.TestAxisRunner -v
```

## 项目来源与致谢

Wuwa Pilot 是 [ok-oldking/ok-wuthering-waves](https://github.com/ok-oldking/ok-wuthering-waves) 的二次开发项目。本次干净重建以该项目 `master` 的 `ca0be964bed6a7cd5553733452c0605a56312483` 为源码快照；详细记录见 [UPSTREAM.md](UPSTREAM.md)。自动化框架来自 [OK-Script](https://ok-script.com)，连段轴格式与社区内容来自 [WWCOMBO](https://nova.fb520.site/)。

感谢 OK-WW 原作者、OK-Script、WWCOMBO，以及所有分享连段轴的社区作者。社区轴内容归各自作者所有，Wuwa Pilot 只解析用户主动导入的文件。

本项目在功能设计、代码实现、重构、测试和文档整理过程中使用了 AI 辅助。AI 仅作为开发工具，最终代码、发布内容和维护决定由项目维护者审核并负责。

## 上游同步

本仓库不合并或变基 `ok-oldking/ok-wuthering-waves` 的 Git 历史。需要同步时：

1. 下载上游最新 `master` 的干净源码快照，不复制其 `.git` 目录。
2. 以 [UPSTREAM.md](UPSTREAM.md) 记录的快照 SHA 为基线比较文件变化。
3. 将上游变化应用到临时分支，解决与连段轴功能的冲突并运行测试。
4. 审核无误后，以一个简单提交 `sync upstream` 合入 `master`。
5. 更新 `UPSTREAM.md` 中的快照 SHA。

不要执行会把上游提交图带入本仓库的 `git merge upstream/master` 或 `git rebase upstream/master`。

## 许可证与风险

本项目保留原项目的版权与来源说明，并沿用 [GNU Affero General Public License v3.0](LICENSE.txt)。分发修改版本或通过网络提供其功能时，请遵守 AGPL-3.0 的源码提供义务。

本软件不读取游戏内存、不修改游戏文件，但会模拟玩家输入。游戏运营方可能将自动战斗、宏脚本或其他第三方自动化认定为违规行为。使用者应自行了解并遵守游戏规则，并承担由此产生的全部风险。
