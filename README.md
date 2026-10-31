# Unified Cheat Menu

A single-player cheat menu for **Crusader Kings III 1.20 "Crozier"**. Inspired by Skonester Cheat Menu Gold and Daddy Pika's Cheat Menu, it puts everything in one tabbed window.

## Install

1. Put this folder in `Documents/Paradox Interactive/Crusader Kings III/mod/` (or link it there).
2. Add a `.mod` file next to it pointing at the folder, for example `path="mod/unified_cheat_menu"`.
3. Enable **Unified Cheat Menu** in a launcher playset.

Achievements: since CK3 1.9 neither Ironman nor an unmodified checksum is required to keep them ([Paradox wiki](https://ck3.paradoxwikis.com/Achievements)), so loading the mod should not by itself block them. This is from the wiki, not tested in-game with this mod. What does turn them off, as in vanilla:
- turning on debug mode or using console commands (the debug-mode buttons say so);
- switching to another character (the switch and play-as cheats say so);
- multiplayer, observer mode, or game rules that block achievements.

The cheats themselves don't block achievements, but the mod does change game data (checksum), so check the in-game achievement indicator before relying on it.

## Use

- **Right-click any character → Open Cheat Menu.** The window opens with that character as the **target**. Every button acts on the target unless it says otherwise.
- **Right-click someone → Set as Second Character** for actions that need two people: marriage, relationships, alliances, parentage and the like.
- **Group actions** (Court and Realm tabs): pick a group taken from the target, such as courtiers, vassals, house or the realm's counties, then an action. You see a count and confirm before anything changes.
- **Quick Actions** has the always-on cheats (income, health, levies and more) with strength, tier and frequency settings.
- Buttons labelled as decisions act on you and your realm. Buttons that can't apply are greyed out.

**Single-player only:** everything is hidden and the timed cheats stop while a second player is connected.

## Languages

English, German, Russian, Simplified Chinese and Turkish.

## Repository

| Path | What |
| --- | --- |
| `docs/unified-cheat-menu-spec.md` | Design spec (v1.3) and engine verification |
| `docs/phase*.md` | What each development phase added, with in-game test checklists |
| `docs/ek2-compatch-plan.md` | Elder Kings 2 compatibility survey and plan |
| `compat/ek2/` | Elder Kings 2 compatch, a separate mod that loads after both (see its `descriptor.mod`) |
| `tools/ck3parse.py` | Shared parsing helpers for the generators |
| `tools/audit_baseline.py` | Fails if code inherited from the original baseline reappears |
| `tools/check_refs.py` | Reports references to effects, triggers, events, traits and loc keys nothing defines |
| `tools/gen_ek2_compatch.py` | Regenerates the derived files in `compat/ek2/`, including the EK2 faith editor data and picker stubs |
| `tools/gen_faith_editor.py` | Generates the faith editor's data effects from the 1.20 doctrine, tenet and religion databases |
| `tools/gen_trait_editor.py` | Generates the trait editor window, its click dispatcher and its labels from the trait database |
| `tools/gen_artifact_crafter.py` | Generates the artifact crafter and editor: stack modifiers, effects, scripted GUIs, labels and windows |
| `tools/gen_lifestyle.py` | Generates the lifestyle editor from the perk database |
| `tools/gen_court_positions.py` | Generates the one-click court reshuffle position lists from the court position types |
| `tools/gen_ucm_realm_actions.py` | Generates the locked succession laws, elective laws and realm-wide actions (holdings, buildings, cures) from the vanilla law, trigger and building data |
| `tools/gen_ucm_main_menu.py` | Generates `gui/ucm_main_menu.gui` from a list of tabs and buttons |
| `tools/gen_ucm_extra.py` | Generates the Phase 12 actions merged into the main menu, the modifier editor and the tenet picker (run before `gen_ucm_main_menu.py`); other-language text comes from `tools/ucm_extra_translations.json` |
| `tools/gen_ucm_translations.py` | Generates the German, Russian, Chinese and Turkish menu text from the English |
| `tools/gen_cw_tradition_picker_lists.py` | Regenerates the tradition picker lists after a game update |
| `tools/gen_army_spawner.py` | Generates the army spawner window from the men-at-arms data |
| `tools/gen_ek2_tab.py` | Regenerates the Elder Kings 2 tab scripted GUIs, values and English text |
| `tools/gen_icons.py` | Redraws every DDS under `gfx/` as a badge built from its file name |
| `tools/gen_pickers.py` | Generates the culture, religion, faith and tradition pickers |
| `tools/gen_ucm_crozier.py` | Generates the Crozier toggles and actions |
| `tools/gen_ucm_domicile.py` | Generates the estate presets from the domicile buildings |

The game-data generators take `--game-dir <CK3>/game` (or `CK3_GAME_DIR`); rerun them after a game update instead of editing their output.

`ucm_` is the mod's namespace: everything the mod defines uses it, apart from engine-mandated keys. The core menu files are:
- `common/scripted_guis/ucm_{sguis,character_sguis,court_sguis,group_sguis,military_sguis,realm_sguis}.txt`
- `common/scripted_effects/ucm_effects.txt`, `common/scripted_triggers/ucm_triggers.txt`, `common/script_values/ucm_values.txt`
- `common/on_action/ucm_on_actions.txt`, `common/character_interactions/ucm_interactions.txt`
- `events/ucm_group_events.txt`
- `gui/ucm_main_menu.gui`, `gui/scripted_widgets/ucm_scripted_widgets.txt`
- `localization/*/ucm_l_*.yml`

## Releasing

`git archive --format=zip HEAD -o release.zip` gives a clean mod folder; `.gitattributes` marks docs, tools and repo files `export-ignore`.

## Credits and license

Inspired by **Skonester Cheat Menu Gold** by skonester (<https://github.com/skonester/Skonester-Cheat-Menu>) and **Daddy Pika's Cheat Menu** by DaddyPika, with contributions by **Zhuge**, Pavel, Bone, Leech, Sol, Xorxidox, Gravity, x4077, jestelf and other community contributors. The current mod no longer contains their code; earlier versions in this repository's git history derive from those mods under CC BY 4.0.

Licensed under [Creative Commons Attribution 4.0 International](LICENSE). Compared with the mods above, this one adds:
- the tabbed menu, targeting and group actions;
- the single-player gate;
- new translations;
- a full rewrite: no code from the original mods remains;
- no vanilla file overrides beyond what a feature needs, with vanilla-only data split out so total conversions can patch it;
- an Elder Kings 2 compatch.

See `docs/` for details.
