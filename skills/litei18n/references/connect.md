# Connecting to LiteI18n

## The link

```
https://mcp.litei18n.com/mcp
```

A hosted MCP server using Streamable HTTP and OAuth 2.1 browser sign-in. There is nothing to
install and no token to copy. Current per-app guides: https://litei18n.com/agents.

| App | How |
|---|---|
| Claude (web, desktop, mobile) | **Customize → Connectors → + Add → Add custom connector**, paste the link, **Connect** |
| ChatGPT | **chatgpt.com/plugins → + → Add custom MCP server**, choose **OAuth**, **Create as a plugin** |
| Claude Code | `claude mcp add --transport http litei18n https://mcp.litei18n.com/mcp`, then `/mcp` |
| Codex | `codex mcp add litei18n --url https://mcp.litei18n.com/mcp`, then `codex mcp login litei18n` |
| Cursor | `.cursor/mcp.json`: `{"mcpServers":{"litei18n":{"url":"https://mcp.litei18n.com/mcp"}}}` |
| VS Code | `.vscode/mcp.json`: `{"servers":{"litei18n":{"type":"http","url":"https://mcp.litei18n.com/mcp"}}}` |
| OpenCode | `opencode.json`: `{"mcp":{"litei18n":{"type":"remote","url":"…"}}}`, then `opencode mcp auth litei18n` |
| Devin Desktop (Windsurf), Antigravity | `mcp_config.json`: `{"mcpServers":{"litei18n":{"serverUrl":"…"}}}` |
| Zed | **Settings → AI → MCP Servers → Add Server → Add Remote Server** |

## Signing in

The AI app opens LiteI18n in the browser. The user signs in, picks a workspace, the projects, and
an access level (Read only, Read and write, or Full access), and approves. Approving needs the
**owner** or **admin** role in that workspace, and a plan that includes MCP access.

Each connection appears under **Connect AI** in the workspace sidebar, where it can be
disconnected. Disconnecting revokes its access at once.

Never ask the user for their password or an API token, and never put one in a config file you
write. If a tool asks for sign-in, tell the user to finish it in their AI app.

## Permission problems

The connection's scopes are per project and fixed at approval time. To change them, the user
disconnects under **Connect AI** and connects again with the right projects and access level.

| Needed for | Scope | Preset that includes it |
|---|---|---|
| Finding keys | `keys:read` | Read only |
| Creating, deleting, restoring keys | `keys:write` | Read and write |
| Saving drafts | `translations:write` | Read and write |
| Publishing drafts | `drafts:commit` | Read and write |
| Listing releases | `releases:read` | Read only |
| Creating releases | `releases:write` | Full access (Starter plan or above) |

## CI and scripts

Automated jobs can send a LiteI18n API token as `Authorization: Bearer litei18n_…` to the same
link. Tokens are created under **API Tokens** in the workspace. They belong in the CI system's
secret store, never in a repository, a chat, or a shared config file.
