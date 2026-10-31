"""Regenerate gui/ucm_main_menu.gui, the Unified Cheat Menu window, from TABS below.

Each tab is a list of items:
    ("h", loc_key)        section header
    ("t", loc_key)        note text
    ("sg", sgui)          button running scripted GUI `sgui` (common/scripted_guis/ucm_*.txt);
                          text is loc key `sgui`, tooltip `sgui_tt`
    ("row", [sgui, ...])  the same, as small buttons side by side
    ("ia", interaction)   button opening an existing character interaction on the target;
                          shown/enabled/named exactly as the interaction itself
    ("dec", decision)     button opening an existing decision's detail view; decisions
                          always act on the player, not the target
    ("cz", name)          button(s) for ucm_crozier_cheats_sg_<name> (tools/gen_ucm_crozier.py);
                          a tog_ toggle shows as an on/off pair
    ("czrow", [name, ...], label_key)  the same, side by side
    ("picks", [group, ...])  group-action picker buttons (ucm_group_pick_<group>), shown pressed
                          when that group is picked
    ("steps",)            step-size selector (ucm_step_*)
    ("skill", name)       skill row: value, minus and plus (ucm_skill_<name>_down/_up)
    ("value", label_key, binding, sgui)  the same for any GUI data binding (<sgui>_down/_up)
    ("vs", var, loc_key)  button toggling a side window shown while GUI variable `var` exists
    ("togglerow", [(sgui, flag), ...])  scripted GUI buttons, shown pressed while the player has `flag`

Run after editing TABS:
    python tools/gen_ucm_main_menu.py
"""
import os

import gen_ucm_crozier
import gen_ucm_extra

MOD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(MOD_DIR, "gui", "ucm_main_menu.gui")
R = "GuiScope.SetRoot( GetPlayer.MakeScope ).End"
C = "GetPlayer.MakeScope.Var( 'ucm_target' ).Char"

EK2_LIFESTYLES = {"magic": "Magic", "dark_arts": "Dark Arts"}
EK2_TREES = ["conjuration", "destruction", "alteration", "illusion", "restoration", "necromancy"]
EK2_PERK_RANKS = ["novice", "apprentice", "minor_rituals", "journeyman", "medium_rituals", "expert", "major_rituals", "master"]


def ek2_tree_items(trees):
    out = []
    for t in trees:
        out += [("h", f"UCM_SEC_EK2_TREE_{t.upper()}"), ("sg", f"ucm_ek2_perks_{t}")]
        out += [("sg", f"ucm_ek2_perk_{t}_{r}_perk") for r in EK2_PERK_RANKS]
    return out


TABS = [
    ("quick", [
        ("sg", "ucm_quick_gold"), ("sg", "ucm_quick_prestige"), ("sg", "ucm_quick_piety"), ("sg", "ucm_clear_stress"),
        ("h", "UCM_SEC_ALWAYS_ON"),
        ("t", "UCM_ALWAYS_ON_NOTE"),
        ("czrow", ["pow_1", "pow_2", "pow_3", "pow_4", "pow_5", "pow_6", "pow_7"], "UCM_CROZIER_CHEATS_POW_LABEL"),
        ("czrow", ["tier_1", "tier_2", "tier_3"], "UCM_CROZIER_CHEATS_TIER_LABEL"),
        ("cz", "do_freq_week"), ("cz", "do_freq_month"), ("cz", "do_freq_quarter"),
        ("czrow", ["pon_char_self", "poff_char_self"]),
        ("cz", "tog_income"),
        ("cz", "tog_monthly_gold"),
        ("cz", "tog_domain"),
        ("cz", "tog_vassals"),
        ("cz", "tog_prestige"),
        ("cz", "tog_prestige_mult"),
        ("cz", "tog_piety"),
        ("cz", "tog_renown"),
        ("cz", "tog_renown_mult"),
        ("cz", "tog_influence"),
        ("cz", "tog_merit_gain"),
        ("cz", "tog_legit_gain"),
        ("cz", "tog_health"),
        ("cz", "tog_stress"),
        ("cz", "tog_life"),
        ("cz", "tog_immortal_player"),
        ("cz", "tog_disease_player"),
        ("cz", "tog_long_reign"),
        ("cz", "tog_skills"),
        ("cz", "tog_skills_mult"),
        ("cz", "tog_lifestyle_xp"),
        ("cz", "tog_innovation"),
        ("cz", "tog_slots"),
        ("cz", "tog_travel_safe"),
        ("cz", "tog_legend_spread"),
        ("cz", "tog_auto_gold_floor"),
        ("cz", "tog_auto_prestige_floor"),
        ("cz", "tog_auto_no_prison"),
        ("cz", "tog_auto_ascension"),
        ("cz", "tog_auto_forever_young"),
        ("cz", "do_toasts_toggle"),
    ]),
    ("character", [
        ("h", "UCM_SEC_EDITORS"),
        ("sg", "ucm_open_trait_editor"), ("sg", "ucm_open_lifestyle_editor"),
        ("ia", "daddy_pika_edit_character"),
        ("h", "UCM_SEC_IDENTITY"),
        ("ia", "ucm_change_age_interaction"),
        ("row", ["ucm_sexuality_heterosexual", "ucm_sexuality_homosexual", "ucm_sexuality_bisexual", "ucm_sexuality_asexual"]),
        ("ia", "daddy_pika_change_dynasty"), ("ia", "daddy_pika_change_character"),
        ("h", "UCM_SEC_ATTRIBUTES"),
        ("steps",),
        ("skill", "diplomacy"), ("skill", "martial"), ("skill", "stewardship"),
        ("skill", "intrigue"), ("skill", "learning"), ("skill", "prowess"),
        ("row", ["ucm_skill_all_down", "ucm_skill_all_up"]),
        ("row", ["ucm_weight_down", "ucm_weight_up"]),
        ("value", "UCM_RENOWN", f"{C}.GetDynasty.GetPrestige|0", "ucm_renown"),
        ("row", ["ucm_renown_1000_down", "ucm_renown_1000_up"]),
        ("row", ["ucm_renown_level_down", "ucm_renown_level_up"]),
        ("ia", "daddy_pika_boost_stats"),
        ("h", "UCM_SEC_TRAITS"),
        ("ia", "zhuge_yixue_02"), ("ia", "zhueg_yixue_03"), ("ia", "zhuge_yixue_04"), ("ia", "zhuge_yixue_06"),
        ("h", "UCM_SEC_HEALTH"),
        ("sg", "ucm_clear_stress"),
        ("ia", "zhuge_yixue_01"), ("ia", "zhuge_yixue_05"),
        ("ia", "set_immortal_interaction"), ("ia", "set_mortal_interaction"),
        ("ia", "toc_celibate_interaction"),
        ("h", "UCM_SEC_LIFESTYLE"),
        ("ia", "zhuge_lifexp_all_xp"),
        ("h", "UCM_SEC_PRESETS"),
        ("ia", "set_super_interaction"), ("ia", "set_unsuper_interaction"),
        ("ia", "set_super_governor_interaction"), ("ia", "set_unsuper_governor_interaction"),
        ("ia", "set_super_general_interaction"), ("ia", "set_unsuper_general_interaction"),
        ("ia", "set_all_in_one_interaction"), ("ia", "set_unall_in_one_interaction"),
        ("h", "UCM_SEC_RESOURCES"),
        ("ia", "daddy_pika_character_currency_menu"),
    ]),
    ("relationships", [
        ("h", "UCM_SEC_SECOND"),
        ("sg", "ucm_second_set_target"), ("sg", "ucm_second_clear"),
        ("t", "UCM_SECOND_NOTE"),
        ("h", "UCM_SEC_RELATIONS"),
        ("row", ["ucm_relation_friend", "ucm_relation_best_friend", "ucm_relation_rival"]),
        ("row", ["ucm_relation_nemesis", "ucm_relation_lover", "ucm_relation_soulmate"]),
        ("sg", "ucm_relation_clear"),
        ("ia", "zhuge_set_relation_interaction"),
        ("h", "UCM_SEC_MARRIAGE"),
        ("row", ["ucm_marry_second", "ucm_marry_second_matrilineal"]),
        ("row", ["ucm_betroth_second", "ucm_betroth_second_matrilineal"]),
        ("row", ["ucm_break_betrothal_second", "ucm_divorce_second"]),
        ("ia", "daddy_pika_arrange_marriage_inter"), ("ia", "divorce_character_cheat"), ("ia", "daddy_pika_concubine_cheat"),
        ("h", "UCM_SEC_FAMILY"),
        ("row", ["ucm_second_as_father", "ucm_second_as_real_father", "ucm_second_as_mother"]),
        ("sg", "ucm_join_second_house"),
        ("ia", "daddy_pika_adopt_m"), ("ia", "daddy_pika_adopt_f"), ("ia", "daddy_pika_disown"),
        ("ia", "daddy_pika_designate_heir"), ("ia", "toc_setheira_interaction"), ("ia", "toc_disinherit_interaction"),
        ("ia", "daddy_pika_extermination_process"),
        ("h", "UCM_SEC_PREGNANCY"),
        ("row", ["ucm_pregnant_by_second_1", "ucm_pregnant_by_second_2", "ucm_pregnant_by_second_3"]),
        ("sg", "ucm_end_pregnancy"),
        ("ia", "toc_pregnancy_interaction"),
        ("h", "UCM_SEC_HOOKS"),
        ("row", ["ucm_second_hook_on_target", "ucm_target_hook_on_second"]),
        ("ia", "daddy_pika_add_strong_hook"),
        ("row", ["ucm_learn_target_secrets", "ucm_expose_target_secrets"]),
    ]),
    ("titles", [
        ("h", "UCM_SEC_CLAIMS"),
        ("sg", "ucm_target_claims_second_title"),
        ("ia", "daddy_pika_usurpy_surp"), ("ia", "daddy_pika_claim_title"), ("ia", "daddy_pika_revoke_title"),
        ("ia", "take_title_interaction"), ("ia", "take_title_and_vassals_interaction"),
        ("ia", "take_domain_interaction"), ("ia", "take_realm_interaction"),
        ("ia", "get_claim_interaction"), ("ia", "get_claim_on_all_creatable_interaction"),
        ("ia", "ucm_create_titular"), ("ia", "mt_merge_titles_interaction"), ("ia", "mt_clear_selection_interaction"),
        ("ia", "destroy_title_interaction"), ("ia", "zhuge_destroy_title"),
        ("ia", "become_conqueror_interaction"), ("ia", "remove_conqueror_interaction"),
        ("h", "UCM_SEC_DEJURE"),
        ("ia", "zhuge_organize_titles"), ("dec", "ucm_one_click_transfer_vassals_decision"),
        ("h", "UCM_SEC_VASSALS"),
        ("row", ["ucm_target_independent", "ucm_target_vassal_of_second"]),
        ("ia", "daddy_pika_offer_vassal_inter"), ("ia", "daddy_pika_char_modify_vassal_contract_inter"),
        ("ia", "daddy_pika_vassal_mod_vassal_contract_inter"), ("ia", "zhuge_mpo_qiyue"),
        ("dec", "ucm_imprison_vassals_decision"), ("dec", "ucm_dynasty_grant_titles_decision"),
        ("dec", "ucm_one_click_grant_titles_decision"), ("dec", "ucm_official_land_cap_decision"),
        ("dec", "ucm_one_click_strip_official_titles_decision"),
        ("h", "UCM_SEC_GOVERNMENT"),
        ("row", ["ucm_gov_feudal", "ucm_gov_clan", "ucm_gov_tribal"]),
        ("row", ["ucm_gov_administrative", "ucm_gov_republic", "ucm_gov_theocracy"]),
        ("row", ["ucm_gov_nomadic", "ucm_gov_herder", "ucm_gov_celestial"]),
        ("row", ["ucm_gov_meritocratic", "ucm_gov_mandala", "ucm_gov_steppe_admin"]),
        ("row", ["ucm_gov_japan_feudal", "ucm_gov_japan_administrative"]),
        ("ia", "zhuge_set_authority_inter"),
        ("h", "UCM_SEC_YOUR_SUCCESSION"),
        ("t", "UCM_DECISIONS_NOTE"),
        ("dec", "change_Realm_succession_law_mod_decision"), ("dec", "change_succession_single"),
        ("dec", "change_succession_single_youngest"), ("dec", "gender_Succession_events_mod_decision"),
        ("dec", "dynasty_of_many_crowns_decision"),
        ("h", "UCM_SEC_DIPLOMACY"),
        ("row", ["ucm_ally_second", "ucm_break_alliance_second", "ucm_truce_second"]),
        ("ia", "debug_alliance_interaction"), ("ia", "zhuge_add_truce_interaction"), ("ia", "debug_add_truce_interaction"),
        ("h", "UCM_SEC_WARS"),
        ("sg", "ucm_end_wars_white_peace"),
        ("ia", "sol_war_without_bounds_interaction"), ("ia", "sol_expansion_war_interaction"),
        ("ia", "dp_debug_start_great_holy_war_interaction"),
        ("ia", "dp_debug_start_era_of_crusades_interaction"), ("ia", "dp_debug_start_era_of_jihads_interaction"),
        ("h", "UCM_SEC_AI"),
        ("dec", "ucm_ai_yearly_pulse_toggle_decision"), ("dec", "ucm_ai_yearly_de_jure_transfer_toggle_decision"),
        ("dec", "ucm_ai_yearly_admin_conversion_toggle_decision"), ("dec", "ucm_ai_boost_toggle_decision"),
        ("dec", "ucm_world_ai_boost_pause_decision"), ("dec", "ucm_world_ai_boost_resume_decision"),
        ("dec", "ucm_boost_world_ai_rulers_decision"),
    ]),
    ("faith_culture", [
        ("h", "UCM_SEC_EDITORS"),
        ("sg", "ucm_open_culture_picker"), ("sg", "ucm_open_religion_picker"), ("sg", "ucm_open_tradition_picker"),
        ("h", "UCM_SEC_FAITH"),
        ("sg", "ucm_adopt_second_faith"),
        ("ia", "daddy_pika_change_religion"), ("ia", "toc_religionconvert_interaction"), ("ia", "toc_yapaconvert_interaction"),
        ("ia", "daddy_pika_excommunicate"), ("ia", "daddy_pika_remove_excommunication"),
        ("ia", "pope_select_interaction"), ("ia", "grandmaster_select_interaction"),
        ("dec", "dynasty_pope_0_decision"), ("dec", "dynasty_grandmaster_0_decision"),
        ("h", "UCM_SEC_CULTURE"),
        ("sg", "ucm_adopt_second_culture"), ("sg", "ucm_culture_all_innovations"),
        ("ia", "daddy_pika_change_culture"), ("ia", "change_cultural_acceptance_debug_interaction"),
        ("ia", "learn_language_debug_interaction"), ("ia", "zhuge_buff_04"),
        ("h", "UCM_SEC_REALM_CONVERSION"),
        ("t", "UCM_DECISIONS_NOTE"),
        ("dec", "convert_religion"), ("dec", "convert_culture"),
        ("dec", "pcm_convert_subrealm_to_religion_decision"), ("dec", "pcm_convert_subrealm_to_culture_decision"),
        ("dec", "culture_cheat"), ("dec", "X_unify"),
    ]),
    ("realm", [
        ("h", "UCM_SEC_GROUP_PICKER"),
        ("t", "UCM_GROUP_PICKER_NOTE"),
        ("t", "UCM_GROUP_COUNTIES"),
        ("picks", ["sub_realm_counties", "dejure_counties", "culture_counties", "faith_counties"]),
        ("t", "UCM_GROUP_COUNTY_ACTIONS"),
        ("row", ["ucm_group_run_max_development", "ucm_group_run_max_control"]),
        ("row", ["ucm_group_run_county_faith", "ucm_group_run_county_culture"]),
        ("h", "UCM_SEC_COUNTIES"),
        ("ia", "toc_county_modifier_interaction"), ("ia", "debug_change_every_county"),
        ("t", "UCM_DECISIONS_NOTE"),
        ("dec", "realm_control"), ("dec", "realm_development"),
        ("h", "UCM_SEC_HOLDINGS"),
        ("dec", "ch_convert_holding_to_castle_decision"), ("dec", "ch_convert_holding_to_city_decision"),
        ("dec", "ch_convert_holding_to_temple_decision"), ("dec", "ch_convert_holding_to_temple_citadel_decision"),
        ("dec", "ch_convert_holding_to_tribal_decision"), ("dec", "ch_convert_holding_to_nomad_decision"),
        ("dec", "ucm_realm_repair_holding_bases_decision"),
        ("h", "UCM_SEC_BUILDINGS"),
        ("dec", "pcm_b_max_all_buildings_sub_realm_decision"), ("dec", "pcm_b_add_building_slot_7_sub_realm_decision"),
        ("dec", "pcm_b_lucky_7_sub_realm_decision"),
        ("dec", "X_build"), ("dec", "X_city"), ("dec", "X_temple"), ("dec", "X_castle"),
        ("h", "UCM_SEC_ECONOMY"),
        ("dec", "pcm_money_decision"), ("dec", "ucm_fiscal_treasury_officials_decision"),
        ("dec", "ucm_population_management_hub_decision"),
        ("h", "UCM_SEC_OFFICIALS"),
        ("dec", "ucm_one_click_purge_bad_governors_decision"), ("dec", "ucm_one_click_imperial_examination_promote_decision"),
        ("dec", "ucm_learn_all_realm_officials_secrets_decision"), ("dec", "ucm_seduce_shield_for_consorts_decision"),
    ]),
    ("military", [
        ("h", "UCM_SEC_ARMIES"),
        ("sg", "ucm_open_army_spawner"),
        ("ia", "inheritable_optroop_interaction"), ("ia", "non_inheritable_optroop_interaction"),
        ("ia", "toc_givearmyhorde_interaction"),
        ("cz", "do_combo_army"), ("cz", "tog_levy"), ("cz", "t_t_armies_to"),
        ("h", "UCM_SEC_ENEMY_ARMIES"),
        ("cz", "t_enemy_commander"), ("cz", "t_enemy_deplete"), ("cz", "t_enemy_supply"),
        ("h", "UCM_SEC_KNIGHTS"),
        ("ia", "zhuge_buff_05"), ("ia", "add_glory_interaction"), ("ia", "zhuge_buff_02"),
        ("cz", "t_t_knight_force"), ("cz", "t_t_knight_off"),
    ]),
    ("artifacts", [
        ("h", "UCM_SEC_EDITORS"),
        ("sg", "ucm_open_artifact_crafter"), ("sg", "ucm_open_artifact_repair"),
        ("h", "UCM_SEC_TARGET_ARTIFACTS"),
        ("row", ["ucm_artifacts_repair_all", "ucm_artifacts_all_illustrious"]),
        ("ia", "add_artifact_interaction"), ("ia", "take_artifact_interaction"), ("ia", "add_artifact_claim_interaction"),
        ("ia", "debug_destroy_artifact_interaction"), ("ia", "generate_artifact_with_history_interaction"),
        ("ia", "zhuge_set_artifact_interaction"), ("ia", "zhuge_huoqu_artifact_interaction"),
        ("cz", "t_t_rob_artifacts"), ("cz", "t_t_artifact_claims"),
        ("h", "UCM_SEC_YOUR_ARTIFACTS"),
        ("cz", "do_forge_crown"), ("dec", "Artifact_1000"),
    ]),
    ("court", [
        ("h", "UCM_SEC_GROUP_PICKER"),
        ("t", "UCM_GROUP_PICKER_NOTE"),
        ("t", "UCM_GROUP_CHARACTERS"),
        ("picks", ["courtiers", "vassals", "all_vassals", "councillors", "knights", "children", "close_family", "extended_family", "spouses", "lovers", "friends", "rivals", "house", "dynasty", "house_bloc", "faith_members", "culture_members"]),
        ("t", "UCM_GROUP_CHAR_ACTIONS"),
        ("row", ["ucm_group_run_clear_stress", "ucm_group_run_skills_up", "ucm_group_run_gold"]),
        ("row", ["ucm_group_run_convert_faith", "ucm_group_run_convert_culture", "ucm_group_run_max_opinion"]),
        ("row", ["ucm_group_run_prestige", "ucm_group_run_piety"]),
        ("h", "UCM_SEC_GENERATION"),
        ("ia", "toc_spawn_character_interaction"), ("ia", "toc_addcharacter_interaction"),
        ("ia", "toc_addcourtier_interaction"), ("ia", "toc_addwombmancourtier_interaction"), ("ia", "spawn_courtier_interaction"),
        ("cz", "t_t_child_now"), ("cz", "t_t_child_me"),
        ("h", "UCM_SEC_COURT"),
        ("ia", "daddy_pika_add_to_court"), ("ia", "add_to_court_interaction"), ("ia", "jkm_send_courtier_interaction"),
        ("cz", "t_t_guest"), ("ia", "antagonise_court"),
        ("h", "UCM_SEC_COUNCIL"),
        ("cz", "t_t_councillor_chancellor"), ("cz", "t_t_councillor_steward"), ("cz", "t_t_councillor_marshal"),
        ("cz", "t_t_councillor_spymaster"), ("cz", "t_t_councillor_court_chaplain"),
        ("cz", "t_t_cp_court_physician"), ("cz", "t_t_cp_court_tutor"), ("cz", "t_t_cp_bodyguard"),
        ("cz", "t_t_cp_champion"), ("cz", "t_t_cp_master_assassin"), ("cz", "t_t_cp_royal_architect"),
        ("ia", "debug_change_council_task_interaction"), ("ia", "toc_finishcounciltask_interaction"),
        ("h", "UCM_SEC_COURT_TOOLS"),
        ("t", "UCM_DECISIONS_NOTE"),
        ("dec", "ucm_court_management_decision"), ("dec", "ucm_positions_mass_reshuffle_decision"),
        ("dec", "yyz_open_menu_decision"), ("dec", "ucm_bulk_guardian_run_decision"),
        ("dec", "pcm_cure_all_decision"), ("dec", "pcm_cure_pox_decision"), ("dec", "pcm_cure_inbred_decision"),
        ("h", "UCM_SEC_PRISON"),
        ("ia", "daddy_pika_imprison"), ("ia", "debug_imprison_simple_interaction"),
        ("cz", "t_t_hostage"), ("cz", "t_t_hostage_free"), ("cz", "t_t_family_hostages"),
        ("h", "UCM_SEC_DANGER"),
        ("t", "UCM_DANGER_NOTE"),
        ("ia", "toc_deposed_interaction"), ("cz", "t_t_depose"), ("cz", "t_t_banish"),
        ("ia", "daddy_pika_murder"), ("ia", "slay_character_interaction"), ("cz", "t_t_execute"),
        ("ia", "daddy_pika_commit_suicide"),
    ]),
    ("dlc", [
        ("h", "UCM_SEC_REGENCY"),
        ("row", ["ucm_diarchy_start_regency", "ucm_diarchy_start_co_monarchy", "ucm_diarchy_start_vizierate"]),
        ("sg", "ucm_diarchy_second_as_diarch"),
        ("steps",),
        ("row", ["ucm_diarchy_swing_down", "ucm_diarchy_swing_up"]),
        ("sg", "ucm_diarchy_end"),
        ("h", "UCM_SEC_SCHEMES"),
        ("ia", "debug_buff_schemes"), ("ia", "debug_progress_all_active_schemes_interaction"),
        ("ia", "debug_clear_agents_from_schemes"), ("ia", "give_infinite_schemes_of_type_interaction"),
        ("cz", "t_t_schemes_end"), ("cz", "t_t_schemes_expose"),
        ("h", "UCM_SEC_INSPIRATIONS"),
        ("ia", "inspire_interaction"), ("ia", "sponsor_inspiration_debug"),
        ("h", "UCM_SEC_LEGENDS"),
        ("ia", "spawn_legend_interaction"), ("cz", "tog_legend_spread"),
        ("h", "UCM_SEC_ACTIVITIES"),
        ("ia", "start_bout_interaction"), ("ia", "change_hunt_success_chance"), ("ia", "change_tournament_score"),
        ("ia", "debug_give_animal_interaction"), ("ia", "change_coronation_law"),
        ("ia", "debug_coronation_add_to_guest_subset_interaction"),
        ("h", "UCM_SEC_ADVENTURERS"),
        ("ia", "debug_move_domicile_interaction"), ("ia", "debug_make_laamp"), ("ia", "create_task_contract_interaction"),
        ("ia", "debug_populate_contracts"), ("ia", "debug_add_to_contact_list_interaction"),
        ("ia", "debug_travel_to_ruler_interaction"), ("cz", "do_travel_arrive"),
        ("h", "UCM_SEC_EPIDEMICS"),
        ("ia", "spawn_epidemic_interaction"),
        ("cz", "t_t_epidemic_bubonic_plague"), ("cz", "t_t_epidemic_smallpox"), ("cz", "t_t_epidemic_measles"),
        ("cz", "t_t_epidemic_consumption"), ("cz", "t_t_epidemic_dysentery"), ("cz", "t_t_epidemic_typhus"),
        ("cz", "t_t_epidemic_ergotism"), ("cz", "t_t_pneumonic"),
        ("h", "UCM_SEC_SITUATIONS"),
        ("ia", "debug_change_dynastic_cycle"), ("ia", "debug_change_silk_road_cycle"), ("ia", "debug_set_mandala_aspect"),
        ("ia", "debug_change_the_great_steppe"), ("ia", "zhuge_great_steppe"), ("ia", "zhuge_ymbuff_02"),
    ]),
    ("settings", [
        ("h", "UCM_SEC_MENU"),
        ("sg", "ucm_second_clear"), ("sg", "ucm_menu_reset"),
        ("h", "UCM_SEC_CLASSIC"),
        ("t", "UCM_CLASSIC_NOTE"),
        ("ia", "cheateb_editmenu_interaction"), ("dec", "open_daddypika_menu"), ("dec", "daddy_pika_information"),
        ("h", "UCM_SEC_DEBUG"),
        ("sg", "ucm_open_console_helper"), ("ia", "toc_main_debug_interaction"),
    ]),
    # Effects live in compat/ek2; the main mod ships is_shown = no stubs, so the tab only appears with EK2.
    ("ek2", [
        ("h", "UCM_SEC_EK2_ARCANA"),
        ("sg", "ucm_ek2_max_arcana"), ("sg", "ucm_ek2_refill_magicka"),
        ("steps",),
        ("value", "UCM_SKILL_ARCANA", f"{C}.MakeScope.ScriptValue( 'ucm_ek2_arcana_value' )|0", "ucm_ek2_arcana"),
        ("value", "UCM_SKILL_MAGICKA", f"{C}.MakeScope.ScriptValue( 'ucm_ek2_magicka_value' )|0", "ucm_ek2_magicka"),
        ("h", "UCM_SEC_EK2_LIFESTYLE"),
        *[("sg", f"ucm_ek2_{ls}_{k}") for ls in EK2_LIFESTYLES for k in ("point", "xp")],
        ("h", "UCM_SEC_EK2_SCHOOLS"),
        *ek2_tree_items(EK2_TREES[:5]),
        ("h", "UCM_SEC_EK2_DARK"),
        *ek2_tree_items(EK2_TREES[5:]),
    ]),
]
_extra = gen_ucm_extra.build(gen_ucm_extra.game_dir([]))
for _tab, _items in TABS:
    _items.extend(_extra.get(_tab, []))
# Tabs shown only while this scripted GUI's is_shown holds.
TAB_GATES = {"ek2": "ucm_ek2_tab"}


def tab_shown(t):
    if t == "quick":
        return "[Or( GetVariableSystem.HasValue( 'ucm_tab', 'quick' ), Not( GetVariableSystem.Exists( 'ucm_tab' ) ) )]"
    return f"[GetVariableSystem.HasValue( 'ucm_tab', '{t}' )]"


def sgui_button(name, ind, width="0", expand=True):
    return [
        f"{ind}button_standard = {{",
        *([f"{ind}  layoutpolicy_horizontal = expanding"] if expand else []),
        f"{ind}  size = {{ {width} 30 }}",
        f'{ind}  text_single = {{ parentanchor = vcenter|left position = {{ 10 0 }} text = "{name}" using = Font_Size_Small }}',
        f'{ind}  tooltip = "{name}_tt"',
        f"{ind}  enabled = \"[GetScriptedGui( '{name}' ).IsValid( {R} )]\"",
        f"{ind}  onclick = \"[GetScriptedGui( '{name}' ).Execute( {R} )]\"",
        f"{ind}}}",
    ]


# Fixed-size buttons in a czrow: name prefix -> (width, label key, tooltip key).
CZ_FIXED = {
    "pow": (58, "UCM_CROZIER_CHEATS_POW_{}", "UCM_CROZIER_CHEATS_POW_TT"),
    "tier": (78, "UCM_CROZIER_CHEATS_TIER_{}", "UCM_CROZIER_CHEATS_TIER_TT"),
}
CZ_ALL = {"pon_char_self": "ALLON", "poff_char_self": "ALLOFF"}


def _cz_button(sg, text, tooltip, label_width, scope=R, size="layoutpolicy_horizontal = expanding size = { 0 28 }", attrs="", fx=""):
    fx_label = f' text_single = {{ parentanchor = vcenter|right position = {{ -10 0 }} text = "{fx}" using = Font_Size_Small default_format = "#high" }}' if fx else ""
    return (f'button_standard = {{ {size}{attrs} tooltip = "{tooltip}" onclick = "[GetScriptedGui( ' + repr(sg) + f' ).Execute( {scope} )]" '
            f'text_single = {{ parentanchor = vcenter|left position = {{ 10 0 }} text = "{text}" max_width = {label_width} fontsize_min = 9 using = Font_Size_Small }}{fx_label} }}')


def crozier_buttons(name, ind):
    """The button(s) for scripted GUI ucm_crozier_cheats_sg_<name>; see gen_ucm_crozier.py for the naming."""
    sg = f"ucm_crozier_cheats_sg_{name}"
    kind, _, rest = name.partition("_")
    if kind == "tog" and rest in gen_ucm_crozier.TOGGLES:
        st = f"GetScriptedGui( 'ucm_crozier_cheats_sg_st_{rest}' ).IsShown( {R} )"
        key = f"UCM_CROZIER_CHEATS_B_{rest}"
        levelled = rest in gen_ucm_crozier.LEVELLED
        out = [
            _cz_button(sg, f"{key}_ON", f"{key}_TT", 376 if levelled else 430, attrs=f' visible = "[And( Not( GameHasMultiplePlayers ), {st} )]" down = yes',
                       fx=f"UCM_CROZIER_CHEATS_FX_{rest}" if levelled else ""),
            _cz_button(sg, f"{key}_OFF", f"{key}_TT", 430, attrs=f' visible = "[And( Not( GameHasMultiplePlayers ), Not( {st} ) )]"'),
        ]
    elif kind in CZ_FIXED and rest.isdigit():
        width, text, tooltip = CZ_FIXED[kind]
        out = [_cz_button(sg, text.format(rest), tooltip, width - 16, size=f"size = {{ {width} 26 }}", attrs=f" down = \"[GetScriptedGui( '{sg}' ).IsShown( {R} )]\"")]
    elif name in CZ_ALL:
        key = f"UCM_CROZIER_CHEATS_PANEL_{CZ_ALL[name]}"
        out = [_cz_button(sg, key, f"{key}_TT", 184, size="size = { 200 26 }")]
    elif name == "do_toasts_toggle" or (kind == "do" and name in gen_ucm_crozier.ACTIONS):
        key = f"UCM_CROZIER_CHEATS_B_{rest}"
        out = [_cz_button(sg, key, f"{key}_TT", 430)]
    elif kind == "t" and name in gen_ucm_crozier.ACTIONS:
        key = f"UCM_CROZIER_CHEATS_B_{rest}"
        scope = R.replace(".End", f".AddScope( 'ucm_crozier_cheats_char', {C}.MakeScope ).End")
        out = [_cz_button(sg, key, f"{key}_TT", 460, scope=scope, attrs=f" enabled = \"[GetScriptedGui( '{sg}' ).IsValid( {scope} )]\"")]
    else:
        raise ValueError(f"no Crozier button for {name}")
    return [ind + b for b in out]


def item(it, ind):
    if it[0] == "vs":
        return [f"{ind}button_standard = {{", f"{ind}  layoutpolicy_horizontal = expanding", f"{ind}  size = {{ 0 30 }}", f'{ind}  text = "{it[2]}"',
                f"{ind}  down = \"[GetVariableSystem.Exists( '{it[1]}' )]\"", f"{ind}  onclick = \"[GetVariableSystem.Toggle( '{it[1]}' )]\"", f"{ind}}}"]
    if it[0] == "togglerow":
        lines = [f"{ind}hbox = {{", f"{ind}  layoutpolicy_horizontal = expanding", f"{ind}  spacing = 4"]
        for name, flag in it[1]:
            b = sgui_button(name, ind + "  ")
            b.insert(1, f"{ind}    down = \"[GetPlayer.MakeScope.HasFlag('{flag}')]\"")
            lines += b
        return lines + [f"{ind}}}"]
    if it[0] == "cz":
        return crozier_buttons(it[1], ind)
    if it[0] == "picks":
        # Rows of 3: a flowcontainer doesn't wrap, and one long row widens the whole pane past the window.
        lines = []
        for i in range(0, len(it[1]), 3):
            lines += [f"{ind}hbox = {{", f"{ind}  layoutpolicy_horizontal = expanding", f"{ind}  spacing = 4"]
            for g in it[1][i:i + 3]:
                lines += [
                    f"{ind}  button_standard = {{",
                    f"{ind}    layoutpolicy_horizontal = expanding",
                    f"{ind}    size = {{ 0 28 }}",
                    f'{ind}    text = "ucm_group_pick_{g}"',
                    f'{ind}    tooltip = "ucm_group_pick_{g}_tt"',
                    f"{ind}    down = \"[ObjectsEqual( GetPlayer.MakeScope.Var( 'ucm_group_pick' ).GetFlagName, '{g}' )]\"",
                    f"{ind}    onclick = \"[GetScriptedGui( 'ucm_group_pick_{g}' ).Execute( {R} )]\"",
                    f"{ind}  }}",
                ]
            lines.append(f"{ind}}}")
        return lines
    if it[0] == "czrow":
        lines = [f"{ind}hbox = {{", f"{ind}  spacing = 2"]
        if len(it) > 2:
            lines.append(f'{ind}  text_single = {{ text = "{it[2]}" using = Font_Size_Small }}')
        for name in it[1]:
            lines += crozier_buttons(name, ind + "  ")
        return lines + [f"{ind}  expand = {{}}", f"{ind}}}"]
    kind = it[0]
    if kind == "h":
        return [f'{ind}text_single = {{ layoutpolicy_horizontal = expanding text = "{it[1]}" using = Font_Size_Medium default_format = "#high" }}']
    if kind == "t":
        return [f'{ind}text_multi = {{ layoutpolicy_horizontal = expanding autoresize = yes max_width = 560 text = "{it[1]}" default_format = "#low" }}']
    if kind == "sg":
        return sgui_button(it[1], ind)
    if kind == "row":
        lines = [f"{ind}hbox = {{", f"{ind}  layoutpolicy_horizontal = expanding", f"{ind}  spacing = 4"]
        for name in it[1]:
            lines += sgui_button(name, ind + "  ")
        return lines + [f"{ind}}}"]
    if kind == "ia":
        k = it[1]
        return [
            f"{ind}button_standard = {{",
            f"{ind}  layoutpolicy_horizontal = expanding",
            f"{ind}  size = {{ 0 30 }}",
            f"{ind}  visible = \"[{C}.IsPlayerInteractionShown( '{k}' )]\"",
            f"{ind}  enabled = \"[{C}.IsPlayerInteractionValid( '{k}' )]\"",
            f"{ind}  text = \"[{C}.GetPlayerInteractionName( '{k}' )]\"",
            f"{ind}  tooltip = \"[{C}.GetPlayerInteractionTooltip( '{k}' )]\"",
            f"{ind}  onclick = \"[{C}.OpenPlayerInteraction( '{k}' )]\"",
            f"{ind}}}",
        ]
    if kind == "dec":
        return [
            f"{ind}button_standard = {{",
            f"{ind}  layoutpolicy_horizontal = expanding",
            f"{ind}  size = {{ 0 30 }}",
            f"{ind}  datacontext = \"[GetDecisionWithKey( '{it[1]}' )]\"",
            f"{ind}  visible = \"[GetDecisionWithKey( '{it[1]}' ).IsShownForPlayer]\"",  # spelled out: grid() lifts it onto the row, outside this datacontext
            f'{ind}  text = "[Decision.GetTitleForPlayer]"',
            f'{ind}  tooltip = "[Decision.GetShortDescForPlayer]"',
            f"{ind}  onclick = \"[OpenGameViewData( 'decision_detail', Decision.Self )]\"",
            f"{ind}}}",
        ]
    if kind == "steps":
        lines = [f"{ind}hbox = {{", f"{ind}  layoutpolicy_horizontal = expanding", f"{ind}  spacing = 4",
                 f'{ind}  text_single = {{ text = "UCM_STEP_LABEL" }}']
        for n in (1, 5, 10, 25, 100):
            lines += sgui_button(f"ucm_step_{n}", ind + "  ", "56", expand=False)
        return lines + [f"{ind}  expand = {{}}", f"{ind}}}"]
    if kind == "value":
        _, label, value, sg = it
        return [
            f"{ind}hbox = {{",
            f"{ind}  layoutpolicy_horizontal = expanding",
            f"{ind}  spacing = 4",
            f'{ind}  text_single = {{ size = {{ 140 30 }} text = "{label}" }}',
            f"{ind}  text_single = {{ size = {{ 50 30 }} raw_text = \"[{value}]\" default_format = \"#high\" }}",
            *sgui_button(f"{sg}_down", ind + "  ", "56", expand=False),
            *sgui_button(f"{sg}_up", ind + "  ", "56", expand=False),
            f"{ind}  expand = {{}}",
            f"{ind}}}",
        ]
    if kind == "skill":
        s = it[1]
        return [
            f"{ind}hbox = {{",
            f"{ind}  layoutpolicy_horizontal = expanding",
            f"{ind}  spacing = 4",
            f'{ind}  text_single = {{ size = {{ 140 30 }} text = "UCM_SKILL_{s.upper()}" }}',
            f"{ind}  text_single = {{ size = {{ 50 30 }} raw_text = \"[{C}.GetSkill( '{s}' )]\" default_format = \"#high\" }}",
            *sgui_button(f"ucm_skill_{s}_down", ind + "  ", "56", expand=False),
            *sgui_button(f"ucm_skill_{s}_up", ind + "  ", "56", expand=False),
            f"{ind}  expand = {{}}",
            f"{ind}}}",
        ]
    raise ValueError(it)


GRID_KINDS = ("sg", "ia", "dec")


def _split_visible(lines):
    """Pull a button's `visible = "[...]"` line out; returns (lines without it, condition or None)."""
    for l in lines:
        if l.strip().startswith("visible = "):
            return [x for x in lines if x is not l], l.strip()[len('visible = "['):-len(']"')]
    return lines, None


def grid(run, ind):
    """Lay a run of plain buttons out two per row. Rows are fixed pairs (flowcontainer doesn't
    wrap). An hbox holding a hidden button lays out wrong in game (its partner collapses), so the
    visibility moves onto the rows: each pair becomes up to three rows (both / left only / right
    only), and every row holds only buttons that are showing."""
    lines = []

    def row(cond, buttons):
        out = [f"{ind}hbox = {{", f"{ind}  layoutpolicy_horizontal = expanding", f"{ind}  spacing = 4"]
        if cond:
            out.append(f'{ind}  visible = "[{cond}]"')
        for b in buttons:
            out += b
        return out + [f"{ind}}}"]

    for i in range(0, len(run), 2):
        pair = [_split_visible(item(it, ind + "  ")) for it in run[i:i + 2]]
        if len(pair) == 1:
            lines += row(pair[0][1], [pair[0][0]])
            continue
        (a, va), (b, vb) = pair
        if va is None and vb is None:
            lines += row(None, [a, b])
            continue
        both = " ".join(filter(None, [va, vb]))
        lines += row(f"And( {va}, {vb} )" if va and vb else both, [a, b])
        if va:  # right only
            lines += row(f"And( Not( {va} ), {vb} )" if vb else f"Not( {va} )", [b])
        if vb:  # left only
            lines += row(f"And( {va}, Not( {vb} ) )" if va else f"Not( {vb} )", [a])
    return lines


def section(items, ind):
    out, run = [], []
    for it in items + [None]:
        if it is not None and it[0] in GRID_KINDS:
            run.append(it)
            continue
        if run:
            out += grid(run, ind)
            run = []
        if it is not None:
            out += item(it, ind)
    return out


def main():
    o = [
        "# AUTO-GENERATED by tools/gen_ucm_main_menu.py; edit TABS there, not this file.",
        "# Unified Cheat Menu main menu (spec Section 2, Layer 2), opened by the ucm_open_cheat_menu interaction.",
        "# Tabs are GUI-only state (GetVariableSystem 'ucm_tab').",
        "window = {",
        '  name = "ucm_main_menu_window"',
        "  parentanchor = center",
        "  size = { 880 680 }",
        "  layer = top",
        "  movable = yes",
        "  alwaystransparent = no",
        "  filter_mouse = all",
        f"  visible = \"[GetScriptedGui( 'ucm_menu_visible' ).IsShown( {R} )]\"",
        "",
        "  widget = {",
        "    size = { 100% 100% }",
        "    background = { using = Background_Area_Dark alpha = 1.0 }",
        "  }",
        "",
        "  vbox = {",
        "    using = Window_Margins",
        "    layoutpolicy_horizontal = expanding",
        "    layoutpolicy_vertical = expanding",
        "    spacing = 8",
        "",
        "    header_pattern = {",
        "      layoutpolicy_horizontal = expanding",
        '      blockoverride "header_text" { text = "UCM_MENU_TITLE" }',
        f"      blockoverride \"button_close\" {{ onclick = \"[GetScriptedGui( 'ucm_menu_close' ).Execute( {R} )]\" }}",
        "    }",
        "",
        '    text_single = { layoutpolicy_horizontal = expanding text = "UCM_MENU_TARGET" }',
        "    text_single = {",
        "      layoutpolicy_horizontal = expanding",
        "      visible = \"[GetGlobalVariable( 'ucm_crozier_cheats_other' ).IsSet]\"",
        '      text = "UCM_MENU_SECOND"',
        "    }",
        "    text_single = {",
        "      layoutpolicy_horizontal = expanding",
        "      visible = \"[Not( GetGlobalVariable( 'ucm_crozier_cheats_other' ).IsSet )]\"",
        '      text = "UCM_MENU_SECOND_NONE"',
        '      default_format = "#low"',
        "    }",
        "",
        "    hbox = {",
        "      layoutpolicy_horizontal = expanding",
        "      layoutpolicy_vertical = expanding",
        "      spacing = 12",
        "",
        "      # Category tabs",
        "      vbox = {",
        "        layoutpolicy_vertical = expanding",
        "        spacing = 4",
    ]
    for t, _ in TABS:
        o += [
            "        button_standard = {",
            "          size = { 220 34 }",
            f'          text = "UCM_TAB_{t.upper()}"',
            *([f"          visible = \"[GetScriptedGui( '{TAB_GATES[t]}' ).IsShown( {R} )]\""] if t in TAB_GATES else []),
            f'          down = "{tab_shown(t)}"',
            f"          onclick = \"[GetVariableSystem.Set( 'ucm_tab', '{t}' )]\"",
            "        }",
        ]
    o += ["        expand = {}", "      }", "", "      # Category contents"]
    for t, items in TABS:
        o += [
            "      scrollbox = {",
            "        size = { 600 540 }",
            f'        visible = "{tab_shown(t)}"' if t not in TAB_GATES else
            f"        visible = \"[And( {tab_shown(t)[1:-1]}, GetScriptedGui( '{TAB_GATES[t]}' ).IsShown( {R} ) )]\"",
            '        blockoverride "scrollbox_content" {',
            "          vbox = {",
            "            layoutpolicy_horizontal = expanding",
            "            spacing = 4",
            f'            text_single = {{ layoutpolicy_horizontal = expanding text = "UCM_TAB_{t.upper()}" using = Font_Size_Big default_format = "#high" }}',
        ]
        o += section(items, "            ")
        o += ["          }", "        }", "      }"]
    o += ["    }", "  }", "}"]
    with open(OUT, "wb") as fh:
        fh.write(b"\xef\xbb\xbf" + ("\r\n".join(o) + "\r\n").encode("utf-8"))
    print(f"{sum(len(i) for _, i in TABS)} items -> {os.path.relpath(OUT, MOD_DIR)}")


if __name__ == "__main__":
    main()
