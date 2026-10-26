# Elder Kings 2 compatibility patch — plan

Survey date: 2026-10-25. EK2 0.21.1 (workshop 2887120253, `supported_version="1.20.1.2"`) against UCM on
`spec/unified-cheat-menu` at `11b3faf` (after the upstream simplification pass). Static survey only;
step 0's load test is still to do.

Survey scripts (static, no game run):
`C:\Users\gabyn\AppData\Local\Temp\claude\C--dev-CK3-Mod\69947ded-eeb7-4e77-8370-4ed5965f4cab\scratchpad\ek2_survey.py`, `ek2_survey2.py`, `ek2_survey3.py`, `ek2_survey4.py` (same folder).

## What the survey found

EK2 targets the same CK3 version (1.20.1.2), so no version gap. It `replace_path`s cultures, faiths,
religions, doctrines, holy sites, landed titles, dynasties and all history. Vanilla traits, men-at-arms
(MAA), laws and buildings are mostly kept and extended.

| Area | Under EK2 | Severity |
|---|---|---|
| `gui/window_character.gui` | EK2 also ships it (149 changed lines vs vanilla: arcana, praxis, important characters, modifier layout). UCM changes 409 lines. Whichever loads last wipes the other. | **Blocker** |
| `gui/frontend_ingame_menu.gui`, `gui/interaction_menu_window.gui` | EK2 keeps vanilla, so UCM's override still works | OK |
| Hardcoded cultures | ~250 vanilla cultures; **none** exist in EK2 (EK2 has 100). Files: `events/dp_char_editor.txt` (228), `events/ucm_cast_culture_faith_generated.txt` (242), `events/ucm_char_design_events.txt` (184), `common/scripted_effects/ucm_acm_culture_list_effects.txt` (143), `events/ucm_culture_taxonomy_events.txt` (143), `events/ucm_beauty_companion_classified_generated.txt` (108) | High: load errors + broken pickers |
| Hardcoded faiths/religions | 78 faiths, 49 religions; none exist (EK2 has 73 faiths in `faith_types`, 36 religions). Same files plus `ucm_acm_faith_editor_data_effects.txt` | High |
| Doctrines | 3,120 used, only 14 missing (Abrahamic/Sinitic/Eastern/pagan hostility, Muhammad succession, temple authority, Zoroastrian branches). EK2 keeps vanilla doctrine keys. `ucm_force_marry_religion.txt` uses one missing hostility doctrine | Medium |
| Titles | 24 missing: `h_china`, `h_roman_empire`, the Mongol/Horde/Yuan empires, `e_france`, `e_spain`, `e_britannia`, `k_england`... in `ucm_legend_master_effects.txt`, `rse_vanilla_overrides.txt`, `zzz_ucm_sand_spawn_maa_fix.txt`, `yyz_paradox_kludges.txt`, the compat probe, the China safety triggers | Medium |
| Scripted effects EK2 removes | 119 vanilla historical-artifact effects (`create_artifact_excalibur_effect`...) are gone; all are called from `common/decisions/pcm_decisions.txt` (12 decisions). Triggers, script values, modifiers: 0 hits | Medium |
| Duplicate keys (both mods define them) | 56 character interactions (EK2 `00_debug_interactions.txt` vs UCM `99_ucm_interactions_modified.txt`), 5 gender laws (`rse_gender_laws.txt` vs EK2 `00_succession_laws.txt`), 7 succession/marriage triggers (`rse_vanilla_overrides.txt`), 3 vassal-contract script values | Medium: EK2's edits to those keys may be lost; needs a per-key diff |
| MAA | All 13 UCM-referenced types exist. EK2 adds 202 types the generated MAA catalog doesn't list | Low (feature gap) |
| Buildings | 179 vanilla special buildings referenced by UCM catalogs don't exist; EK2's own buildings aren't listed | Low-medium |
| Traits | Runtime trait lists pick up EK2's 585 traits automatically. 8 refs missing (`eunuch`, `maester`, `nightswatch`, `physician_3`...), but they are missing in vanilla too, so it's not an EK2 problem | Low |

What the static survey can't see: runtime breakage inside EK2's own systems (vampirism/lycanthropy
story cycles, arcana) when the cheat menu sets traits or stats directly, plus any error-log noise from
parse order. A load test (step 0) is the source of truth.

## Approach

Follow the existing AGOT pattern (`ucm_compat_agot_loaded_trigger`, `zzz_ucm_compat_probe.txt`,
`gen_cw_tradition_picker_lists.py --agot-dir`):

- **Main mod**: detect EK2 at game start, gate vanilla-map features, and move hardcoded vanilla data into
  data-only files. This also helps any other total conversion.
- **Separate compatch mod** ("UCM – Elder Kings 2 Compatch", loads after both): the merged
  character window, EK2 versions of the data-only files, and merged duplicate keys.

Why not just gate everything in the main mod: a `culture:roman` reference to a missing object logs an
error at load time and can rewrite the surrounding trigger logic (see the TGP note in
`ucm_compat_triggers.txt`). Runtime gating stops broken behavior but not the load errors. Only
replacing the file removes the errors.

## Steps

### 0. Baseline
1. Static survey re-run at `11b3faf`: numbers above are current.
2. Load test: EK2 alone on 1.20.1.2 and save `error.log` as the baseline. Then EK2 + UCM and diff the logs.
   The diff is the real work list. Note the playset order (UCM after EK2).

### 1. Detection (main mod) — done
- `zzz_ucm_compat_probe.txt`: `exists = title:h_tamriel` sets `ucm_compat_ek2_loaded`.
- `ucm_compat_triggers.txt`: `ucm_compat_ek2_loaded_trigger`.

### 2. Guard vanilla-map features (main mod) — done
The bug class that matters: a missing `title:`/`faith:`/doctrine key is dropped at load, so a `limit`
or `is_shown` holding only that check becomes empty, which counts as **true**. Fixed:
- `zzz_ucm_sand_spawn_maa_fix.txt`: the China/Liao branches would spawn MAA on a missing title →
  `ucm_is_h_china_emperor_title_holder_trigger` / `exists = title:e_great_liao`.
- `99_ucm_interactions_modified.txt`: dynastic-cycle interaction shown to everyone → same China trigger.
- `yyz_paradox_kludges.txt`: keeper-of-swans / chief-qadi aptitude granted to everyone → `exists` guards.
- `99_ucm_consolidated.txt`: Crusade/Jihad interactions shown but inert → `exists = faith:...`.
- `zzzzzzzz_0toc_deb_int.txt`: Adamite convert → `exists = faith:adamites`.
- `ucm_legend_master_events.txt`: seed-legends page (vanilla characters/titles/cultures) hidden under EK2 and AGOT.
- `ucm_acm_faith_editor_data_effects.txt` line ~15822: Toric virtue display gated on EK2. **This file is
  marked auto-generated by `tools/gen_faith_editor_display.py`, which isn't in the repo** — re-apply if it's regenerated.

Left alone on purpose:
- `pcm_decisions.txt` is **one** decision (`Artifact_1000`) with 119 calls, not 12. Missing effects
  are just dropped, so gating them changes nothing. Its books, equipment and banners still work.
- `rse_vanilla_overrides.txt` Mongol `OR` lists: a dropped entry in an `OR` is harmless.
- Faith-editor `remove_doctrine` blocks and `flag:` keys: they collapse to empty or are plain strings.
- `ucm_force_marry_religion.txt` (`pagan_hostility_doctrine`): no hostility doctrine exists in both games → compatch step 4.4.

### 3. Isolate vanilla data (main mod, biggest UCM-side change)
Split the culture/faith/religion lists out of the six event/effect files into `*_generated.txt`
data files. Then a compatch can replace the data without copying the logic. Extend
`tools/ck3parse.py`-based generators with `--ek2-dir` (same shape as `--agot-dir`) so the EK2 lists
regenerate after each EK2 update. If a list is only a legacy duplicate of a runtime picker
(spec §9.3 says culture/faith pickers should be runtime lists), delete it instead.

### 4. Compatch mod
1. `descriptor.mod` with both mods as dependencies, plus a loads-after note.
2. **`gui/window_character.gui`**: 3-way merge (base: vanilla 1.20.1.2; theirs: EK2; ours: UCM).
   Keep EK2's arcana/praxis/important-characters additions and UCM's menu hooks.
3. EK2 data files from the step-3 generators: 100 cultures, 73 faiths, 36 religions.
4. `ucm_force_marry_religion.txt`: EK2 version using an EK2 religion family and hostility doctrine.
5. Duplicate keys: per key, diff EK2 vs vanilla. Where EK2 changed gameplay (succession-law triggers,
   gender laws, debug interactions), ship a merged copy. First confirm which copy wins for each
   database type (load test).
6. Optional: regenerated MAA / building / artifact catalogs that include EK2 content (spec §9.3).

### 5. EK2 systems review
Check what the cheat menu does to EK2-only mechanics: trait guard and trait editor on vampire/werewolf/
arcana traits, stat-lock monthly pulses vs arcana, AI boost vs EK2 AI. Add exclusions where setting
a trait directly would skip EK2's story-cycle setup.

### 6. Verify
- Load test EK2 + UCM + compatch. `error.log` should show no new errors over the EK2-alone baseline.
- Smoke test in a game started from an EK2 bookmark: main menu, character window (EK2 panels and UCM
  buttons both present), culture/faith pickers, faith editor, MAA spawn, artifacts, succession menu.
- Save, reload, play a few years at speed 5.

### 7. Release
- Check EK2's terms before publishing. The merged `window_character.gui` contains EK2's GUI code, so it
  needs their permission (their repo/credits have no license file in the workshop copy).
- Workshop item with required-items links to UCM and EK2. Credits per spec §9.4.
- Note in the description that the compatch must be re-merged after EK2 updates that touch
  the character window. The data files just need the generators re-run.

## Size

- Steps 1–2: small, a few files.
- Step 3: the largest UCM-side change, ~6 files, mostly mechanical.
- Step 4.2 (GUI merge): the riskiest piece, redone on EK2 GUI updates.
- Step 4.5: depends on the per-key diff, unknown until done.

A minimal first release is steps 0–2 + 4.1–4.2 + 6. It's playable, with vanilla-only pickers hidden
under EK2. The EK2 culture/faith pickers and catalogs come after that.
