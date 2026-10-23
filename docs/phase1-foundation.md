# Phase 1 — Foundation

Implements spec v1.3 Phase 1: single-player gate, clicked-target and second-character targeting, the main menu, and the group-action framework with confirmation. Checked in single-player on 2026-10-23: the menu's buttons open the Skonester editors or apply their action. The multiplayer gate, group-action counts and `error.log` haven't been checked yet (checklist items 5–10).

## What changed

**Single-player gate.** `ucm_single_player_trigger` (`common/scripted_triggers/ucm_triggers.txt`) is `has_multiple_players = no`. It was added to:

- `is_shown` of all 204 interactions, all 92 decisions, and all 2,153 scripted GUIs (653 had no `is_shown` and got one).
- `trigger` of 36 cheat pulse on_actions, such as `ucm_crozier_cheats_quarterly`, the authority/government locks, deterrence, water of life, supply and levy pulses, and the AI boost pulses. Startup, compatibility, trait-guard, and cleanup on_actions are left alone.
- GUI elements Skonester injects into vanilla screens, which now also check `Not( GameHasMultiplePlayers )`: 115 Crozier cheat elements in `window_character.gui`, the menu-height controls in `interaction_menu_window.gui`, the pause-menu debug button, and the yyz shortcut buttons.
- `tools/gen_ucm_cw_innovation_sguis.py`, which now emits the gate.

New interactions, decisions, scripted GUIs, and cheat pulses must include it too.

Limits: a window that's already open when a second player connects stays open until closed. Cheats already applied as traits or modifiers stay on characters; only the recurring pulses stop.

**Targeting.**

- Right-click → **Open Cheat Menu** stores the clicked character as the target (`var:ucm_target` on the player) and opens the main menu. It also sets the baseline's recipient, so editors opened from the menu edit that character.
- Right-click → **Set as Second Character** / **Clear Second Character** use the baseline's existing `global_var:ucm_crozier_cheats_other`, so the Crozier two-character cheats keep working.
- When the target or second character dies, they're forgotten (`common/on_action/ucm_on_actions.txt`).

**Main menu** (`gui/ucm_main_menu.gui`). A window showing the target, the second character, and 11 category tabs. Tabs that already have tools in the baseline link to them:

| Tab | Buttons |
| --- | --- |
| Quick Actions | +1,000 gold, prestige, piety |
| Character & Genetics | Trait editor, cheat trait editor, lifestyle editor |
| Relationships & Family | Make target the second character, clear second character |
| Faith & Culture | Culture picker, faith picker, tradition editor |
| Realm, Holdings & Construction | Group: max development / max control in every realm county |
| Military & Warfare | Army spawner |
| Artifacts & Equipment | Artifact workshop, artifact editor |
| Court & Character Generation | Group: clear stress for every courtier |
| Settings & Utilities | Debug mode helper, clear second character |
| Titles, DLC | Placeholder (later phases) |

The picker interactions in `01_ucm_gui_launcher_interactions.txt` now call shared effects (`ucm_open_*_picker_effect`) so the menu and the interactions use one implementation.

**Group actions** (`common/scripted_effects/ucm_effects.txt`, `events/ucm_group_events.txt`). A button sets the group and action, then event `ucm_group.1` shows the group size and how many members will change, with Apply/Cancel. Applying visits every member, changes eligible ones, counts the rest as skipped, and shows the result in `ucm_group.2`. Groups so far: `sub_realm_counties`, `courtiers`. Actions so far: `max_development`, `max_control`, `clear_stress`.

**Localization.** English only (`localization/english/ucm_l_english.yml`). Other languages show raw keys for the new text until Phase 7.

## In-game test checklist

Load with only this mod, as in the Phase 0 baseline.

1. Start or load a single-player game. Right-click any character: **Open Cheat Menu** and **Set as Second Character** appear alongside the usual Skonester entries.
2. Open Cheat Menu on an NPC. The window shows "Target: <their name>" and the Quick Actions tab.
3. Click **Add 1,000 Gold**. The NPC's gold goes up, not yours.
4. Click through each tab. Every button opens its editor for the NPC, and closing the editor returns you to the menu.
5. Set a second character, reopen the menu, and check its name appears. Clear it from the menu.
6. On a ruler, Realm tab → **Max Development in Every Realm County**. The confirmation shows counts. Cancel changes nothing. Apply raises development and the result shows changed/skipped.
7. Run the same action again. "Will change" is 0 and Apply isn't offered.
8. Kill the second character (console or in game). The menu shows "none" afterwards.
9. Check `error.log` against the 2,717-entry baseline. Look especially for lines mentioning `ucm_`.
10. Multiplayer (if possible): host a game and have a second player join. No cheat interactions, decisions, Crozier panels or windows appear, and cheat pulses stop.
