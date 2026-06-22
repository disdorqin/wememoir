# WeMemoir

本地优先的微信聊天记录整理、清洗与回忆录生成工具。

WeMemoir 只处理**用户自己合法导出的聊天记录文件**，所有操作默认在本地完成，不上传云端、不自动发消息、不做数据库破解。

## 功能

- **多格式导入**：CSV / JSON / TXT / HTML（适配 wechat-cli、WechatExporter、WxEcho 等导出格式）。
- **智能清洗**：删除无意义语气词、系统通知、重复消息，合并连续短消息，还原成“正常可读对话”。
- **回忆录生成**：按时间线自动划分章节（初识期、高频聊天期、转折期、稳定期等），输出标题、时间范围、关系阶段、代表性原话、情绪变化。
- **Highlights**：抽取第一次聊天、最长连续聊天、深夜聊天、反复话题、重要承诺、约定、争吵/和好、搞笑片段、回忆录标题候选。
- **AI Skill 包**：生成 contact / self / memoir 三类 Skill，支持 generic markdown、Claude SKILL.md、Codex AGENTS.md、Cursor .mdc。
- **本地 Web UI**：上传 → 预览 → 清洗 → 生成回忆录 / Skill → 下载。

## 安装

```bash
pip install -e .
```

## CLI 使用

```bash
# 导入聊天记录
wememoir import examples/sample_chat.csv --source auto --self-name Me --out data/imported.json

# 清洗成可读对话
wememoir clean data/imported.json --out output/cleaned_dialogue.md

# 生成回忆录
wememoir memoir data/imported.json --out output/memoir.md

# 生成 highlights
wememoir highlights data/imported.json --out output/highlights.md

# 生成 Codex AGENTS.md
wememoir skill data/imported.json --type contact --target codex --out output/AGENTS.md

# 启动本地 Web UI
wememoir web
```

## Web UI 使用

```bash
wememoir web
```

浏览器打开 `http://127.0.0.1:5000`，上传聊天记录文件后：

1. 预览原始消息
2. 一键清洗
3. 一键生成回忆录
4. 一键生成 Skill
5. 下载 Markdown / JSON / ZIP

## 支持格式

| 格式 | 说明 |
|------|------|
| CSV | `timestamp,sender,content` 三列，可选 `message_type` |
| JSON | WeMemoir 内部格式或消息数组 |
| TXT | 常见微信文本导出：`YYYY-MM-DD HH:MM:SS 发送者: 内容` 或 `[发送者] 内容` |
| HTML | 通过文本提取兼容常见 HTML 导出 |

## 隐私声明

- **本地优先**：所有解析、清洗、生成步骤默认在本地运行，不调用远程 API，不上传聊天记录。
- **用户数据归用户**：导入的聊天记录和生成的文件都保存在用户指定的本地目录。
- **不自动发消息**：WeMemoir 不会调用微信接口发送任何消息。
- **第一版只做导入适配器**：不实现微信数据库破解、密钥提取或任何非授权访问。

## 合规声明

- 请只处理**您自己拥有合法权利导出和查看**的聊天记录。
- 请尊重聊天对方的隐私，生成的 Skill 包、回忆录等文件不要随意公开或共享。
- 本项目仅供个人整理、纪念与学习使用，开发者不对滥用行为负责。

## Roadmap

- **v0.1**：导入 + 清洗 + Markdown 回忆录
- **v0.2**：Web UI
- **v0.3**：Skill 导出
- **v0.4**：接入 wechat-cli / WeLink / WechatExporter 作为可选本地适配器
- **v0.5**：时间线图、关系图、聊天 DNA、纪念日卡片
- **v0.6**：打包 Windows/macOS 桌面应用

## 许可证

MIT License
