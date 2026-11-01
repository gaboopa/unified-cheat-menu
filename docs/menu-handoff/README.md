# Unified Cheat Menu layout handoff

A mockup of the in-game cheat menu (`gui/ucm_main_menu.gui`, 880×680 window), one screenshot per tab.
Labels come from `localization/english`. The interactive canvas is at
https://claude.ai/artifact/QcTNQrC7A55GvqP1XgdMTt (private until shared).

## Structure

- **Header:** title, `Target:` line, second-character line.
- **Left:** 11 category tabs, driven by `GetVariableSystem 'ucm_tab'`. Quick Actions is the default.
- **Right:** the active tab's pane: section headings (`UCM_SEC_*`), then a two-column grid of buttons.

## Tabs

| # | Tab | Screenshot |
|---|-----|-----------|
| 1 | Quick Actions | ![](screenshots/01-quick-actions.png) |
| 2 | Character & Genetics | ![](screenshots/02-character-genetics.png) |
| 3 | Relationships & Family | ![](screenshots/03-relationships-family.png) |
| 4 | Titles, Government & Diplomacy | ![](screenshots/04-titles-government-diplomacy.png) |
| 5 | Faith & Culture | ![](screenshots/05-faith-culture.png) |
| 6 | Realm, Holdings & Construction | ![](screenshots/06-realm-holdings-construction.png) |
| 7 | Military & Warfare | ![](screenshots/07-military-warfare.png) |
| 8 | Artifacts & Equipment | ![](screenshots/08-artifacts-equipment.png) |
| 9 | Court & Character Generation | ![](screenshots/09-court-character-generation.png) |
| 10 | DLC & Advanced Systems | ![](screenshots/10-dlc-advanced-systems.png) |
| 11 | Settings & Utilities | ![](screenshots/11-settings-utilities.png) |

## Caveats

- Screenshots show each tab's full length. In game the pane scrolls inside the 680 px window.
- The colours are an approximation of CK3's dark-and-gold style, not the game's textures.
- `[Buttons built from scripted lists]` marks sections whose buttons are generated at runtime: Holdings, Buildings, Economy & Population, Rulers & Officials, AI Behavior, Succession & Realm Laws, Convert Your Realm and Court Tools.
- Some interactions have no English name. Their labels are made from the internal key, for example "Take title and vassals" from `take_title_interaction`. Those keys need real localization.
- The Quick Actions toggles are shown in the OFF state, and the Character skills use a placeholder value of 8.
