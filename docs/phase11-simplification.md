# Phase 11: Simplification, bug fixes, dead code round 2

Works through the rest of the earlier code review after [phase10-dead-code.md](phase10-dead-code.md). Nothing here has been load-tested yet. Haiku agents did the mechanical rewrites and Sonnet agents the two design-heavy ones (artifact windows, monthly pulses). Every result was re-checked as described below.

**Equivalence checker.** Where a rewrite should not change behaviour, a script inlined the new parameterised helpers (substituting `$PARAM$`) and compared every top-level object with the git HEAD version, ignoring whitespace and comments. "N/N equivalent" below means every effect or event expands back to exactly the old text.

## Our menu code

| Was | Now |
| --- | --- |
| `ucm_menu_open_effect` and `ucm_menu_close_effect` each listed the same 13 sub-menu flags | One list in `ucm_menu_sub_flags_effect`, passed the on or off step (`$DO$`, as `ucm_group_for_each_effect` already does). Equivalent except the next row |
| Close also cleared two Phase 2 marker flags | Removed. Only dev builds ever set them; the menu was never released with them |
| 14 `ucm_group_picked_*` scripted GUIs decided which group button shows pressed | The generator uses `ObjectsEqual( GetPlayer.MakeScope.Var( 'ucm_group_pick' ).GetFlagName, '<group>' )`, the pattern vanilla uses in `chariot_race_widget_types.gui:105` |

## Bug fixes

| Where | Was | Now |
| --- | --- | --- |
| `ucm_acm_artifact_slot_sync_effects.txt` | Each detection block wrote the modifier into slot 1, then (plain `if`s) slots 2–5 too, so one modifier filled every slot | One `put` helper with `else_if`: each modifier the artifact has takes the next free slot. 106 blocks became 98 calls; 8 duplicate blocks (same modifier, different count) dropped, since they would now take a second slot. 7,654 to 344 lines |
| `00_special_gift_2.txt` | `NOT = { is_adult = no has_trait = water_of_life }` offered the gift to spouses who already had the trait | `is_adult = yes` and `NOT = { has_trait = water_of_life }` |
| `ucm_imperial_examination_merit_override.txt` | Stale copy of vanilla `imperial_examination.9000/9001` (wrong skill descriptions, old `stress_impact`, wrong background) | Fresh 1.20.1.2 copy. Differs from vanilla only in `id_override_priority`, the skill-scaled merit (2 lines), the government-lock call (2) and the mod's examiner fetch |

## Copy-paste folded into parameterised effects (behaviour unchanged)

| File | Lines | Check |
| --- | --- | --- |
| `events/ucm_char_design_events.txt` + new `common/scripted_effects/ucm_char_design_effects.txt` | 40,023 to 25,269 + 5,291. 306 option bodies call 102 helpers (`PARENT`, `CHANCE`); option wrappers stay in the events because names and triggers can't move into an effect | 61/61 equivalent |
| `old_modifier_effects.txt` | 5,569 to 1,943 (5 helpers over 266 keys; about 11 irregular blocks left written out) | 9/9 equivalent |
| `old_child_effects.txt` | 2,819 to 869 (4 helpers; the age-18 heirs have extra traits, so they get their own two) | 70/70 equivalent |

## GUI work per frame

| Where | Was | Now |
| --- | --- | --- |
| `ucm_trait_editor.gui`, `ucm_cheat_trait_editor.gui` | 945 calls into a 301-branch scripted GUI just to ask "has trait X" | `GetPlayer.MakeScope.Var('ucm_trait_gui_target').Char.HasTrait( GetTrait('x') )`. `ucm_trait_gui_has` (1,212 lines) and `ucm_cheat_trait_gui_has` deleted |
| `ucm_acm_mod_pick_guis.txt` | 375 "is selected" scripted GUIs | The GUI compares the slot variable directly (`EqualTo_CFixedPoint( ...Var('ucm_craft_m1').GetValue, '(CFixedPoint)3' )`). The 375 "pick" scripted GUIs stay (GUI can't pass a number into `Execute`) but are one-liners now. 10,500 to 4,486 lines. Side effect: with nothing picked, value 0 ("none") shows as selected |
| `ucm_artifact_craft.gui`, `ucm_artifact_repair.gui` | The five modifier-slot panels (≈4,000 lines) were byte-identical in both windows | Defined once as types in the new `gui/ucm_artifact_shared.gui`. 4,504 + 4,212 to 524 + 232 + 3,992 |

## Performance

**Monthly pulses.** Trait guard (two traits), stats-100, levy overflow and supply each scanned every living character every month. Now:
- Each one iterates a global holder list (`ucm_<x>_holders`).
- The cheats add characters to the list when they grant the trait or modifier (`ucm_holder_list_add_effect`).
- After the work, stale entries (dead, or no longer holding it) are collected in a temporary list and removed, so nothing is removed while the list is being iterated.
- Existing saves have holders but no list, so the first pulse does the old full scan once to build it (`ucm_<x>_list_built`).
- Water of life works the same way (`ucm_water_of_life_holders`). Its six grant sites register the holder: the four special gifts, `water_of_life_effect` (the decision) and the hooded old man that `water_of_life.1008` creates. This was the only one of these scans that ran for every player, since it had no feature gate.
- The AI-boost spread loop is left as is. The boost is off by default in every save (`ucm_ai_write_defaults_once_effect`) and only runs if the player turns it on, and a cap of 600 across tiers had no safe one-pass equivalent.

**Loops.** Two kinds of loop now make a single call:
- `while count = 600 { add_dread = -1 }` (×3, which set dread to zero) is now `add_dread = -600`.
- `while count = 150 { add_dread = 1 }` (which locked dread at 100) is now `add_dread = 100`.

Both rely on dread being clamped to 0–100 (`MAX_DREAD = 100`). The loops that step towards a target value were left alone, since dread can be fractional. So were the `count = 11` modifier loops, because those modifiers have `stacking = yes`.

## Dead code, round 2

- **Definitions.** 637 scripted effects, triggers, script values and modifiers that nothing reaches (52 whole files, 355 blocks). Reachability was taken to a fixpoint and expanded names built from parameters (`$MOD$_neg`). It kept 12 vanilla overrides and every name that vanilla's own files mention.
- **Localization.** 1,428 keys across the five languages that belonged only to definitions removed since `fa52434` (event text, scripted GUI labels, modifier names) and that nothing else references. All their owners have a mod prefix. 12 localization files were left empty and are deleted.
- **Unused tenet effects.** `ucm_acm_faith_fill/clear_empty_tenet_slots_effect` are removed. Nothing in upstream or here ever called them, and the spec line asking to keep them is struck.

## Not done
- **Decision illustrations:** converting the 4 uncompressed images to DXT1 (about 6.5 MB saved). There is no DDS encoder on this machine; use texconv or paint.net with BC1/DXT1.
- **Generators:** the headers of the slot sync, faith editor and trait editor files name generators that aren't in the repo. These files are now hand-edited, so don't regenerate them from an old copy.

## Test checklist
- [ ] Load test with only this mod: compare error.log with Phase 9 (725 main menu / 853 save). Watch for unknown effects, triggers, scripted GUIs or loc keys.
- [ ] Main menu: open and close; the classic right-click and decision entries appear while it's open and disappear after. Pick each group: the right button shows pressed.
- [ ] Trait editor and cheat trait editor: checkmarks match the target's traits; toggling works.
- [ ] Artifact crafter and repair: all five modifier rows show and highlight the picked value; crafting and repairing apply the chosen modifiers. Repairing an artifact with 2–3 modifiers fills exactly that many slots.
- [ ] Character design events (`sarc_char_design`): create a male and a female character; parent and gender are right.
- [ ] Heir spawns from the DP child menu (ages 0–18, both genders) and the DP modifier +/−/reset pages.
- [ ] Imperial exam (Celestial): palace exam merit is skill-scaled; descriptions match the skill.
- [ ] Special gift 2 is not offered to a spouse who already has water of life.
- [ ] Old save with a stats-100 or levy-overflow character: after one month the cheat still applies; a new holder is picked up the month after it's granted.
- [ ] Water of life: on an old save, a holder's illnesses are still cleared monthly; a character given the trait by a special gift or the decision is restored the following month.
- [ ] Set dread to zero and lock at 100 from the menu.
