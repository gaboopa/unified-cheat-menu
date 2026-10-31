# Phase 8 — Full-repo review fixes

A whole-repo review (new menu code, vanilla overrides, on_actions, inherited script, localization, tooling) found the issues below. All are fixed here. A load test was run (see **Load test**); the click-through checklist is still open.

## New menu code

| Fix | Where |
| --- | --- |
| Three buttons read `var:ucm_target` inside another character's scope, so they used the wrong character. "Vassal of second" could create a liege loop. Now `root.var:ucm_target` / `this` | `ucm_realm_sguis.txt` (`ucm_target_vassal_of_second`, `ucm_ally_second`), `ucm_character_sguis.txt` (`ucm_second_hook_on_target`) |
| "Vassal of second" requires the second character to hold a higher tier | `ucm_realm_sguis.txt` |
| "End wars" only ends wars where the target is primary attacker or defender | `ucm_end_wars_white_peace` |
| "Learn secrets" can't target yourself | `ucm_learn_target_secrets` |
| Group actions skip dead characters; convert faith/culture skip you | `ucm_triggers.txt` |
| Group confirm event re-checks the target is valid; both events have the single-player gate | `ucm_group_events.txt` |
| Removed unused `ucm_group_start_effect`; closing the menu clears the picked group | `ucm_effects.txt` |

## Things that changed the game for everyone

| Was | Now |
| --- | --- |
| Celestial governor 3-year rotation ran every year in any single-player game | Opt-in: `ucm_celestial_governor_rotation_enabled`, toggled in Population Administration (`ucm_officials.9080`) |
| TGP minister override applied loose court-appointment rules to every player court | Opt-in: `ucm_loose_court_appointment_enabled`, same menu. Off = vanilla |
| AI buffs: the "disabled" defaults were only written on a new game, so adding the mod to a save turned them on | Defaults written once per save (`ucm_ai_defaults_written`) by `ucm_ai_write_defaults_once_effect`, which every AI pulse calls first and the player's quarterly pulse calls on loaded saves (`on_game_start_after_lobby` only fires for new games). The decisions still toggle them; on a loaded save they can show "on" for up to a quarter until the defaults are written |
| `has_too_many_held_duchies_trigger` 3 → 5 | Removed (vanilla) |
| 11 vanilla congenital/beauty traits (stale copies, changed inheritance) | Removed (vanilla) |
| Elective, tribal elective and noble-family succession laws loosened | Removed (vanilla). The mod's own `oligarchic`, `peasant` and `old_theocratic` laws stay |
| `nomadic_authority_1-5` values ×5 | Removed (vanilla) |
| Pre-1.20 copies of `can_be_chancellor/steward/marshal_trigger`, `can_be_granted_titles_by` | Removed (vanilla) |
| Brewery requirement, `beauty` portrait morphs | Removed (vanilla) |
| `marriage_interaction_*` triggers were a stale copy | Re-synced to 1.20.1.2 plus the force-marriage escape |
| `intrigue_per_piety_level` defined twice (second was a typo) | Second renamed `intrigue_per_stress_level` |
| `yan_on_action.txt`, `GM_value_on_action.txt` (Great Ming mod leftovers, ~350 error entries) | Deleted |

Still overriding vanilla, on purpose: the gender succession laws and `can_keep_*` triggers (`rse_*`, needed by the gender-succession cheat; identical to 1.20.1.2 apart from the flag escapes), the fake-DLC front-end widgets (`000_overrided_fronted_bookmark.gui`), and the overrides listed in Phase 7.

## Timed features that never ran

`monthly_global_pulse`, `monthly_playable_pulse`, `daily_global_pulse`, `daily_playable_pulse`, `on_quarterly_playable_pulse` and `on_yearly_pulse` aren't engine on_actions, so nothing hooked to them ran.

- **New monthly tick** (`common/on_action/ucm_monthly_tick.txt`): reschedules itself through the player every month, started on load and re-checked yearly. Per-player work runs in hidden event `ucm_monthly_tick.0001`.
- **Moved to the tick:** stats-100 lock, levy overflow, supply, baidubuqin/xinwuguai upkeep, water of life, AI audit/refresh/opposition/boost spread, fidelity sweep (was daily), marriage-ban sweep, realm-authority upkeep, government-lock upkeep (players already locked), strong and world deterrence. RSE enforcement moved to `quarterly_playable_pulse`.
- **Deleted** (no opt-in or destructive): monthly/daily trait and military guards, daily court-guest kick, daily removal of vanilla `grateful_opinion`, automatic government lock on load, titular AI wars (their titles don't exist), the broken guardian pulse.
- Startup: one world scan on load (`ucm_startup_sweep.txt`) instead of about seven.

## Inherited script

- Samge reaping and "kill dynasty" no longer kill your close or extended family or spouse; reaping builds its list once instead of two world scans per kill.
- World purge really caps at 25 per batch.
- Building effects no longer ask for tiers that don't exist (holding base; domicile presets pass each chain's tier count).
- Tradition editor: removed "undo last" and favourites, which checked flags nothing set (~786 error entries).
- Removed: calls to missing `holy_dynasty.0003/0004`, the unused innovation picker and its templates, the unreachable foreman feature, 31 dead `yyz` GUI buttons and their values, and orphaned events (`ucm_cheat_menu.1150`, `1800`–`1867`, `5050`, `ucm_officials.9061`–`9064`, `9087`, `9110`–`9112`, and others) with their effects and text.
- Duplicate definitions (later one won): the earlier copy is removed, so behaviour is unchanged.
- `interaction_menu_window.gui` called the missing `set_xa_size`; now `set_xa_height`.

## Localization and tools

- Pause-menu Debug/Fog of War labels translated; every `localization/replace/<lang>` file has the same 35 keys as English (German was overriding 352 vanilla keys).
- `gen_ucm_translations.py` checks the replace files too, builds every language before writing, and marks its output AUTO-GENERATED.
- `tools/ck3parse.py` is shared by the innovation and tradition generators (string-aware parsing, `--out`). The vanilla tradition list no longer references AGOT-only traditions (135 error entries); the AGOT list is a separate compatch under `tools/out/agot/`.
- Removed two `.vsix` files, three `.bak` files and a broken `.bat`; the icon pipeline moved to `tools/icon_pipeline/`. Added `.gitignore` and `.gitattributes` (pinned line endings, `export-ignore` for releases).
- `descriptor.mod`: standard tag only, `picture="thumbnail.png"`.

## Load test

CK3 1.20.1.2, only this mod.

| Run | error.log entries |
| --- | --- |
| Before (Phase 7), main menu | 2,706 |
| After, main menu | 995 |
| After, Phase 0 save loaded | 1,091 |

- The first run added 19 "should be in utf8-bom" entries (edited files had lost their BOM) and moved an old `scheme_type = romance` error (1.20 calls it `courting`). Both fixed.
- Two months on the Phase 0 save showed the AI ruthless-governance pulse firing on 1 January (806 entries): the "off" defaults were only written from `on_game_start_after_lobby`, which doesn't fire on load, and the monthly tick likewise only started on new games. Fixed with the quarterly player bootstrap in `ucm_monthly_tick.txt`.
- Re-run on the same save past 1 January with temporary error probes: the quarterly bootstrap ran, wrote the AI defaults, then the monthly tick fired a month later. No ruthless-governance entries. Probes removed.
- Remaining errors are inherited: 653 never-set variable/flag warnings, the character editor (`old_char_editor.txt`), Great Ming government code, other mods' titles, vanilla scheme scripts on that save.
- Saves from before the rebrand reference `the baseline mod_force_marry_religion`/`_faith`, which no longer exist; that custom faith is lost on load.

## Test checklist


- [ ] Target a king, second = his duke: "Vassal of second" is greyed out.
- [ ] Ally / hook buttons with a target that isn't you.
- [ ] Group convert-faith on your liege's vassals: you aren't converted.
- [ ] Population Administration: the governor rotation and loose court toggles show, switch and persist.
- [ ] Load an old save: AI enhancement features are off.
- [ ] After a month: `ucm_monthly_tick_alive` exists (console `global_var`), and a monthly feature you switched on (e.g. stats-100 lock) applies.
- [ ] Interaction menu opens at the saved height.
- [ ] Pause menu in German: Debug Mode and Fog of War have text.
