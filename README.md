# openGym × MiniMax-M3 安卓兼容版

本仓库仅用于从 [openGym 官方开源项目](https://github.com/DuarteSantos8/openGym) 编译 Android 测试版 APK，并修复 MiniMax-M3 在 **OpenAI-Compatible Endpoint** 模式下不支持 `response_format` 的问题。

- **不会**在仓库存储 MiniMax API Key 或个人训练数据。
- **仅 MiniMax-M3** 的请求移除 `response_format`；保留 JSON 格式提示与训练计划安全校验。
- APK 使用 `ch.duartesantos.opengym.test` 应用 ID，可与正式版并存；正式版数据不会自动同步到测试版。
- 此版本是第三方修改的测试版，不代表 openGym 官方，也尚未经过你的手机和 MiniMax API 的真实验证。

自动构建：打开仓库 Actions 标签，找到 *Build openGym MiniMax-M3 APK*。构建成功后，可从 Actions 的 Artifacts 或 Releases 下载。

测试版首次配置：AI 教练 → 使用自己的 API Key → OpenAI-Compatible Endpoint → 地址 `https://api.minimaxi.com/v1` → 模型 `MiniMax-M3`。

补丁代码和构建过程公开可查。上游 openGym 的许可是 AGPL-3.0-or-later，修改版继承适用的许可义务。
