# Privacy & Data Handling

WeMemoir is designed with **local-first privacy** as a core principle. This document explains how your data is handled and what you should know before using the tool.

## Core Privacy Principles

1. **All processing happens on your machine.** WeMemoir does not upload chat records to any remote server, cloud API, or third-party service.
2. **Your data stays in your specified output directory.** WeMemoir does not maintain a central database of imported records.
3. **No external network calls** are made during import, cleaning, memoir generation, or skill export — unless you explicitly configure an AI API key for enhanced features.
4. **You control what gets deleted.** WeMemoir provides CLI flags for cleaning temporary files and removing imported data.

## What WeMemoir Does NOT Do

- ❌ Does not call WeChat API or any messaging platform API
- ❌ Does not send messages automatically
- ❌ Does not decrypt WeChat databases or extract credentials
- ❌ Does not access your phone or desktop chat client directly
- ❌ Does not collect telemetry, usage stats, or error reports
- ❌ Does not store or log your imported chat content

## Handling Sensitive Chat Data

Since WeMemoir processes real conversation records, consider these precautions:

- **Use the `--out` flag** to control exactly where output files are written
- **Review generated memoirs** before sharing — they may contain identifying information about conversation partners
- **Do not commit imported data** to public repositories (add `data/` and `output/` to `.gitignore`)
- **Use the `examples/` directory** for testing — it contains synthetic sample data only
- **Delete temporary files** after use: `rm -rf data/ output/`

## AI / LLM Integration

When using WeMemoir's AI-powered features (e.g., enhanced memoirs via API):

- Your chat content is **only sent to the API you configure**, not to WeMemoir servers
- Use local models (Ollama, llama.cpp) for fully offline operation
- If using cloud APIs, review their privacy policy for data handling practices

## Export & Portability

All WeMemoir output is **plain Markdown and standard JSON files** — no proprietary formats. You can:

- Open `.md` files in any text editor
- Import `.json` exports into other tools
- Archive or delete output files at any time
- Process files with standard Unix tools (`grep`, `sed`, `jq`, etc.)

## Responsible Use

- Process only chat records you have **legal right to access and export**
- Respect the privacy of conversation partners — do not publish memoirs without consent
- Generated Skill packages (`AGENTS.md`, `SKILL.md`) may contain personal interaction patterns — review before sharing

---

*WeMemoir is a tool for personal reflection and memory preservation. Use it responsibly.*
