# LiteI18n workflows

Step-by-step recipes. Each ends in a known state: drafts, live, or released.

## Contents

- [Start](#start)
- [Add new copy](#add-new-copy)
- [Edit existing translations](#edit-existing-translations)
- [Fill missing translations](#fill-missing-translations)
- [Delete or restore keys](#delete-or-restore-keys)
- [Publish (commit)](#publish-commit)
- [Ship an OTA release](#ship-an-ota-release)
- [Recover from failures](#recover-from-failures)

## Start

1. `list_projects`. Pick the project by the name or slug the user gave. If several match or none
   do, ask.
2. Note `id`, `primary_language`, `supported_languages`, `ai_context`, `ai_tone` and
   `permissions`.
3. If a permission the task needs is missing, stop and tell the user which one (see
   [connect.md](connect.md#permission-problems)).

Never take a project id from memory or an old conversation when `list_projects` is available.

## Add new copy

1. Search first: `list_keys` with `query` set to the intended key name, its prefix
   (`checkout.`), and the source text. Reuse an existing key when it already means the same
   thing; ask if unsure.
2. Follow the project's naming. Look at neighbouring keys and match their style (dots, casing,
   feature prefixes).
3. `create_key` with up to 100 keys. Add a `description` that tells translators where the text
   appears. Include `translations` for the primary language and, if asked, every supported
   language.
4. Read `errors` and `warnings` in the result.
5. Verify: `list_keys` with `key_ids` from `created`.
6. Report the keys as **drafts**. Commit only if the user asked to publish.

## Edit existing translations

1. Find the keys with `list_keys` (`query`, `key_ids` or `tags`). Note the live `value` and any
   existing `draft`: someone else may already have a draft pending.
2. `upsert_draft` with exact `key_id` and `language_code`, up to 500 per call. Split larger jobs
   by language or feature.
3. Verify with `list_keys` using `key_ids` (and `language_code` to keep it small).
4. Show the user the before and after for anything non-trivial, then commit if asked.

## Fill missing translations

There is no "missing only" filter. A language is missing for a key when `translations[lang]` has
no `value` and no `draft`.

1. Narrow the scope: a tag, a key prefix, a feature, or named keys. For a large project with no
   scope, ask for one before writing.
2. Page through `list_keys` (follow `next_offset`) and collect the gaps.
3. Translate from the primary language using `ai_context` and `ai_tone`. Keep placeholders,
   ICU plural and select syntax, markup and trailing punctuation exactly as in the source. Match
   the formality of existing translations in that language.
4. `upsert_draft` in batches; check `errors` and `warnings` after each.
5. Report counts per language and leave the drafts for review unless told to publish.

## Delete or restore keys

1. Find the key with `list_keys` and confirm its exact name with the user, unless they named it
   exactly.
2. `delete_key`. Read the result:
   - `pending_delete: true`: the key had published translations. It disappears at the next
     `commit_drafts`; `restore_key` undoes it until then.
   - `deleted_immediately: true`: it was never published and is gone. It cannot be restored.
3. A key's removal reaches apps only after a commit and a release.

## Publish (commit)

1. Find out what will go live. `list_keys` shows drafts per key; for a large project, search the
   area you changed and ask whether unrelated pending drafts may exist.
2. If only one language should go live, pass `locale`.
3. Unless the user asked to publish this exact set, confirm: "This publishes N changes in
   PROJECT (all languages / LOCALE). Go ahead?"
4. `commit_drafts` with a message such as `Add checkout button copy (en, fr, es)`.
5. Report `version` and `change_count`. "No drafts to commit" means nothing was pending: check,
   do not retry.

## Ship an OTA release

1. Make sure the user wants apps to receive the change, not only to publish it in LiteI18n.
2. Commit first if there are drafts to include. A release ships the **latest commit**.
3. Confirm, unless the user asked for a release just now: "This ships commit vN of PROJECT to
   every app reading its files. Go ahead?"
4. `create_release`, with `tag_name` if the user uses version tags.
5. Report the release `version` and `storage_path`. For app URLs see [ota.md](ota.md).
6. For very large projects (tens of thousands of keys), fetch the release's `all.json` and check
   a few keys in each language before calling it complete: the file generator can stop early
   without reporting an error.

## Recover from failures

- **Partial write** (`errors` not empty): re-fetch the affected keys, fix only the failed items,
  and tell the user what failed and why.
- **"Release created (vN) but asset generation failed"**: the release exists but its files may
  not. Run `list_releases`, then fetch `locales/<project_id>/vN/all.json`. Tell the user before
  creating another release; a second release is usually not the fix.
- **App still shows old text**: check, in order, that the change was committed, that a release
  was created after the commit, that `latest/<lang>.json` contains it, then the app's cache and
  fallback merge order. Compare with `v<version>/` to separate a cache delay from a missing file.
- **Permission or plan errors**: retrying will not help. Explain what the user needs to change.
