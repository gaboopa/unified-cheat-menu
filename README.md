# Unified Cheat Menu

A single-player cheat menu for **Crusader Kings III 1.20 "Crozier"**. It's built on Skonester Cheat Menu Gold and organized into one tabbed window.

## Install

1. Put this folder in `Documents/Paradox Interactive/Crusader Kings III/mod/` (or link it there).
2. Add a `.mod` file next to it pointing at the folder, for example `path="mod/unified_cheat_menu"`.
3. Enable **Unified Cheat Menu** in a launcher playset.

The mod changes game files, so achievements and ironman are off while it's enabled.

## Use

- **Right-click any character → Open Cheat Menu.** The window opens with that character as the **target**. Every button acts on the target unless it says otherwise.
- **Right-click someone → Set as Second Character** for actions that need two people: marriage, relationships, alliances, parentage and the like.
- **Group actions** (Court and Realm tabs): pick a group taken from the target, such as courtiers, vassals, house or the realm's counties, then an action. You see a count and confirm before anything changes.
- **Quick Actions** has the always-on cheats (income, health, levies and more) with strength, tier and frequency settings.
- Buttons labelled as decisions act on you and your realm. Buttons that can't apply are greyed out.
- The original event-based menus are still under **Settings & Utilities → Classic Menus**.

**Single-player only:** everything is hidden and the timed cheats stop while a second player is connected.

## Languages

English, German, Russian, Simplified Chinese and Turkish.

## Repository

| Path | What |
| --- | --- |
| `docs/unified-cheat-menu-spec.md` | Design spec (v1.3) and engine verification |
| `docs/phase*.md` | What each development phase added, with in-game test checklists |
| `docs/upstream/` | The original project's README and development notes |
| `tools/gen_ucm_main_menu.py` | Generates `gui/ucm_main_menu.gui` from a list of tabs and buttons |
| `tools/gen_ucm_translations.py` | Generates the German, Russian, Chinese and Turkish menu text from the English |
| `tools/gen_ucm_cw_innovation_sguis.py`, `tools/gen_cw_tradition_picker_lists.py` | Regenerate the innovation and tradition pickers after a game update |

The menu's own files are `common/**/ucm_*` (scripted GUIs, effects, triggers, interactions), `events/ucm_*`, `gui/ucm_main_menu.gui` and `localization/*/ucm_l_*.yml`.

## Credits and license

Based on **Skonester Cheat Menu Gold** by skonester (<https://github.com/skonester/Skonester-Cheat-Menu>). That project in turn builds on **Daddy Pika's Cheat Menu** by DaddyPika, with contributions by **Zhuge**, Pavel, Bone, Leech, Sol, Xorxidox, Gravity, x4077, jestelf and other community contributors.

Licensed under [Creative Commons Attribution 4.0 International](LICENSE). **This is a modified version.** Changes include:
- the tabbed menu, targeting and group actions;
- the single-player gate;
- renaming all identifiers and visible branding;
- new translations;
- removed and rebased vanilla overrides.

See `docs/` for details.
