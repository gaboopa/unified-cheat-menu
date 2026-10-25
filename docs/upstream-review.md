# Upstream code review

A read-only review of the code inherited from Skonester Cheat Menu Gold. It covers about 846 files and 575k lines; the 20 menu files that are new to this mod (listed in the README) are out of scope. Nothing has been changed yet.

**Method.** Five reviewers each took one area. They checked it against vanilla CK3 1.20.1.2, grepped the whole repo for references, and traced which events can be reached. The Phase 8 load-test error.log was overwritten when the game was later launched with a different playset, so the findings come from static checks. A few early error.log categories were matched to causes before it was overwritten. Every Critical item, and a sample of the Required items, was checked by hand.

**Status:** C1–C10 are done, and the Great Ming, titular-title and dragon-page code is removed; see [phase9-upstream-fixes.md](phase9-upstream-fixes.md). Dead faith doctrine lists, scripted GUIs and events are removed; see [phase10-dead-code.md](phase10-dead-code.md).

Severity: **Critical** changes the game for everyone or is broken in a way players will hit. **Required** is a bug, a stale vanilla copy, or content the AI gets. **Optional** is duplication or performance. **Nit** is cleanup.

## Critical: the base game changes for every game

| # | Where | Problem | Fix |
|---|---|---|---|
| C1 | `common/script_values/skone_legends_values.txt` | Overrides vanilla `spread_chance_legends_default_value` (314 lines) with 20 lines. Player legends get +80, AI legends get −0.99, and the vanilla formula is gone. | Delete |
| C2 | `common/script_values/ucm_cheat_values.txt:1` | `erudition_legacy_5_percentage` is 10 in vanilla and 100 here, for every dynasty. The `is_ai = no` limit is commented out. | Delete |
| C3 | `common/decisions/005_zhuge_qita_decisions.txt:41` | Stale copy of vanilla `dynasty_of_many_crowns_decision`. It needs 2 kingdoms instead of 10, the AI can take it, and it is checked at every tier every 120 days. | Delete the override |
| C4 | `common/buildings/DB_duchy_*.txt` (4 files, 72 buildings) | An entire other mod is embedded here. The AI builds these in every game (`ai_value = 20`, no gate), and no mod script references them. | Delete, along with the `DB_buildings_l_*` loc and the `icon_db_*` icons |
| C5 | `common/men_at_arms_types/notvanilla.txt:7,63` | Every human player can recruit house guard and house cavalry normally: damage 180/150, cost 1, upkeep 0. | `can_recruit = { always = no }`. The cheat uses `spawn_army`, which ignores this |
| C6 | `common/traits/knightBlood.txt`, `savant_traits.txt` | Super-traits are seeded into the population (`birth` 0.03–0.1). The AI gets +5–6 skills. | `birth = 0`, `random_creation = 0` |
| C7 | `common/laws/skone_title_succession_laws.txt` | 1-prestige elective title laws are open to every duke or higher, AI included. | Add `is_ai = no` plus a flag to `can_have` |
| C8 | `common/script_values/09_mpo_values.txt` | A full copy of a 2,979-line vanilla file, made to add 19 lines (a `bloodline_god` bonus). Any vanilla change to the other 230 values is silently lost. | Delete; override the one key in its own file if wanted |
| C9 | `gui/yyz_buttons.gui:17` | Takes over Ctrl+Y (vanilla `redo`) to open the Court Positions list. Its other 8 shortcuts don't exist. | Delete the file and its line in `scripted_widgets/yyz.txt` |
| C10 | `common/scripted_effects/ucm_crozier_cheats_effects.txt:633,865,1313` | Kill, execute, depose and banish have no self or family guard and no confirm step. This is the same hole Phase 8 closed for samge and kill-dynasty. | Add the same family/spouse/self limit |

## Required

### Broken references (content that doesn't exist in 1.20)
- **Great Ming leftovers.** These remove another mod's globals at game start, which breaks our own compat probe:
  - Files: `ucm_government_bianshen_daming_effects/triggers.txt`, `ucm_daming_ming_gov_menu_decisions.txt`, `events/ucm_government_reform_events.txt` (unreachable: `ucm_chenzhi_menu_pending` is never set), `change_sansi_government`, the `zhuge_sansi` menu, `zhuge_daming_currency_menu`, `zhuge_uec_on_actions.txt:34`, and `Data_tuiju`/`hq_check` in `ucm_tgp_glue_on_actions.txt`.
  - They reference 10 governments that don't exist.
  - **Fix:** delete all of it, then simplify the 29 `ucm_is_gm_yan_*` callers.
- ~~`japan_administrative_government` not in 1.20~~ **Wrong, retracted in Phase 9.** It exists in vanilla `01_japan_government_types.txt`. `003_daddy_pikas_decisions.txt:1` and `:584` are still two near-duplicate decisions, and `:584` also turns every county into a city. That's duplication, not breakage.
- **Titles that don't exist.** `ucm_authority_title_*`, `ucm_expansion_title_*` and `ucm_titular_supremacy_*` (effects, triggers, modifiers) reference 10 `e_/k_ucm_*` titles that are never defined. All 23 effects have 0 callers. **Fix:** delete.
- **`eunuch` is `eunuch_1` in 1.20:**
  - `ucm_ce_unl_doctrines.txt` (16 `sins/virtues`)
  - `DP_present_effects.txt:591`
  - `events/dp_char_editor.txt:4129`

  **Fix:** rename.
- **Dragon page.** `events/dp_char_editor.txt:15384–15621` (`.514`, `.515`) uses 13 AGOT `dragon_*` traits. **Fix:** delete both events and the option that opens them.
- **Missing game rule.** `events/Realm_Succession_events_mod.txt` checks `change_Realm_succession_law_game_mod_on` 8 times, and no game rule defines it. **Fix:** remove the innovation gating.
- **Genetic traits with `inherit_chance`.** 10 `blood_ancester_*` and 3 `toc_patrilinealblood*` traits set both, which the engine flags as an error. **Fix:** drop `inherit_chance`.
- **Missing textures:**
  - `gui/ucm_acm_faith_editor.gui:189,232`: `sin_big.dds` and `virtue_big.dds` don't exist; use `sin.dds` and `virtue.dds`.
  - `gui/ucm_sand_soldiers.gui`: 14 Great Ming MAA icons; use `[MenAtArmsType.GetIcon]`.
- **Missing loc key.** `FAITH_WINDOW_TENET_TOOLTIP` is no longer in vanilla; it is used in 4 faith-editor GUIs. **Fix:** define it.
- **Wrong comparison.** `99_ucm_consolidated.txt:1737` compares `faith = root`, a faith against a character. **Fix:** `scope:awakening_faith`.

### Logic bugs
- **Realm succession flags.** `events/Realm_Succession_events_mod.txt:131,189,247,355,413,471`: "Only me" sets a law flag without clearing the other five, so the quarterly enforcement then applies several laws in a row. **Fix:** a `realm_rse_flag_cleanup` effect like the gender version, called in all 18 options. This also removes 12 copy-pasted blocks.
- **Artifact slot sync.** `ucm_acm_artifact_slot_sync_effects.txt:99–7613`: each of the 402 detection blocks uses plain `if`s that each add 1 to the slot counter, so the first modifier found fills all five slots. **Fix:** `else_if`, or regenerate the block as one parameterised effect.
- **Imperial exam override.** `events/ucm_imperial_examination_merit_override.txt` is a stale copy of vanilla `imperial_examination.9000/9001`:
  - all four skill descriptions point to the diplomacy text;
  - it uses `stress_impact` where 1.20 uses `stress_and_fulfillment_impact`;
  - it has the wrong background.

  **Fix:** re-copy the 1.20.1.2 events and change only the merit, or delete the file.
- **`special_gift_2`.** `00_special_gift_2.txt` puts `is_adult = no` inside a `NOT`, which inverts the intended check.

### Stale vanilla copies (they drift every patch)
| File | What drifted | Fix |
|---|---|---|
| `gui/window_character.gui` (6,175 lines) | Missing about 25 vanilla 1.20 lines (clergy-ruler Court tab), plus 5 layout hacks from the EPE mod | Move the Crozier panels (line 4573+) into a `ucm_main_menu` tab, then delete. Short term: re-copy vanilla and paste the block back |
| `gui/00_ucm_interaction_templates.gui` | Drops the 1.20 puppet-interaction glow; its only change is a font size | Delete |
| `gui/interaction_menu_window.gui` | Height and fold quality-of-life code from another mod, plus an override of `flowcontainer_category_group` | Re-copy vanilla and keep only the `CanCustomizePortrait` line |
| `zzzzzzzz_0toc_deb_int.txt` | 10 vanilla debug interactions as pre-1.18 copies (`is_landed`, no landless handling) | Delete those 10 blocks |
| `99_ucm_interactions_modified.txt` | 47 vanilla debug interactions, 6 of them stale (artifact options, `rite`, `?=` lost) | Delete, or generate from vanilla each patch |
| `music/main_themes/music.txt` | Replaces the vanilla file to add one track | Rename to `ucm_music.txt` |
| `localization/simp_chinese/fully_consolidated_l_simp_chinese.yml:738–1302` | A full copy of vanilla `debug_l` (546 keys) | Delete that section; `replace/` already has the changed keys |

### Content shown to everyone
- **Empty tenets.** `religion/tenet_types/ucm_mts_empty_tenets.txt` shows 20 zero-cost "empty" tenets in every faith reform. **Fix:** delete, or gate on the cheat flag.
- **Polygamy traditions.** `culture/traditions/zz_ucm_variations_of_cultural_polygamy.txt` is visible to every player, and its parameters don't exist in 1.20. **Fix:** gate on the cheat flag and drop the dead parameters.

## Optional: performance

- **Monthly world scans.** Five upstream sub-pulses on our monthly tick each scan every living character, every month: trait guard, levy overflow, supply, stats-100, water of life. **Fix:** keep a global list of the characters who got the cheat and iterate that. At minimum, gate each pulse on "feature in use".
- **AI boost spread.** `ucm_ai_boost_spread_effects.txt:22`: `while count = 600` runs 3–4 world scans per pass, up to about 2,400 a month when the feature is on. **Fix:** one `ordered_living_character`.
- **Auto marriage.** `auto_marriage` fires 7 events for every character every year, scanning the global lists before cheap checks such as `is_adult`. **Fix:** gate the on_action on the lists existing.
- **Trait editor.** `gui/ucm_trait_editor.gui` makes 903 scripted-GUI calls per frame, each a chain of about 300 `trigger_if`s. **Fix:** use `Character.HasTrait(GetTrait(...))` and delete `ucm_trait_editor_sgui.txt`. The same applies to `ucm_cheat_trait_editor.gui`.
- **Strategic audit.** `ucm_ai_monthly_strategic_audit.txt:52` has an O(n²) `while` + `any_vassal` loop.
- **Dread loops.** `ucm_cheat_menu_edit_resources_effects.txt` has six `while count = 600 { add_dread = ±1 }` loops. **Fix:** one `add_dread`.
- **Uncompressed images.** 4 decision illustrations, 7.7 MB. **Fix:** convert to DXT1, saving about 6.5 MB.

## Optional: duplication

| Where | Now | After |
|---|---|---|
| `events/ucm_char_design_events.txt` | 40,023 lines; 6 creation events of about 3,100 lines each, male and female differing only in `gender_female_chance` | About 3,000 lines using 2 parameterised effects |
| `DP_child_effects.txt` | 2,819 lines; 14 heir effects that differ only by age and gender | About 200 |
| `DP_modifier_effects.txt` | 5,569 lines; 274 blocks repeated in each of 5 effects | One `$MOD$` step effect |
| `ucm_crozier_cheats_effects.txt` | 31 features × 5 effects, minified (lines up to 64k characters) | One `$KEY$` set |
| `ucm_ce_unl_doctrines.txt` | 41,986 lines (94 traits × 32 slots); the generator is missing | Fewer slots, or restore the generator |
| `ucm_enfeoffment_effects.txt` | 4 copies of the pool builder | 1 |
| `sol_*` casus belli (5 files) | Near-identical; `target_de_jure_regions_above` set twice | 1 file |
| `00_special_gift_1..4` | About 95% identical | 1 interaction |
| `ucm_religion_on_actions.txt` | A subset of `ucm_mts_religion_on_actions.txt` | Delete |
| Legacy open/close toggles (`001_`/`002_` decisions, `pcm_*`, `toc_*`, bone, optroop) | Duplicate `ucm_menu_open_effect` | Delete |

**Missing generators.** About 25 files are marked AUTO-GENERATED, but their generators aren't in `tools/`. Either restore the generators or remove the headers and edit the files by hand.

## Dead code

| Area | Amount | Main pieces |
|---|---|---|
| Scripted effects | 305 effects, about 48,900 lines | 40,483 lines of `ucm_acm_faith_doctrine_lists_effects.txt` (`refresh_active_doctrine_lists`, fill/clear tenets) and 39 whole files (marriage, betrothal and pregnancy ports, old craft-on-owner, positions snapshot, `ucm_remove_bad_traits`, …). The full list is in the reviewer's `dead_trans.txt` |
| Events | 277 events, about 10,000 lines | Old artifact-crafting chain (about 4,000 lines), treasure maker (35 events), faith picker `3300–3456`, culture selector `1900–1940`, beauty companion `3000–3034`, birth cheat, `ucm_auto_appointment_test`. The activity cheats `3091…` are listed in the spec, so reconnect them instead |
| Scripted GUIs, triggers, values | About 500 | 216 `ucm_cw_innovation_*` sguis (with their generator), 182 of 205 in `ucm_artifact_craft_gui.txt` (66 defined twice), `ucm_acm_weapon_craft_gui.txt`, the title and conversion triggers, the `yyz` filters |
| Data | 25 modifiers, 20 traits, 3 nicknames, 57 custom-loc entries | Most of the `toc_*`, `ucm_clear_secrets_preview.txt` (about 700 lines), `wandering_life` concept, `pcm` decision group |
| GUI files | 3 | `ucm_acm_faith_pick_panel.gui` and `_bridge.gui` (not registered, duplicate types), `yyz_buttons.gui` |
| Assets | 90 files | 71 byte-identical to vanilla (1.4 MB); 19 unreferenced (1.2 MB) |
| Localization | About 2,500 keys per language | Biggest: `ucm_officials` (839), `sarc_char_design` (520), `new_tocmod` (400) |
| Comment-only files | About 12 | `zzzzzzzz_01_toc_maa_types.txt`, `ucm_acm_pick/slot_modifiers.txt`, `zhuge_concepts.txt` (wrong folder), `ucm_repair_artifact_effects.txt`, `ucm_heir_ui_refresh_on_actions.txt`, `zzz_ucm_daming_ming_gov_menu_probe.txt`, `ucm_domicile_cheat_decisions.txt`, … |

## Nit
- Chinese comments in 125 of 156 effect files and 29 event files. Some are mojibake, in `99_zhuge_character_interaction.txt`.
- `ucm_cheat_menu_events.txt` is 52% blank lines.
- **Localization headers and languages:**
  - `german/.../zhuge_curry_menu_events_l_german.yml` has an `l_english:` header.
  - German, Russian and Chinese override 8, 30 and 11 vanilla keys outside `replace/`.
  - Turkish isn't a 1.20 language: 20 files, 4,583 keys short.
- **Unprefixed globals.** `yyz_triggers.txt` uses unprefixed global names and `root` without `?=`, the likely cause of the null-target errors.
- **File names.** Prefixes come from source mods (`DP_`, `X_`, `zhuge_`, `toc`, `zzzzzzzz_`, `sol_`). Rename them by feature only while doing the deletions above.

## Checked and fine
- No duplicate event ids, no `trigger_event` to an event that doesn't exist, and no namespace collisions except the deliberate imperial-exam override.
- The data layer redefines no vanilla keys other than the documented `rse_*` gender laws. `frontend_ingame_menu.gui` is in sync with 1.20.1.2.
- All 501 crozier decision-cooldown keys, every faith-editor doctrine and tenet, and every innovation, building and law reference resolve in 1.20.1.2.
- No decision has a non-zero `ai_will_do` with a reachable `is_shown` (except C3), and no interaction has `ai_targets`.
- World purge, imprisoning vassals, the marriage-ban strip, water of life and the `rse_gender` code are small and correct.

## Suggested order
1. **Critical C1–C10.** Small diffs, and they remove the global side effects.
2. **Delete the broken references.** Great Ming, Japan admin, titular titles, dragon page. These clear most of the remaining error.log noise.
3. **Delete dead code**, one area at a time (effects, events, sguis, data, assets, loc), each followed by a load test.
4. **Fix the stale vanilla copies** (window_character, interaction menu, debug interactions).
5. **Remove duplication and fix performance.** Char design, DP files, monthly pulses, trait editor.
