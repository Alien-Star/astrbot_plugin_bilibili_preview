# 📺 BiliBili 预览

![版本](https://img.shields.io/badge/version-1.1.0-blue.svg)
![AstrBot版本](https://img.shields.io/badge/AstrBot-%3E%3D4.16.0-green.svg)
![许可证](https://img.shields.io/badge/license-MIT-orange.svg)

**🔗 自动解析BV/AV/短链接 · 💬 支持QQ小程序卡片 · 🖼️ 图文预览 · ⚡ 内存缓存**

> 📌 本插件仅用于自用练手，由 AI 辅助编写，功能持续完善中。

---

## ✨ 功能亮点

- **🔗 多格式识别**：BV号、AV号、b23.tv 短链接
- **💬 QQ小程序解析**：直接识别转发的B站卡片
- **🧠 智能缓存**：内存缓存，避免重复请求
- **🖼️ 图文预览**：文本摘要 + 封面图片
- **📊 数据格式化**：播放/弹幕/点赞自动转万/亿
- **⚙️ 可配置**：通过 `metadata.yaml` 开关功能

---

## 📖 使用方法

在群里发送以下任意格式的内容，机器人会自动回复预览信息：

```text
# 纯文本链接
https://www.bilibili.com/video/BV1xx411c7mD
b23.tv/abc123
BV1xx411c7mD
av123456

# 小程序分享（QQ转发）
直接转发B站视频卡片即可

```
```text
示例输出
🎬 【全自动B站预览插件开发教程】
👤 UP主：技术宅
📊 播放：12.3万  💬 弹幕：245  ❤️ 点赞：1.2万
⏱️ 时长：15:30  📁 分区：科技
📝 简介：本期视频手把手教你写AstrBot插件...
🔗 https://www.bilibili.com/video/BV1xx411c7mD
[封面图片]
