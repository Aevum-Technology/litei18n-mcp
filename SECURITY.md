# Security policy

## Reporting a vulnerability

Please report security issues privately. Do not open a public issue.

- In this repository: open the **Security** tab and click **Report a vulnerability**.
- Or contact us through [litei18n.com/contact](https://litei18n.com/contact) and say it is a
  security report.

Reports about the hosted service at `mcp.litei18n.com`, its sign-in flow, or the LiteI18n app are
welcome through either route. We aim to acknowledge reports within three business days and will
keep you updated until the issue is fixed.

## Scope

- The hosted MCP server (`https://mcp.litei18n.com/mcp`) and its OAuth sign-in.
- Guidance in `skills/litei18n` that could lead an agent to mishandle credentials or take a
  destructive action without asking.
- Anything in this repository that should not be public.

## Credentials

The hosted server uses browser sign-in, so AI apps never need a LiteI18n password or token. If you
use an API token for CI, keep it in your CI secret store. Never paste it into chat, an issue or a
commit. If one leaks, revoke it under **API Tokens** in your workspace.
