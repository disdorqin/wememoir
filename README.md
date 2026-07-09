# WeMemoir




![tests](https://github.com/disdorqin/wememoir/actions/workflows/test.yml/badge.svg)
本地优先的微信聊天记录整理、清洗与回忆录生成工具。
WeMemoir 只处理**用户自己合法导出的聊天记录文件**，所有操作默认在本地完成，不上传云端、不自动发消息、不做数据库破解。
## 当前状态
MVP 已可运行：支持 CSV / JSON / TXT / HTML 导入、对话清洗、回忆录生成、Highlights 抽取、AI Skill 包导出以及本地 Web UI。
## 快速开始
```bash
# 1. 克隆仓库并安装
pip install -e ".[dev]"
# 2. 导入示例聊天记录
wememoir import examples/sample_chat.csv --source auto --self-name Me --out data/imported.json
# 3. 清洗、生成回忆录与 Skill
wememoir clean data/imported.json --out output/cleaned_dialogue.md
wememoir memoir data/imported.json --out output/memoir.md
wememoir highlights data/imported.json --out output/highlights.md
wememoir skill data/imported.json --type contact --target codex --out output/AGENTS.md
```
## 功能
- **多格式导入**：CSV / JSON / TXT / HTML（适配 wechat-cli、WechatExporter、WxEcho 等导出格式）。
- **智能清洗**：删除无意义语气词、系统通知、重复消息，合并连续短消息，还原成“正常可读对话”。
- **回忆录生成**：按时间线自动划分章节（初识期、高频聊天期、转折期、稳定期等），输出标题、时间范围、关系阶段、代表性原话、情绪变化。
- **Highlights**：抽取第一次聊天、最长连续聊天、深夜聊天、反复话题、重要承诺、约定、争吵/和好、搞笑片段、回忆录标题候选。
- **AI Skill 包**：生成 contact / self / memoir 三类 Skill，支持 generic markdown、Claude SKILL.md、Codex AGENTS.md、Cursor .mdc。
- **本地 Web UI**：上传 → 预览 → 清洗 → 生成回忆录 / Skill → 下载。
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
## Demo 输出示例
清洗后的对话片段（`output/cleaned_dialogue.md`）：
```markdown
## 2023-01-01
[Me] 你好
[Alice] 你好呀
[Me] 你在吗？明天有空吗
[Alice] 有啊
[Me] 那我们一起吃个饭吧
[Alice] 好呀，那明天晚上七点见
[Me] 我答应你，一定准时到
```
回忆录片段（`output/memoir.md`）：
```markdown
## 初识期（2023-01-01 ~ 2023-01-01）
**主要事件**：本阶段共有 12 条消息。
**代表性原话**：
> [Me] 我答应你，一定准时到
> [Alice] 那明天晚上七点见
**情绪变化**：愉悦 4 次、平静 8 次。
```
Highlights 片段（`output/highlights.md`）：
```markdown
- **第一次聊天**：2023-01-01 10:00 [Me] 你好
- **最长连续聊天**：12 条，从 2023-01-01 10:00 到 2023-01-01 10:11
- **深夜聊天**：共 5 条，例如 2023-03-01 23:30 [Me] 还没睡吗
- **重要承诺**：2 条，例如 [Me] 我答应你，一定准时到
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
## 隐私与安全说明
- **本地优先**：所有解析、清洗、生成步骤默认在本地运行，不调用远程 API，不上传聊天记录。
- **用户数据归用户**：导入的聊天记录和生成的文件都保存在用户指定的本地目录。
- **不自动发消息**：WeMemoir 不会调用微信接口发送任何消息。
- **不破解数据库**：第一版只做“导入已有导出文件”的适配器，不实现微信数据库解密、密钥提取或任何非授权访问。
- **不上传云端**：不默认接入云端数据库，所有数据默认离线处理。
## 合规声明
- 请只处理**您自己拥有合法权利导出和查看**的聊天记录。
- 请尊重聊天对方的隐私，生成的 Skill 包、回忆录等文件不要随意公开或共享。
- 本项目仅供个人整理、纪念与学习使用，开发者不对滥用行为负责。
## CI
每次 push / pull_request 都会在 Python 3.9–3.12 上自动运行：
```bash
python -m pytest -q
wememoir --help
```
## Roadmap
- **v0.1**：导入 + 清洗 + Markdown 回忆录 ✅
- **v0.2**：Web UI ✅
- **v0.3**：Skill 导出 ✅
- **v0.4**：接入 wechat-cli / WeLink / WechatExporter 作为可选本地适配器
- **v0.5**：时间线图、关系图、聊天 DNA、纪念日卡片
- **v0.6**：打包 Windows/macOS 桌面应用
## 许可证
MIT License
