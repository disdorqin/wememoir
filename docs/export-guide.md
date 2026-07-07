# Export Guide

WeMemoir imports chat records from files **you have already exported** using third-party tools. This guide explains supported formats and how to prepare your data.

## Important: WeMemoir Does Not Export Chat Records

WeMemoir is a **post-export processing tool**. You must first use a legitimate WeChat export tool to produce the export file, then use WeMemoir to clean, analyze, and generate memoirs.

WeMemoir does **not**:
- Connect to WeChat or any messaging platform
- Extract data from phone backups or database files
- Circumvent any platform's export limitations
- Provide tools for unauthorized data access

## Supported Input Formats

| Format | Detection | Notes |
|--------|-----------|-------|
| **CSV** | `--source auto` or `--source csv` | Requires columns: `timestamp`, `sender`, `content`. Optional: `message_type` |
| **JSON** | `--source auto` or `--source json` | WeMemoir internal JSON format or message array |
| **TXT** | `--source auto` or `--source txt` | Common export pattern: `YYYY-MM-DD HH:MM:SS Sender: Content` |
| **HTML** | `--source auto` or `--source html` | Text extraction from table-based exports |

### CSV Format Requirements

```csv
timestamp,sender,content,message_type
2023-01-01 10:00:00,Alice,Hello!,text
2023-01-01 10:01:00,Me,Hi Alice,text
```

- Timestamp should be in `YYYY-MM-DD HH:MM:SS` format
- `message_type` is optional; common values: `text`, `image`, `system`, `unknown`

### JSON Format

```json
[
  {"timestamp": "2023-01-01 10:00:00", "sender": "Alice", "content": "Hello!", "message_type": "text"}
]
```

### TXT Format Examples

WeMemoir auto-detects these common patterns:

```
2023-01-01 10:00:00 Alice: Hello!
[Alice] Hello!
Alice (2023-01-01 10:00:00): Hello!
```

## Quick Start

```bash
# Import from CSV
wememoir import path/to/export.csv --source auto --self-name "YourName" --out data/imported.json

# Clean the dialogue
wememoir clean data/imported.json --out output/cleaned.md

# Generate memoir
wememoir memoir data/imported.json --out output/memoir.md
```

## Troubleshooting

**"No messages found" after import**
- Check that your file has the expected format
- Try specifying `--source csv` or `--source txt` explicitly
- Verify the file is not empty and contains readable text

**Character encoding issues**
- WeMemoir expects UTF-8 encoded files
- For Chinese text, ensure your export tool produces UTF-8 output
- If using Windows Notepad, save with UTF-8 encoding (not ANSI)

**Missing sender names**
- Use `--self-name` to identify which sender is "Me"
- Ensure sender names are consistent throughout the file

## See Also

- [CLI Usage](../README.md#cli-usage) in the main README
- [Privacy Policy](privacy.md) for data handling practices
