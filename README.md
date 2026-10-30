# 読み物 (Yomimono)

Short Japanese stories to read on the iPad, written from the kanji you already know on WaniKani.
A single-page web app: no server, no accounts.
Your WaniKani token and Anthropic API key live in the browser's storage on the device, and the page talks to the two APIs directly.

## What it does

- **Sync** pulls your WaniKani level, every kanji and vocabulary subject up to that level, and your SRS stage for each.
  A kanji counts as known from the stage you choose in Settings (default Guru I).
  It re-syncs by itself when the data is more than a day old.
- **Write me a story** asks Claude for a short narrative that uses only known kanji (anything else goes in kana), prefers vocabulary you know, and is pitched at a grammar level that follows your WaniKani level.
  Give it a theme or let it choose.
  Stories are returned as structured JSON (sentences, tokens, readings, two wrong readings per kanji word, English per sentence) and saved to the library.
  Kanji that slipped through outside your list are marked with a dotted underline and always show their reading.
- **Read mode:** tap a kanji word to show or hide its furigana; the ふりがな button shows all of them.
  The small 英 after each sentence opens its English in a drawer (with a 🔊 button that reads the sentence aloud with the iPad's Japanese voice); the English button lays every sentence out with its translation beneath.
- **Quiz mode:** every kanji word becomes a button.
  Tap one and either choose its reading from three, or, for words marked with a gold underline and their furigana already shown, choose its English meaning from three.
  Mix (the default) asks about half of each kind, chosen afresh each run; Readings and Meanings ask only one kind.
  Each answer is read aloud in the iPad's Japanese voice (🔊 in the toolbar mutes it).
  With a keyboard (Mac): Space, Enter or → opens the next unanswered word, 1 / 2 / 3 picks a choice and moves on, Esc skips; in read mode ← / → step through sentence translations.
  Firefox on macOS adds a loud pop after each spoken word (its speech engine; the same voice is clean from the `say` command and in Safari), so mute it there or use Safari.
  Right answers turn green and reveal the furigana, wrong ones red.
  A score bar tracks progress, and the summary lists what you missed.
  Misses are remembered per kanji and the next story is asked to feature them, along with kanji that are freshly at Guru.
- **Library:** stories are kept in the browser, newest first, with quiz scores.
  Settings has an export (JSON) and a delete-all.

## Bundled stories (no API key needed)

`stories.json` next to the page holds stories written outside the app.
On every load the app adds any it hasn't seen to the library (deleted ones stay deleted).
They come from `tools/stories_src.txt`, a plain-text format where each kanji word is written `surface[reading|wrong1,wrong2]`,
meanings for the meaning quiz live in `tools/meanings.txt` (word, meaning, two wrong meanings),
and `python3 tools/build_stories.py` validates every kanji against `tools/known_kanji.txt` (a snapshot of the WaniKani sync, Guru and above) and writes `stories.json`.
To add stories: append to the source file, rebuild, push.
To refresh the known list after levelling up, replace the snapshot with the kanji string printed by the sync (or ask Claude to re-pull it).

## Setup on the iPad

1. Open the deployed page in Safari and add it to the home screen (Share → Add to Home Screen) so it runs full-screen.
2. In ⚙︎ Settings, paste a WaniKani personal access token (read-only is all it needs; Settings → API Tokens on wanikani.com) and an Anthropic API key (console.anthropic.com).
3. Tap Sync WaniKani, go back, and write a story.

Costs are shown on each story.
Opus 5.5 is the default for the most natural Japanese; Sonnet 5.5 is quicker and cheaper, and Haiku 5.5 cheapest.
The known-kanji and vocabulary lists are sent with a cache marker, so repeat stories reuse them at the cached rate.

## Build and deploy

`app.html` is the whole app.
`python3 build.py` copies it to `dist/web/index.html` with the manifest and icons; the GitHub Actions workflow does that on every push to `main` and publishes `dist/web` to GitHub Pages.
To regenerate the icons after editing `assets/icon.svg`: `rsvg-convert -w 512 -h 512 assets/icon.svg -o assets/icon-512.png` and the same at 180.

To try it locally: `python3 build.py && python3 -m http.server -d dist/web 8765`, then open http://localhost:8765.
