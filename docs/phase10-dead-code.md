# Phase 10: Dead code: faith doctrine lists, scripted GUIs, events

Removes upstream code that nothing can reach, from the "Dead code" section of the earlier code review. Nothing reachable changed. This phase has not been load-tested yet.

## Faith doctrine lists (commit fa52434)

Deleted `ucm_acm_faith_refresh_active_doctrine_lists_effect` and `ucm_acm_faith_remove_doctrine_from_selected_effect` from `ucm_acm_faith_doctrine_lists_effects.txt` (40,354 lines; 53,216 to 12,862). Neither had a caller, and the `ucm_acm_fe_active_*` lists the refresh effect filled are never read.

**Kept:** `ucm_acm_faith_fill_empty_tenet_slots_effect` and `ucm_acm_faith_clear_empty_tenet_slots_effect`. Nothing calls them, but the spec lists them under the faith editor, so wiring them up or removing them is a spec decision.

## Scripted GUIs (398 of 2,230)

A scripted GUI is dead when its name appears nowhere else: not in `gui/`, `data_binding/`, `localization/`, `common/` or `events/`. No GUI builds scripted GUI names at runtime, so a literal search is complete.

| File | Removed |
| --- | --- |
| `ucm_cw_innovation_unlock_generated.txt`, `ucm_cw_innovation_remove_generated.txt`, `ucm_cw_innovation_toggle_sgui.txt` | Whole files (218). Their generator's docstring says the culture window built the names with `Concatenate('ucm_cw_unlock_', key)`, but no GUI in the repo's history ever did. `tools/gen_ucm_cw_innovation_sguis.py` is removed too |
| `ucm_acm_weapon_craft_gui.txt`, `ucm_culture_window_sidebar.txt` | Whole files (29 + 7) |
| `ucm_artifact_craft_gui.txt` | 115 of 139. The 66 names defined twice were identical copies, and all of them were among the dead ones |
| `old_scripted_gui.txt` | 18 of 128 (the `open_yyz_*_list` openers) |
| `ucm_acm_faith_editor_sgui.txt`, `ucm_cw_tradition_picker_sgui.txt`, `ucm_acm_culture_picker_sgui.txt` | 8, 2 and 1 |

## Events (260 of 1,047)

Roots are event ids referenced from `common/` and `gui/`. Edges are the references from one event to another. Event ids compare as namespace plus a number, so `.0004` and `.4` are the same event. Everything unreachable from a root was removed, except the 15 events below.

| File | Removed |
| --- | --- |
| `ucm_global_culture_selector_generated.txt` | Whole file (41, culture selector `1900–1940`) |
| `ucm_beauty_companion_generated.txt` | Whole file (35) |
| `ucm_cheat_menu_craft_mod_picker_generated.txt` | Whole file (35, old artifact-crafting chain) |
| `ucm_treasure_maker_stat_menu_generated.txt`, `ucm_treasure_maker_events.txt` | Whole files (30 + 5, a closed loop) |
| `ucm_birth_cheat_events.txt`, `ucm_auto_appointment_test_events.txt` | Whole files (7 + 4) |
| `ucm_cast_culture_faith_generated.txt` | 64 of 159 (faith picker `3300–3456`; `.3186` is used and stays) |
| `ucm_global_pillars_on_selected_generated.txt` | 22 of 54 |
| `ucm_cheat_menu_events.txt` | 16 of 98 (old crafting confirm pages `0030–0038`, `0106–0109`, …) |
| `old_char_editor.txt` | `.67` (regional innovation page, only opened by itself) |

**Kept though unreachable:**
- `imperial_examination.9000/9001`: they override vanilla events that the game fires itself. The stale copy is a separate Required item in the review.
- The 12 activity cheats (`ucm_cheat_menu.3091…`): the spec's Activities section wants them reconnected.
- `ucm_domicile_cheat.0100`: rewritten in Phase 8 and deliberately reachable from the console.

## Left for later
- Localization keys of the removed events and scripted GUIs (part of the review's dead-localization item).
- Scripted effects, triggers and modifiers whose only callers were removed here, such as the treasure-maker stat tiers.

## Checks run
- Every edited file kept its BOM and brace balance, and its non-blank lines are an in-order subset of the old file (only deletions; the diff shows some insertions because runs of blank lines were squeezed).
- Re-running both scans finds no dead scripted GUIs, and the reachable event count is unchanged (772).

## Test checklist
- [ ] Load test with only this mod enabled. Compare error.log with the Phase 9 counts (725 main menu / 853 save). Expect no new missing scripted GUI or event errors.
- [ ] Faith editor, culture picker, tradition picker, artifact crafter and Court Positions list open and work.
- [ ] Character editor (`old_char_editor`) regional innovation options still work.
- [ ] Culture/faith casting and pillar pickers from the classic menus still open their pages.
