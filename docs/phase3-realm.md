# Phase 3 — Titles, Faith & Culture, Realm tabs

Fills the main menu's **Titles, Government & Diplomacy**, **Faith & Culture** and **Realm, Holdings & Construction** tabs (spec 4.3–4.5). Static checks pass. **Not tested in game.**

## How it's built

Same approach as Phase 2, plus one new button type:

- **Interaction buttons** open the baseline's right-click interaction on the target.
- **Decision buttons** (new) open a baseline decision's detail view (`OpenGameViewData( 'decision_detail', … )`). Decisions always act on **you**, not the target, and each section that uses them says so.
- **New scripted GUIs** are in `common/scripted_guis/ucm_realm_sguis.txt`.
- Opening the menu now turns on every sub-menu toggle the baseline's interactions and decisions need: `toc_*` debug toggles, the decision sub-menus, house guard and unrestricted warfare. Closing the menu turns off whichever ones it turned on. While the menu is open, those entries also show in the right-click menu and the decision list.

## Titles, Government & Diplomacy

| Section | New | Linked |
| --- | --- | --- |
| Titles & Claims | Target claims the second character's primary title | Usurp, claim, revoke, take title / with vassals / domain / realm, claims, create titular, merge titles, destroy title, legendary titles |
| De Jure | | Organize de jure; de jure vassal reassignment (decision) |
| Vassals & Contracts | Make target independent; target becomes second's vassal | Force vassal, modify contracts, tribute contract; imprison vassals, enfeoffment, consolidate or strip titles (decisions) |
| Target's Government | 14 governments, each through the baseline's own conversion effect (it handles holdings and DLC checks) | Set authority |
| Your Succession | | Succession law, single heir, youngest heir, gender succession, dynasty of many crowns, subject government (decisions) |
| Alliances & Truces | Ally, break alliance, 10-year truce (target ↔ second) | Make ally, adjust or add truce |
| Wars | End all the target's wars with a white peace | Unrestricted and expansion wars, great holy war, crusade and jihad eras |
| AI Behavior | | The seven AI toggle decisions |

## Faith & Culture

| Section | New | Linked |
| --- | --- | --- |
| Editors | | Culture picker, faith picker, tradition editor |
| Faith | Adopt second character's faith | Change religion, convert, convert to heresy, excommunicate or lift it, appoint pope or grandmaster |
| Culture | Adopt second character's culture; unlock all innovations for the target's culture (`every_culture_innovation`) | Change culture, cultural acceptance, learn language |
| Convert Your Realm | | Six realm conversion decisions |

## Realm, Holdings & Construction

All decisions except the Phase 1 group actions and two county interactions: control, development, the six holding conversions, repairing zero-tax holdings, max buildings, building slots, great works, treasury, population, and rulers and officials.

## Not done

- Target-scoped holding and building actions (the baseline's are capital or realm decisions on you). Group versions come in Phase 6.
- The "vassal of second" button doesn't check title tiers; the engine decides whether it's valid.
- Removing a title's de jure liege, creating or destroying titles directly from the menu: covered only through the linked interactions.

## In-game test checklist

1. Open the menu on an NPC ruler → Titles. Interaction buttons open their dialogs, and decision buttons open the decision view.
2. Change the NPC's government to Tribal. Their character window shows the new government.
3. Set a second ruler: Make Allies works, and Break Alliance becomes clickable.
4. Faith & Culture → Unlock All Innovations: the target's culture window shows the innovations.
5. Close the menu. The extra right-click entries and decisions are hidden again.
6. Check `error.log` for `ucm_` lines.
