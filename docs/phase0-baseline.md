# Phase 0 — Baseline report

Baseline: upstream `bfcb175`, CK3 1.20.1.2. Tasks refer to [spec](unified-cheat-menu-spec.md) Section 10.

| # | Task | Status |
| --- | --- | --- |
| 1 | Error.log baseline (vanilla + this mod only) | Done: **2,717 entries** (below) |
| 2 | `script_docs` dump | Done: spec v1.2 corrected from it (below) |
| 3 | Vanilla overrides and global defines review | Done (below) |
| 4 | Per-player global variable inventory | Done (below) |
| 5 | Innovation generator | Done: rewritten |
| 6 | Feature click-through | Accepted based on prior play with the base mod; no separate click-through of this build. Domicile presets have known errors (see baseline) |

## How to run the baseline (tasks 1, 2)

The repo is registered as a local mod: `Documents/Paradox Interactive/Crusader Kings III/mod/unified_cheat_menu_dev.mod`, shown in the launcher as **Unified Cheat Menu (dev)** and pointing at `C:/dev/CK3 Mod`.

1. In the launcher, create a playset containing **only** Unified Cheat Menu (dev). Your current playset has Community Flavor Pack and Divine Intervention enabled, which would pollute the baseline.
2. Start a new game (any bookmark), unpause for one in-game month, and save.
3. Open the console (`` ` `` with debug mode on) and run `script_docs`.
4. Quit the game. Then the logs can be analyzed: `logs/error.log` for the baseline count and the `script_docs` output for the "verify" items.

The existing log (2,892 lines, from Community Flavor Pack + Divine Intervention, without this mod) isn't usable as a baseline.

Note: `mod/Skonester_Cheat_Menu_Gold/` is an old **1.19** build (`9.27.26-PreBGA`) with no `.mod` file, so the launcher doesn't load it. It can be deleted.

## Error.log baseline (task 1)

Run on 2026-10-23: CK3 1.20.1.2, all DLC, playset with only this mod (`dlc_load.json` confirms), new game, one month, `script_docs`.

**2,717 error entries** (3,855 lines). This is the number to beat. `agent.md` reported 11,577 after the port, so later upstream fixes already cut most of them. No vanilla-only run was done, but nearly every entry traces to the mod:

- **982 entries cite a file:** 666 are mod files and 316 are vanilla paths. 282 of the vanilla-path ones are in `00_building_effects.txt`, called by the mod's domicile presets (`ucm_cheat_menu_domicile_preset_effects.txt:3262`) with bad arguments.
- **Most of the rest are load-time warnings about mod names:** "variable/flag used but never set" and "set but never used" (1,312 entries). 1,294 of them name variables or flags that appear in mod files.

**Biggest groups:**

| Count | What | Where |
| --- | --- | --- |
| 1,198 | Variable/flag used but never set | Mod variables and flags throughout |
| 377 | Script system error (bad trigger/effect arguments) | Mostly the domicile presets (158), `dp_char_editor.txt` (36), `ucm_government_bianshen_daming_effects.txt` (30), `GM_value_on_action.txt` (29) |
| 185 | Landed title not found | `yan_on_action.txt` (78), `GM_value_on_action.txt` (52), authority/expansion title effects. These reference titles from other mods |
| 135 | Tradition not found | `ucm_cw_tradition_picker_lists_generated.txt`: AGOT-only keys, expected per the file header. Goes away when the picker uses `every_culture_tradition` |
| 92 | Variable set but never used | Mod variables |
| 67 | Orphaned events | `ucm_cheat_menu.*` and others |
| 54 | Missing characters `character:yannv*` / `yannan*` | `yan_on_action.txt` |

**Quick wins:** `yan_on_action.txt` + `GM_value_on_action.txt` (about 300 entries combined, compatibility code for other mods running unguarded), the domicile presets (about 200), and the generated tradition list (135).

## script_docs results (task 2)

The engine's documentation overturned two claims that were based on searching game files:

- **Characters can be renamed:** `change_first_name = <dynamic_description>`.
- **Script can loop over the database** for traits, innovations, traditions, pillars, tenets, doctrines, government, holding, court position, CB, accolade, legend and activity types, and more. Only building types, men-at-arms types, and artifact templates lack a loop.

Also found: `set_culture_name`, `set_faith_name`, `set_rite_name`, `add_rite_tenet`; `set_immortal_age` only works on characters who are already immortal; `personal_tenet_slot_add` is a modifier. No baby-sex parameter on `make_pregnant`. The spec is updated to v1.2 and Appendix A now cites the engine docs.

## Vanilla overrides (task 3)

Each override is a full copy of the 1.20.1.2 vanilla file with small edits (whitespace-insensitive diff).

| File | Change vs vanilla | Recommendation |
| --- | --- | --- |
| `gui/window_character.gui` | +384 / −25. Adds the "Crozier cheats" panel (open button, secret type list `UCM_CROZIER_CHEATS_XR_*`) and adjusts court-tab text | Keep for now. Phase 1: move the panel into a scripted widget so this override can go |
| `gui/interaction_menu_window.gui` | +181 / −4. Adds a collapsible category grid, portrait height (`xa_height`) ± controls, and removes the `CanCustomizePortrait` gate | Keep for now. Phase 1: same as above |
| `gui/interaction_confirmation.gui` | +4 / −3, **layout only** (margins, minimum height 480 → 380) | **Remove the override.** No functionality depends on it |
| `gui/frontend_ingame_menu.gui` | +37 / −1. Adds a pause-menu button that calls `ExecuteConsoleCommand('debug_mode')` | Keep. Low conflict risk |
| `common/on_action/dlc/tgp/tgp_china_minister_on_action.txt` | Replaces 9 `would_be_valid_for_court_position` checks with `ucm_positions_loose_court_appointment_candidate_trigger` | **Changes AI behavior for every Chinese-government ruler**, not just cheat users. Move behind a game rule or player check, or remove |
| `common/script_values/09_mpo_values.txt` | +19 in `study_commander_trait_success_chance_value`: +50/+100/+666 for `bloodline_god_1/2/3` | Only affects cheat-trait holders. Keep, but must be re-merged on every game update |
| `common/culture/traditions/_traditions.info`, `common/succession_election/_succession_election.info` | Documentation files; not loaded | Delete the copies |
| `localization/english/debug_l_english.yml` | Renames the debug interaction labels ("DEBUG Main" → "Skonester Cheat Menu") | Move the changed keys to `localization/replace/english/` instead of overriding the whole file |
| `localization/german/debug_l_german.yml` | Whole file differs (out-of-date translation) | Same: move only the changed keys to `localization/replace/german/` |

Finding for the spec: GUI can call `ExecuteConsoleCommand`. That's narrower than generic console access (it needs debug mode for most commands), so spec 7.3's "don't promise console commands" still stands.

## Global defines (task 3)

| Define | Vanilla | Mod | Who it affects | Recommendation |
| --- | --- | --- | --- | --- |
| `NProvince.MAX_BUILDINGS` | 7 | 1453 | Cap only. Matters only when slot modifiers push a province past 7, which is effectively only through cheats | Keep, document |
| `NModifier.STANDARD_MINIMUM_VALUE` | 0.1 | 0.0 | **Everyone.** Stacked reductions can now reach 0% instead of a 10% floor (needed for "effectively zero upkeep") | Keep (the cheat depends on it), document as a balance change |
| `NCharacterOpinion.MAX_DUCHIES_BEFORE_PENALTY` | 2 | 4 | **Everyone.** Kings and emperors (AI too) can hold 4 duchies before vassals object. Not a cheat | **Remove**, or ship as an optional sub-mod |

## Global variables (task 4)

114 global variable names are set in `common/` and `events/`.

> **Update (spec v1.3):** The mod is now single-player only, so none of this needs migrating. The inventory is kept for reference. Phase 1 instead hides every entry point while `has_multiple_players = yes`.

**Per-player state (would only matter in multiplayer):**

- **Targets:** `ucm_crozier_cheats_other`, `ucm_crozier_cheats_prev_char`, `ucm_cheat_menu_recipient`, `ucm_acm_recipient`, `ucm_acm_repair_target`. The primary target is already a character variable (`var:ucm_crozier_cheats_target`), so only the secondary targets are global.
- **Persistent cheat toggles:** 32 cheats, each with three globals: `ucm_crozier_cheats_on_<cheat>` (flag), `_fx_<cheat>` and `_lv_<cheat>` (numbers). Cheats include income, health, stress, skills, immortal, levy, legend spread, and auto-ascension. In multiplayer, one player enabling a cheat enables it for everyone the tick applies to.
- **Toggle settings:** `ucm_crozier_cheats_tier`, `_power`, `_freq`, `_no_toast`, `_tick_pending`, `_realm`.
- **UI state:** `yyz_list_mode`, `yyz_sort_key`, `yyz_sort_desc`, `xa_height`.
- **Other:** `ucm_domicile_cheat_active`.

**World-wide, fine as globals:**

- Compatibility detection: `ucm_compat_*_loaded`, `MTS_is_loaded`.
- AI world settings: `ucm_ai_*`, `ucm_world_ai_boost_*`, `ucm_celestial_governor_rotation_grace_skip`, `ucm_samge_years_accum`.
- World rules: `ucm_family_planning_*`, `ucm_daming_ming_gov_menu_unlocked`, `zhuge_has_guoxi1`, `save_the_data`. Check these in Phase 1; some may be per-player.
- Read-only catalogs: tradition and men-at-arms global lists.

## Innovation generator (task 5)

The missing script couldn't be recovered: it's not in the git history. It's rewritten as `tools/gen_ucm_cw_innovation_sguis.py`, which reuses the parser from `gen_cw_tradition_picker_lists.py`.

Running it against 1.20.1.2 reproduces the shipped files byte-for-byte except for **two innovations the shipped files were missing**: `fp3_innovation_fritware` and `fp3_innovation_mural_sextant` (Legacy of Persia). Their culture-window unlock/remove buttons pointed at scripted GUIs that didn't exist. The regenerated files are included.

```
python tools/gen_ucm_cw_innovation_sguis.py --game-dir "C:/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game"
```
