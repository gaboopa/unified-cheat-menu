# Unified Cheat Menu

A single-player cheat menu for **Crusader Kings III 1.20 "Crozier"**. It's built on Skonester Cheat Menu Gold and organized into one tabbed window.

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
| `tools/icon_pipeline/` | Trait icon regeneration scripts (V + ComfyUI), kept out of `gfx/`. See its README |

Only the generators above are in the repo. The other big `*_generated.txt` files (faith editor, trait editor, culture/faith casting, crafting modifiers, lifestyle, court positions, treasure-maker stat tiers, beauty companion) came from upstream scripts that upstream never published, so edit those files by hand.

`ucm_` is the mod's namespace; upstream files were renamed into it too, so not every `ucm_` file is new. The genuinely new menu files are:
- `common/scripted_guis/ucm_{sguis,character_sguis,court_sguis,group_sguis,military_sguis,realm_sguis}.txt`
- `common/scripted_effects/ucm_effects.txt`, `common/scripted_triggers/ucm_triggers.txt`, `common/script_values/ucm_values.txt`
- `common/on_action/ucm_on_actions.txt`, `common/character_interactions/ucm_interactions.txt`
- `events/ucm_group_events.txt`
- `gui/ucm_main_menu.gui`, `gui/scripted_widgets/ucm_scripted_widgets.txt`
- `localization/*/ucm_l_*.yml` and `localization/replace/*`

`music/skonegold.ogg` (the alternate main-menu theme) comes from upstream with no recorded source or license; it is not covered by the CC BY 4.0 grant until that is known.

## Releasing

`git archive --format=zip HEAD -o release.zip` gives a clean mod folder; `.gitattributes` marks docs, tools and repo files `export-ignore`.

## Credits and license

Based on **Skonester Cheat Menu Gold** by skonester (<https://github.com/skonester/Skonester-Cheat-Menu>). That project in turn builds on **Daddy Pika's Cheat Menu** by DaddyPika, with contributions by **Zhuge**, Pavel, Bone, Leech, Sol, Xorxidox, Gravity, x4077, jestelf and other community contributors.

Licensed under [Creative Commons Attribution 4.0 International](LICENSE). **This is a modified version.** Changes include:
- the tabbed menu, targeting and group actions;
- the single-player gate;
- renaming all identifiers and visible branding;
- new translations;
- removed and rebased vanilla overrides.

See `docs/` for details.
