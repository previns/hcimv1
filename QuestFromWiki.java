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

    // === Step Fields ===
    QuestStep step_all_settings__0;
    QuestStep npc_father_aereck_1;
    QuestStep npc_woman_2;
    QuestStep npc_drop_3;
    QuestStep item_buy_4;
    QuestStep step_head_5;
    QuestStep npc_hans_6;
    QuestStep npc_duke_horacio_7;
    QuestStep step_collect_8;
    QuestStep step_bank_9;
    QuestStep step_bank_10;
    QuestStep step_click_11;
    QuestStep item_run_12;
    QuestStep step_go_13;
    QuestStep item_empty_14;
    QuestStep obj_jug_15;
    QuestStep step_complete_2nd_step_16;
    QuestStep npc_kill_17;
    QuestStep step_head_18;
    QuestStep npc_father_urhney_19;
    QuestStep item_use_20;
    QuestStep move_head_21;
    QuestStep item_take_22;
    QuestStep item_collect_23;
    QuestStep move_talk_24;
    QuestStep npc_kill_25;
    QuestStep item_collect_26;
    QuestStep npc_talk_27;
    QuestStep step_bank_28;
    QuestStep item_withdraw_29;
    QuestStep item_collect_30;
    QuestStep step_complete_3rd_step_31;
    QuestStep npc_morgan_32;
    QuestStep step_collect_33;
    QuestStep step_click_34;
    QuestStep step_train_draynor_agility_35;
    QuestStep step_bank_36;
    QuestStep npc_fortunato_37;
    QuestStep npc_start_38;
    QuestStep step_complete_4th_step_39;
    QuestStep npc_veos_40;
    QuestStep item_collect_41;
    QuestStep move_travel_42;
    QuestStep npc_veos_43;
    QuestStep item_mine_44;
    QuestStep obj_open_45;
    QuestStep item_take_46;
    QuestStep item_use_47;
    QuestStep npc_talk_48;
    QuestStep item_take_49;
    QuestStep item_use_50;
    QuestStep npc_robin_51;
    QuestStep step_teleport_52;
    QuestStep npc_bob_53;
    QuestStep npc_restless_ghost_54;
    QuestStep npc_count_check_55;
    QuestStep step_complete_3_floors_56;
    QuestStep step_take_57;
    QuestStep npc_catablepon_58;
    QuestStep step_once_you_have_59;
    QuestStep item_collect_60;
    QuestStep item_collect_61;
    QuestStep npc_gertrude_62;
    QuestStep item_collect_63;
    QuestStep step_bank_64;

    // === Item Requirements ===
    ItemRequirement step_run_0;
    ItemRequirement step_air_talisman_1;
    ItemRequirement step_beer_2;
    ItemRequirement step_boots_of_the_3;
    ItemRequirement step_bread_4;
    ItemRequirement step_bronze_daggerunp_5;
    ItemRequirement step_cheese_6;
    ItemRequirement step_chisel_7;
    ItemRequirement step_clue_scroll_beginner_8;
    ItemRequirement step_coins_9;
    ItemRequirement step_cooked_meat_10;
    ItemRequirement step_empty_11;
    ItemRequirement step_feather_12;
    ItemRequirement step_lamp_13;
    ItemRequirement step_logs_14;
    ItemRequirement step_run_15;
    ItemRequirement step_mysterious_herb_16;
    ItemRequirement step_spade_17;
    ItemRequirement step_tinderbox_18;
    ItemRequirement step_wizard_hat_19;

    @Override
    public Map<Integer, QuestStep> loadSteps()
    {
        Map<Integer, QuestStep> steps = new HashMap<>();
        int idx = 0;

        steps.put(idx++, step_all_settings__0);
        steps.put(idx++, npc_father_aereck_1);
        steps.put(idx++, npc_woman_2);
        steps.put(idx++, npc_drop_3);
        steps.put(idx++, item_buy_4);
        steps.put(idx++, step_head_5);
        steps.put(idx++, npc_hans_6);
        steps.put(idx++, npc_duke_horacio_7);
        steps.put(idx++, step_collect_8);
        steps.put(idx++, step_bank_9);
        steps.put(idx++, step_bank_10);
        steps.put(idx++, step_click_11);
        steps.put(idx++, item_run_12);
        steps.put(idx++, step_go_13);
        steps.put(idx++, item_empty_14);
        steps.put(idx++, obj_jug_15);
        steps.put(idx++, step_complete_2nd_step_16);
        steps.put(idx++, npc_kill_17);
        steps.put(idx++, step_head_18);
        steps.put(idx++, npc_father_urhney_19);
        steps.put(idx++, item_use_20);
        steps.put(idx++, move_head_21);
        steps.put(idx++, item_take_22);
        steps.put(idx++, item_collect_23);
        steps.put(idx++, move_talk_24);
        steps.put(idx++, npc_kill_25);
        steps.put(idx++, item_collect_26);
        steps.put(idx++, npc_talk_27);
        steps.put(idx++, step_bank_28);
        steps.put(idx++, item_withdraw_29);
        steps.put(idx++, item_collect_30);
        steps.put(idx++, step_complete_3rd_step_31);
        steps.put(idx++, npc_morgan_32);
        steps.put(idx++, step_collect_33);
        steps.put(idx++, step_click_34);
        steps.put(idx++, step_train_draynor_agility_35);
        steps.put(idx++, step_bank_36);
        steps.put(idx++, npc_fortunato_37);
        steps.put(idx++, npc_start_38);
        steps.put(idx++, step_complete_4th_step_39);
        steps.put(idx++, npc_veos_40);
        steps.put(idx++, item_collect_41);
        steps.put(idx++, move_travel_42);
        steps.put(idx++, npc_veos_43);
        steps.put(idx++, item_mine_44);
        steps.put(idx++, obj_open_45);
        steps.put(idx++, item_take_46);
        steps.put(idx++, item_use_47);
        steps.put(idx++, npc_talk_48);
        steps.put(idx++, item_take_49);
        steps.put(idx++, item_use_50);
        steps.put(idx++, npc_robin_51);
        steps.put(idx++, step_teleport_52);
        steps.put(idx++, npc_bob_53);
        steps.put(idx++, npc_restless_ghost_54);
        steps.put(idx++, npc_count_check_55);
        steps.put(idx++, step_complete_3_floors_56);
        steps.put(idx++, step_take_57);
        steps.put(idx++, npc_catablepon_58);
        steps.put(idx++, step_once_you_have_59);
        steps.put(idx++, item_collect_60);
        steps.put(idx++, item_collect_61);
        steps.put(idx++, npc_gertrude_62);
        steps.put(idx++, item_collect_63);
        steps.put(idx++, step_bank_64);

        return steps;
    }

    @Override
    public void setupRequirements()
    {

        step_run_0 = new ItemRequirement("Air rune", ItemID.AIR_RUNE);
        step_air_talisman_1 = new ItemRequirement("Air talisman", ItemID.AIR_TALISMAN);
        step_beer_2 = new ItemRequirement("Beer", ItemID.BEER);
        step_boots_of_the_3 = new ItemRequirement("Boots of the eye", ItemID.BOOTS_OF_THE_EYE);
        step_bread_4 = new ItemRequirement("Bread", ItemID.BREAD);
        step_bronze_daggerunp_5 = new ItemRequirement("Bronze dagger#(unp)", ItemID.BRONZE_DAGGERUNP);
        step_cheese_6 = new ItemRequirement("Cheese", ItemID.CHEESE);
        step_chisel_7 = new ItemRequirement("Chisel", ItemID.CHISEL);
        step_clue_scroll_beginner_8 = new ItemRequirement("Clue scroll (beginner)", ItemID.CLUE_SCROLL_BEGINNER);
        step_coins_9 = new ItemRequirement("Coins", ItemID.COINS);
        step_cooked_meat_10 = new ItemRequirement("Cooked meat", ItemID.COOKED_MEAT);
        step_empty_11 = new ItemRequirement("Empty jug", ItemID.EMPTY_JUG);
        step_feather_12 = new ItemRequirement("Feather", ItemID.FEATHER);
        step_lamp_13 = new ItemRequirement("Lamp", ItemID.LAMP);
        step_logs_14 = new ItemRequirement("Logs", ItemID.LOGS, 3);
        step_run_15 = new ItemRequirement("Mind rune", ItemID.MIND_RUNE);
        step_mysterious_herb_16 = new ItemRequirement("Mysterious herb", ItemID.MYSTERIOUS_HERB);
        step_spade_17 = new ItemRequirement("Spade", ItemID.SPADE);
        step_tinderbox_18 = new ItemRequirement("Tinderbox", ItemID.TINDERBOX);
        step_wizard_hat_19 = new ItemRequirement("Wizard hat", ItemID.WIZARD_HAT);
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

    @Override
    public void setupSteps()
    {

        step_all_settings__0 = new DetailedQuestStep(this, "All Settings -> Disable level-up");
        npc_father_aereck_1 = new NpcStep(this, NpcID.FATHER_AERECK, new WorldPoint(3243, 3206, 0), "Talk to");
        npc_father_aereck_1.addDialogSteps("3", "1");
        npc_woman_2 = new NpcStep(this, NpcID.WOMAN, new WorldPoint(3224, 3218, 0), "Pickpocket a man/woman");
        npc_drop_3 = new DetailedQuestStep(this, "Head North-West to  & drop Air & Mind Runes and claim more.");
        item_buy_4 = new DetailedQuestStep(this, "Sell Bronze Dagger, Sword, Wooden Shield & Shortbow to General Store. Buy a Spade Chisel & hammer");
        step_head_5 = new DetailedQuestStep(this, "Head East & Start X Marks the Spot on Veos  & complete the first step (Install Quest Helper plug in on Runelite)");
        npc_hans_6 = new NpcStep(this, NpcID.HANS, new WorldPoint(3215, 3219, 0), "Check playtime on");
        npc_duke_horacio_7 = new NpcStep(this, NpcID.DUKE_HORACIO, new WorldPoint(3210, 3222, 1), "Go upstairs and Talk to");
        npc_duke_horacio_7.addDialogSteps("1", "1");
        step_collect_8 = new DetailedQuestStep(this, "Go upstairs again and Collect 4x logs on the top floor");
        step_bank_9 = new DetailedQuestStep(this, "Bank at Lumbridge castle top floor and deposit all");
        step_bank_10 = new DetailedQuestStep(this, "Keep the Shrimps in your bank for later");
        step_click_11 = new DetailedQuestStep(this, "Move Coins into first bank slot & Runes to the top slots. Click the lock to Always set Placeholders. Set Bank pin for Count Check randoms or delete the pin from Tutorial Island.");
        item_run_12 = new DetailedQuestStep(this, "Withdraw: Coins, Air Runes, Mind Runes, Bread, Spade, Tinderbox, Air Talisman, Treasure Scroll");
        step_go_13 = new DetailedQuestStep(this, "Go down south staircase twice");
        item_empty_14 = new DetailedQuestStep(this, "Collect the Empty Jug, Bowl & Knife in Lumbridge kitchen");
        obj_jug_15 = new ObjectStep(this, ObjectID.JUG, new WorldPoint(1445, 9336, 0), "Fill the jug & bowl on the sink in the kitchen");
        step_complete_2nd_step_16 = new DetailedQuestStep(this, "Complete 2nd Step of X Marks The Spot");
        npc_kill_17 = new DetailedQuestStep(this, "Kill a giant rat with Wind Strike and collect the Bones + Raw Rat Meat");
        step_head_18 = new DetailedQuestStep(this, "Head West towards Draynor hugging the fence to avoid the Jail Guards");
        npc_father_urhney_19 = new NpcStep(this, NpcID.FATHER_URHNEY, new WorldPoint(3147, 3175, 0), "Talk to  in the lumbridge swamp for Ghost Speak Amulet.  Wield this.");
        npc_father_urhney_19.addDialogSteps("2", "1");
        item_use_20 = new DetailedQuestStep(this, "Take Leather Gloves on the table inside his house & wield");
        move_head_21 = new DetailedQuestStep(this, "Head to the Wizards Tower");
        item_take_22 = new DetailedQuestStep(this, "Take Leather Boots off the table & wield");
        item_collect_23 = new DetailedQuestStep(this, "Collect 3x Logs next to the stairs");
        move_talk_24 = new DetailedQuestStep(this, "Head to the basement & Talk to  to continue Rune Mysteries");
        npc_kill_25 = new DetailedQuestStep(this, "Kill a Chicken. Take Everything (Make sure you get a feather, else hop worlds and repeat)");
        item_collect_26 = new DetailedQuestStep(this, "Collect 3x Logs");
        npc_talk_27 = new DetailedQuestStep(this, "Return to Draynor & talk to  and obtain Forestry kit (right click shop and buy 1)");
        step_bank_28 = new DetailedQuestStep(this, "Bank at Draynor and Deposit all");
        item_withdraw_29 = new DetailedQuestStep(this, "Withdraw: Coins, Spade, Feather & Mysterious Orb");
        item_collect_30 = new DetailedQuestStep(this, "Collect Cheese from");
        step_complete_3rd_step_31 = new DetailedQuestStep(this, "Complete 3rd Step of X Marks the Spot");
        npc_morgan_32 = new NpcStep(this, NpcID.MORGAN, new WorldPoint(3098, 3268, 0), "Talk to  and start Vampyre Slayer");
        npc_morgan_32.addDialogSteps("1");
        step_collect_33 = new DetailedQuestStep(this, "Go up the stairs and collect 4x Garlic from the cupboard");
        step_click_34 = new DetailedQuestStep(this, "You can get multiple garlic by spamclicking the cupboard");
        step_train_draynor_agility_35 = new DetailedQuestStep(this, "Train Draynor Agility to 5 Agility");
        step_bank_36 = new DetailedQuestStep(this, "Bank at Draynor and deposit the Garlic & cheese");
        npc_fortunato_37 = new NpcStep(this, NpcID.FORTUNATO, new WorldPoint(3085, 3251, 0), "Talk to  & buy 5 wines. Hop worlds and buy 10 in total.");
        npc_start_38 = new DetailedQuestStep(this, "Start");
        step_complete_4th_step_39 = new DetailedQuestStep(this, "Complete 4th Step of X Marks the Spot");
        npc_veos_40 = new NpcStep(this, NpcID.VEOS, new WorldPoint(3228, 3242, 0), "Head West to Port Sarim and talk to  to complete X Marks The Spot.");
        item_collect_41 = new DetailedQuestStep(this, "Destroy the lamp. You can collect this later as you can't bank it.");
        move_travel_42 = new DetailedQuestStep(this, "Travel to Port Piscarilius");
        npc_veos_43 = new NpcStep(this, NpcID.VEOS, new WorldPoint(3228, 3242, 0), "Talk to");
        npc_veos_43.addDialogSteps("4", "1");
        item_mine_44 = new DetailedQuestStep(this, "Take Minecart to Shayzien East");
        obj_open_45 = new DetailedQuestStep(this, "Open Minimap & follow the path South-West to Shayzien");
        item_take_46 = new DetailedQuestStep(this, "Take the Beer");
        item_use_47 = new DetailedQuestStep(this, "Use your feather on the enchanted scroll in your inventory");
        npc_talk_48 = new DetailedQuestStep(this, "Talk to  for Client of Kourend");
        item_take_49 = new DetailedQuestStep(this, "Take Tinderbox");
        item_use_50 = new DetailedQuestStep(this, "Take Wizard Hat & Orange Dye [Shadow of the Storm, Goblin Diplomacy] from house to the west (Shayzien Styles)");
        npc_robin_51 = new NpcStep(this, NpcID.ROBIN, new WorldPoint(3675, 3495, 0), "Trade  and buy a");
        step_teleport_52 = new DetailedQuestStep(this, "Home teleport to Lumbridge");
        npc_bob_53 = new NpcStep(this, NpcID.BOB, new WorldPoint(2748, 3559, 0), "Talk to  and buy a Steel Axe");
        npc_restless_ghost_54 = new NpcStep(this, NpcID.RESTLESS_GHOST, new WorldPoint(3250, 3195, 0), "Talk to");
        npc_restless_ghost_54.addDialogSteps("1");
        npc_count_check_55 = new NpcStep(this, NpcID.COUNT_CHECK, new WorldPoint(3238, 3199, 0), "Talk to  and be teleported to Stronghold of Security");
        npc_count_check_55.addDialogSteps("3", "1");
        step_complete_3_floors_56 = new DetailedQuestStep(this, "Complete 3 Floors of Stronghold of Security.");
        step_take_57 = new DetailedQuestStep(this, "On Floor 3, Spider max is 7 so if you take 3 or more damage, drink a wine before going through the door to avoid being stacked. Take the east doors.");
        npc_catablepon_58 = new NpcStep(this, NpcID.CATABLEPON, new WorldPoint(2144, 5281, 0), "Max is 9 so drink on any damage.");
        step_once_you_have_59 = new DetailedQuestStep(this, "Once you have 10,000GP from Floor 3, leave via the ropes");
        item_collect_60 = new DetailedQuestStep(this, "Collect 3x Beer inside the Longhall");
        item_collect_61 = new DetailedQuestStep(this, "Collect a Cooked Meat");
        npc_gertrude_62 = new NpcStep(this, NpcID.GERTRUDE, new WorldPoint(3151, 3415, 0), "Head east and Talk to");
        npc_gertrude_62.addDialogSteps("1");
        item_collect_63 = new DetailedQuestStep(this, "Collect a Doogle Leaf south of Gertrude");
        step_bank_64 = new DetailedQuestStep(this, "Bank at Varrock West Bank and deposit all");
    }

    @Override
    public List<PanelDetails> getPanels()
    {
        List<PanelDetails> panels = new ArrayList<>();

        PanelDetails step_starting_out_0 = new PanelDetails("Starting out", Arrays.asList(step_all_settings__0, npc_drop_3, item_buy_4, step_head_5, step_bank_9, step_click_11));
        panels.add(step_starting_out_0);
        PanelDetails step_general_2 = new PanelDetails("General", Arrays.asList(npc_father_aereck_1, npc_woman_2, npc_hans_6, npc_duke_horacio_7, step_collect_8, step_bank_10, obj_jug_15, npc_kill_17, item_collect_23, npc_kill_25, item_collect_26, item_withdraw_29, item_collect_30, step_complete_3rd_step_31, npc_morgan_32, step_collect_33, step_click_34, step_train_draynor_agility_35, step_bank_36, npc_fortunato_37, npc_start_38, step_complete_4th_step_39, npc_veos_40, item_collect_41, move_travel_42, npc_veos_43, item_mine_44, obj_open_45, item_take_46, item_use_47, npc_talk_48, item_take_49, item_use_50, npc_robin_51, step_teleport_52, npc_bob_53, npc_restless_ghost_54, npc_count_check_55, step_complete_3_floors_56, step_take_57, npc_catablepon_58, step_once_you_have_59, item_collect_60, item_collect_61, npc_gertrude_62, item_collect_63, step_bank_64));
        panels.add(step_general_2);
        PanelDetails step_bank_4 = new PanelDetails("Bank 1", Arrays.asList(item_run_12, step_go_13, item_empty_14, step_complete_2nd_step_16, step_head_18, npc_father_urhney_19, item_use_20, move_head_21, item_take_22, move_talk_24, npc_talk_27, step_bank_28));
        panels.add(step_bank_4);
        return panels;
    }

}
