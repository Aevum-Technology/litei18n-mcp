# LiteI18n MCP tools

The hosted server at `https://mcp.litei18n.com/mcp` exposes nine tools. Every call acts only inside
the workspace and projects the user approved, with the permissions they chose.

## Contents

- [Summary](#summary)
- [Parameters and limits](#parameters-and-limits)
- [Results](#results)
- [Errors](#errors)

## Summary

| Tool | Title | Hints | Permission |
|---|---|---|---|
| `list_projects` | List projects | read-only | — |
| `list_keys` | Find keys | read-only | `keys:read` |
| `create_key` | Create keys | write | `keys:write` (+ `translations:write` if translations are given) |
| `upsert_draft` | Save draft translations | write, idempotent | `translations:write` |
| `delete_key` | Delete key | **destructive**, idempotent | `keys:write` |
| `restore_key` | Restore deleted key | write, idempotent | `keys:write` |
| `commit_drafts` | Publish drafts | **destructive** | `drafts:commit` |
| `list_releases` | List releases | read-only | `releases:read` |
| `create_release` | Create OTA release | **destructive** | `releases:write` |

All tools have `openWorldHint: false`: they touch only the user's own workspace.

## Parameters and limits

**`list_projects`**: no parameters.

**`list_keys`**
- `project_id` (uuid, required)
- `query` (2–500 chars): searches key names, descriptions and translation values
- `key_id` (uuid) or `key_ids` (up to 500 uuids): fetch exact keys
- `tags` (up to 20): filter by tag
- `language_code`: return translations for one language only
- `include_translations` (default `true`): set `false` for a cheap list of names
- `limit` (1–500, default 100), `offset`

**`create_key`**
- `project_id` (uuid, required)
- `keys`: 1–100 items of `{ key_name (≤500), description? (≤2000), translations? { lang: value } }`
- Values are up to 50,000 characters. Translations are saved as drafts.

**`upsert_draft`**
- `project_id` (uuid, required)
- `drafts`: 1–500 items of `{ key_id, language_code, value (≤50,000) }`
- Saving the same value twice is harmless.

**`delete_key`**: `key_id`. **`restore_key`**: `key_id`.

**`commit_drafts`**
- `project_id` (uuid, required)
- `message` (≤500): say what changed and why
- `locale`: publish only this language's drafts. Without it, every pending draft in the project
  goes live, including other people's.

**`list_releases`**: `project_id`.

**`create_release`**
- `project_id` (uuid, required)
- `tag_name` (≤100), e.g. `v1.4.0`
- Always releases the **latest commit**. Choosing an older commit is only possible in the app.

Other limits: 60 requests a minute per connection; 1 MB request body.

## Results

Results are structured data (each tool has an output schema), also sent as JSON text.

- `list_projects` → `projects[]`: `id`, `name`, `slug`, `description`, `primary_language`,
  `supported_languages`, `key_count`, `permissions` (what this connection may do there),
  `ai_context` and `ai_tone` (the team's translation guidance).
- `list_keys` → `keys[]` of `{ id, key_name, description, tags, translations }`, where
  `translations[lang]` is `{ value (live), draft (unpublished), is_verified }`. Also `count`,
  `offset`, `limit`, and possibly `partial_results`, `truncated`, `next_offset`. Answers are capped
  at about 100,000 characters: when `next_offset` is present, more keys exist.
- `create_key` → `created[]` (`key_id`, `key_name`, `drafts_created`), `errors[]`
  (`key_name`, `error`), `warnings[]`, `summary` (`keys_created`, `keys_failed`,
  `total_drafts_created`). Can partly succeed.
- `upsert_draft` → `upserted_count`, `error_count`, `errors[]`, `warnings[]`. Can partly succeed.
- `delete_key` → `key_name`, `pending_delete` (removed at next commit; restorable),
  `deleted_immediately` (never published; gone for good), `drafts_discarded`.
- `restore_key` → `restored`, `key_name`.
- `commit_drafts` → `commit_id`, `version`, `change_count`.
- `list_releases` → `releases[]`: `id`, `version`, `tag_name`, `is_latest`, `is_active`,
  `created_at`, `commit_id`, `storage_path` (e.g. `locales/<project_id>/v7`).
- `create_release` → `release_id`, `version`, `storage_path`, `commit_version`.

`warnings[]` flags characters that may render badly (invisible characters, look-alikes), with the
affected key, language, character and a hint. The write still went through; fix the value with
`upsert_draft` if the character is a mistake.

## Errors

| Message | Meaning | What to do |
|---|---|---|
| Sign-in requested again / HTTP 401 | The connection was disconnected or expired | Ask the user to sign in again from their AI app |
| `No access to this project…` | The project was not approved for this connection | User reconnects and selects the project |
| `Permission denied…` | Missing scope for this project | Name the scope from the table above; user reconnects with more access |
| `Your plan does not allow this action. Please upgrade.` | The plan lacks this feature (usually releases, which need Starter or above) | Explain the plan limit; nothing to retry |
| `This workspace has been suspended` / account suspended | Suspended by support | Tell the user to contact support |
| `No drafts to commit` | Nothing pending (for that `locale`) | Check `list_keys` for drafts; do not retry |
| `No commits found. Commit drafts first.` | Release before any commit | Commit first, if the user wants that |
| `Release created (vN) but asset generation failed…` | Release row exists, files may be missing | Run `list_releases`, check the files, then ask before retrying |
| `Key not found…` | Wrong id or key in another project | Re-find the key with `list_keys` |
| Too many requests / HTTP 429 | Over 60 requests a minute | Wait, batch more per call |
| `Request body too large (max 1 MB)` | Batch too big | Split the batch |
