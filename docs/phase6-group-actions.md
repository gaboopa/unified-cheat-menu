# Phase 6: Group actions across modules

Extends the Phase 1 group framework (spec Section 5) from 2 groups and 3 actions to **14 groups and 10 actions**, picked in the menu. Static checks pass. **Not tested in game.**

## How it works

1. In the **Court** tab (character groups) or **Realm** tab (county groups), click a group. It's taken from the menu's target, and the button stays pressed (`var:ucm_group_pick` on the player).
2. Click an action. Character actions are only clickable with a character group picked, and county actions only with a county group.
3. Event `ucm_group.1` shows the action, the group, how many members it has and how many will change, with Apply or Cancel.
4. Applying visits every member, changes the eligible ones, counts the rest as skipped, and shows the result (`ucm_group.2`).

Character groups never include the target themselves.

| Character groups | County groups |
| --- | --- |
| Courtiers, direct vassals, all vassals (every level), councillors, knights, children, close family, spouses, house, dynasty | Realm counties (sub-realm), de jure counties of the primary title, counties of the target's culture, counties of the target's faith |

| Character actions | County actions |
| --- | --- |
| Clear stress; all skills +step; +1,000 gold; convert to target's faith; convert to target's culture; max opinion of target | Max development; max control; convert to target's faith; convert to target's culture |

"Skipped" means already done (for example, already that faith).

## Files

- `common/scripted_effects/ucm_effects.txt`: group iteration (`ucm_group_for_each_effect`) and actions (`ucm_group_apply_member_effect`). The comment at the top lists what to touch to add a group or an action.
- `common/scripted_triggers/ucm_triggers.txt`: eligibility per action; `ucm_group_pick_is_county_trigger`.
- `common/scripted_guis/ucm_group_sguis.txt`: pick, picked-state and run scripted GUIs.
- `events/ucm_group_events.txt`: confirmation and results.

The three Phase 1 one-off group buttons are replaced by the picker.

## Notes

- **Max opinion** uses the baseline's `ucm_loyal_vassal_opinion` (+999) for 100 years.
- **Culture- and faith-wide county groups** can cover a large part of the map, and the summary shows the count before you confirm. Every-character-in-the-world groups aren't offered (spec 5.1).

## In-game test checklist

1. Court → pick Courtiers → Clear Stress. The summary shows the count, and Apply reports changed and skipped.
2. Realm → pick Realm Counties → Convert to Target's Faith on a ruler of another faith. The counties change.
3. With a county group picked, the character actions are greyed out.
4. Check `error.log` for `ucm_` lines.
