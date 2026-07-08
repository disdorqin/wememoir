# WeMemoir Privacy FAQ

WeMemoir processes your WeChat chat history. This FAQ explains what happens (and doesn't happen) with your data.

## Does WeMemoir upload my chat history anywhere?

**No.** All import, cleaning, memoir generation, and skill export run entirely on your local machine. There is no cloud sync, no telemetry, and no data egress.

## Does WeMemoir call external APIs?

**Not by default.** The core pipeline works fully offline. The only optional exception is the AI Skill export feature, which can format output for AI tools (Claude, Codex, Cursor) — but the formatted files stay on your machine.

## Does WeMemoir access WeChat directly?

**No.** WeMemoir only processes files *you* have already exported using third-party tools like WechatExporter, wechat-cli, or WxEcho. It does not interact with WeChat's database, network interface, or authentication system.

## What input formats are supported?

CSV, JSON, TXT, and HTML. See [the README](../README.md#support-formats) for the expected schema for each format.

## Can I delete my imported data?

**Yes.** All imported data and generated output files live in your local working directory. Delete the directory (or the individual files) and they are gone. WeMemoir maintains no external index or cache.

## Is the exported AI Skill pack safe to share?

**Use your judgment.** A Skill pack (`AGENTS.md`, `SKILL.md`, etc.) contains structured summaries of your chat history — including representative quotes, relationship stages, and behavioral patterns. Review the content before sharing it with anyone, including AI assistants that may have their own data policies.

## What about the other person's privacy?

WeMemoir processes conversations you are a party to. The generated memoir and highlights quote the other person's messages. We recommend:

- Not sharing the raw output publicly
- Redacting or anonymizing when sharing excerpts
- Being mindful of what you feed into AI assistants that may train on your data

## How does WeMemoir handle encryption?

The tool operates on exported plaintext files. If your export tool already produced encrypted files, decrypt them before importing into WeMemoir. WeMemoir does not implement its own encryption layer — your data's protection depends on how you store the working directory.

## Can I audit what WeMemoir does?

**Yes.** The entire source is open under the MIT license. The import → clean → memoir pipeline is readable in a single pass through `wememoir/`. No obfuscated code, no binary blobs, no network calls in the core modules.

## Who should I contact about a privacy concern?

Open an issue on GitHub. Since all processing is local, most privacy concerns are about input/output handling — and we take those seriously.
