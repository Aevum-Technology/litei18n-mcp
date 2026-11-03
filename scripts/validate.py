#!/usr/bin/env python3
"""Checks the skill, plugin and registry files. Run: python3 scripts/validate.py"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "litei18n"
TOOLS = ["list_projects", "list_keys", "create_key", "upsert_draft", "delete_key",
         "restore_key", "commit_drafts", "list_releases", "create_release"]
# Outdated setup that must never come back: the npm package and env token were dropped.
STALE = ["@litei18n/mcp-server", "LITEI18N_API_TOKEN", "LITEI18N_URL", "npx -y @litei18n"]
MCP_URL = "https://mcp.litei18n.com/mcp"
errors = []


def check(ok, message):
    if not ok:
        errors.append(message)


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        top = re.match(r"^([a-z-]+):\s*(.*)$", line)
        if top:
            fields[top.group(1)] = top.group(2).strip()
    return fields


skill_md = (SKILL / "SKILL.md").read_text(encoding="utf-8")
fm = frontmatter(skill_md)
check(fm is not None, "SKILL.md: missing YAML frontmatter")
if fm:
    name = fm.get("name", "")
    desc = fm.get("description", "")
    check(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) is not None and len(name) <= 64,
          "SKILL.md: name must be lowercase letters, digits and hyphens, at most 64 characters")
    check(name == SKILL.name, f"SKILL.md: name '{name}' must match its folder '{SKILL.name}'")
    check(0 < len(desc) <= 1024, "SKILL.md: description must be 1-1024 characters")
    check("<" not in desc and ">" not in desc, "SKILL.md: description must not contain angle brackets")
    check("Use when" in desc, "SKILL.md: description should say when to use the skill ('Use when ...')")
    check(len(fm.get("compatibility", "")) <= 500, "SKILL.md: compatibility must be at most 500 characters")
check(len(skill_md.splitlines()) <= 500, "SKILL.md: keep the body under 500 lines")

markdown = list(SKILL.rglob("*.md")) + [ROOT / "README.md"]
for path in markdown:
    text = path.read_text(encoding="utf-8")
    for stale in STALE:
        check(stale not in text, f"{path.relative_to(ROOT)}: outdated setup '{stale}'")
    for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
        if re.match(r"^[a-z]+:", target):
            continue
        check((path.parent / target).exists(), f"{path.relative_to(ROOT)}: broken link '{target}'")

for ref in (SKILL / "references").glob("*.md"):
    check(f"references/{ref.name}" in skill_md, f"SKILL.md does not point to references/{ref.name}")
    check("/references/" not in ref.read_text(encoding="utf-8"),
          f"references/{ref.name}: keep references one level deep (no nested reference links)")

tools_md = (SKILL / "references" / "tools.md").read_text(encoding="utf-8")
for tool in TOOLS:
    check(f"`{tool}`" in tools_md, f"references/tools.md: tool '{tool}' is not documented")
    check(f"`{tool}`" in (ROOT / "README.md").read_text(encoding="utf-8"), f"README.md: tool '{tool}' missing")


def load(path):
    try:
        return json.loads((ROOT / path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"{path}: {exc}")
        return {}


server = load("server.json")
check(server.get("name") == "com.litei18n/mcp", "server.json: name must be com.litei18n/mcp")
check(len(server.get("description", "")) <= 100, "server.json: description must be at most 100 characters")
check(any(r.get("url") == MCP_URL for r in server.get("remotes", [])), f"server.json: remote {MCP_URL} missing")
check(load(".mcp.json").get("mcpServers", {}).get("litei18n", {}).get("url") == MCP_URL,
      ".mcp.json: litei18n url must be the hosted link")
plugin = load(".claude-plugin/plugin.json")
check(plugin.get("name") == "litei18n", ".claude-plugin/plugin.json: name must be litei18n")
market = load(".claude-plugin/marketplace.json")
check(any(p.get("name") == "litei18n" for p in market.get("plugins", [])), "marketplace.json: litei18n plugin missing")
load("glama.json")
gemini = load("gemini-extension.json")
check(gemini.get("name") == "litei18n", "gemini-extension.json: name must be litei18n")
check(gemini.get("mcpServers", {}).get("litei18n", {}).get("httpUrl") == MCP_URL,
      "gemini-extension.json: litei18n httpUrl must be the hosted link")

if errors:
    print("\n".join(f"FAIL {e}" for e in errors))
    sys.exit(1)
print("OK: skill, plugin and registry files are valid")
