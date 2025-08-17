package com.questhelper.helpers.playerguide;

import net.runelite.api.ItemID;
import net.runelite.api.NpcID;
import net.runelite.api.ObjectID;
import net.runelite.api.coords.WorldPoint;
import com.questhelper.BasicQuestHelper;
import com.questhelper.QuestStep;
import com.questhelper.steps.*;
import com.questhelper.requirements.*;
import com.questhelper.requirements.item.ItemRequirement;
import com.questhelper.requirements.item.ItemRequirements;
import com.questhelper.panel.PanelDetails;
import com.questhelper.requirements.util.*;
import com.questhelper.ItemCollections;
import java.util.*;

public class QuestFromWiki extends BasicQuestHelper {
    // Item Requirements
    ItemRequirement logs_3x;

    // Step Fields
    QuestStep step_all_settings__disable_levelup_0;
    QuestStep step_talk_to_father_aereck_31_restless_ghost_1;
    QuestStep step_pickpocket_a_manwoman_lumbridge_easy_diary_2;
    QuestStep step_head_northwest_to_magic_combat_tutor_and_drop_air_and_mind_runes_and_claim_more_3;
    QuestStep step_sell_bronze_dagger_sword_wooden_shield_and_shortbow_to_general_store_buy_a_spade_chisel_and_hammer_4;
    QuestStep step_head_east_and_start_x_marks_the_spot_on_veos_21_and_complete_the_first_step_install_quest_helper_plug_in_on_runelite_5;
    QuestStep step_check_playtime_on_hans_lumbridge_easy_diary_6;
    QuestStep step_go_upstairs_and_talk_to_duke_horacio_11_rune_mysteries_7;
    QuestStep step_go_upstairs_again_and_collect_4x_logs_on_the_top_floor_tree_gnome_village_8;
    QuestStep step_bank_at_lumbridge_castle_top_floor_and_deposit_all_9;
    QuestStep step_keep_the_shrimps_in_your_bank_for_later_family_crest_quest_10;
    QuestStep step_move_coins_into_first_bank_slot_and_runes_to_the_top_slots_11;
    QuestStep step_click_the_lock_to_always_set_placeholders_12;
    QuestStep step_set_bank_pin_for_count_check_randoms_or_delete_the_pin_from_tutorial_island_13;
    QuestStep step_withdraw_coins_air_runes_mind_runes_bread_spade_tinderbox_air_talisman_treasure_scroll_8_inventory_slots_14;
    QuestStep step_go_down_south_staircase_twice_15;
    QuestStep step_collect_the_empty_jug_bowl_and_knife_in_lumbridge_kitchen_16;
    QuestStep step_fill_the_jug_and_bowl_on_the_sink_in_the_kitchen_monks_friend_17;
    QuestStep step_complete_2nd_step_of_x_marks_the_spot_18;
    QuestStep step_kill_a_giant_rat_with_wind_strike_and_collect_the_bones__raw_rat_meat_druidic_ritual_19;
    QuestStep step_head_west_towards_draynor_hugging_the_fence_to_avoid_the_jail_guards_20;
    QuestStep step_talk_to_father_urhney_in_the_lumbridge_swamp_for_ghost_speak_amulet_21_wield_this_21;
    QuestStep step_take_leather_gloves_on_the_table_inside_his_house_and_wield_22;
    QuestStep step_head_to_the_wizards_tower_23;
    QuestStep step_take_leather_boots_off_the_table_and_wield_24;
    QuestStep step_collect_3x_logs_next_to_the_stairs_tree_gnome_village_25;
    QuestStep step_head_to_the_basement_and_talk_to_sedridor_to_continue_rune_mysteries_121_26;
    QuestStep step_kill_a_chicken_take_everything_make_sure_you_get_a_feather_else_hop_worlds_and_repeatclient_of_kourend__druidic_ritual_27;
    QuestStep step_collect_3x_logs_tree_gnome_village_28;
    QuestStep step_return_to_draynor_and_talk_to_friendly_forester_and_obtain_forestry_kit_right_click_shop_and_buy_1_29;
    QuestStep step_bank_at_draynor_and_deposit_all_30;

    @Override
    public void setupRequirements()
    {
        logs_3x = new ItemRequirement("Logs", ItemID.LOGS, 3);
    }

    @Override
    public void setupSteps()
    {
        step_all_settings__disable_levelup_0 = new DetailedQuestStep(this, "All Settings -> Disable level-up");
        step_talk_to_father_aereck_31_restless_ghost_1 = new NpcStep(this, NpcID.FATHER_AERECK_2812, new WorldPoint(3243, 3206, 0), "Talk to [[Father Aereck]] (3,1) [Restless Ghost]");
        step_talk_to_father_aereck_31_restless_ghost_1.addDialogSteps("3", "1");
        step_pickpocket_a_manwoman_lumbridge_easy_diary_2 = new DetailedQuestStep(this, "Pickpocket a man/woman [Lumbridge Easy Diary]");
        step_head_northwest_to_magic_combat_tutor_and_drop_air_and_mind_runes_and_claim_more_3 = new DetailedQuestStep(this, "Head North-West to [[Magic combat tutor]] & drop Air & Mind Runes and claim more.");
        step_sell_bronze_dagger_sword_wooden_shield_and_shortbow_to_general_store_buy_a_spade_chisel_and_hammer_4 = new DetailedQuestStep(this, "Sell Bronze Dagger, Sword, Wooden Shield & Shortbow to General Store. Buy a Spade Chisel & hammer");
        step_head_east_and_start_x_marks_the_spot_on_veos_21_and_complete_the_first_step_install_quest_helper_plug_in_on_runelite_5 = new DetailedQuestStep(this, "Head East & Start X Marks the Spot on Veos (2,1) & complete the first step (Install Quest Helper plug in on Runelite)");
        step_check_playtime_on_hans_lumbridge_easy_diary_6 = new ObjectStep(this, ObjectID.UNKNOWN_0, new WorldPoint(3215, 3219, 0), "Check playtime on [[Hans]] [Lumbridge Easy Diary]");
        step_go_upstairs_and_talk_to_duke_horacio_11_rune_mysteries_7 = new DetailedQuestStep(this, "Go upstairs and Talk to [[Duke Horacio]] (1,1) [Rune Mysteries]");
        step_go_upstairs_again_and_collect_4x_logs_on_the_top_floor_tree_gnome_village_8 = new DetailedQuestStep(this, "Go upstairs again and Collect 4x logs on the top floor [Tree Gnome Village]");
        step_bank_at_lumbridge_castle_top_floor_and_deposit_all_9 = new DetailedQuestStep(this, "Bank at Lumbridge castle top floor and deposit all");
        step_keep_the_shrimps_in_your_bank_for_later_family_crest_quest_10 = new DetailedQuestStep(this, "Keep the Shrimps in your bank for later [Family Crest Quest]");
        step_move_coins_into_first_bank_slot_and_runes_to_the_top_slots_11 = new DetailedQuestStep(this, "Move Coins into first bank slot & Runes to the top slots.");
        step_click_the_lock_to_always_set_placeholders_12 = new DetailedQuestStep(this, "Click the lock to Always set Placeholders.");
        step_set_bank_pin_for_count_check_randoms_or_delete_the_pin_from_tutorial_island_13 = new DetailedQuestStep(this, "Set Bank pin for Count Check randoms or delete the pin from Tutorial Island.");
        step_withdraw_coins_air_runes_mind_runes_bread_spade_tinderbox_air_talisman_treasure_scroll_8_inventory_slots_14 = new DetailedQuestStep(this, "Withdraw: Coins, Air Runes, Mind Runes, Bread, Spade, Tinderbox, Air Talisman, Treasure Scroll (8 Inventory slots)");
        step_go_down_south_staircase_twice_15 = new DetailedQuestStep(this, "Go down south staircase twice");
        step_collect_the_empty_jug_bowl_and_knife_in_lumbridge_kitchen_16 = new DetailedQuestStep(this, "Collect the Empty Jug, Bowl & Knife in Lumbridge kitchen");
        step_fill_the_jug_and_bowl_on_the_sink_in_the_kitchen_monks_friend_17 = new DetailedQuestStep(this, "Fill the jug & bowl on the sink in the kitchen [Monk's Friend]");
        step_complete_2nd_step_of_x_marks_the_spot_18 = new DetailedQuestStep(this, "Complete 2nd Step of X Marks The Spot");
        step_kill_a_giant_rat_with_wind_strike_and_collect_the_bones__raw_rat_meat_druidic_ritual_19 = new DetailedQuestStep(this, "Kill a giant rat with Wind Strike and collect the Bones + Raw Rat Meat [Druidic Ritual]");
        step_head_west_towards_draynor_hugging_the_fence_to_avoid_the_jail_guards_20 = new DetailedQuestStep(this, "Head West towards Draynor hugging the fence to avoid the Jail Guards");
        step_talk_to_father_urhney_in_the_lumbridge_swamp_for_ghost_speak_amulet_21_wield_this_21 = new NpcStep(this, NpcID.FATHER_URHNEY_923, new WorldPoint(3147, 3175, 0), "Talk to [[Father Urhney]] in the lumbridge swamp for Ghost Speak Amulet. (2,1) Wield this.");
        step_take_leather_gloves_on_the_table_inside_his_house_and_wield_22 = new ObjectStep(this, ObjectID.UNKNOWN_0, null, "Take Leather Gloves on the table inside his house & wield");
        step_head_to_the_wizards_tower_23 = new DetailedQuestStep(this, "Head to the Wizards Tower");
        step_take_leather_boots_off_the_table_and_wield_24 = new ObjectStep(this, ObjectID.TABLE_41880, null, "Take Leather Boots off the table & wield");
        step_collect_3x_logs_next_to_the_stairs_tree_gnome_village_25 = new DetailedQuestStep(this, "Collect 3x Logs next to the stairs [Tree Gnome Village]");
        step_head_to_the_basement_and_talk_to_sedridor_to_continue_rune_mysteries_121_26 = new DetailedQuestStep(this, "Head to the basement & Talk to [[Sedridor]] to continue Rune Mysteries (1,2,1)");
        step_kill_a_chicken_take_everything_make_sure_you_get_a_feather_else_hop_worlds_and_repeatclient_of_kourend__druidic_ritual_27 = new DetailedQuestStep(this, "Kill a Chicken. Take Everything (Make sure you get a feather, else hop worlds and repeat)[Client of Kourend + Druidic Ritual]");
        step_collect_3x_logs_tree_gnome_village_28 = new DetailedQuestStep(this, "Collect 3x Logs [Tree Gnome Village]");
        // World points for Friendly Forester (ID 6724) need to be manually added in QuestFromWiki.java
        step_return_to_draynor_and_talk_to_friendly_forester_and_obtain_forestry_kit_right_click_shop_and_buy_1_29 = new NpcStep(this, NpcID.FRIENDLY_FORESTER_6724, null, "Return to Draynor & talk to [[Friendly Forester]] and obtain Forestry kit (right click shop and buy 1)");
        step_bank_at_draynor_and_deposit_all_30 = new DetailedQuestStep(this, "Bank at Draynor and Deposit all");
    }

    @Override
    public Map<Integer, QuestStep> loadSteps()
    {
        Map<Integer, QuestStep> steps = new HashMap<>();
        int idx = 0;
        steps.put(idx++, step_all_settings__disable_levelup_0);
        steps.put(idx++, step_talk_to_father_aereck_31_restless_ghost_1);
        steps.put(idx++, step_pickpocket_a_manwoman_lumbridge_easy_diary_2);
        steps.put(idx++, step_head_northwest_to_magic_combat_tutor_and_drop_air_and_mind_runes_and_claim_more_3);
        steps.put(idx++, step_sell_bronze_dagger_sword_wooden_shield_and_shortbow_to_general_store_buy_a_spade_chisel_and_hammer_4);
        steps.put(idx++, step_head_east_and_start_x_marks_the_spot_on_veos_21_and_complete_the_first_step_install_quest_helper_plug_in_on_runelite_5);
        steps.put(idx++, step_check_playtime_on_hans_lumbridge_easy_diary_6);
        steps.put(idx++, step_go_upstairs_and_talk_to_duke_horacio_11_rune_mysteries_7);
        steps.put(idx++, step_go_upstairs_again_and_collect_4x_logs_on_the_top_floor_tree_gnome_village_8);
        steps.put(idx++, step_bank_at_lumbridge_castle_top_floor_and_deposit_all_9);
        steps.put(idx++, step_keep_the_shrimps_in_your_bank_for_later_family_crest_quest_10);
        steps.put(idx++, step_move_coins_into_first_bank_slot_and_runes_to_the_top_slots_11);
        steps.put(idx++, step_click_the_lock_to_always_set_placeholders_12);
        steps.put(idx++, step_set_bank_pin_for_count_check_randoms_or_delete_the_pin_from_tutorial_island_13);
        steps.put(idx++, step_withdraw_coins_air_runes_mind_runes_bread_spade_tinderbox_air_talisman_treasure_scroll_8_inventory_slots_14);
        steps.put(idx++, step_go_down_south_staircase_twice_15);
        steps.put(idx++, step_collect_the_empty_jug_bowl_and_knife_in_lumbridge_kitchen_16);
        steps.put(idx++, step_fill_the_jug_and_bowl_on_the_sink_in_the_kitchen_monks_friend_17);
        steps.put(idx++, step_complete_2nd_step_of_x_marks_the_spot_18);
        steps.put(idx++, step_kill_a_giant_rat_with_wind_strike_and_collect_the_bones__raw_rat_meat_druidic_ritual_19);
        steps.put(idx++, step_head_west_towards_draynor_hugging_the_fence_to_avoid_the_jail_guards_20);
        steps.put(idx++, step_talk_to_father_urhney_in_the_lumbridge_swamp_for_ghost_speak_amulet_21_wield_this_21);
        steps.put(idx++, step_take_leather_gloves_on_the_table_inside_his_house_and_wield_22);
        steps.put(idx++, step_head_to_the_wizards_tower_23);
        steps.put(idx++, step_take_leather_boots_off_the_table_and_wield_24);
        steps.put(idx++, step_collect_3x_logs_next_to_the_stairs_tree_gnome_village_25);
        steps.put(idx++, step_head_to_the_basement_and_talk_to_sedridor_to_continue_rune_mysteries_121_26);
        steps.put(idx++, step_kill_a_chicken_take_everything_make_sure_you_get_a_feather_else_hop_worlds_and_repeatclient_of_kourend__druidic_ritual_27);
        steps.put(idx++, step_collect_3x_logs_tree_gnome_village_28);
        steps.put(idx++, step_return_to_draynor_and_talk_to_friendly_forester_and_obtain_forestry_kit_right_click_shop_and_buy_1_29);
        steps.put(idx++, step_bank_at_draynor_and_deposit_all_30);
        return steps;
    }

    @Override
    public List<PanelDetails> getPanels()
    {
        List<PanelDetails> panels = new ArrayList<>();
        PanelDetails panel_starting_out = new PanelDetails("Starting out", Arrays.asList(step_all_settings__disable_levelup_0, step_talk_to_father_aereck_31_restless_ghost_1, step_pickpocket_a_manwoman_lumbridge_easy_diary_2, step_head_northwest_to_magic_combat_tutor_and_drop_air_and_mind_runes_and_claim_more_3, step_sell_bronze_dagger_sword_wooden_shield_and_shortbow_to_general_store_buy_a_spade_chisel_and_hammer_4, step_head_east_and_start_x_marks_the_spot_on_veos_21_and_complete_the_first_step_install_quest_helper_plug_in_on_runelite_5, step_check_playtime_on_hans_lumbridge_easy_diary_6, step_go_upstairs_and_talk_to_duke_horacio_11_rune_mysteries_7, step_go_upstairs_again_and_collect_4x_logs_on_the_top_floor_tree_gnome_village_8, step_click_the_lock_to_always_set_placeholders_12, step_go_down_south_staircase_twice_15, step_collect_the_empty_jug_bowl_and_knife_in_lumbridge_kitchen_16, step_fill_the_jug_and_bowl_on_the_sink_in_the_kitchen_monks_friend_17, step_complete_2nd_step_of_x_marks_the_spot_18, step_head_west_towards_draynor_hugging_the_fence_to_avoid_the_jail_guards_20, step_talk_to_father_urhney_in_the_lumbridge_swamp_for_ghost_speak_amulet_21_wield_this_21, step_take_leather_gloves_on_the_table_inside_his_house_and_wield_22, step_head_to_the_wizards_tower_23, step_take_leather_boots_off_the_table_and_wield_24, step_collect_3x_logs_next_to_the_stairs_tree_gnome_village_25, step_head_to_the_basement_and_talk_to_sedridor_to_continue_rune_mysteries_121_26, step_collect_3x_logs_tree_gnome_village_28, step_return_to_draynor_and_talk_to_friendly_forester_and_obtain_forestry_kit_right_click_shop_and_buy_1_29));
        panels.add(panel_starting_out);
        PanelDetails panel_bank_1 = new PanelDetails("Bank 1", Arrays.asList(step_bank_at_lumbridge_castle_top_floor_and_deposit_all_9, step_keep_the_shrimps_in_your_bank_for_later_family_crest_quest_10, step_move_coins_into_first_bank_slot_and_runes_to_the_top_slots_11, step_set_bank_pin_for_count_check_randoms_or_delete_the_pin_from_tutorial_island_13, step_withdraw_coins_air_runes_mind_runes_bread_spade_tinderbox_air_talisman_treasure_scroll_8_inventory_slots_14, step_kill_a_giant_rat_with_wind_strike_and_collect_the_bones__raw_rat_meat_druidic_ritual_19, step_kill_a_chicken_take_everything_make_sure_you_get_a_feather_else_hop_worlds_and_repeatclient_of_kourend__druidic_ritual_27, step_bank_at_draynor_and_deposit_all_30));
        panels.add(panel_bank_1);
        return panels;
    }

    @Override
    public void setupZones()
    {
        // Define zones if needed
    }

    @Override
    public void setupConditions()
    {
        // Define conditions if needed
    }
}