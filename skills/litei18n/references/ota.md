# Loading LiteI18n translations over the air

A release writes public JSON files that apps fetch at runtime, so text changes reach users without
an app store release.

## Contents

- [URLs](#urls)
- [File shapes](#file-shapes)
- [Choosing a file](#choosing-a-file)
- [Loading with a fallback](#loading-with-a-fallback)
- [Caching](#caching)
- [Checking it works](#checking-it-works)
- [Common mistakes](#common-mistakes)

## URLs

Paths use the project **id** (the uuid from `list_projects`), not its slug:

```text
{BASE}/locales/{projectId}/latest/all.json
{BASE}/locales/{projectId}/latest/{locale}.json
{BASE}/locales/{projectId}/v{version}/all.json
{BASE}/locales/{projectId}/v{version}/{locale}.json
```

`{BASE}` is the public release storage URL shown on the project's **Releases** page in the
LiteI18n app (its copy buttons give the full URL). It has the form
`https://<storage-host>/storage/v1/object/public/releases`. Do not invent a host: ask the user to
copy one URL from the Releases page if you do not have it. `list_releases` returns each release's
`storage_path` (`locales/{projectId}/v{version}`), which is the part after `{BASE}/`.

## File shapes

`{locale}.json` is a flat map for one language:

```json
{ "home.title": "Bienvenue", "checkout.pay": "Payer" }
```

`all.json` maps every language:

```json
{ "en": { "home.title": "Welcome" }, "fr": { "home.title": "Bienvenue" } }
```

Only committed and released translations appear. Drafts never do.

## Choosing a file

| File | Use when | Trade-off |
|---|---|---|
| `latest/all.json` | Few languages; you want every language in one request | Larger download |
| `latest/{locale}.json` | Many languages or large catalogs; load on language switch | One request per language |
| `v{version}/…` | A build must keep exactly the text it was tested with | You update the version yourself |

`latest/` changes with every release, and when someone picks an older release as latest on the Releases page (a rollback). `v{version}/` never changes.

## Loading with a fallback

Always ship bundled translations with the app and merge the downloaded ones on top. A failed or
slow download must never block startup, rendering or switching language.

```javascript
const BASE = "https://<storage-host>/storage/v1/object/public/releases"; // from the Releases page
const PROJECT_ID = "<project uuid>";

async function fetchLocale(locale, { timeoutMs = 5000 } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(`${BASE}/locales/${PROJECT_ID}/latest/${locale}.json`, {
      signal: controller.signal,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const messages = await res.json();
    if (typeof messages !== "object" || messages === null) throw new Error("not an object");
    return messages;
  } catch (error) {
    console.warn(`[litei18n] using bundled ${locale} translations:`, error);
    return null; // keep bundled or cached messages
  } finally {
    clearTimeout(timer);
  }
}
```

Merge, never replace, so keys missing from the download keep their bundled text:

| Library | Merge call |
|---|---|
| vue-i18n | `i18n.global.mergeLocaleMessage(locale, messages)` |
| i18next | `i18next.addResourceBundle(locale, "translation", messages, true, true)` |
| react-intl / FormatJS | `setMessages({ ...bundled[locale], ...messages })` |
| Flutter, iOS, Android, custom | Overlay the downloaded map on the bundled one before lookup |

Keys are flat dotted names (`home.title`). If the app's library expects nested objects, convert
them, or turn on its flat-key option (for example i18next `keySeparator: false` when keys contain
dots that are not nesting).

## Caching

- Store the last good download (localStorage, a file, or the platform's cache) and load it before
  the network on the next start. This gives offline support and instant startup.
- Treat `latest/` as changing and `v{version}/` as permanent.
- Do not add cache-busting query strings by default. Use them only for a deliberate "refresh now"
  action.

## Checking it works

1. Open the expected `latest/{locale}.json` URL directly and confirm it has your keys.
2. Change a string in LiteI18n, commit, and create a release.
3. Reload the app (or re-run its fetch) without rebuilding it: the new text should appear. If it does not, clear the app's own cache and any CDN or proxy in front of the files.
4. Block the URL (offline mode or a wrong host): the app should still show bundled text.

## Common mistakes

- Using the project slug in the URL instead of the project id.
- Expecting drafts or unreleased commits in the files.
- Replacing the whole dictionary and losing bundled fallbacks.
- Waiting for the download before first render.
- Rendering translation values as raw HTML without sanitising them.
- Pointing a build that must not change at `latest/`.
