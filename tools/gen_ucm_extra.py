"""Generate the native menu actions:
    common/scripted_guis/ucm_extra_sguis.txt          actions on the target and second character
    common/scripted_guis/ucm_extra_vanilla_sguis.txt  buildings, innovation eras, legends (vanilla keys)
    common/modifiers/ucm_extra_modifiers.txt
    common/scripted_effects/ucm_extra_effects.txt, common/script_values/ucm_extra_values.txt  spawner
    common/modifiers/ucm_modifier_editor_modifiers.txt, common/scripted_guis/ucm_modifier_editor_sguis.txt
    gui/ucm_modifier_editor.gui, gui/ucm_tenet_picker.gui, gui/ucm_pillar_picker.gui, gui/ucm_spawn_picker.gui
    compat/ek2/common/scripted_guis/ucm_extra_vanilla_sguis.txt  EK2 version (vanilla-key actions greyed out)
    localization/<lang>/ucm_extra_l_<lang>.yml  (other languages from tools/ucm_extra_translations.json)
build() returns the items merged into the tabs by gen_ucm_main_menu.py. Run this, then that:
    python tools/gen_ucm_extra.py [--game-dir <CK3>/game]      (or CK3_GAME_DIR; CK3_LOG_DIR for modifiers.log from script_docs)
"""
import argparse
import glob
import json
import os
import re

import ck3parse

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_GAME = r"C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game"

T = "ucm_menu_target_valid_trigger = yes"
P = "ucm_menu_pair_valid_trigger = yes"
TG = "var:ucm_target"
SEC = "global_var:ucm_crozier_cheats_other"
UP, DOWN = "ucm_step_value", "ucm_step_negative_value"
PROV = f"{TG}.capital_province"
COUNTY = f"{TG}.capital_county"
HAS_COUNTY = f"{T} exists = {COUNTY}"

DEFAULT_LOGS = os.path.expanduser(r"~\OneDrive\Documents\Paradox Interactive\Crusader Kings III\logs")

SGUIS, VANILLA_SGUIS, LOC = [], [], {}
VANILLA_LOC = {}


def vanilla_label(key, fallback):
    """A `$key$` reference when the base game names this key (translated for free), else English."""
    return f"${key}$" if key in VANILLA_LOC else fallback


def load_vanilla_loc(game):
    if VANILLA_LOC:
        return
    for f in glob.glob(os.path.join(game, "localization", "english", "**", "*.yml"), recursive=True):
        with open(f, encoding="utf-8-sig", errors="ignore") as fh:
            for m in re.finditer(r"(?m)^[ \t]*([\w.\-]+):\d*[ \t]*\"", fh.read()):
                VANILLA_LOC[m.group(1)] = True


def sg(key, label, tip, valid, effect, out=SGUIS):
    out.append(f"{key} = {{\n\tscope = character\n\tis_shown = {{ ucm_single_player_trigger = yes }}\n"
               f"\tis_valid = {{ {valid} }}\n\teffect = {{ {effect} }}\n}}\n")
    LOC[key], LOC[key + "_tt"] = label, tip
    return key


def steps(key, name, valid, effect):
    """- and + buttons; effect has {v} for the signed step."""
    return ("row", [sg(f"{key}_down", f"− {name}", f"Lower the target's {name.lower()} by the step size.", valid, effect.replace("{v}", DOWN)),
                    sg(f"{key}_up", f"+ {name}", f"Raise the target's {name.lower()} by the step size.", valid, effect.replace("{v}", UP))])


def h(key, label):
    LOC[key] = label
    return ("h", key)


def humanize(key):
    return re.sub(r"_+", " ", key).strip().capitalize()


HEAL_TRAITS = ("bubonic_plague", "smallpox", "typhus", "cancer", "consumption", "gout_ridden", "sickly", "ill", "pneumonic", "great_pox", "early_great_pox",
               "lovers_pox", "leper", "wounded_1", "wounded_2", "wounded_3", "maimed", "one_legged", "disfigured", "infirm", "incapable", "blind", "inbred")
AUTHORITY = (("crown_authority", 0, 3), ("tribal_authority", 0, 3), ("nomadic_authority", 1, 5), ("imperial_bureaucracy", 0, 3), ("celestial_bureaucracy", 0, 3))


# --- Character: stats, locks, resources -----------------------------------------------------------
# The trait editor lists only the game's traits, so these get their own toggles.
MOD_TRAITS = ["omnipotent", "challenger", "instant_build", "no_stress", "no_tyranny", "undying"]
LEARNED_TRACKS = {"pilgrim": [], "lifestyle_mystic": [], "lifestyle_blademaster": [], "lifestyle_reveler": [], "lifestyle_physician": [],
                  "lifestyle_hunter": ["hunter", "falconer"], "lifestyle_traveler": ["travel", "danger"],
                  "tourney_participant": ["foot", "bow", "horse", "wit"],
                  "gallowsbait": ["bandit", "trickster", "thief", "poacher", "marauder"]}


def character():
    items = [h("UCM_SEC_STATS", "Stats")]
    items += [steps("ucm_stat_stress", "Stress", T, f"{TG} = {{ add_stress = {{v}} }}"),
              steps("ucm_stat_dread", "Dread", T, f"{TG} = {{ add_dread = {{v}} }}"),
              steps("ucm_stat_tyranny", "Tyranny", T, f"{TG} = {{ add_tyranny = {{v}} }}"),
              steps("ucm_stat_legitimacy", "Legitimacy", T, f"{TG} = {{ add_legitimacy = {{v}} }}"),
              steps("ucm_stat_fulfillment", "Spiritual Fulfillment", f"{T} {TG} = {{ is_playable_character = yes }}",
                    f"{TG} = {{ change_spiritual_fulfillment = {{v}} }}")]
    ages = [sg(f"ucm_visual_age_{a}", f"Look {a}", f"Set the immortal target's visual age to {a}.", f"{T} {TG} = {{ is_immortal = yes }}",
               f"{TG} = {{ set_immortal_age = {a} }}") for a in (18, 30, 50, 100)]
    items.append(("row", ages))
    for lock, mod, name in (("stress", "ucm_extra_lock_stress", "stress"), ("tyranny", "ucm_extra_lock_tyranny", "tyranny"), ("dread", "ucm_extra_lock_dread", "dread"),
                            ("legitimacy", "ucm_extra_lock_legitimacy", "legitimacy"), ("fulfillment", "ucm_extra_divine_grace", "spiritual fulfillment")):
        items.append(("row", [
            sg(f"ucm_lock_{lock}", f"Lock {name}", f"Stop the target's {name} from changing naturally.",
               f"{T} {TG} = {{ NOT = {{ has_character_modifier = {mod} }} }}", f"{TG} = {{ add_character_modifier = {mod} }}"),
            sg(f"ucm_unlock_{lock}", f"Unlock {name}", f"Remove the {name} lock from the target.",
               f"{T} {TG} = {{ has_character_modifier = {mod} }}", f"{TG} = {{ remove_character_modifier = {mod} }}")]))
    items.append(h("UCM_SEC_RES_EDITOR", "Resource Editor"))
    items += [steps("ucm_res_gold", "Gold", T, f"{TG} = {{ add_gold = {{v}} }}"),
              steps("ucm_res_treasury", "Treasury or Gold", T, f"{TG} = {{ add_treasury_or_gold = {{v}} }}"),
              steps("ucm_res_prestige", "Prestige", T, f"{TG} = {{ add_prestige = {{v}} }}"),
              steps("ucm_res_piety", "Piety", T, f"{TG} = {{ add_piety = {{v}} }}"),
              steps("ucm_res_influence", "Influence", T, f"{TG} = {{ change_influence = {{v}} }}"),
              steps("ucm_res_merit", "Merit", T, f"{TG} = {{ change_merit = {{v}} }}"),
              steps("ucm_res_barter", "Barter Goods", T, f"{TG} = {{ add_barter_goods = {{v}} }}"),
              steps("ucm_res_herd", "Herd", f"{T} exists = {TG}.domicile {TG} = {{ government_has_flag = government_has_herd }}", f"{TG}.domicile = {{ change_herd = {{v}} }}")]
    items.append(h("UCM_SEC_IDENTITY_EXTRA", "Name"))
    items.append(sg_item("ucm_rename_target", "Rename…", "Choose a new first name for the target.", T, "trigger_event = ucm_extra.3"))
    items.append(h("UCM_SEC_MOD_TRAITS", "Traits From This Mod"))
    for i in range(0, len(MOD_TRAITS), 3):
        items.append(("row", [sg(f"ucm_mod_trait_{t}", f"$trait_ucm_trait_{t}$", "Add this trait to the target, or remove it if they have it.", T,
                                 f"{TG} = {{ if = {{ limit = {{ has_trait = ucm_trait_{t} }} remove_trait = ucm_trait_{t} }} else = {{ add_trait = ucm_trait_{t} }} }}")
                              for t in MOD_TRAITS[i:i + 3]]))
    def add_xp(t, tracks):
        return " ".join(f"add_trait_xp = {{ trait = {t} {f'track = {k} ' if k else ''}value = 100 }}" for k in tracks or [None])
    xp = "".join(f"if = {{ limit = {{ has_trait = {t} }} {add_xp(t, tracks)} }} " for t, tracks in LEARNED_TRACKS.items())
    items.append(sg_item("ucm_max_learned_trait_xp", "Max Learned Trait XP",
                         "Fill the experience of the target's pilgrim, lifestyle, traveler, tournament and criminal traits.", T, f"{TG} = {{ {xp}}}"))
    items.append(h("UCM_SEC_TARGET_TOOLS", "Target Tools"))
    items.append(steps("ucm_age", "Age", T, f"{TG} = {{ change_age = {{v}} }}"))
    items.append(sg_item("ucm_play_as_target", "Play as Target", "Closes this menu and switches you to the target.", f"{T} NOT = {{ {TG} = root }}",
                         f"ucm_menu_close_effect = yes set_player_character = {TG}"))
    items.append(sg_item("ucm_heal_target", "Heal", "Remove diseases, wounds and maimings from the target.", T,
                         f"{TG} = {{ " + " ".join(f"remove_trait = {x}" for x in HEAL_TRAITS) + " }"))
    items.append(("row", [sg("ucm_make_immortal", "Make Immortal", "The target stops aging and can't die of old age.", T, f"{TG} = {{ add_trait = ucm_trait_undying set_immortal_age = 25 }}"),
                          sg("ucm_make_mortal", "Make Mortal", "Remove the target's immortality.", f"{T} {TG} = {{ has_trait = ucm_trait_undying }}", f"{TG} = {{ remove_trait = ucm_trait_undying }}")]))
    return items


# --- Relationships ----------------------------------------------------------------------------------
def relationships():
    preg = f"{T} {TG} = {{ is_pregnant = yes }}"
    items = [h("UCM_SEC_BABY", "Baby's Sex"), ("row", [
        sg("ucm_baby_male", "Boy", "Make the target's pregnancy a boy.", preg, f"{TG} = {{ set_pregnancy_gender = male }}"),
        sg("ucm_baby_female", "Girl", "Make the target's pregnancy a girl.", preg, f"{TG} = {{ set_pregnancy_gender = female }}")])]
    items.append(h("UCM_SEC_REMOVE_HOOKS", "Remove Hooks"))
    items.append(("row", [
        sg("ucm_remove_hook_second_on_target", "Remove Second's Hook", "Remove the second character's hook on the target.",
           f"{P} {SEC} = {{ has_hook = root.{TG} }}", f"{SEC} = {{ remove_hook = {{ target = root.{TG} }} }}"),
        sg("ucm_remove_hook_target_on_second", "Remove Target's Hook", "Remove the target's hook on the second character.",
           f"{P} {TG} = {{ has_hook = {SEC} }}", f"{TG} = {{ remove_hook = {{ target = {SEC} }} }}")]))
    items.append(sg_item("ucm_make_house_head", "Make House Head", "Make the target the head of their house.",
                         f"{T} exists = {TG}.house NOT = {{ {TG}.house.house_head = {TG} }}", f"{TG}.house = {{ set_house_head = root.{TG} }}"))
    secrets = [("deviant", "Deviant"), ("homosexual", "Homosexual"), ("cannibal", "Cannibal"), ("witch", "Witch"), ("non_believer", "Non-believer")]
    paired = [("lover", "Lover"), ("incest", "Incest"), ("murder", "Murder")]
    items.append(h("UCM_SEC_PLANT_SECRETS", "Plant Secrets"))
    for i in range(0, len(secrets), 3):
        items.append(("row", [sg(f"ucm_plant_{k}", n, f"Give the target a {n.lower()} secret.", T,
                                 f"{TG} = {{ add_secret = {{ type = secret_{k} }} }}") for k, n in secrets[i:i + 3]]))
    items.append(("row", [sg(f"ucm_plant_{k}", f"{n} (Second)", f"Give the target a {n.lower()} secret involving the second character.", P,
                             f"{TG} = {{ add_secret = {{ type = secret_{k} target = {SEC} }} }}") for k, n in paired]))
    items.append(h("UCM_SEC_SECOND_TIES", "Ties to Second"))
    items.append(("row", [sg("ucm_concubine_of_second", "Concubine of Second", "Make the target a concubine of the second character.", f"{P} {TG} = {{ is_concubine = no }}", f"{SEC} = {{ make_concubine = root.{TG} }}"),
                          sg("ucm_heir_of_second", "Heir of Second", "Make the target the second character's designated heir.", P, f"{SEC} = {{ set_designated_heir = root.{TG} }}")]))
    items.append(("row", [sg("ucm_court_of_second", "Court of Second", "Move the target to the second character's court.", P, f"{SEC} = {{ add_courtier = root.{TG} }}"),
                          sg("ucm_make_lowborn", "Make Lowborn", "Remove the target's house.", T, f"{TG} = {{ set_to_lowborn = yes }}")]))
    items.append(("row", [sg("ucm_imprison_by_second", "Second Imprisons", "The second character imprisons the target.", P, f"{SEC} = {{ imprison = {{ target = root.{TG} type = dungeon }} }}"),
                          sg("ucm_release_target", "Release", "Release the target from prison.", f"{T} {TG} = {{ is_imprisoned = yes }}", f"{TG} = {{ release_from_prison = yes }}")]))
    return items


def sg_item(*a):
    return ("sg", sg(*a))


# --- Titles and diplomacy --------------------------------------------------------------------------
def titles():
    def list_claims(limit):
        return (f"{TG} = {{ every_claim = {{ {limit} add_to_temporary_list = ucm_claims }} "
                f"every_in_list = {{ list = ucm_claims save_temporary_scope_as = ucm_claim root.{TG} = {{ remove_claim = scope:ucm_claim }} }} }}")
    primary = f"{T} {TG} = {{ is_landed = yes }}"
    other = f"{primary} NOT = {{ {TG} = root }}"
    change = "create_title_and_vassal_change = {{ type = conquest save_scope_as = change }} {} resolve_title_and_vassal_change = scope:change"
    grab = "change_title_holder_include_vassals = { holder = root change = scope:change }"
    items = [h("UCM_SEC_TAKEOVER", "Take Titles (for you)"),
             ("ia", "ucm_take_title"), ("ia", "ucm_claim_title"),
             ("row", [sg("ucm_take_domain", "Take Domain", "You take every title the target holds, with their vassals.", other, change.format(f"{TG} = {{ every_held_title = {{ {grab} }} }}")),
                      sg("ucm_take_realm", "Take Realm", "You take every county-or-higher title in the target's realm, with their vassals.", other,
                         change.format(f"{TG} = {{ every_sub_realm_title = {{ limit = {{ tier > tier_barony }} {grab} }} }}")),
                      sg("ucm_claim_creatable", "Claim Creatable", "You get a pressed claim on every title you could create.", "always = yes",
                         "every_alert_creatable_title = { root = { add_pressed_claim = prev } }")]),
             ("ia", "ucm_modify_vassal_contract"),
             h("UCM_SEC_MERGE", "Merge Titles"), ("ia", "ucm_merge_title"),
             sg_item("ucm_merge_title_clear", "Forget Marked Title", "Clear the title marked for merging.", "has_variable = ucm_merge_title", "remove_variable = ucm_merge_title"),
             sg_item("ucm_organize_dejure", "Organize De Jure", "Make every lower-tier title held by the target and their direct vassals de jure under the target's primary title.", primary,
                     f"{TG} = {{ every_held_title = {{ limit = {{ tier > tier_barony this.tier < root.{TG}.primary_title.tier }} set_de_jure_liege_title = root.{TG}.primary_title }} "
                     f"every_vassal = {{ every_held_title = {{ limit = {{ tier > tier_barony this.tier < root.{TG}.primary_title.tier }} set_de_jure_liege_title = root.{TG}.primary_title }} }} }}"),
             sg_item("ucm_sort_vassals_dejure", "Sort My Vassals De Jure", "Put each of your vassals under the nearest de jure liege in your realm. No titles change hands.",
                     "ucm_has_de_jure_transferable_direct_vassals_trigger = yes", "ucm_one_click_transfer_direct_vassals_to_de_jure_liege_effect = yes"),
             sg_item("ucm_max_authority", "Max Realm Authority", "Raise the target's crown authority or equivalent law to the top level.", f"{T} {TG} = {{ is_independent_ruler = yes }}",
                     f"{TG} = {{ " + " ".join(f"if = {{ limit = {{ OR = {{ " + " ".join(f"has_realm_law = {law}_{i}" for i in range(low, top)) + f" }} }} add_realm_law = {law}_{top} }}" for law, low, top in AUTHORITY) + " }"),
             h("UCM_SEC_CLAIM_REMOVE", "Remove Claims"), ("row", [
        sg("ucm_remove_all_claims", "All Claims", "Remove every explicit claim the target has. Inherited claims from living relatives stay.", T, list_claims("")),
        sg("ucm_remove_claims_on_second", "Claims on Second", "Remove the target's explicit claims on the second character's titles.", P,
           list_claims(f"limit = {{ holder ?= {SEC} }}"))])]
    items.append(h("UCM_SEC_DEJURE_BUILD", "De Jure Tools"))
    liege = f"{TG}.primary_title.de_jure_liege"
    items.append(sg_item("ucm_create_dejure_liege", "Take De Jure Liege Title", "Give the target the unheld de jure liege title of their primary title.",
                         f"{primary} exists = {liege} NOT = {{ exists = {liege}.holder }}", f"{TG} = {{ get_title = {liege} }}"))
    items.append(sg_item("ucm_create_dejure_vassals", "Take Unheld De Jure Vassals", "Give the target every unheld county-or-higher de jure vassal title of their primary title.", primary,
                         f"{TG}.primary_title = {{ every_direct_de_jure_vassal_title = {{ limit = {{ tier >= tier_county NOT = {{ exists = holder }} }} root.{TG} = {{ get_title = prev }} }} }}"))
    items.append(sg_item("ucm_dejure_under_second", "De Jure Under Second", "Make the second character's primary title the de jure liege of the target's primary title.",
                         f"{P} {TG} = {{ is_landed = yes }} {SEC} = {{ is_landed = yes highest_held_title_tier > root.{TG}.highest_held_title_tier }}",
                         f"{TG}.primary_title = {{ set_de_jure_liege_title = {SEC}.primary_title }}"))
    items.append(sg_item("ucm_destroy_primary_confirm", "Destroy Primary Title…", "Asks first, then destroys the target's primary title.", primary,
                         "trigger_event = ucm_extra.2"))
    gov = [("ecclesiastical", "Ecclesiastical"), ("wanua", "Wanua")]
    items.append(("row", [sg(f"ucm_gov_{k}", n, f"Change the target's government to {n}.", primary,
                             f"{TG} = {{ change_government = {k}_government }}") for k, n in gov]))
    items.append(h("UCM_SEC_PACT", "Permanent Truce"))
    items.append(sg_item("ucm_truce_second_permanent", "Permanent Truce", "A 9,999-year truce between the target and the second character.",
                         f"{P} {TG} = {{ is_ruler = yes }} {SEC} = {{ is_ruler = yes }}",
                         f"{TG} = {{ add_truce_both_ways = {{ character = {SEC} years = 9999 override = yes name = ucm_truce_name }} }}"))

    def wars(limit, win):
        side = "attacker" if win else "defender"
        other = "defender" if win else "attacker"
        return (f"{TG} = {{ every_character_war = {{ limit = {{ {limit} }} if = {{ limit = {{ primary_attacker = root.{TG} }} end_war = {side} }} "
                f"else_if = {{ limit = {{ primary_defender = root.{TG} }} end_war = {other} }} }} }}")
    atwar = f"{T} {TG} = {{ is_at_war = yes }}"
    leader = f"OR = {{ primary_attacker = root.{TG} primary_defender = root.{TG} }}"
    versus = f"{leader} is_participant = {SEC}"
    items.append(h("UCM_SEC_WAR_OUTCOMES", "War Outcomes"))
    items.append(("row", [sg("ucm_wars_win_all", "Win All Wars", "End every war the target leads as a victory.", atwar, wars(leader, True)),
                          sg("ucm_wars_lose_all", "Lose All Wars", "End every war the target leads as a defeat.", atwar, wars(leader, False))]))
    items.append(("row", [sg("ucm_wars_win_second", "Win vs Second", "Win the target's wars that involve the second character.", f"{atwar} {P}", wars(versus, True)),
                          sg("ucm_wars_lose_second", "Lose vs Second", "Lose the target's wars that involve the second character.", f"{atwar} {P}", wars(versus, False)),
                          sg("ucm_wars_peace_second", "White Peace vs Second", "White peace in the target's wars that involve the second character.", f"{atwar} {P}",
                             f"{TG} = {{ every_character_war = {{ limit = {{ {versus} }} end_war = white_peace }} }}")]))
    items.append(sg_item("ucm_holy_war_second", "Great Holy War on Second", "The target's faith calls a great holy war against the second character.", f"{P} {SEC} = {{ is_landed = yes }}",
                         f"{TG}.faith = {{ start_great_holy_war = {{ target_character = {SEC} target_title = {SEC}.primary_title delay = 110 }} }}"))
    declare = f"{P} {TG} = {{ is_ruler = yes }} {SEC} = {{ is_landed = yes }}"
    items.append(("row", [sg(f"ucm_declare_{t}", f"Declare: {n}", f"The target declares a {n.lower()} war on the second character.", declare,
                             f"{TG} = {{ start_war = {{ cb = ucm_war_{t} target = {SEC} }} }}")
                          for t, n in (("county", "County"), ("duchy", "Duchy"), ("kingdom", "Kingdom"), ("empire", "Empire"))]))
    return items


# --- Faith and culture ----------------------------------------------------------------------------
def faith_culture():
    tenets = "any_personal_tenet = { always = yes }"
    items = [h("UCM_SEC_PERSONAL_TENETS", "Personal Tenets"),
             sg_item("ucm_copy_personal_tenets", "Copy Second's Personal Tenets", "Give the target each of the second character's personal tenets. The game drops the worst one when out of slots.",
                     f"{P} {TG} = {{ is_playable_character = yes }}",
                     f"{SEC} = {{ every_personal_tenet = {{ save_temporary_scope_as = ucm_tenet root.{TG} = {{ force_set_personal_tenet = scope:ucm_tenet }} }} }}"),
             ("row", [sg("ucm_remove_worst_tenet", "Remove Worst Tenet", "Remove the target's worst personal tenet.", f"{T} {TG} = {{ {tenets} }}", f"{TG} = {{ remove_worst_personal_tenet = yes }}"),
                      sg("ucm_clear_personal_tenets", "Clear Tenets", "Remove all of the target's personal tenets.", f"{T} {TG} = {{ {tenets} }}",
                         f"{TG} = {{ while = {{ limit = {{ {tenets} }} remove_worst_personal_tenet = yes }} }}")]),
             h("UCM_SEC_RITES", "Rites & Clergy"),
             ("row", [sg("ucm_learn_second_rite", "Learn Second's Rite", "The target learns the second character's rite without converting.", f"{P} {TG} = {{ is_playable_character = yes }}",
                         f"{TG} = {{ add_known_rite = {SEC}.rite }}"),
                      sg("ucm_join_second_rite", "Join Second's Rite", "The target converts to the second character's rite.", P, f"{TG} = {{ set_character_rite = {SEC}.rite }}")]),
             sg_item("ucm_make_cardinal", "Make Cardinal", "Appoint the target through the game's cardinalate rules.", f"{T} {TG} = {{ pam_can_receive_cardinalate_trigger = yes exists = capital_county }}",
                     f"{TG} = {{ grant_cardinal_title_effect = {{ CARDINAL_COUNTY = capital_county }} }}"),
             h("UCM_SEC_CULTURE_TOOLS", "Culture Tools"),
             sg_item("ucm_create_divergent_culture", "Create Divergent Culture", "The target founds a divergent culture keeping the current pillars and traditions. Use the culture editors to change it.",
                     f"{T} exists = {TG}.culture", f"{TG} = {{ create_divergent_culture = yes }}"),
             sg_item("ucm_learn_second_language", "Learn Second's Language", "The target learns the language of the second character's culture.", P, f"{TG} = {{ learn_language_of_culture = {SEC}.culture }}"),
             steps("ucm_acceptance_second", "Cultural Acceptance with Second", f"{P} NOT = {{ {TG}.culture = {SEC}.culture }}",
                   f"{TG}.culture = {{ change_cultural_acceptance = {{ target = {SEC}.culture value = {{v}} desc = ucm_acceptance_reason }} }}"),
             sg_item("ucm_culture_remove_all_innovations", "Remove All Innovations", "Remove every innovation from the target's culture. This changes the whole culture.", f"{T} exists = {TG}.culture",
                     f"{TG}.culture = {{ save_temporary_scope_as = ucm_culture every_culture_innovation = {{ limit = {{ scope:ucm_culture = {{ has_innovation = prev }} }} scope:ucm_culture = {{ remove_innovation = prev }} }} }}")]
    LOC["ucm_acceptance_reason"] = "Cheat menu"
    LOC.update(ucm_take_title="Take Title", ucm_take_title_desc="Pick one of this character's titles to take.", ucm_take_title_with_vassals="Include its vassals",
               ucm_claim_title="Claim Title", ucm_claim_title_desc="Pick one of this character's titles to get a pressed claim on.",
               ucm_merge_title="Merge Title", ucm_merge_title_desc="Pick a title to mark it, then pick the title to merge it into: the same tier, or one tier higher.",
               ucm_merge_title_invalid_pair="The marked title can only merge into a different title of the same tier (duchy or higher), or into the tier directly above, and not its current de jure liege.",
               ucm_modify_vassal_contract="Modify Contract", ucm_modify_vassal_contract_desc="Change this vassal's contract at no cost.")
    return items


# --- Realm: county, holdings ------------------------------------------------------------------------
MODS = [("opinion", "Popular Opinion +100", "county_opinion_add = 100"), ("taxes", "Taxes +50%", "tax_mult = 0.5"), ("levies", "Levies +50%", "levy_size = 0.5"),
        ("supply", "Supply Limit +100%", "supply_limit_mult = 1"), ("plague", "Plague Resistance +100", "epidemic_resistance = 100")]


def knights():
    return [h("UCM_SEC_GLORY", "Glory"), steps("ucm_glory", "Glory", f"{T} {TG} = {{ is_acclaimed = yes }}", f"{TG} = {{ accolade = {{ add_glory = {{v}} }} }}")]


def realm():
    items = [h("UCM_SEC_CAPITAL_COUNTY", "Target's Capital County"),
             steps("ucm_county_control", "Control", HAS_COUNTY, f"{COUNTY} = {{ change_county_control = {{v}} }}"),
             steps("ucm_county_development", "Development", HAS_COUNTY, f"{COUNTY} = {{ change_development_level = {{v}} }}")]
    presets = []
    for n in (0, 50, 100):
        presets.append(sg(f"ucm_county_control_{n}", f"Control {n}", f"Set the capital county's control to {n}.", HAS_COUNTY,
                          f"{COUNTY} = {{ change_county_control = {{ value = {n} subtract = county_control }} }}"))
    items.append(("row", presets))
    presets = []
    for n in (0, 50, 100):
        presets.append(sg(f"ucm_county_dev_{n}", f"Develop {n}", f"Set the capital county's development to {n}.", HAS_COUNTY,
                          f"{COUNTY} = {{ change_development_level = {{ value = {n} subtract = development_level }} }}"))
    items.append(("row", presets))
    for k, name, _ in MODS:
        mod = f"ucm_extra_county_{k}"
        items.append(("row", [
            sg(f"ucm_add_{mod}", f"Add {name}", f"Add a lasting {name} modifier to the target's capital county.",
               f"{HAS_COUNTY} NOT = {{ {COUNTY} = {{ has_county_modifier = {mod} }} }}", f"{COUNTY} = {{ add_county_modifier = {mod} }}"),
            sg(f"ucm_rem_{mod}", f"Remove {name}", f"Remove this modifier from the target's capital county.",
               f"{HAS_COUNTY} {COUNTY} = {{ has_county_modifier = {mod} }}", f"{COUNTY} = {{ remove_county_modifier = {mod} }}")]))
    other_county = f"tier = tier_county NOT = {{ this = root.{COUNTY} }}"
    other_barony = f"tier = tier_barony title_province = {{ has_holding = yes NOT = {{ this = root.{PROV} }} }}"
    items.append(h("UCM_SEC_CAPITALS", "Capitals & Holdings"))
    items.append(sg_item("ucm_move_realm_capital", "Move Realm Capital", "Move the target's realm capital to another county they personally hold, chosen at random.",
                         f"{T} {TG} = {{ any_held_title = {{ {other_county} }} }}",
                         f"{TG} = {{ random_held_title = {{ limit = {{ {other_county} }} save_temporary_scope_as = ucm_new_capital }} set_realm_capital = scope:ucm_new_capital }}"))
    items.append(sg_item("ucm_move_county_capital", "Move County Capital", "Make another barony with a holding the capital of the target's capital county, chosen at random.",
                         f"{HAS_COUNTY} {COUNTY} = {{ any_direct_de_jure_vassal_title = {{ {other_barony} }} }}",
                         f"{COUNTY} = {{ random_direct_de_jure_vassal_title = {{ limit = {{ {other_barony} }} set_capital_barony = yes }} }}"))
    items.append(sg_item("ucm_remove_holdings_confirm", "Remove Other Holdings…", "Asks first, then removes every holding in the capital county except the county capital.", HAS_COUNTY,
                         "trigger_event = ucm_extra.1"))
    items.append(("row", [
        sg("ucm_add_building_slot", "Add Building Slot", "Add a lasting extra building slot to the target's capital holding.",
           f"{T} {PROV} = {{ NOT = {{ has_province_modifier = ucm_extra_building_slot }} }}", f"{PROV} = {{ add_province_modifier = ucm_extra_building_slot }}"),
        sg("ucm_remove_building_slot", "Remove Slot", "Remove the extra building slot.",
           f"{T} {PROV} = {{ has_province_modifier = ucm_extra_building_slot }}", f"{PROV} = {{ remove_province_modifier = ucm_extra_building_slot }}"),
        sg("ucm_ai_build", "AI Builds One", "Add one building to the target's capital holding using the AI's choice.", T, f"{PROV} = {{ generate_building = yes }}")]))
    return items


# --- Generated from vanilla data ---------------------------------------------------------------------
BUILDING_FILES = ("00_admin_buildings", "00_castle_buildings", "00_city_buildings", "00_common_buildings", "00_duchy_capital_buildings", "00_nomad_buildings",
                  "00_standard_economy_buildings", "00_standard_fortification_buildings", "00_standard_military_buildings", "00_temple_buildings", "00_tribal_buildings",
                  "temple_citadel_buildings")


def buildings(game):
    items = [h("UCM_SEC_BUILD_CATALOG", "Build on Target's Capital Holding")]
    for stem in BUILDING_FILES:
        objs = {k: re.search(r"next_building\s*=\s*(\w+)", b) for k, b in ck3parse.top_level_objects(os.path.join(game, "common", "buildings", stem + ".txt"))}
        nexts = {m.group(1) for m in objs.values() if m}
        for root in sorted(k for k in objs if k not in nexts):
            chain, cur = [root], objs[root]
            while cur and cur.group(1) in objs:
                chain.append(cur.group(1))
                cur = objs[cur.group(1)]
            name = vanilla_label(f"building_type_{root}", humanize(re.sub(r"_?0*1$", "", root)))
            up = "".join(f"{'if' if i == 0 else 'else_if'} = {{ limit = {{ NOT = {{ has_building_or_higher = {b} }} }} add_building = {b} }} " for i, b in enumerate(chain))
            down = "".join(f"{'if' if i == 0 else 'else_if'} = {{ limit = {{ has_building = {b} }} remove_building = {b} }} " for i, b in enumerate(reversed(chain)))
            items.append(("row", [
                sg(f"ucm_bld_{root}_down", f"− {name}", f"Remove the highest level of {name} from the target's capital holding.", T, f"{PROV} = {{ {down}}}", VANILLA_SGUIS),
                sg(f"ucm_bld_{root}_up", f"+ {name}", f"Build the next level of {name} ({len(chain)} levels) on the target's capital holding.", T, f"{PROV} = {{ {up}}}", VANILLA_SGUIS)]))
    return items


ERAS = (("tribal", "Tribal"), ("early_medieval", "Early Medieval"), ("high_medieval", "High Medieval"), ("late_medieval", "Late Medieval"))


def innovation_eras(game):
    by_era = {e: [] for e, _ in ERAS}
    for f in ck3parse.effective_files(os.path.join("common", "culture", "innovations"), game):
        for k, b in ck3parse.top_level_objects(f):
            m = re.search(r"culture_era\s*=\s*culture_era_(\w+)", b)
            if m and m.group(1) in by_era:
                by_era[m.group(1)].append(k)
    items = [h("UCM_SEC_INNOVATION_ERAS", "Innovations by Era")]
    valid = f"{T} exists = {TG}.culture"
    for e, n in ERAS:
        items.append(("row", [
            sg(f"ucm_era_add_{e}", f"Add {n}", f"Add every {n} innovation to the target's culture.", valid,
               f"{TG}.culture = {{ " + " ".join(f"add_innovation = {k}" for k in by_era[e]) + " }", VANILLA_SGUIS),
            sg(f"ucm_era_remove_{e}", f"Remove {n}", f"Remove every {n} innovation from the target's culture.", valid,
               f"{TG}.culture = {{ " + " ".join(f"remove_innovation = {k}" for k in by_era[e]) + " }", VANILLA_SGUIS)]))
    return items


def activities_legends():
    act = f"{T} exists = {TG}.involved_activity"
    items = [h("UCM_SEC_ACTIVITY_CONTROLS", "Current Activity"),
             ("row", [sg("ucm_activity_skip", "Skip Phase", "Skip the current phase of the target's activity.", act, f"{TG}.involved_activity = {{ skip_activity_phase = yes }}"),
                      sg("ucm_activity_finish", "Finish", "Skip through the remaining phases of the target's activity (up to 8).", act,
                         f"{TG}.involved_activity = {{ {' '.join(['skip_activity_phase = yes'] * 8)} }}"),
                      sg("ucm_activity_cancel", "Cancel", "Cancel the target's activity outright.", act, f"{TG}.involved_activity = {{ invalidate_activity = yes }}")]),
             h("UCM_SEC_ESTATE_PRESETS", "Estate Presets")]
    setup = f"set_global_variable = {{ name = ucm_cheat_menu_recipient value = {TG} }} save_scope_as = actor"
    estate = f"{T} {TG} = {{ is_alive = yes domicile ?= {{ OR = {{ is_domicile_type = estate is_domicile_type = east_asian_estate is_domicile_type = japanese_manor }} }} }}"
    items.append(("row", [sg(f"ucm_estate_{p}", n, f"Apply the {n.lower()} estate preset to the target's domicile.", estate,
                             f"{TG} = {{ ucm_domicile_preset_{p}_effect = yes }}") for p, n in (("economy", "Economic"), ("military", "Military"), ("balanced", "Balanced"))]))
    items.append(h("UCM_SEC_LEGEND_MAKER", "Create a Legend for the Target"))
    items.append(sg_item("ucm_legend_clear", "Clear Target's Legends", "Remove the legends the target owns.", T, f"{setup} ucm_legend_master_clear_owned_legends_effect = yes"))
    with open(os.path.join(MOD, "common", "scripted_effects", "ucm_legend_master_effects.txt"), encoding="utf-8-sig") as fh:
        keys = sorted(set(re.findall(r"(?m)^ucm_legend_master_add_(\w+)_effect\s*=", fh.read())))
    row = []
    for k in keys:
        row.append(sg(f"ucm_legend_{k}", humanize(k), f"Give the target the {humanize(k).lower()} legend.", T,
                      f"{TG} = {{ save_scope_as = ucm_cheat_menu_target }} ucm_legend_master_add_{k}_effect = yes", VANILLA_SGUIS))
        if len(row) == 2:
            items.append(("row", row))
            row = []
    if row:
        items.append(("row", row))
    return items


# --- Spawner -----------------------------------------------------------------------------------------
SKILL_ROLES = (("commander", "Commander", "martial"), ("knight", "Knight", "prowess"))
COUNCIL = (("chancellor", "Chancellor", "diplomacy"), ("marshal", "Marshal", "martial"), ("steward", "Steward", "stewardship"),
           ("spymaster", "Spymaster", "intrigue"), ("court_chaplain", "Chaplain", "learning"))
SKILLS = ("diplomacy", "martial", "stewardship", "intrigue", "learning", "prowess")
# A skill value of 0 leaves the rolled skill alone; anything else sets it exactly.
SET_SKILLS = "\n".join(f"\t\tif = {{ limit = {{ root = {{ ucm_spawn_{k}_value > 0 }} }} add_{k}_skill = {{ value = root.var:ucm_spawn_{k} subtract = {k} }} }}" for k in SKILLS)
SPAWN_EFFECTS = """ucm_spawn_create_effect = {
	if = {
		limit = { exists = root.var:ucm_spawn_culture }
		root.var:ucm_spawn_culture = { save_temporary_scope_as = ucm_spawn_culture }
	}
	else = {
		root.var:ucm_target.culture = { save_temporary_scope_as = ucm_spawn_culture }
	}
	if = {
		limit = { exists = root.var:ucm_spawn_faith }
		root.var:ucm_spawn_faith = { save_temporary_scope_as = ucm_spawn_faith }
	}
	else = {
		root.var:ucm_target.faith = { save_temporary_scope_as = ucm_spawn_faith }
	}
	if = {
		limit = { has_character_flag = ucm_spawn_no_traits }
		create_character = { age = ucm_spawn_age_value gender_female_chance = ucm_spawn_female_chance_value random_traits = no culture = scope:ucm_spawn_culture faith = scope:ucm_spawn_faith dynasty = $DYNASTY$ employer = root.var:ucm_target save_temporary_scope_as = ucm_new }
	}
	else = {
		create_character = { age = ucm_spawn_age_value gender_female_chance = ucm_spawn_female_chance_value culture = scope:ucm_spawn_culture faith = scope:ucm_spawn_faith dynasty = $DYNASTY$ employer = root.var:ucm_target save_temporary_scope_as = ucm_new }
	}
	scope:ucm_new = {
		if = {
			limit = { root = { has_character_flag = ucm_spawn_stats } }
			add_diplomacy_skill = 100 add_martial_skill = 100 add_stewardship_skill = 100 add_intrigue_skill = 100 add_learning_skill = 100 add_prowess_skill = 100
			force_character_skill_recalculation = yes
		}
		if = {
			limit = { root = { has_character_flag = ucm_spawn_good } }
			add_trait = intellect_good_3 add_trait = beauty_good_3 add_trait = physique_good_3
		}
		if = {
			limit = { root = { has_character_flag = ucm_spawn_immortal } }
			add_trait = ucm_trait_undying
			set_immortal_age = 25
		}
		force_character_skill_recalculation = yes
""" + SET_SKILLS + """
		force_character_skill_recalculation = yes
	}
}
"""
SPAWN_VALUES = """ucm_spawn_age_value = {
	value = 20
	if = { limit = { has_variable = ucm_spawn_age } value = var:ucm_spawn_age }
}

ucm_spawn_count_value = {
	value = 1
	if = { limit = { has_variable = ucm_spawn_count } value = var:ucm_spawn_count }
}

ucm_spawn_female_chance_value = {
	value = 0
	if = { limit = { has_character_flag = ucm_spawn_female } value = 100 }
}
""" + "".join(f"""
ucm_spawn_{k}_value = {{
\tvalue = 0
\tif = {{ limit = {{ has_variable = ucm_spawn_{k} }} value = var:ucm_spawn_{k} }}
}}
""" for k in SKILLS)


def spawner(game):
    me = "GetPlayer.MakeScope.ScriptValue( '%s' )|0"
    LOC.update(UCM_SPAWN_AGE="Age", UCM_SPAWN_COUNT="Count")
    items = [h("UCM_SEC_SPAWN_OPTIONS", "New Characters: Options"),
             ("value", "UCM_SPAWN_AGE", me % "ucm_spawn_age_value", sg_pair("ucm_spawn_age", "age", "ucm_spawn_age_value", "ucm_step_value", 0, 100)),
             ("value", "UCM_SPAWN_COUNT", me % "ucm_spawn_count_value", sg_pair("ucm_spawn_count", "count", "ucm_spawn_count_value", "1", 1, 20))]
    opts = []
    for k, n, tip in (("female", "Female", "New characters are women."), ("no_traits", "No Traits", "New characters start without random traits."),
                      ("stats", "Max Skills", "New characters get +100 in every skill."), ("good", "Best Genes", "New characters get the best intellect, beauty and physique traits."),
                      ("immortal", "Immortal", "New characters are immortal.")):
        opts.append((sg(f"ucm_spawn_opt_{k}", n, tip, "always = yes",
                        f"if = {{ limit = {{ has_character_flag = ucm_spawn_{k} }} remove_character_flag = ucm_spawn_{k} }} else = {{ add_character_flag = ucm_spawn_{k} }}"), f"ucm_spawn_{k}"))
    items += [("togglerow", opts[:3]), ("togglerow", opts[3:]), ("vs", "ucm_spawn_picker", "ucm_open_spawn_picker"), h("UCM_SPAWN_SKILL_NOTE", "Skills (0 keeps the rolled skill)")]
    for k in SKILLS:
        LOC[f"UCM_SPAWN_{k.upper()}"] = k.capitalize()
        items.append(("value", f"UCM_SPAWN_{k.upper()}", me % f"ucm_spawn_{k}_value", sg_pair(f"ucm_spawn_{k}", k, f"ucm_spawn_{k}_value", "ucm_step_value", 0, 100)))
    spawn_picker_sguis()
    many = lambda dyn, after: f"while = {{ count = ucm_spawn_count_value ucm_spawn_create_effect = {{ DYNASTY = {dyn} }} {after} }}"
    items.append(h("UCM_SEC_SPAWN_FAMILY", "New Family Members"))
    younger = f"{T} ucm_spawn_age_value < {TG}.age"
    older = f"{T} ucm_spawn_age_value > {TG}.age"
    parent = f"if = {{ limit = {{ root.{TG} = {{ is_female = yes }} }} set_mother = root.{TG} }} else = {{ set_father = root.{TG} }}"
    spouse = (f"if = {{ limit = {{ exists = root.{TG}.primary_spouse root.{TG} = {{ is_female = yes }} }} set_father = root.{TG}.primary_spouse }} "
              f"else_if = {{ limit = {{ exists = root.{TG}.primary_spouse }} set_mother = root.{TG}.primary_spouse }}")
    house = f"if = {{ limit = {{ exists = root.{TG}.house }} set_house = root.{TG}.house }}"
    items.append(("row", [
        sg("ucm_spawn_child", "Child", "Spawn children of the target (and their spouse). Must be younger than the target.", younger,
           many("none", f"scope:ucm_new = {{ {parent} {spouse} {house} }}")),
        sg("ucm_spawn_sibling", "Sibling", "Spawn siblings of the target, sharing the target's parents.", f"{T} OR = {{ exists = {TG}.father exists = {TG}.mother }}",
           many("none", f"scope:ucm_new = {{ if = {{ limit = {{ exists = root.{TG}.father }} set_father = root.{TG}.father }} if = {{ limit = {{ exists = root.{TG}.mother }} set_mother = root.{TG}.mother }} {house} }}")),
    ]))
    items.append(("row", [
        sg("ucm_spawn_parent", "Parent", "Spawn the target's missing mother (Female on) or father. Must be older than the target.",
           f"{older} OR = {{ AND = {{ has_character_flag = ucm_spawn_female NOT = {{ exists = {TG}.mother }} }} AND = {{ NOT = {{ has_character_flag = ucm_spawn_female }} NOT = {{ exists = {TG}.father }} }} }}",
           f"ucm_spawn_create_effect = {{ DYNASTY = generate }} if = {{ limit = {{ has_character_flag = ucm_spawn_female }} {TG} = {{ set_mother = scope:ucm_new }} }} else = {{ {TG} = {{ set_father = scope:ucm_new }} }}"),
        sg("ucm_spawn_spouse", "Spouse", "Spawn a spouse and marry them to the target. Age must be 16 or more.", f"{T} {TG} = {{ is_adult = yes }} ucm_spawn_age_value >= 16",
           f"ucm_spawn_create_effect = {{ DYNASTY = generate }} {TG} = {{ marry = scope:ucm_new }}"),
    ]))
    items.append(h("UCM_SEC_SPAWN_COURT", "New Courtiers"))
    items.append(("row", [
        sg("ucm_spawn_courtier", "Courtier", "Spawn courtiers with their own house at the target's court.", T, many("generate", "")),
        sg("ucm_spawn_lowborn", "Lowborn", "Spawn lowborn courtiers at the target's court.", T, many("none", "")),
    ] + [sg(f"ucm_spawn_{k}", n, f"Spawn {n.lower()}s with +25 {skill} at the target's court.", T, many("generate", f"scope:ucm_new = {{ add_{skill}_skill = 25 }}")) for k, n, skill in SKILL_ROLES]))
    items.append(h("UCM_SEC_SPAWN_COUNCIL", "New Councillors (replaces the sitting one)"))
    adult = f"{T} {TG} = {{ is_ruler = yes }} ucm_spawn_age_value >= 16"
    for i in range(0, len(COUNCIL), 3):
        items.append(("row", [sg(f"ucm_spawn_council_{k}", n, f"Spawn a {n.lower()} with +25 {skill} and seat them on the target's council.", adult,
                                 f"ucm_spawn_create_effect = {{ DYNASTY = generate }} scope:ucm_new = {{ add_{skill}_skill = 25 }} {TG} = {{ assign_councillor_type = {{ type = councillor_{k} target = scope:ucm_new remove_existing_councillor = yes }} }}")
                              for k, n, skill in COUNCIL[i:i + 3]]))
    items.append(h("UCM_SEC_SPAWN_POSITIONS", "New Court Position Holders"))
    row = []
    for f in sorted(glob.glob(os.path.join(game, "common", "court_positions", "types", "*.txt"))):
        for k, _ in ck3parse.top_level_objects(f):
            n = vanilla_label(k, humanize(k.replace("_court_position", "")))
            row.append(sg(f"ucm_spawn_pos_{k}", n, "Spawn a new character and appoint them to this position at the target's court.",
                          f"{T} {TG} = {{ can_employ_court_position_type = {k} }}",
                          f"ucm_spawn_create_effect = {{ DYNASTY = generate }} {TG} = {{ appoint_court_position = {{ recipient = scope:ucm_new court_position = {k} }} }}", VANILLA_SGUIS))
            if len(row) == 2:
                items.append(("row", row))
                row = []
    if row:
        items.append(("row", row))
    return items


def spawn_picker_sguis():
    LOC.update(ucm_open_spawn_picker="Culture & Faith of New Characters", UCM_SPAWN_PICKER="Culture & Faith", UCM_SPAWN_TARGETS="Target's",
               UCM_SPAWN_PICKER_NOTE="Click a culture or faith to give it to every character you spawn from now on. Until you pick one, they use the target's.",
               UCM_SPAWN_CULTURE_LABEL="Culture:", UCM_SPAWN_FAITH_LABEL="Faith:")
    for kind, name in (("culture", "culture"), ("faith", "faith")):
        sg(f"ucm_spawn_{kind}_clear", "Use Target's", f"New characters use the target's {name} again.", f"has_variable = ucm_spawn_{kind}", f"remove_variable = ucm_spawn_{kind}")
        SGUIS.append(f"ucm_spawn_pick_{kind} = {{\n\tscope = character\n\tsaved_scopes = {{ selected_{kind} }}\n\tis_shown = {{ ucm_single_player_trigger = yes }}\n"
                     f"\tis_valid = {{ exists = scope:selected_{kind} }}\n\teffect = {{ set_variable = {{ name = ucm_spawn_{kind} value = scope:selected_{kind} }} }}\n}}\n")
    SGUIS.append("ucm_spawn_lists_load = {\n\tscope = character\n\tis_shown = { ucm_single_player_trigger = yes }\n\tis_valid = { always = yes }\n"
                 "\teffect = { ucm_picker_fill_heritages_effect = yes ucm_picker_fill_religions_effect = yes }\n}\n")


def sg_pair(key, name, value, step, lo, hi):
    sg(f"{key}_up", "+", f"Raise the spawn {name}.", f"{value} < {hi}", f"set_variable = {{ name = {key} value = {{ value = {value} add = {step} max = {hi} }} }}")
    sg(f"{key}_down", "−", f"Lower the spawn {name}.", f"{value} > {lo}", f"set_variable = {{ name = {key} value = {{ value = {value} subtract = {step} min = {lo} }} }}")
    return key


# --- Group additions (their branches live in ucm_effects.txt and ucm_triggers.txt) ---------------------
EX_GROUPS = (("lovers", "Lovers", "the target's lovers"), ("friends", "Friends", "the target's friends"), ("rivals", "Rivals", "the target's rivals"),
             ("extended_family", "Extended Family", "the target's extended family"), ("house_bloc", "House Bloc", "the members of the target's house bloc"),
             ("faith_members", "Faith", "everyone of the target's faith, worldwide"), ("culture_members", "Culture", "everyone of the target's culture, worldwide"))


def group_loc():
    for k, n, d in EX_GROUPS:
        LOC[f"ucm_group_pick_{k}"] = n
        LOC[f"ucm_group_pick_{k}_tt"] = f"Use {d} as the group."
        LOC[f"ucm_group.1.group.{k}"] = f"\\nGroup: {d}."
    for k, n in (("prestige", "Prestige"), ("piety", "Piety")):
        LOC[f"ucm_group_run_{k}"] = f"+1,000 {n}"
        LOC[f"ucm_group_run_{k}_tt"] = f"Give every member of the picked group 1,000 {n.lower()}."
        LOC[f"ucm_group.1.action.{k}"] = f"Give 1,000 {n.lower()}."


# --- Modifier editor ------------------------------------------------------------------------------------
CATS = (("opinion", "Opinion", r"opinion"), ("schemes", "Schemes", r"scheme"),
        ("military", "Military", r"levy|garrison|men_at_arms|maa|army|siege|supply|attrition|advantage|combat|movement|naval|embark|knight|commander|hostile|retreat|casualty|raid|pursu|screen|damage|toughness|counter|regiment"),
        ("resources", "Income & Resources", r"income|tax|gold|prestige|piety|renown|dynasty|influence|merit|herd|provisions|contribution|hire_cost"),
        ("personal", "Health & Personal", r"health|fertility|life_exp|stress|dread|tyranny|genetic|inherit|inbreed|years_of|attraction|fulfillment"),
        ("skills", "Skills & Lifestyle", r"lifestyle|_xp|diplomacy|martial|stewardship|intrigue|learning|prowess"),
        ("realm", "Realm & Buildings", r"build|holding|development|county|control|domain|vassal_limit|title|legitimacy|tribal|castle|city|church"),
        ("other", "Other", r""))
SKIP_MOD = re.compile(r"^(ai_|no_|ignore_|can_|negate_|allow_|disable_|treasury_|force_)|_budget_|^stacking")


def modifier_catalog(logs):
    with open(os.path.join(logs, "modifiers.log"), encoding="utf-8", errors="ignore") as fh:
        rows = re.findall(r"Tag: (\S+)\nUse areas: ([^\n]*)", fh.read())
    tags = sorted({t for t, areas in rows if "$" not in t and "character" in areas and not SKIP_MOD.search(t)})
    out = {c: [] for c, _, _ in CATS}
    for t in tags:
        cat = next(c for c, _, pat in CATS if not pat or re.search(pat, t))
        amount = 10 if "opinion" in t else 10 if "success_chance" in t else 0.25 if t.endswith("_mult") else 1
        out[cat].append((t, amount))
    return out


def modifier_editor(logs):
    cat = modifier_catalog(logs)
    mods, sguis, clear = [], [], []
    for c, name, _ in CATS:
        LOC[f"UCM_MODCAT_{c.upper()}"] = name
    LOC.update(UCM_MOD_EDITOR="Modifier Editor", UCM_MOD_EDITOR_NOTE="Each click stacks one more modifier on the target (+ removes a negative stack first, − a positive one).",
               ucm_mod_clear="Clear All", ucm_mod_clear_tt="Remove every stack this editor added to the target.", UCM_MOD_UP_TT="Add one stack, or remove one negative stack.",
               UCM_MOD_DOWN_TT="Remove one stack, or add one negative stack.", ucm_open_modifier_editor="Modifier Editor", ucm_open_tenet_picker="Pick Personal Tenets",
               UCM_TENET_PICKER="Personal Tenets", UCM_TENET_NOTE="Click a tenet to add it to the target, or to remove it if they already hold it. The game drops the worst tenet when out of slots.")
    for c, _, _ in CATS:
        for t, a in cat[c]:
            pos, neg = f"ucm_mp_{t}", f"ucm_mn_{t}"
            mods.append(f"{pos} = {{\n\ticon = social_positive\n\t{t} = {a}\n}}\n{neg} = {{\n\ticon = social_negative\n\t{t} = -{a}\n}}\n")
            label = vanilla_label(f"MOD_{t.upper()}", humanize(t))
            sign = f"{a:g}"
            LOC[pos], LOC[neg] = f"{label} +{sign}", f"{label} −{sign}"
            LOC[f"ucm_m_{t}"] = f"{label} (±{sign})"
            for d, a1, a2 in (("up", neg, pos), ("down", pos, neg)):
                sguis.append(f"ucm_m_{t}_{d} = {{\n\tscope = character\n\tis_shown = {{ ucm_single_player_trigger = yes }}\n\tis_valid = {{ {T} }}\n"
                             f"\teffect = {{ {TG} = {{ if = {{ limit = {{ has_character_modifier = {a1} }} remove_character_modifier = {a1} }} else = {{ add_character_modifier = {a2} }} }} }}\n}}\n")
            clear += [f"remove_all_character_modifier_instances = {pos}", f"remove_all_character_modifier_instances = {neg}"]
    sguis.append(f"ucm_mod_clear = {{\n\tscope = character\n\tis_shown = {{ ucm_single_player_trigger = yes }}\n\tis_valid = {{ {T} }}\n\teffect = {{ {TG} = {{ {' '.join(clear)} }} }}\n}}\n")
    return cat, mods, sguis


R = "GuiScope.SetRoot( GetPlayer.MakeScope ).End"


def window(name, anchor, var, title, note, body, sgui=None, size=(500, 720), extra=""):
    """The shared picker window. Opened by a VariableSystem toggle (var), or with sgui=key by a character flag:
    <key>_visible and <key>_close scripted GUIs, and no menu-target line since events open those too."""
    close = f"GetScriptedGui( '{sgui}_close' ).Execute( {R} )" if sgui else f"GetVariableSystem.Toggle( '{var}' )"
    shown = f"GetScriptedGui( '{sgui}_visible' ).IsShown( {R} )" if sgui else f"And( GetVariableSystem.Exists( '{var}' ), GetScriptedGui( 'ucm_menu_visible' ).IsShown( {R} ) )"
    return "\n".join([
        "window = {", f'  name = "{name}"', f"  parentanchor = {anchor}", f"  size = {{ {size[0]} {size[1]} }}", "  layer = top", "  movable = yes", "  alwaystransparent = no", "  filter_mouse = all",
        f'  visible = "[{shown}]"', *([extra] if extra else []),
        "  widget = {", "    size = { 100% 100% }", "    background = { using = Background_Area_Dark alpha = 1.0 }", "  }",
        "  vbox = {", "    using = Window_Margins", "    layoutpolicy_horizontal = expanding", "    layoutpolicy_vertical = expanding", "    spacing = 6",
        "    header_pattern = {", "      layoutpolicy_horizontal = expanding", f'      blockoverride "header_text" {{ text = "{title}" }}',
        f'      blockoverride "button_close" {{ onclick = "[{close}]" }}', "    }",
        *([] if sgui else ['    text_single = { layoutpolicy_horizontal = expanding text = "UCM_MENU_TARGET" }']),
        f'    text_multi = {{ layoutpolicy_horizontal = expanding autoresize = yes max_width = {size[0] - 40} text = "{note}" default_format = "#low" }}',
        body, "  }", "}", ""])


def group_list(datamodel, group_ctx, group, children, item, onclick, extra=""):
    """Scrollbox of expandable groups from a global list: heritage -> culture, religion -> faith. extra goes inside each item."""
    expanded = f"ConcatIfNeitherEmpty({group}.GetNameNoTooltip,'children_visible')"
    return f"""    scrollbox = {{
      layoutpolicy_horizontal = expanding
      layoutpolicy_vertical = expanding
      blockoverride "scrollbox_content" {{
        vbox = {{
          layoutpolicy_horizontal = expanding
          datamodel = "[GetGlobalList('{datamodel}')]"
          item = {{
            vbox = {{
              layoutpolicy_horizontal = expanding
              datacontext = "[{group_ctx}]"
              button_standard_hover = {{
                layoutpolicy_horizontal = expanding
                size = {{ 0 30 }}
                onclick = "[GetVariableSystem.Toggle({expanded})]"
                text_single = {{ parentanchor = vcenter|left position = {{ 8 0 }} text = "[{group}.GetNameNoTooltip]" default_format = "#high" }}
              }}
              vbox = {{
                layoutpolicy_horizontal = expanding
                margin_left = 12
                datamodel = "[{group}.{children}]"
                visible = "[GetVariableSystem.Exists({expanded})]"
                item = {{
                  button_standard_hover = {{
                    layoutpolicy_horizontal = expanding
                    size = {{ 0 28 }}
                    onclick = "[{onclick}]"
                    text_single = {{ parentanchor = vcenter|left position = {{ 8 0 }} text = "[{item}.GetNameNoTooltip]" default_format = "#clickable" }}{extra}
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}"""


def modifier_gui(cat):
    def shown(c):
        if c == CATS[0][0]:
            return f"[Or( GetVariableSystem.HasValue( 'ucm_mod_cat', '{c}' ), Not( GetVariableSystem.Exists( 'ucm_mod_cat' ) ) )]"
        return f"[GetVariableSystem.HasValue( 'ucm_mod_cat', '{c}' )]"

    def btn(key, label, tip):
        return (f'button_standard = {{ size = {{ 44 26 }} tooltip = "{tip}" enabled = "[GetScriptedGui( \'{key}\' ).IsValid( {R} )]" onclick = "[GetScriptedGui( \'{key}\' ).Execute( {R} )]" '
                f'text_single = {{ parentanchor = center raw_text = "{label}" }} }}')
    o = []
    for i in range(0, len(CATS), 4):
        o.append("    hbox = {\n      layoutpolicy_horizontal = expanding\n      spacing = 4")
        for c, _, _ in CATS[i:i + 4]:
            o.append(f'      button_standard = {{ layoutpolicy_horizontal = expanding size = {{ 0 28 }} down = "{shown(c)}" onclick = "[GetVariableSystem.Set( \'ucm_mod_cat\', \'{c}\' )]" '
                     f'text_single = {{ parentanchor = center text = "UCM_MODCAT_{c.upper()}" using = Font_Size_Small }} }}')
        o.append("    }")
    o.append(f'    button_standard = {{ size = {{ 120 28 }} tooltip = "ucm_mod_clear_tt" enabled = "[GetScriptedGui( \'ucm_mod_clear\' ).IsValid( {R} )]" onclick = "[GetScriptedGui( \'ucm_mod_clear\' ).Execute( {R} )]" text_single = {{ parentanchor = center text = "ucm_mod_clear" }} }}')
    for c, _, _ in CATS:
        o += ["    scrollbox = {", "      layoutpolicy_horizontal = expanding", "      layoutpolicy_vertical = expanding", f'      visible = "{shown(c)}"',
              '      blockoverride "scrollbox_content" {', "        vbox = {", "          layoutpolicy_horizontal = expanding", "          spacing = 2"]
        for t, _ in cat[c]:
            o.append(f'          hbox = {{ layoutpolicy_horizontal = expanding spacing = 4 text_single = {{ layoutpolicy_horizontal = expanding size = {{ 0 26 }} text = "ucm_m_{t}" using = Font_Size_Small }} '
                     f"{btn(f'ucm_m_{t}_down', '−', 'UCM_MOD_DOWN_TT')} {btn(f'ucm_m_{t}_up', '+', 'UCM_MOD_UP_TT')} }}")
        o += ["        }", "      }", "    }"]
    return window("ucm_modifier_editor_window", "left|vcenter", "ucm_modifier_editor", "UCM_MOD_EDITOR", "UCM_MOD_EDITOR_NOTE", "\n".join(o))


def tenet_gui():
    body = f"""    scrollbox = {{
      layoutpolicy_horizontal = expanding
      layoutpolicy_vertical = expanding
      blockoverride "scrollbox_content" {{
        dynamicgridbox = {{
          datamodel = "[GetGlobalList('ucm_acm_doctrine_list_core_tenets')]"
          flipdirection = yes
          item = {{
            widget = {{
              size = {{ 460 44 }}
              datacontext = "[GetTenetType( Scope.GetFlagName )]"
              datacontext = "[GetPlayer.MakeScope.Var('ucm_target').Char.GetFaith]"
              datacontext = "[Faith.GetMainRite]"
              button_standard_hover = {{
                size = {{ 460 42 }}
                tooltip = "FAITH_WINDOW_TENET_TOOLTIP"
                onclick = "[GetScriptedGui('ucm_toggle_personal_tenet').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).AddScope('pick_tenet', MakeScopeFlag(Scope.GetFlagName)).End)]"
                hbox = {{
                  margin = {{ 8 0 }}
                  spacing = 8
                  icon = {{ size = {{ 34 34 }} texture = "[TenetType.GetIcon( Faith.Self )]" }}
                  text_single = {{ layoutpolicy_horizontal = expanding text = "[TenetType.GetNameNoTooltip( Rite.Self )]" default_format = "#clickable" autoresize = no }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}"""
    return window("ucm_tenet_picker_window", "right|vcenter", "ucm_tenet_picker", "UCM_TENET_PICKER", "UCM_TENET_NOTE", body)


def spawn_picker_gui():
    def section(kind, cap, label, datamodel, group_ctx, group, children, item):
        var = f"GetPlayer.MakeScope.Var('ucm_spawn_{kind}')"
        clear = f"GetScriptedGui('ucm_spawn_{kind}_clear')"
        load = f"""      state = {{ name = _show on_start = "[GetScriptedGui('ucm_spawn_lists_load').Execute({R})]" }}\n""" if kind == "culture" else ""
        return f"""    hbox = {{
      layoutpolicy_horizontal = expanding
      spacing = 6
{load}      text_single = {{ text = "{label}" default_format = "#high" }}
      text_single = {{ layoutpolicy_horizontal = expanding visible = "[{var}.IsSet]" raw_text = "[{var}.{cap}.GetNameNoTooltip]" }}
      text_single = {{ layoutpolicy_horizontal = expanding visible = "[Not({var}.IsSet)]" text = "UCM_SPAWN_TARGETS" }}
      button_standard = {{ size = {{ 130 28 }} tooltip = "ucm_spawn_{kind}_clear_tt" enabled = "[{clear}.IsValid({R})]" onclick = "[{clear}.Execute({R})]" text_single = {{ parentanchor = center text = "ucm_spawn_{kind}_clear" }} }}
    }}
""" + group_list(datamodel, group_ctx, group, children, item, f"GetScriptedGui('ucm_spawn_pick_{kind}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).AddScope('selected_{kind}', {item}.MakeScope).End)")
    body = (section("culture", "Culture", "UCM_SPAWN_CULTURE_LABEL", "ucm_picker_heritages", "Scope.Culture.GetHeritage", "CulturePillar", "GetCulturesWithPillar", "Culture") + "\n"
            + section("faith", "Faith", "UCM_SPAWN_FAITH_LABEL", "ucm_picker_religions", "Scope.Religion", "Religion", "GetFaiths", "Faith"))
    return window("ucm_spawn_picker_window", "right|vcenter", "ucm_spawn_picker", "UCM_SPAWN_PICKER", "UCM_SPAWN_PICKER_NOTE", body)


def tenet_sgui(data_path):
    with open(data_path, encoding="utf-8-sig") as fh:
        text = fh.read()
    block = text[text.index("ucm_acm_doctrine_list_core_tenets"):]
    end = re.search(r"clear_global_variable_list = (?!ucm_acm_doctrine_list_core_tenets)", block)
    block = block[:end.start()] if end else block
    flags = sorted(set(re.findall(r"target = flag:(\w+)", block)))
    ladder = " ".join(f"{'if' if i == 0 else 'else_if'} = {{ limit = {{ scope:pick_tenet = flag:{t} }} if = {{ limit = {{ any_personal_tenet = {{ this = tenet:{t} }} }} remove_personal_tenet = tenet:{t} }} else = {{ force_set_personal_tenet = tenet:{t} }} }}"
                      for i, t in enumerate(flags))
    return (f"ucm_toggle_personal_tenet = {{\n\tscope = character\n\tsaved_scopes = {{ pick_tenet }}\n\tis_shown = {{ ucm_single_player_trigger = yes }}\n"
            f"\tis_valid = {{ {T} {TG} = {{ is_playable_character = yes }} }}\n\teffect = {{ {TG} = {{ {ladder} }} }}\n}}\n")


PILLAR_TYPES = ("ethos", "heritage", "language", "martial_custom")


def pillars_by_type(game):
    out = {t: [] for t in PILLAR_TYPES}
    for f in ck3parse.effective_files(os.path.join("common", "culture", "pillars"), game):
        for k, b in ck3parse.top_level_objects(f):
            m = re.search(r"\btype\s*=\s*(\w+)", b)
            if m and m.group(1) in out:
                out[m.group(1)].append(k)
    return out


def pillar_gui(pillars):
    o = ["    scrollbox = {", "      layoutpolicy_horizontal = expanding", "      layoutpolicy_vertical = expanding", '      blockoverride "scrollbox_content" {',
         "        vbox = {", "          layoutpolicy_horizontal = expanding", "          spacing = 2"]
    for t, keys in pillars.items():
        o.append(f'          text_single = {{ layoutpolicy_horizontal = expanding text = "UCM_PILLAR_{t.upper()}" default_format = "#high" }}')
        for k in sorted(keys):
            sg_ref = f"GetScriptedGui( 'ucm_pillar_{k}' )"
            o.append(f'          button_standard = {{ layoutpolicy_horizontal = expanding size = {{ 0 26 }} visible = "[{sg_ref}.IsShown( {R} )]" enabled = "[{sg_ref}.IsValid( {R} )]" onclick = "[{sg_ref}.Execute( {R} )]" '
                     f'text_single = {{ parentanchor = center text = "{k}_name" using = Font_Size_Small }} }}')
    o += ["        }", "      }", "    }"]
    return window("ucm_pillar_picker_window", "right|vcenter", "ucm_pillar_picker", "UCM_PILLAR_PICKER", "UCM_PILLAR_NOTE", "\n".join(o))


def pillar_sguis(pillars):
    """One scripted GUI per pillar; vanilla keys, so EK2 stubs them with the other vanilla actions."""
    for keys in pillars.values():
        for k in sorted(keys):
            VANILLA_SGUIS.append(f"ucm_pillar_{k} = {{\n\tscope = character\n\tis_shown = {{ ucm_single_player_trigger = yes }}\n"
                                 f"\tis_valid = {{ {T} exists = {TG}.culture {TG}.culture = {{ NOT = {{ has_cultural_pillar = {k} }} }} }}\n"
                                 f"\teffect = {{ {TG}.culture = {{ set_culture_pillar = {k} }} }}\n}}\n")
    LOC.update(UCM_PILLAR_PICKER="Culture Pillars", UCM_PILLAR_NOTE="Click a pillar to set it on the target's culture. This changes the culture for everyone in it.",
               ucm_open_pillar_picker="Culture Pillars", UCM_PILLAR_ETHOS="Ethos", UCM_PILLAR_HERITAGE="Heritage", UCM_PILLAR_LANGUAGE="Language", UCM_PILLAR_MARTIAL_CUSTOM="Martial Custom")


def build(game):
    """Fill SGUIS, VANILLA_SGUIS and LOC; return {tab: items}."""
    SGUIS.clear(), VANILLA_SGUIS.clear(), LOC.clear()
    load_vanilla_loc(game)
    group_loc()
    faith = faith_culture()
    faith.insert(1, ("vs", "ucm_tenet_picker", "ucm_open_tenet_picker"))
    faith.insert(2, ("vs", "ucm_pillar_picker", "ucm_open_pillar_picker"))
    pillar_sguis(pillars_by_type(game))
    return {"character": [("vs", "ucm_modifier_editor", "ucm_open_modifier_editor")] + character(), "relationships": relationships(), "titles": titles(),
            "faith_culture": faith + innovation_eras(game), "realm": realm() + buildings(game), "dlc": activities_legends(), "court": spawner(game), "military": knights()}


def game_dir(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--game-dir", default=os.environ.get("CK3_GAME_DIR", DEFAULT_GAME))
    return p.parse_args(argv).game_dir


def write(path, text):
    with open(os.path.join(MOD, *path.split("/")), "wb") as fh:
        fh.write(b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode("utf-8"))


def main():
    game = game_dir()
    build(game)
    logs = os.environ.get("CK3_LOG_DIR", DEFAULT_LOGS)
    cat, mod_defs, mod_sguis = modifier_editor(logs)
    data = "common/scripted_effects/ucm_acm_faith_editor_data_effects.txt"
    tenet = tenet_sgui(os.path.join(MOD, *data.split("/")))
    head = "# AUTO-GENERATED by tools/gen_ucm_extra.py; edit there, not this file.\n# Root = player; target var:ucm_target, second character global_var:ucm_crozier_cheats_other.\n\n"
    write("common/scripted_guis/ucm_extra_sguis.txt", head + "\n".join(SGUIS))
    write("common/scripted_guis/ucm_extra_vanilla_sguis.txt", head + "\n".join(VANILLA_SGUIS + [tenet]))
    stubs = "".join(f"{k} = {{ scope = character is_shown = {{ always = no }} is_valid = {{ always = no }} effect = {{ }} }}\n" for k in re.findall(r"(?m)^(\w+) = \{", "".join(VANILLA_SGUIS)))
    ek2_data = os.path.join(MOD, "compat", "ek2", *data.split("/"))
    write("compat/ek2/common/scripted_guis/ucm_extra_vanilla_sguis.txt", head + stubs + "\n" + (tenet_sgui(ek2_data) if os.path.exists(ek2_data) else ""))
    write("common/scripted_guis/ucm_modifier_editor_sguis.txt", head + "\n".join(mod_sguis))
    write("common/modifiers/ucm_modifier_editor_modifiers.txt", head + "\n".join(mod_defs))
    write("gui/ucm_modifier_editor.gui", modifier_gui(cat))
    write("gui/ucm_tenet_picker.gui", tenet_gui())
    write("gui/ucm_pillar_picker.gui", pillar_gui(pillars_by_type(game)))
    write("gui/ucm_spawn_picker.gui", spawn_picker_gui())
    write("common/scripted_effects/ucm_extra_effects.txt", head + SPAWN_EFFECTS)
    write("common/script_values/ucm_extra_values.txt", head + SPAWN_VALUES)
    mods = "".join(f"ucm_extra_county_{k} = {{\n\ticon = county_modifier_development_positive\n\t{body}\n}}\n\n" for k, _, body in MODS)
    mods += ("ucm_extra_building_slot = {\n\ticon = county_modifier_development_positive\n\tbuilding_slot_add = 1\n}\n\n"
             "ucm_extra_lock_legitimacy = {\n\ticon = social_positive\n\tlegitimacy_gain_mult = -1\n\tlegitimacy_loss_mult = -1\n}\n\n"
             "ucm_extra_lock_stress = {\n\ticon = social_positive\n\tstress_gain_mult = -10\n\tstress_loss_mult = -10\n}\n\n"
             "ucm_extra_lock_tyranny = {\n\ticon = social_positive\n\ttyranny_gain_mult = -10\n\ttyranny_loss_mult = -10\n}\n\n"
             "ucm_extra_lock_dread = {\n\ticon = social_positive\n\tdread_decay_mult = -10\n\tdread_gain_mult = -10\n\tdread_loss_mult = -10\n}\n\n"
             "ucm_extra_divine_grace = {\n\ticon = social_positive\n\tcharacter_spiritual_fulfillment_loss_mult = -1\n}\n")
    write("common/modifiers/ucm_extra_modifiers.txt", head + mods)
    for k, name, _ in MODS:
        LOC[f"ucm_extra_county_{k}"] = name
    LOC.update(ucm_extra_building_slot="Extra Building Slot", ucm_extra_lock_legitimacy="Legitimacy Locked", ucm_extra_lock_stress="Stress Locked", ucm_extra_lock_tyranny="Tyranny Locked", ucm_extra_lock_dread="Dread Locked", ucm_extra_divine_grace="Fulfillment Protected")
    LOC.update({"ucm_extra.1.t": "Remove Holdings", "ucm_extra.1.desc": "Every holding in the target's capital county, except the county capital, will be removed. Restoring a save is the only way back.",
                "ucm_extra.2.t": "Destroy Title", "ucm_extra.2.desc": "The target's primary title will be destroyed. Restoring a save is the only way back.",
                "ucm_extra.3.t": "Rename", "ucm_extra.3.desc": "Type the target's new first name.", "ucm_extra.close": "Done",
                "ucm_extra.a": "Do it", "ucm_extra.b": "Cancel"})
    write("localization/english/ucm_extra_l_english.yml", "l_english:\n" + "".join(f' {k}: "{v}"\n' for k, v in LOC.items()))
    tr_path = os.path.join(MOD, "tools", "ucm_extra_translations.json")
    tr = json.load(open(tr_path, encoding="utf-8")) if os.path.exists(tr_path) else {}
    for lang in ("german", "russian", "simp_chinese", "turkish"):
        table = tr.get(lang, {})
        write(f"localization/{lang}/ucm_extra_l_{lang}.yml", f"l_{lang}:\n" + "".join(f' {k}: "{table.get(v, v)}"\n' for k, v in LOC.items()))
    print(f"{len(SGUIS)} actions, {len(VANILLA_SGUIS)} vanilla-data actions, {len(LOC)} loc keys")


if __name__ == "__main__":
    main()
