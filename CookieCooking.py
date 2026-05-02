

import math
import random
import json
import re

import pyspigot as ps

from org.bukkit import Location, Bukkit, Material, Sound, Registry, Particle, NamespacedKey
from org.bukkit.util import Transformation
from org.bukkit.block import BlockFace
from org.bukkit.entity import Player, EntityType, ItemDisplay
from org.bukkit.inventory import EquipmentSlot, ItemStack
from org.bukkit.event.player import PlayerInteractEvent
from org.bukkit.event.block import BlockBreakEvent, Action
from org.bukkit.event.inventory import InventoryType, InventoryCloseEvent

from java.lang import System
from java.time import Duration
from org.joml import Vector3f, Quaternionf

from net.kyori.adventure.text import Component, TextReplacementConfig
from net.kyori.adventure.text.serializer.gson import GsonComponentSerializer
from net.kyori.adventure.text.serializer.plain import PlainTextComponentSerializer
from net.kyori.adventure.text.serializer.legacy import LegacyComponentSerializer
from net.kyori.adventure.text.minimessage import MiniMessage
from net.kyori.adventure.title import Title

class ConfigManager:


    config = None
    choppingBoardRecipe = None
    wokRecipe = None
    grinderRecipe = None
    steamerRecipe = None
    data = None
    prefix = None

    @staticmethod
    def setConfigValue(configFile, path, defaultValue, comments=None):

        if not configFile.contains(path):
            configFile.setIfNotExists(path, defaultValue)
            if comments is not None:
                configFile.setComments(path, comments)

    @staticmethod
    def loadConfig():

        configPath = "CookieCooking/Config.yml"
        configFile = ps.config.loadConfig(configPath)


        ConfigManager.setConfigValue(configFile, "Setting.General.SearchRadius", 0.45,[u"Search radius for display entities"])


        ConfigManager.setConfigValue(configFile,"Setting.ChoppingBoard.Drop",True,[u"Drop the finished item after chopping board processing"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.StealthInteraction", True, [
            u"Require sneaking to interact with the chopping board",
            u"Enabled: players must sneak to use chopping board features",
            u"Disabled: players can interact directly without sneaking"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.Custom", False, [
            u"Use a custom block as the chopping board",
            u"Enabled: use blocks from compatible plugins (for example: CraftEngine)",
            u"Disabled: use vanilla blocks",
            "",
            u"CraftEngine block: craftengine <Key>:<ID>"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.Material", "OAK_LOG")
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.SpaceRestriction", False, [
            u"Allow blocks above the chopping board",
            u"Enabled: the chopping board cannot be used when a block is above it",
            u"Disabled: blocks above the chopping board are allowed"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.Delay", 1.0, [
            u"Minimum chopping board interaction interval (seconds)",
            u"Prevents players from interacting too quickly",
            u"Set to 0 for no delay"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.KitchenKnife.Custom", False, [
            u"Use a custom knife",
            u"Enabled: use items from compatible plugins (for example: CraftEngine, MMOItems)",
            u"Disabled: use vanilla items",
            "",
            u"CraftEngine item: craftengine <Key>:<ID>",
            u"MMOItems item: mmoitems <Type>:<ID>"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.Damage.Enable", True, [
            u"Enable the chopping board event",
            u"Enabled: cutting ingredients has a chance to hurt the player's finger"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.Damage.Chance", 10)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.Damage.Value", 2)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.KitchenKnife.Material", ["minecraft IRON_AXE"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Offset.X", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Offset.Y", 1.02)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Offset.Z", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Rotation.X", 90.0)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Rotation.Y", 0.0)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Rotation.Z", 0.0, [
            u"Allows decimal Z-axis rotation angles (0.0, 360.0)",
            u"Also allows a random range value (0.0-360.0)"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Item.Scale", 0.5)

        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Offset.X", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Offset.Y", 1.125)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Offset.Z", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Rotation.X", 0.0)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Rotation.Y", 90.0)
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Rotation.Z", 0.0, [
            u"Allows decimal Z-axis rotation angles (0.0, 360.0)",
            u"Also allows a random range value (0.0-360.0)"])
        ConfigManager.setConfigValue(configFile, "Setting.ChoppingBoard.DisplayEntity.Block.Scale", 0.25)


        ConfigManager.setConfigValue(configFile, "Setting.Wok.Drop", True, [u"Drop the finished item after wok cooking"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.StealthInteraction", True, [
            u"Require sneaking for wok interactions",
            "",
            u"Enabled: all wok interactions (adding ingredients, removing ingredients, and stir-frying) require sneaking",
            u"If Setting.Wok.NeedBowl is disabled, serving the finished dish with an empty hand does not require sneaking",
            "",
            u"Disabled: all wok interactions (adding ingredients, removing ingredients, and stir-frying) do not require sneaking",
            u"If Setting.Wok.NeedBowl is disabled, serving the finished dish with an empty hand requires sneaking"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Custom", False, [
            u"Use a custom wok block",
            u"Enabled: use blocks from compatible plugins (for example: CraftEngine)",
            u"Disabled: use vanilla blocks",
            "",
            u"CraftEngine block: craftengine <Key>:<ID>"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Material", "IRON_BLOCK")
        ConfigManager.setConfigValue(
            configFile, "Setting.Wok.HeatControl", {"CAMPFIRE": 1,"MAGMA_BLOCK": 2,"LAVA": 3,},[
                u"Define the cooking strength for each heat source",
                u"Higher values mean stronger heat",
                "",
                u"Supports CraftEngine blocks and furniture",
                u"CraftEngine block: craftengine <Key>:<ID>: <HeatLevel>"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.NeedBowl", True, [
            u"Require a bowl to serve finished wok dishes",
            u"Enabled: players must hold a bowl to serve the finished dish",
            u"Disabled: players can serve the finished dish with an empty hand",
            u"If enabled, sneaking for serving is controlled by Setting.Wok.StealthInteraction"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.InvalidRecipeOutput", "STONE", [
            u"This option is used when a player adds an incomplete or invalid ingredient combination",
            u"Serving the result will give this item as the failed output"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Delay", 5, [
            u"Wok stir-fry delay time (seconds)",
            u"This value should be less than Setting.Wok.TimeOut"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Damage.Enable", True, [
            u"Enable burn damage when taking ingredients out of the wok",
            u"Enabled: if ingredients are in the wok and have been stir-fried, taking them out will deal damage",
            u"Disabled: taking ingredients out of the wok will not deal any damage"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Damage.Value", 2)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Failure.Enable", True, [
            u"Enable the wok cooking failure event",
            u"Enabled: cooking can still fail randomly even when ingredients and steps are correct",
            u"Disabled: cooking always succeeds when ingredients and steps are correct"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Failure.Chance", 5)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Failure.Type", "BONE_MEAL", [
            u"Output item generated when wok cooking fails"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.TimeOut", 30, [
            u"Maximum wait time after a single stir-fry action (seconds)",
            u"This timer resets after each stir-fry action",
            u"If the timer ends before another stir-fry, ingredients in the wok burn into failed output"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Spatula.Custom", False, [
            u"Use a custom spatula",
            u"Enabled: use items from compatible plugins (for example: CraftEngine, MMOItems)",
            u"Disabled: use vanilla items",
            u"CraftEngine item: craftengine <Key>:<ID>",
            u"MMOItems item: mmoitems <Type>:<ID>"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.Spatula.Material", ["minecraft IRON_SHOVEL"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Offset.X", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Offset.Y", 1.02)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Offset.Z", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Rotation.X", 90.0)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Rotation.Y", 0.0)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Rotation.Z", "0.0-90.0", [
            u"Allows decimal Z-axis rotation angles (0.0, 360.0)",
            u"Also allows a random range value (0.0-360.0)"])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Item.Scale", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Offset.X", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Offset.Y", 1.125)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Offset.Z", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Rotation.X", 0.0)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Rotation.Y", 90.0)
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Rotation.Z", 0.0, [
            u"Allows decimal Z-axis rotation angles (0.0, 360.0)",
            u"Also allows a random range value (0.0-360.0)",
            u"",
            u"Currently not recommended"
            ])
        ConfigManager.setConfigValue(configFile, "Setting.Wok.DisplayEntity.Block.Scale", 0.25)


        ConfigManager.setConfigValue(configFile, "Setting.Grinder.Drop", True, [u"Drop the finished item after grinder processing"])
        ConfigManager.setConfigValue(configFile, "Setting.Grinder.StealthInteraction", True, [
            u"Require sneaking to interact with the grinder"])
        ConfigManager.setConfigValue(configFile, "Setting.Grinder.Custom", False, [
            u"Use a custom grinder block",
            u"Enabled: use blocks from compatible plugins (for example: CraftEngine)",
            u"Disabled: use vanilla blocks",
            "",
            u"CraftEngine block: craftengine <Key>:<ID>"])
        ConfigManager.setConfigValue(configFile, "Setting.Grinder.Material", "GRINDSTONE")
        ConfigManager.setConfigValue(configFile, "Setting.Grinder.CheckDelay", 20, [
            u"Grinder completion check delay (ticks)",
            u"This also controls the interval for particles and sounds during grinding"
        ])


        ConfigManager.setConfigValue(configFile, "Setting.Steamer.Material", "BARREL", [
            u"CraftEngine block: craftengine <Key>:<ID>"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.StealthInteraction", True, [
            u"Require sneaking to interact with the steamer",
            u"Enabled: players must sneak to use chopping board features",
            u"Disabled: players can interact directly without sneaking"])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.OpenInventory.Type", "HOPPER", [
            u"Opened container type",
            u"See details: https://jd.papermc.io/paper/1.21.11/org/bukkit/event/inventory/InventoryType.html"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.OpenInventory.Title", u"<dark_gray>Steamer")
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.OpenInventory.Slot", 9, [
            u"Only effective when Setting.Steamer.OpenInventory.Type is CHEST"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.HeatControl", ["FURNACE", "SMOKER"], [
            u"Blocks that can provide heat to the steamer",
            u"",
            u"CraftEngine block: craftengine <Key>:<ID>"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.Ignite", True, [
            u"If the heat source block can be lit, ignite it after adding fuel"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.Fuel", {
            "STICK": 5,
            "COAL": 80,
            "CHARCOAL": 80,
        }, [
            u"Allowed fuel items for the steamer, in seconds",
            u""
            u"CraftEngine item: craftengine <Key>:<ID>",
            u"MMOItems item: mmoitems <Type>:<ID>"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.Moisture", [
            "minecraft WATER_BUCKET & minecraft BUCKET & 120",
            "minecraft POTION & minecraft GLASS_BOTTLE & 40"
        ], [
            u"Items that can provide moisture to the steamer",
            u"Input item & output item & provided moisture value",
            u"If no output item is wanted, set the output item to AIR",
            u"",
            u"CraftEngine item: craftengine <Key>:<ID>",
            u"MMOItems item: mmoitems <Type>:<ID>"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.ResetToZero", True, [
            u"If set to True, when steamer steam is 0, all cooking progress inside the steamer resets to 0",
            u"If set to False, the current cooking progress is preserved"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.SteamProductionEfficiency", 10, [
            u"Steam production efficiency. This controls how item moisture converts 1 moisture into 10 steam per second",
            u"That is 10 steam/s"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.SteamConversionEfficiency", 1, [
            u"Steam conversion efficiency. This controls how fast ingredients consume steam",
            u"That is 1 steam/s"
        ])
        ConfigManager.setConfigValue(configFile, "Setting.Steamer.SteamConsumptionEfficiency", 1, [
            u"Steam consumption efficiency. This controls the steamer's default steam drain rate, even when no ingredients are cooking",
            u"That is 1 steam/s"
        ])


        Messages = {
            "Messages.Prefix": u"<gray>[ <gradient:#FF80FF:#00FFFF>CookieCooking</gradient> ]</gray>",
            "Messages.Load": u"{Prefix} <green>Welcome to CookieCooking! Version {Version} is ready!",
            "Messages.Reload.LoadPlugin": u"{Prefix} <green>CookieCooking has been reloaded!",
            "Messages.Reload.LoadChoppingBoardRecipe": u"{Prefix} <green>Loaded {Amount} chopping board recipe(s)",
            "Messages.Reload.LoadWokRecipe": u"{Prefix} <green>Loaded {Amount} wok recipe(s)",
            "Messages.Reload.LoadGrinderRecipe": u"{Prefix} <green>Loaded {Amount} grinder process recipe(s)",
            "Messages.Reload.LoadSteamerRecipe": u"{Prefix} <green>Loaded {Amount} steamer recipe(s)",
            "Messages.InvalidMaterial": u"{Prefix} <red>Chef, this ingredient {Material} does not seem right...",
            "Messages.NotStarted": u"<red>Not started!",
            "Messages.Completed": u"<green>Completed!",
            "Messages.WokTop": u"<gold>Ingredients in the wok:",
            "Messages.WokContent": u" <gray>{ItemName} <dark_gray>x <yellow>{ItemAmount} <gray>Stir count: <yellow>{Count}",
            "Messages.WokDown": u"<gold>Total stir count: <yellow>{Count}",
            "Messages.WokHeatControl": u"<gold>Heat level: <yellow>{Heat}",
            "Messages.NoPermission": u"{Prefix} <red>Chef, you do not have the required permission! ",
            "Messages.Title.CutHand.MainTitle": u"<red>Ouch! You cut your hand! ",
            "Messages.Title.CutHand.SubTitle": u"<gray>Careful with the knife! You took <red>{Damage} <gray>damage",
            "Messages.Title.Scald.MainTitle": u"<red>Too hot! You got burned! ",
            "Messages.Title.Scald.SubTitle": u"<gray>Careful with the hot wok! You took <red>{Damage} <gray>damage",
            "Messages.Title.Grinder.MainTitle": u"<green>Grinding started!",
            "Messages.Title.Grinder.SubTitle": u"<gray>Please wait <green>{Time} <gray>seconds for grinding",
            "Messages.ActionBar.TakeOffItem": u"<gray>Tip: tap the chopping board with an empty hand to take off the ingredient",
            "Messages.ActionBar.WokNoItem": u"<red>The wok is empty. Add some ingredients! ",
            "Messages.ActionBar.WokAddItem": u"<green>Added <white>{Material} <green>to the wok! ",
            "Messages.ActionBar.CutAmount": u"<gray>Cutting progress: <green>{CurrentCount} <dark_gray>/ <green>{NeedCount}",
            "Messages.ActionBar.StirCount": u"<gray>Stir count: <green>{Count}",
            "Messages.ActionBar.ErrorRecipe": u"<red>That is not how this dish is made! Think it over, chef.",
            "Messages.ActionBar.FailureRecipe": u"<red>Cooking failed... The ingredients were wasted, but do not give up! ",
            "Messages.ActionBar.SuccessRecipe": u"<green>Perfect! You cooked a delicious dish! ",
            "Messages.ActionBar.CannotCut": u"<red>Chef, this ingredient cannot be processed here! ",
            "Messages.ActionBar.BurntFood": u"<red>Oops! The heat was too high and the dish burned! ",
            "Messages.ActionBar.RawFood": u"<red>Oops! The dish is not fully cooked yet! ",
            "Messages.ActionBar.StirFriedTooQuickly": u"<red>You stirred too quickly! The ingredients are not fully cooked yet! ",
            "Messages.ActionBar.WokStirItem": u"<green>Stir-frying <gray>{Material}...",
            "Messages.ActionBar.NoGrinderReplace": u"<red>This item is too hard. The grinder cannot process it! ",
            "Messages.ActionBar.OnRunGrinder": u"<red>The grinder is running! Please try again later! ",
            "Messages.ActionBar.SuccessGrinder": u"<green>Grinding succeeded!",
            "Messages.ActionBar.AddFuel": u"<green>Added fuel: <white>{Item} <dark_gray>| <green>Remaining burn time: <yellow>{Second}s",
            "Messages.ActionBar.AddMoisture": u"<green>Added item: <aqua>{Item} <dark_gray>| <green>Added moisture: <aqua>{Moisture} <dark_gray>| <green>Current moisture: <blue>{Total}",
            "Messages.ActionBar.SteamerInfo": u"<gray>Burn time: <yellow>{BurningTime}</yellow>s | Moisture: <aqua>{Moisture}</aqua> | Steam: <white>{Steam}</white> | Cooking progress: <yellow>{Progress}</gray>",
            "Messages.ActionBar.ChoppingBoardTooFast": u"<red>Action too fast! Please wait a moment before continuing!",
            "Messages.PluginLoad.CraftEngine": u"{Prefix} <green>Detected CraftEngine plugin",
            "Messages.PluginLoad.MMOItems": u"{Prefix} <green>Detected MMOItems plugin",
            "Messages.PluginLoad.PlaceholderAPI": u"{Prefix} <green>Detected PlaceholderAPI plugin",
            "Messages.PluginLoad.NeigeItems": u"{Prefix} <green>Detected NeigeItems plugin",
            "Messages.Debug.PAPIParseError": u"{Prefix} <red>PAPI placeholder parse error: {Error}",
            "Messages.Debug.PlayerCommandFailed": u"{Prefix} <red>Command failed when executed as the player; fell back to console: {Error}",
            "Messages.Debug.CommandExecuteFailed": u"{Prefix} <red>Command execution failed: {Error}",
            "Messages.Debug.ConsoleCommandFailed": u"{Prefix} <red>Console command execution failed: {Error}",
            "Messages.Debug.CommandParseError": u"{Prefix} <red>Command parse error: {Error}",
            "Messages.Debug.RewardFormatError": u"{Prefix} <red>Reward format error. It must contain 4 parts: {Reward}",
            "Messages.Debug.AmountRangeFormatErrorMin": u"{Prefix} <red>Amount range format error, using minimum value: {Amount}",
            "Messages.Debug.AmountRangeFormatErrorDirect": u"{Prefix} <red>Amount range format error, using direct parsing: {Amount}",
            "Messages.Debug.AmountRangeParseError": u"{Prefix} <red>Amount range parse error, using default value 1: {Amount}",
            "Messages.Debug.AmountFormatError": u"{Prefix} <red>Amount format error, using default value 1: {Amount}",
            "Messages.Debug.ChanceFormatError": u"{Prefix} <red>Chance format error, using default value 100: {Chance}",
            "Messages.Debug.ItemRewardParseError": u"{Prefix} <red>Item reward parse error: {Error}",
            "Messages.Debug.UnrecognizedItemType": u"{Prefix} <red>Unrecognized item type. A full namespace is required: {ItemKey}",
            "Messages.Debug.MinecraftNamespaceRequired": u"{Prefix} <red>Vanilla items must use the minecraft namespace: {ItemKey}",
            "Messages.Debug.MinecraftItemCreateFailed": u"{Prefix} <red>Failed to create vanilla item: {ItemKey} Error: {Error}",
            "Messages.Debug.RecipeNotFound": u"{Prefix} <red>Recipe not found: {ItemMaterial}",
            "Messages.Debug.RewardProcessFailed": u"{Prefix} <red>Failed to process reward: {ResultMaterial}",
            "Messages.Debug.ItemIdMismatch": u"{Prefix} <red>Item ID mismatch - Item: {ItemNamespace} {ItemId}, Recipe: {RecipeNamespace} {RecipeId}",
            "Messages.Command.NoItemInHand": u"<gray>You do not have an item in your hand",
            "Messages.Startup.NoPlaceholderAPI": u"{Prefix} <red>PlaceholderAPI is not installed on this server!",
            "Messages.Startup.Failed": u"{Prefix} <red>Failed to start CookieCooking",
            "Messages.Startup.Discord": u"{Prefix} <red>Discord: <gray>https://discord.gg/CCUNfyE4aZ",
            "Messages.Startup.Wiki": u"{Prefix} <red>Wiki: <gray>https://github.com/LoveCookieee-java"
        }

        for KEY, VALUE in Messages.items(): ConfigManager.setConfigValue(configFile, KEY, VALUE)


        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.ChoppingBoardAddItem", u"entity.item_frame.add_item", [u"Sound played when adding ingredients to the chopping board"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.ChoppingBoardCutItem", u"item.axe.strip", [u"Sound played when cutting ingredients on the chopping board"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.ChoppingBoardCutHand", u"entity.player.hurt", [u"Sound played when a hand is cut while using the chopping board"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.WokAddItem", u"block.anvil.hit", [u"Sound played when adding ingredients to the wok"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.WokStirItem", u"block.lava.extinguish", [u"Sound played when stir-frying ingredients in the wok"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.WokScald", u"entity.player.hurt_on_fire", [u"Sound played when a hand is burned while stir-frying in the wok"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.WokTakeOffItem", u"entity.item.pickup", [u"Sound played when taking ingredients out of the wok"])
        ConfigManager.setConfigValue(
            configFile, "Setting.Sound.GrinderStart", u"block.grindstone.use", [u"Sound played when the grinder starts grinding"])


        ConfigManager.setConfigValue(
            configFile, "Setting.Particle.ChoppingBoardCutItem.Type", "CLOUD", [u"Particles shown when cutting ingredients on the chopping board"])
        ConfigManager.setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.Amount", 10)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.OffsetX", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.OffsetY", 1.0)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.OffsetZ", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.ChoppingBoardCutItem.Speed", 0.05)

        ConfigManager.setConfigValue(
            configFile, "Setting.Particle.WokStirItem.Type", "CAMPFIRE_COSY_SMOKE", [u"Particles shown when stir-frying ingredients in the wok"])
        ConfigManager.setConfigValue(configFile, "Setting.Particle.WokStirItem.Amount", 10)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.WokStirItem.OffsetX", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.WokStirItem.OffsetY", 1.0)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.WokStirItem.OffsetZ", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.WokStirItem.Speed", 0.05)

        ConfigManager.setConfigValue(
            configFile, "Setting.Particle.GrinderStart.Type", "GLOW", [u"Particles shown when the grinder starts grinding"])
        ConfigManager.setConfigValue(configFile, "Setting.Particle.GrinderStart.Amount", 10)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.GrinderStart.OffsetX", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.GrinderStart.OffsetY", 1.0)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.GrinderStart.OffsetZ", 0.5)
        ConfigManager.setConfigValue(configFile, "Setting.Particle.GrinderStart.Speed", 0.05)

        configFile.save()
        return ps.config.loadConfig(configPath)

    @staticmethod
    def loadChoppingBoardRecipe():

        choppingBoardRecipePath = "CookieCooking/Recipe/ChoppingBoard.yml"
        return ps.config.loadConfig(choppingBoardRecipePath)

    @staticmethod
    def loadWokRecipe():

        wokRecipePath = "CookieCooking/Recipe/Wok.yml"
        return ps.config.loadConfig(wokRecipePath)

    @staticmethod
    def loadSteamerRecipe():

        steamerRecipePath = "CookieCooking/Recipe/Steamer.yml"
        return ps.config.loadConfig(steamerRecipePath)

    @staticmethod
    def loadData():

        dataPath = "CookieCooking/Data.yml"
        return ps.config.loadConfig(dataPath)

    @staticmethod
    def loadGrinderRecipe():

        grinderRecipePath = "CookieCooking/Recipe/Grinder.yml"
        return ps.config.loadConfig(grinderRecipePath)

    @staticmethod
    def getConfig():

        if ConfigManager.config is None:
            ConfigManager.config = ConfigManager.loadConfig()
        return ConfigManager.config

    @staticmethod
    def getChoppingBoardRecipe():

        if ConfigManager.choppingBoardRecipe is None:
            ConfigManager.choppingBoardRecipe = ConfigManager.loadChoppingBoardRecipe()
        return ConfigManager.choppingBoardRecipe

    @staticmethod
    def getWokRecipe():

        if ConfigManager.wokRecipe is None:
            ConfigManager.wokRecipe = ConfigManager.loadWokRecipe()
        return ConfigManager.wokRecipe

    @staticmethod
    def getGrinderRecipe():

        if ConfigManager.grinderRecipe is None:
            ConfigManager.grinderRecipe = ConfigManager.loadGrinderRecipe()
        return ConfigManager.grinderRecipe

    @staticmethod
    def getSteamerRecipe():

        if ConfigManager.steamerRecipe is None:
            ConfigManager.steamerRecipe = ConfigManager.loadSteamerRecipe()
        return ConfigManager.steamerRecipe

    @staticmethod
    def getData():

        if ConfigManager.data is None:
            ConfigManager.data = ConfigManager.loadData()
        return ConfigManager.data

    @staticmethod
    def getPrefix():

        if ConfigManager.prefix is None:
            ConfigManager.prefix = ConfigManager.getConfig().getString("Messages.Prefix")
        return ConfigManager.prefix

    @staticmethod
    def reloadAll():

        ConfigManager.config = ConfigManager.loadConfig()
        ConfigManager.choppingBoardRecipe = ConfigManager.loadChoppingBoardRecipe()
        ConfigManager.wokRecipe = ConfigManager.loadWokRecipe()
        ConfigManager.grinderRecipe = ConfigManager.loadGrinderRecipe()
        ConfigManager.steamerRecipe = ConfigManager.loadSteamerRecipe()
        ConfigManager.data = ConfigManager.loadData()
        ConfigManager.prefix = None

class MiniMessageUtils:


    MiniMessages = MiniMessage.miniMessage()
    GsonSerializer = GsonComponentSerializer.gson()
    PlainTextSerializer = PlainTextComponentSerializer.plainText()
    LegacySerializer = LegacyComponentSerializer.builder().hexColors().hexCharacter(u"#").character(u"&").build()

    @staticmethod
    def isString(MessageObj):

        return isinstance(MessageObj, basestring)

    @staticmethod
    def containsLegacyColors(TextStr):

        if not MiniMessageUtils.isString(TextStr):
            return False

        return "&" in TextStr and re.search(r"&[0-9a-fk-orA-FK-OR]", TextStr) is not None

    @staticmethod
    def convertLegacyToMiniMessage(TextStr):

        if not MiniMessageUtils.isString(TextStr) or not MiniMessageUtils.containsLegacyColors(TextStr):
            return TextStr
        ComponentObj = MiniMessageUtils.LegacySerializer.deserialize(TextStr)
        return MiniMessageUtils.MiniMessages.serialize(ComponentObj)

    @staticmethod
    def stringToComponent(TextStr):

        if not MiniMessageUtils.isString(TextStr):
            return Component.empty()
        TextStr = MiniMessageUtils.convertLegacyToMiniMessage(TextStr)
        return MiniMessageUtils.MiniMessages.deserialize(TextStr)

    @staticmethod
    def jsonToComponent(JsonStr):

        if not MiniMessageUtils.isString(JsonStr):
            return Component.empty()
        try:
            return MiniMessageUtils.GsonSerializer.deserialize(JsonStr)
        except Exception as e:
            return MiniMessageUtils.MiniMessages.deserialize(u"<red>JSON parse error: " + str(e) + "</red>")

    @staticmethod
    def nbtToComponent(NbtStr):

        if not MiniMessageUtils.isString(NbtStr):
            return Component.empty()
        try:
            return MiniMessageUtils.jsonToComponent(NbtStr)
        except:
            return MiniMessageUtils.stringToComponent(NbtStr)

    @staticmethod
    def replaceTextPlaceholders(TextStr, PlaceholdersDict):

        if not MiniMessageUtils.isString(TextStr) or not isinstance(PlaceholdersDict, dict):
            return TextStr
        try:
            return TextStr.format(**PlaceholdersDict)
        except:
            for Placeholder, Replacement in PlaceholdersDict.iteritems():
                PlaceholderPattern = "{" + Placeholder + "}"
                TextStr = TextStr.replace(PlaceholderPattern, str(Replacement))

        return TextStr

    @staticmethod
    def replaceComponentPlaceholders(ComponentObj, PlaceholdersDict):

        if ComponentObj is None or not isinstance(PlaceholdersDict, dict):
            return ComponentObj
        for Placeholder, Replacement in PlaceholdersDict.iteritems():
            ReplacementComp = MiniMessageUtils.processMessage(Replacement, None)
            Config = TextReplacementConfig \
                .builder() \
                .matchLiteral("{" + Placeholder + "}") \
                .replacement(ReplacementComp) \
                .build()
            ComponentObj = ComponentObj.replaceText(Config)

        return ComponentObj

    @staticmethod
    def processMessage(MessageObj, PlaceholdersDict=None):

        if MessageObj is None:
            return Component.empty()
        TextComp = None
        if MiniMessageUtils.isString(MessageObj):
            if MessageObj.strip().startswith("{") and MessageObj.strip().endswith("}"):
                try:
                    json.loads(MessageObj)
                    TextComp = MiniMessageUtils.jsonToComponent(MessageObj)
                except:
                    TextComp = MiniMessageUtils.stringToComponent(MessageObj)
            else:
                TextComp = MiniMessageUtils.stringToComponent(MessageObj)
        elif isinstance(MessageObj, Component):
            TextComp = MessageObj
        else:
            TextComp = MiniMessageUtils.stringToComponent(str(MessageObj))
        if PlaceholdersDict:
            TextComp = MiniMessageUtils.replaceComponentPlaceholders(TextComp, PlaceholdersDict)
        return TextComp

    @staticmethod
    def sendMessage(Target, MessageObj, PlaceholdersDict=None):

        if MessageObj is None:
            return

        Comp = MiniMessageUtils.processMessage(MessageObj, PlaceholdersDict)
        Target.sendMessage(Comp)

    @staticmethod
    def sendTitle(Target, TitleStr, SubtitleStr, PlaceholdersDict=None, FadeIn=10, Stay=70, FadeOut=20):

        if not isinstance(Target, Player):
            return

        TitleComp = MiniMessageUtils.processMessage(
            TitleStr, PlaceholdersDict
            ) if TitleStr else Component.empty()
        SubtitleComp = MiniMessageUtils.processMessage(
            SubtitleStr,PlaceholdersDict
            ) if SubtitleStr else Component.empty()
        Times = Title.Times.times(
            Duration.ofMillis(FadeIn * 50),
            Duration.ofMillis(Stay * 50),
            Duration.ofMillis(FadeOut * 50)
        )
        TitleObj = Title.title(TitleComp, SubtitleComp, Times)
        Target.showTitle(TitleObj)

    @staticmethod
    def sendActionBar(Target, MessageObj, PlaceholdersDict=None):

        if not isinstance(Target, Player) or MessageObj is None:
            return
        Comp = MiniMessageUtils.processMessage(MessageObj, PlaceholdersDict)
        Target.sendActionBar(Comp)

    @staticmethod
    def playSound(Target, SoundStr, Volume=1.0, Pitch=1.0):

        if SoundStr is None: return
        if isinstance(Target, Location):
            location = Target
            world = location.getWorld()
            if world is None:
                return
        elif isinstance(Target, Player):
            location = Target.getLocation()
            world = location.getWorld()
        else:
            return
        SoundObj = None
        if isinstance(SoundStr, Sound):
            SoundObj = SoundStr
        elif isinstance(SoundStr, basestring):
            try:
                if ":" in SoundStr:
                    namespace, key = SoundStr.split(":", 1)
                    namespaced_key = NamespacedKey(namespace, key)
                else:
                    namespaced_key = NamespacedKey.minecraft(SoundStr.lower())

                registry_sound = Registry.SOUNDS.get(namespaced_key)
                if registry_sound:
                    SoundObj = registry_sound
            except Exception:
                pass


        if SoundObj:
            if isinstance(Target, Player):
                Target.playSound(location, SoundObj, Volume, Pitch)
            else:
                world.playSound(location, SoundObj, Volume, Pitch)

Config = ConfigManager.getConfig()
Prefix = ConfigManager.getPrefix()
ChoppingBoardRecipe = ConfigManager.getChoppingBoardRecipe()
WokRecipe = ConfigManager.getWokRecipe()
GrinderRecipe = ConfigManager.getGrinderRecipe()
SteamerRecipe = ConfigManager.getSteamerRecipe()
Data = ConfigManager.getData()
Console = Bukkit.getServer().getConsoleSender()

CraftEngineAvailable = False
MMOItemsAvailable = False
PlaceholderAPIAvailable = False
NeigeItemsAvailable = False

def ServerPluginLoad():

    global CraftEngineAvailable, MMOItemsAvailable, PlaceholderAPIAvailable
    CraftEngineAvailable = Bukkit.getPluginManager().isPluginEnabled("CraftEngine")
    if CraftEngineAvailable:
        MiniMessageUtils.sendMessage(Console,Config.getString("Messages.PluginLoad.CraftEngine"), {"Prefix": Prefix})
        from net.momirealms.craftengine.bukkit.api.event import (
            CustomBlockInteractEvent,
            CustomBlockBreakEvent,
        )
        ps.listener.registerListener(InteractionCraftEngineBlock, CustomBlockInteractEvent)
        ps.listener.registerListener(BreakCraftEngineBlock, CustomBlockBreakEvent)
    MMOItemsAvailable = Bukkit.getPluginManager().isPluginEnabled("MMOItems")
    if MMOItemsAvailable:
        MiniMessageUtils.sendMessage(Console,Config.getString("Messages.PluginLoad.MMOItems"), {"Prefix": Prefix})
    PlaceholderAPIAvailable = Bukkit.getPluginManager().isPluginEnabled("PlaceholderAPI")
    if PlaceholderAPIAvailable:
        MiniMessageUtils.sendMessage(Console, Config.getString("Messages.PluginLoad.PlaceholderAPI"), {"Prefix": Prefix})
    NeigeItemsAvailable = Bukkit.getPluginManager().isPluginEnabled("NeigeItems")
    if NeigeItemsAvailable:
        MiniMessageUtils.sendMessage(Console, Config.getString("Messages.PluginLoad.NeigeItems"), {"Prefix": Prefix})

def InteractionVanillaBlock(Event): return EventHandler.handleInteraction(Event, "vanilla")

def InteractionCraftEngineBlock(Event): return EventHandler.handleInteraction(Event, "craftengine")

def BreakVanillaBlock(Event): return EventHandler.handleBreak(Event, "vanilla")

def BreakCraftEngineBlock(Event): return EventHandler.handleBreak(Event, "craftengine")

class EventHandler:


    @staticmethod
    def handleInteraction(Event, EventType):

        try:

            if ChoppingBoardInteraction(Event, EventType):  return True

            if WokInteraction(Event, EventType):  return True

            if GrinderInteraction(Event, EventType):  return True

            if SteamerInteraction(Event, EventType):  return True
            return False
        except Exception as e:
            MiniMessageUtils.sendMessage(Console, str(e))
            return False

    @staticmethod
    def handleBreak(Event, EventType):

        try:

            if ChoppingBoardBreak(Event, EventType):  return True

            if WokBreak(Event, EventType):  return True

            if GrinderBreak(Event, EventType):  return True

            if SteamerBreak(Event, EventType):  return True

            return False
        except Exception as e:
            MiniMessageUtils.sendMessage(Console, str(e))
            return False

class EventUtils:


    @staticmethod
    def getPlayer(Event, EventType):

        if EventType == "vanilla": return Event.getPlayer()
        elif EventType == "craftengine": return Event.player()
        return None

    @staticmethod
    def getPermission(Player, PermissionNode):

        if Player is None:
            return False
        if Player.isOp():
            return True
        return Player.hasPermission(PermissionNode)

    @staticmethod
    def getInteractionBlock(Event, EventType):

        if EventType == "vanilla": return Event.getClickedBlock()
        elif EventType == "craftengine": return Event.bukkitBlock()
        return None

    @staticmethod
    def getBreakBlock(Event, EventType):

        if EventType == "vanilla": return Event.getBlock()
        elif EventType == "craftengine": return Event.bukkitBlock()
        return None

    @staticmethod
    def getAction(Event, EventType):

        if EventType == "vanilla": return Event.getAction()
        elif EventType == "craftengine": return Event.action()
        return None

    @staticmethod
    def getHand(Event, EventType):

        if EventType == "vanilla": return Event.getHand()
        elif EventType == "craftengine": return Event.hand()
        return None

    @staticmethod
    def isMainHand(Event, EventType):

        if EventType == "vanilla": return Event.getHand() == EquipmentSlot.HAND
        elif EventType == "craftengine":
            from net.momirealms.craftengine.core.entity.player import InteractionHand
            return Event.hand() == InteractionHand.MAIN_HAND

    def isOffHand(Event, EventType):

        if EventType == "vanilla": return Event.getHand() == EquipmentSlot.OFF_HAND
        elif EventType == "craftengine":
            from net.momirealms.craftengine.core.entity.player import InteractionHand
            return Event.hand() == InteractionHand.OFF_HAND

    @staticmethod
    def isLeftClick(Event, EventType):

        if EventType == "vanilla": return Event.getAction() == Action.LEFT_CLICK_BLOCK
        elif EventType == "craftengine": return Event.action() == Event.Action.LEFT_CLICK
        return False

    @staticmethod
    def isRightClick(Event, EventType):

        if EventType == "vanilla": return Event.getAction() == Action.RIGHT_CLICK_BLOCK
        elif EventType == "craftengine": return Event.action() == Event.Action.RIGHT_CLICK
        return False

    @staticmethod
    def isSneaking(EventPlayer, ConfigType):

        SneakingStatus = Config.getBoolean("Setting." + ConfigType + ".StealthInteraction")
        if SneakingStatus and not EventPlayer.isSneaking(): return False
        elif not SneakingStatus and EventPlayer.isSneaking(): return False
        else: return True

    @staticmethod
    def isTargetBlock(Block, Target):

        MaterialSetting = Config.getString("Setting." + Target + ".Material")

        if Config.getBoolean("Setting." + Target + ".Custom"):
            if " " in MaterialSetting:
                Identifier, ID = MaterialSetting.split(" ", 1)
                if Identifier == "craftengine":
                    try:
                        from net.momirealms.craftengine.bukkit.api import CraftEngineBlocks
                        ClickBlockState = CraftEngineBlocks.getCustomBlockState(Block)
                        if ClickBlockState is not None and str(ClickBlockState) == ID:
                            return True
                    except:
                        return False
            return False
        else:
            if " " in MaterialSetting:
                namespace, materialName = MaterialSetting.split(" ", 1)
                if namespace == "minecraft":
                    try:
                        return Block.getType() == Material.valueOf(materialName.upper())
                    except:
                        return False
            else:
                try:
                    materialName = MaterialSetting.upper()
                    return Block.getType() == Material.valueOf(materialName)
                except:
                    return False

    @staticmethod
    def setCancelled(Event, EventType, Cancelled):

        if EventType == "vanilla": Event.setCancelled(Cancelled)
        elif EventType == "craftengine": Event.setCancelled(Cancelled)

    @staticmethod
    def sendParticle(TatgetType, SendLocation):

        ParticleType = Config.getString("Setting.Particle." +  TatgetType + ".Type")
        ParticleAmount = Config.getInt("Setting.Particle." +  TatgetType + ".Amount")
        ParticleoffsetX = Config.getDouble("Setting.Particle." +  TatgetType + ".OffsetX")
        ParticleoffsetY = Config.getDouble("Setting.Particle." +  TatgetType + ".OffsetY")
        ParticleoffsetZ = Config.getDouble("Setting.Particle." +  TatgetType + ".OffsetZ")
        ParticleSpeed = Config.getDouble("Setting.Particle." +  TatgetType + ".Speed")
        try: ParticleType = Particle.valueOf(ParticleType)
        except: ParticleType = Particle.valueOf("CLOUD")
        try:
            SendLocation.getWorld().spawnParticle(
                ParticleType,
                SendLocation,
                ParticleAmount,
                ParticleoffsetX,
                ParticleoffsetY,
                ParticleoffsetZ,
                ParticleSpeed)
        except: pass

class ToolUtils:


    CRAFTENGINE = u"craftengine"
    MMOITEMS = u"mmoitems"
    MINECRAFT = u"minecraft"
    NEIGEITEMS = u"neigeitems"

    @staticmethod
    def matchConfigKey(ConfigSection, TargetKey):

        if ConfigSection is None or TargetKey is None:
            return None
        if ConfigSection.contains(TargetKey):
            return TargetKey
        for key in ConfigSection.getKeys(False):
            if key.upper() == TargetKey.upper():
                return key
        return None

    @staticmethod
    def parseAndExecuteCommand(CommandStr, ExecutePlayer=None, Chance=100, ExecuteCount=1):

        try:
            if not CommandStr.startswith("command "):
                return False
            CommandContent = CommandStr[8:]
            Parts = CommandContent.split(" ")
            ActualCommand = []
            ActualChance = Chance
            ActualExecuteCount = ExecuteCount
            for Part in Parts:
                if Part.startswith("a:"):
                    try:
                        ActualExecuteCount = int(Part[2:])
                    except ValueError:
                        pass
                elif Part.startswith("c:"):
                    try:
                        ActualChance = int(Part[2:])
                    except ValueError:
                        pass
                else:
                    ActualCommand.append(Part)
            if random.randint(1, 100) > ActualChance:
                return False
            FinalCommand = " ".join(ActualCommand)
            if ExecutePlayer:
                FinalCommand = FinalCommand.replace("%player%", ExecutePlayer.getName())
                if PlaceholderAPIAvailable:
                    try:
                        from me.clip.placeholderapi.PlaceholderAPI import setPlaceholders
                        FinalCommand = setPlaceholders(ExecutePlayer, FinalCommand)
                    except Exception as e:
                        MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.PAPIParseError"), {"Prefix": Prefix, "Error": str(e)})
            for i in range(ActualExecuteCount):
                if ExecutePlayer:
                    try:
                        if FinalCommand.startswith(("/", "!")):
                            commandToExecute = FinalCommand[1:] if FinalCommand.startswith("/") else FinalCommand
                        else:
                            commandToExecute = FinalCommand
                        Bukkit.dispatchCommand(ExecutePlayer, commandToExecute)
                    except Exception as playerCmdException:
                        try:
                            Bukkit.dispatchCommand(Bukkit.getConsoleSender(), FinalCommand)
                            MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.PlayerCommandFailed"), {"Prefix": Prefix, "Error": str(playerCmdException)})
                        except Exception as consoleCmdException:
                            MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.CommandExecuteFailed"), {"Prefix": Prefix, "Error": str(consoleCmdException)})
                            return False
                else:
                    try:
                        Bukkit.dispatchCommand(Bukkit.getConsoleSender(), FinalCommand)
                    except Exception as consoleCmdException:
                        MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.ConsoleCommandFailed"), {"Prefix": Prefix, "Error": str(consoleCmdException)})
                        return False
            return True
        except Exception as e:
            MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.CommandParseError"), {"Prefix": Prefix, "Error": str(e)})
            return False

    @staticmethod
    def processReward(RewardStr, RewardPlayer=None, forceGive=False):

        if RewardStr.startswith("command "):
            return ToolUtils.parseAndExecuteCommand(RewardStr, RewardPlayer)
        try:
            parts = RewardStr.strip().split(" ")
            if len(parts) != 4:
                MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.RewardFormatError"), {"Prefix": Prefix, "Reward": RewardStr})
                return False
            itemIdentifier = parts[0] + u" " + parts[1]
            amount_str = parts[2]
            amount = 1
            if "-" in amount_str:
                try:
                    range_parts = amount_str.split("-")
                    if len(range_parts) == 2:
                        min_amount = int(range_parts[0])
                        max_amount = int(range_parts[1])
                        if min_amount <= max_amount:
                            amount = random.randint(min_amount, max_amount)
                        else:
                            amount = min_amount
                            MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.AmountRangeFormatErrorMin"), {"Prefix": Prefix, "Amount": amount_str})
                    else:
                        amount = int(amount_str)
                        MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.AmountRangeFormatErrorDirect"), {"Prefix": Prefix, "Amount": amount_str})
                except ValueError:
                    amount = 1
                    MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.AmountRangeParseError"), {"Prefix": Prefix, "Amount": amount_str})
            else:
                try:
                    amount = int(amount_str)
                except ValueError:
                    amount = 1
                    MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.AmountFormatError"), {"Prefix": Prefix, "Amount": amount_str})
            chance = 100
            try:
                chance = int(parts[3])
            except ValueError:
                MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.ChanceFormatError"), {"Prefix": Prefix, "Chance": parts[3]})
            if random.randint(1, 100) > chance:
                return False
            ResultItemStack = ToolUtils.createItemStack(itemIdentifier, amount)
            if not ResultItemStack:
                MiniMessageUtils.sendMessage(Console,
                    Config.getString("Messages.InvalidMaterial"),
                    {"Prefix": Prefix, "Material": itemIdentifier})
                return False
            if forceGive or not Config.getBoolean("Setting.ChoppingBoard.Drop"):
                if RewardPlayer:
                    GiveItemToPlayer(RewardPlayer, ResultItemStack)
            else:
                DropLocation = RewardPlayer.getLocation() if RewardPlayer else None
                if DropLocation:
                    ItemEntity = DropLocation.getWorld().dropItem(DropLocation, ResultItemStack)
                    ItemEntity.setPickupDelay(20)
            return True
        except Exception as e:
            MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.ItemRewardParseError"), {"Prefix": Prefix, "Error": str(e)})
            return False

    @staticmethod
    def isBlockMaterialType(Item):

        if Item is None: return "Item"
        ItemType = Item.getType()
        if ItemType.isBlock(): return "Block"
        else: return "Item"

    @staticmethod
    def isToolItem(Item, Config, Type, Tool, material=None):

        if not Item or Item.getType() == Material.AIR:
            return False
        if material is not None:
            materialToCheck = material
        else:
            materials = ToolUtils.getToolMaterials(Config, Type, Tool)
            materialToCheck = materials[0] if materials else None
        if materialToCheck is None:
            return False
        itemIdentifier = ToolUtils.getItemIdentifier(Item)
        CustomSetting = Config.getBoolean("Setting." + Type + "." + Tool + ".Custom")
        if CustomSetting:
            return itemIdentifier == materialToCheck
        else:
            return itemIdentifier == materialToCheck

    @staticmethod
    def getToolMaterials(Config, Type, Tool):

        return Config.getStringList("Setting." + Type + "." + Tool + ".Material")

    @staticmethod
    def isCraftEngineItem(Item, ExpectedID):

        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineItems
            if CraftEngineItems.isCustomItem(Item):
                ItemId = CraftEngineItems.getCustomItemId(Item)
                return str(ItemId) == ExpectedID
        except Exception: return False

    @staticmethod
    def isMMOItemsItem(Item, ExpectedID):

        try:
            from io.lumine.mythic.lib.api.item import NBTItem
            NbtItem = NBTItem.get(Item)
            if NbtItem.hasType():
                ItemType = NbtItem.getType()
                ItemId = NbtItem.getString("MMOITEMS_ITEM_ID")
                CombinedId = str(ItemType) + ":" + str(ItemId)
                return CombinedId == ExpectedID
        except Exception: return False

    @staticmethod
    def getItemIdentifier(Item):
        if not Item or Item.getType() == Material.AIR:
            return "minecraft AIR"


        if CraftEngineAvailable:
            craftEngineId = ToolUtils.getCraftEngineItemId(Item)
            if craftEngineId:
                return ToolUtils.CRAFTENGINE + " " + str(craftEngineId)


        if MMOItemsAvailable:
            mmoItemsId = ToolUtils.getMMOItemsItemId(Item)
            if mmoItemsId:
                return ToolUtils.MMOITEMS + " " + mmoItemsId


        if NeigeItemsAvailable:
            neigeItemsId = ToolUtils.getNeigeItemsItemId(Item)
            if neigeItemsId:
                return ToolUtils.NEIGEITEMS + " " + str(neigeItemsId)

        return ToolUtils.MINECRAFT + " " + Item.getType().name()

    @staticmethod
    def getCraftEngineItemId(Item):

        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineItems
            if CraftEngineItems.isCustomItem(Item): return CraftEngineItems.getCustomItemId(Item)
        except Exception: return None

    @staticmethod
    def getMMOItemsItemId(Item):

        try:
            from io.lumine.mythic.lib.api.item import NBTItem
            NbtItem = NBTItem.get(Item)
            if NbtItem.hasType():
                ItemType = NbtItem.getType()
                ItemId = NbtItem.getString("MMOITEMS_ITEM_ID")
                return str(ItemType) + ":" + str(ItemId)
        except Exception: return None

    @staticmethod
    def getNeigeItemsItemId(Item):

        try:
            from pers.neige.neigeitems.utils.ItemUtils import ItemUtils
            itemInfo = ItemUtils.isNiItem(Item)
            if itemInfo:
                return itemInfo.getId()
        except Exception:
            return None
        return None

    @staticmethod
    def createItemStack(ItemKey, Amount=1):

        if not ItemKey or ItemKey.strip() == "":
            return None
        ItemKey = ItemKey.strip()
        if ItemKey.startswith("minecraft "):
            return ToolUtils.createMinecraftItem(ItemKey, Amount)
        Parts = ItemKey.split(" ")
        if len(Parts) < 1:
            return None
        ItemType = Parts[0].lower()
        if ItemType == ToolUtils.NEIGEITEMS and NeigeItemsAvailable:
            return ToolUtils.createNeigeItemsItem(Parts, Amount)
        elif ItemType == ToolUtils.MINECRAFT:
            return ToolUtils.createMinecraftItem(ItemKey, Amount)
        elif ItemType == ToolUtils.CRAFTENGINE and CraftEngineAvailable:
            return ToolUtils.createCraftEngineItem(Parts, Amount)
        elif ItemType == ToolUtils.MMOITEMS and MMOItemsAvailable:
            return ToolUtils.createMMOItemsItem(Parts, Amount)
        else:
            MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.UnrecognizedItemType"), {"Prefix": Prefix, "ItemKey": ItemKey})
            return None

    @staticmethod
    def createMinecraftItem(ItemKey, Amount):
        try:
            if not ItemKey.startswith("minecraft "):
                MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.MinecraftNamespaceRequired"), {"Prefix": Prefix, "ItemKey": ItemKey})
                return None
            materialName = ItemKey[10:].upper()
            ItemMaterial = Material.valueOf(materialName)
            return ItemStack(ItemMaterial, Amount)
        except Exception as e:
            MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.MinecraftItemCreateFailed"), {"Prefix": Prefix, "ItemKey": ItemKey, "Error": str(e)})
            return None

    @staticmethod
    def createCraftEngineItem(Parts, Amount):

        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineItems
            from net.momirealms.craftengine.core.util import Key
            if len(Parts) > 1:
                KeyParts = Parts[1].split(":")
                if len(KeyParts) >= 2:
                    CraftEngineItem = CraftEngineItems.byId(Key(KeyParts[0], KeyParts[1])).buildItemStack()
                    CraftEngineItem.setAmount(Amount)
                    return CraftEngineItem
        except Exception:
            return None
        return None

    @staticmethod
    def createMMOItemsItem(Parts, Amount):

        try:
            from net.Indyuce.mmoitems import MMOItems
            if len(Parts) > 1:
                IdParts = Parts[1].split(":")
                if len(IdParts) >= 2:
                    MMOItemsItem = MMOItems.plugin.getMMOItem(
                        MMOItems.plugin.getTypes().get(IdParts[0]), IdParts[1]
                        ).newBuilder().build()
                    MMOItemsItem.setAmount(Amount)
                    return MMOItemsItem
        except Exception:
            return None
        return None

    @staticmethod
    def createNeigeItemsItem(Parts, Amount):

        try:
            from pers.neige.neigeitems.manager.ItemManager import ItemManager
            if len(Parts) > 1:
                itemId = Parts[1]
                if ItemManager.hasItem(itemId):
                    itemStack = ItemManager.getItemStack(itemId, None, None)
                    if itemStack:
                        itemStack.setAmount(Amount)
                        return itemStack
        except Exception as e:
            return None
        return None

    @staticmethod
    def getItemDisplayName(Item):


        if CraftEngineAvailable:
            try:
                from net.momirealms.craftengine.bukkit.api import CraftEngineItems
                from net.momirealms.craftengine.bukkit.item import BukkitItemManager
                if CraftEngineItems.isCustomItem(Item):
                    return BukkitItemManager.instance().wrap(Item).hoverNameJson().get()
            except Exception: pass

        if MMOItemsAvailable:
            try:
                from io.lumine.mythic.lib.api.item import NBTItem
                NbtItem = NBTItem.get(Item)
                if NbtItem.hasType(): return NbtItem.getString("MMOITEMS_NAME")
            except Exception: pass

        if NeigeItemsAvailable:
            try:
                from pers.neige.neigeitems.utils.ItemUtils import ItemUtils
                return ItemUtils.getItemName(Item)
            except Exception:
                pass

        return Component.translatable(Item.translationKey())

def ChoppingBoardBreak(Event, EventType):

    BreakBlock = EventUtils.getBreakBlock(Event, EventType)
    if not EventUtils.isTargetBlock(BreakBlock, "ChoppingBoard"): return False
    FileKey = GetFileKey(BreakBlock)
    hasExistingDisplay = Data.contains("ChoppingBoard." + FileKey + ".CutCount")
    if not hasExistingDisplay: return False
    StoredItemIdentifier = Data.getString("ChoppingBoard." + FileKey + ".Input")
    if StoredItemIdentifier:
        StoredItem = ToolUtils.createItemStack(StoredItemIdentifier)
        DisplayLocation = CalculateDisplayLocation(BreakBlock, "ChoppingBoard", StoredItem)
    else:
        DisplayLocation = CalculateDisplayLocation(BreakBlock, "ChoppingBoard")
    ItemDisplayEntities = FindNearbyDisplay(DisplayLocation)
    if ItemDisplayEntities:
        ItemDisplayEntity = ItemDisplayEntities[0]
        DisplayItem = ItemDisplayEntity.getItemStack()
        if DisplayItem:
            ItemEntity = BreakBlock.getWorld().dropItem(ItemDisplayEntity.getLocation(), DisplayItem)
            ItemEntity.setPickupDelay(0)
        ItemDisplayEntity.remove()
    Data.set("ChoppingBoard." + FileKey, None)
    Data.save()
    return True

def WokBreak(Event, EventType):

    BreakBlock = EventUtils.getBreakBlock(Event, EventType)
    if not EventUtils.isTargetBlock(BreakBlock, "Wok"): return False
    FileKey = GetFileKey(BreakBlock)
    hasExistingDisplay = Data.contains("Wok." + FileKey)
    if not hasExistingDisplay: return False
    DisplayLocation = CalculateDisplayLocation(BreakBlock, "Wok")
    ItemDisplayEntity = FindNearbyDisplay(DisplayLocation)
    if ItemDisplayEntity:
        for Display in ItemDisplayEntity:
            if Display and not Display.isDead():
                DisplayItem = Display.getItemStack()
                if DisplayItem:
                    ItemEntity = BreakBlock.getWorld().dropItem(Display.getLocation(), DisplayItem)
                    ItemEntity.setPickupDelay(0)
                Display.remove()
    Data.set("Wok." + FileKey, None)
    Data.save()
    return True

def GrinderBreak(Event, EventType):

    BreakBlock = EventUtils.getBreakBlock(Event, EventType)
    if not EventUtils.isTargetBlock(BreakBlock, "Grinder"): return False
    FileKey = GetFileKey(BreakBlock)
    hasExistingGrinder = Data.contains("Grinder." + FileKey)
    if not hasExistingGrinder: return False
    InputItem = Data.getString("Grinder." + FileKey + ".Input")
    if InputItem:
        InputItemStack = ToolUtils.createItemStack(InputItem)
        if InputItemStack:
            DropLocation = BreakBlock.getLocation().add(0.5, 1.0, 0.5)
            ItemEntity = BreakBlock.getWorld().dropItem(DropLocation, InputItemStack)
            ItemEntity.setPickupDelay(0)
    Data.set("Grinder." + FileKey, None)
    Data.save()
    return True

def SteamerBreak(Event, EventType):

    BreakBlock = EventUtils.getBreakBlock(Event, EventType)
    if EventUtils.isTargetBlock(BreakBlock, "Steamer"):
        return HandleSteamerBlockBreak(BreakBlock)
    elif isHeatSourceBlock(BreakBlock):
        return HandleHeatSourceBlockBreak(BreakBlock)
    return False

def HandleSteamerBlockBreak(SteamerBlock):

    try:
        FileKey = GetFileKey(SteamerBlock)
        SteamerDataPath = "Steamer." + FileKey
        if not Data.contains(SteamerDataPath):
            return False
        ExtinguishHeatSource(FileKey)
        DropSteamerItems(SteamerBlock, FileKey)
        Data.set(SteamerDataPath, None)
        Data.save()
        CleanupSteamerTempData(FileKey)
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def HandleHeatSourceBlockBreak(HeatSourceBlock):

    try:
        TopBlock = HeatSourceBlock.getRelative(BlockFace.UP)
        if not EventUtils.isTargetBlock(TopBlock, "Steamer"):
            return False
        return HandleSteamerBlockBreak(TopBlock)
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def DropSteamerItems(SteamerBlock, FileKey):

    try:
        SlotsPath = "Steamer." + FileKey + ".Slots"
        CookingProgressPath = "Steamer." + FileKey + ".CookingProgress"
        if not Data.contains(SlotsPath):
            return
        SlotItems = Data.getStringList(SlotsPath)
        CookingProgress = []
        if Data.contains(CookingProgressPath):
            CookingProgress = Data.getIntegerList(CookingProgressPath)
        if len(CookingProgress) < len(SlotItems):
            CookingProgress.extend([0] * (len(SlotItems) - len(CookingProgress)))
        DropLocation = SteamerBlock.getLocation().add(0.5, 1.0, 0.5)
        for i, itemIdentifier in enumerate(SlotItems):
            if itemIdentifier != "AIR":
                try:
                    CurrentProgress = CookingProgress[i] if i < len(CookingProgress) else 0
                    if SteamerRecipe.contains(itemIdentifier):
                        requiredSteam = SteamerRecipe.getInt(itemIdentifier + ".Steam", 0)
                        outputItem = SteamerRecipe.getString(itemIdentifier + ".Output")
                        if outputItem and CurrentProgress >= requiredSteam:
                            itemToDrop = outputItem
                        else:
                            itemToDrop = itemIdentifier
                    else:
                        for recipeKey in SteamerRecipe.getKeys(False):
                            outputItem = SteamerRecipe.getString(recipeKey + ".Output")
                            if outputItem and outputItem == itemIdentifier:
                                itemToDrop = itemIdentifier
                                break
                        else:
                            itemToDrop = itemIdentifier
                    itemStack = ToolUtils.createItemStack(itemToDrop, 1)
                    if itemStack:
                        itemEntity = SteamerBlock.getWorld().dropItem(DropLocation, itemStack)
                        itemEntity.setPickupDelay(20)
                except Exception as e:
                    MiniMessageUtils.sendMessage(Console, str(e))
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def CleanupSteamerTempData(FileKey):

    try:
        players_to_remove = []
        for player_uuid, steamer_data in SteamerTempData.items():
            if steamer_data.get("steamerKey") == FileKey:
                players_to_remove.append(player_uuid)
        for player_uuid in players_to_remove:
            if player_uuid in SteamerTempData:
                del SteamerTempData[player_uuid]
            if player_uuid in SteamerInventories:
                del SteamerInventories[player_uuid]
        if FileKey in SteamerProcessingData:
            del SteamerProcessingData[FileKey]
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def ChoppingBoardInteraction(Event, EventType):

    ClickPlayer = EventUtils.getPlayer(Event, EventType)
    ClickBlock = EventUtils.getInteractionBlock(Event, EventType)
    if not ClickBlock:
        return False
    if not EventUtils.isTargetBlock(ClickBlock, "ChoppingBoard"):
        return False
    FileKey = GetFileKey(ClickBlock)
    ChoppingBoardDelay = Config.getDouble("Setting.ChoppingBoard.Delay", 1.0)
    if ChoppingBoardDelay > 0:
        LastInteractTime = Data.getLong("ChoppingBoard." + FileKey + ".LastInteractTime", 0)
        CurrentTime = System.currentTimeMillis()
        if CurrentTime - LastInteractTime < ChoppingBoardDelay * 1000:
            MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.ChoppingBoardTooFast"))
            EventUtils.setCancelled(Event, EventType, True)
            return True
    MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
    if not EventUtils.isMainHand(Event, EventType):
        return False
    if EventUtils.isRightClick(Event, EventType):
        if not EventUtils.isTargetBlock(ClickBlock, "ChoppingBoard"):
            return False
        StoredItemIdentifier = Data.getString("ChoppingBoard." + FileKey + ".Input")
        if StoredItemIdentifier:
            StoredItem = ToolUtils.createItemStack(StoredItemIdentifier)
            DisplayLocation = CalculateDisplayLocation(ClickBlock, "ChoppingBoard", StoredItem)
        else:
            DisplayLocation = CalculateDisplayLocation(ClickBlock, "ChoppingBoard", MainHandItem)
        NearbyDisplay = FindNearbyDisplay(DisplayLocation)
        if NearbyDisplay:
            ItemDisplayEntity = NearbyDisplay[0]
            DisplayItem = ItemDisplayEntity.getItemStack()
            if DisplayItem:
                if not MainHandItem or MainHandItem.getType() == Material.AIR:
                    ClickPlayer.getInventory().setItemInMainHand(DisplayItem.clone())
                else:
                    GiveItemToPlayer(ClickPlayer, DisplayItem.clone())
            ItemDisplayEntity.remove()
        Data.set("ChoppingBoard." + FileKey, None)
        Data.save()
        EventUtils.setCancelled(Event, EventType, True)
        return True
    if not EventUtils.isLeftClick(Event, EventType):
        return False
    if not EventUtils.isTargetBlock(ClickBlock, "ChoppingBoard"):
        return False
    if not EventUtils.isSneaking(ClickPlayer, "ChoppingBoard"):
        return False
    if Config.getBoolean("Setting.ChoppingBoard.SpaceRestriction"):
        if ClickBlock.getRelative(BlockFace.UP).getType() != Material.AIR:
            return False
    if not EventUtils.getPermission(ClickPlayer, "cookiecooking.choppingboard.interaction"):
        MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
        EventUtils.setCancelled(Event, EventType, True)
        return False
    Data.set("ChoppingBoard." + FileKey + ".LastInteractTime", System.currentTimeMillis())
    hasExistingDisplay = Data.contains("ChoppingBoard." + FileKey + ".CutCount")
    if MainHandItem and MainHandItem.getType() != Material.AIR:
        if not EventUtils.getPermission(ClickPlayer, "cookiecooking.choppingboard.cut"):
            MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
            EventUtils.setCancelled(Event, EventType, True)
            return False
        if hasExistingDisplay:
            ToolMaterials = ToolUtils.getToolMaterials(Config, "ChoppingBoard", "KitchenKnife")
            isToolValid = False
            for material in ToolMaterials:
                if ToolUtils.isToolItem(MainHandItem, Config, "ChoppingBoard", "KitchenKnife", material):
                    isToolValid = True
                    break
            if isToolValid:
                DisplayLocation = CalculateDisplayLocation(ClickBlock, "ChoppingBoard", MainHandItem)
                ItemDisplayEntities = FindNearbyDisplay(DisplayLocation)
                if not ItemDisplayEntities:
                    return False
                ItemDisplayEntity = ItemDisplayEntities[0]
                DisplayItem = ItemDisplayEntity.getItemStack()
                if not DisplayItem:
                    return False
                ItemMaterial = ToolUtils.getItemIdentifier(DisplayItem)
                RecipeKey = ToolUtils.matchConfigKey(ChoppingBoardRecipe, ItemMaterial)
                if not RecipeKey:
                    EventUtils.setCancelled(Event, EventType, True)
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.CannotCut"))
                    MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.RecipeNotFound"), {"Prefix": Prefix, "ItemMaterial": ItemMaterial})
                    return False
                RequiredCuts = ChoppingBoardRecipe.getInt(RecipeKey + ".Count")
                ReplacePermission = ChoppingBoardRecipe.getString(RecipeKey + ".Permission")
                if ReplacePermission and not EventUtils.getPermission(ClickPlayer, ReplacePermission):
                    EventUtils.setCancelled(Event, EventType, True)
                    MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                    return False
                ResultMaterials = ChoppingBoardRecipe.getStringList(RecipeKey + ".Output")
                if not RequiredCuts or RequiredCuts == 0:
                    EventUtils.setCancelled(Event, EventType, True)
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.CannotCut"))
                    return False
                RemoveDurability = ChoppingBoardRecipe.getInt(ItemMaterial + ".Durability")
                RemoveDurability = 1 if RemoveDurability == 0 else RemoveDurability
                MainHandItem.setDurability(MainHandItem.getDurability() + RemoveDurability)
                ClickPlayer.getInventory().setItemInMainHand(MainHandItem)
                CurrentCuts = Data.getInt("ChoppingBoard." + FileKey + ".CutCount", 0)
                CurrentCuts += 1
                Data.set("ChoppingBoard." + FileKey + ".CutCount", CurrentCuts)
                Data.save()
                ParticleLocation = ClickBlock.getLocation().add(0.5, 1.1, 0.5)
                EventUtils.sendParticle("ChoppingBoardCutItem", ParticleLocation)
                DamageChance = None
                DamageValue = None
                RecipeDamagePath = RecipeKey + ".Damage"
                if ChoppingBoardRecipe.contains(RecipeDamagePath):
                    DamageChance = ChoppingBoardRecipe.getInt(RecipeDamagePath + ".Chance")
                    DamageValue = ChoppingBoardRecipe.getInt(RecipeDamagePath + ".Value")
                elif Config.getBoolean("Setting.ChoppingBoard.Damage.Enable"):
                    DamageChance = Config.getInt("Setting.ChoppingBoard.Damage.Chance")
                    DamageValue = Config.getInt("Setting.ChoppingBoard.Damage.Value")
                if DamageChance is not None and DamageValue is not None:
                    if random.randint(1, 100) <= DamageChance:
                        ClickPlayer.damage(DamageValue)
                        MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.ChoppingBoardCutHand"))
                        MiniMessageUtils.sendTitle(ClickPlayer, Config.getString("Messages.Title.CutHand.MainTitle"),
                            Config.getString("Messages.Title.CutHand.SubTitle"), {"Damage": str(DamageValue)})
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.CutAmount"),
                    {"CurrentCount": str(CurrentCuts), "NeedCount": str(RequiredCuts)})
                MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.ChoppingBoardCutItem"))
                if CurrentCuts >= RequiredCuts:
                    if ResultMaterials and len(ResultMaterials) > 0:
                        for ResultMaterial in ResultMaterials:
                            success = ToolUtils.processReward(ResultMaterial, ClickPlayer, forceGive=True)
                            if not success:
                                MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.RewardProcessFailed"), {"Prefix": Prefix, "ResultMaterial": ResultMaterial})
                    ItemDisplayEntity.remove()
                    Data.set("ChoppingBoard." + FileKey, None)
                    Data.save()
                    EventUtils.setCancelled(Event, EventType, True)
                    return True
                EventUtils.setCancelled(Event, EventType, True)
                return True
            else:
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.TakeOffItem"))
                EventUtils.setCancelled(Event, EventType, True)
                return False
        else:
            DisplayItem = MainHandItem.clone()
            DisplayItem.setAmount(1)
            ItemIdentifier = ToolUtils.getItemIdentifier(DisplayItem)
            if MainHandItem.getAmount() > 1:
                MainHandItem.setAmount(MainHandItem.getAmount() - 1)
                ClickPlayer.getInventory().setItemInMainHand(MainHandItem)
            else:
                ClickPlayer.getInventory().setItemInMainHand(None)
            DisplayLocation = CalculateDisplayLocation(ClickBlock, "ChoppingBoard", MainHandItem)
            CreateItemDisplay(DisplayLocation, DisplayItem, "ChoppingBoard")
            MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.ChoppingBoardAddItem"))
            if not Data.contains("ChoppingBoard." + FileKey + ".CutCount"):
                Data.set("ChoppingBoard." + FileKey + ".CutCount", 0)
                Data.set("ChoppingBoard." + FileKey + ".Input", ItemIdentifier)
                Data.set("ChoppingBoard." + FileKey + ".LastInteractTime", System.currentTimeMillis())
                Data.save()
            EventUtils.setCancelled(Event, EventType, True)
            return True
    elif not MainHandItem or MainHandItem.getType() == Material.AIR:
        if hasExistingDisplay:
            StoredItemIdentifier = Data.getString("ChoppingBoard." + FileKey + ".Input")
            if StoredItemIdentifier:
                StoredItem = ToolUtils.createItemStack(StoredItemIdentifier)
                DisplayLocation = CalculateDisplayLocation(ClickBlock, "ChoppingBoard", StoredItem)
            else:
                DisplayLocation = CalculateDisplayLocation(ClickBlock, "ChoppingBoard", MainHandItem)
            ItemDisplayEntities = FindNearbyDisplay(DisplayLocation)
            if ItemDisplayEntities:
                ItemDisplayEntity = ItemDisplayEntities[0]
                DisplayItem = ItemDisplayEntity.getItemStack()
                if DisplayItem:
                    ClickPlayer.getInventory().setItemInMainHand(DisplayItem.clone())
                ItemDisplayEntity.remove()
            Data.set("ChoppingBoard." + FileKey, None)
            Data.save()
            EventUtils.setCancelled(Event, EventType, True)
            return True
    return False

def WokInteraction(Event, EventType):

    ClickPlayer = EventUtils.getPlayer(Event, EventType)
    ClickBlock = EventUtils.getInteractionBlock(Event, EventType)
    if not ClickBlock: return False
    ItemList = []
    if not EventUtils.isMainHand(Event, EventType): return False
    if not EventUtils.isTargetBlock(ClickBlock, "Wok"): return False
    FileKey = GetFileKey(ClickBlock)
    HeatLevel = 0
    BottomBlock = ClickBlock.getRelative(BlockFace.DOWN)
    BottomBlockType = BottomBlock.getType().name()
    HeatControl = Config.get("Setting.Wok.HeatControl").getKeys(False)
    if CraftEngineAvailable:
        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineBlocks
            if CraftEngineBlocks.isCustomBlock(BottomBlock):
                BottomBlockState = CraftEngineBlocks.getCustomBlockState(BottomBlock)
                CraftEngineKey = "craftengine " + str(BottomBlockState)
                if CraftEngineKey in HeatControl:
                    HeatLevel = Config.getInt("Setting.Wok.HeatControl." + CraftEngineKey)
        except:  pass
    if BottomBlockType in HeatControl:
        HeatLevel = Config.getInt("Setting.Wok.HeatControl." + BottomBlockType)
    if not EventUtils.isSneaking(ClickPlayer, "Wok"): return False
    if not EventUtils.getPermission(ClickPlayer, "cookiecooking.wok.interaction"):
        MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
        EventUtils.setCancelled(Event, EventType, True)
        return False
    hasExistingDisplay = False
    wokData = Data.get("Wok")
    if wokData and wokData.contains(FileKey):
        hasExistingDisplay = True
        ItemList = Data.getStringList("Wok." + FileKey + ".Items")
    if EventUtils.isRightClick(Event, EventType):
        MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
        ToolMaterials = ToolUtils.getToolMaterials(Config, "Wok", "Spatula")
        isToolValid = False
        for material in ToolMaterials:
            if ToolUtils.isToolItem(MainHandItem, Config, "Wok", "Spatula", material):
                isToolValid = True
                break
        if not isToolValid:
            return False
        if hasExistingDisplay:
            TotalCount = Data.getInt("Wok." + FileKey + ".Count", 0)
            MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.WokTop"))
            for Item in ItemList:
                Parts = Item.split(" ")
                if len(Parts) >= 4:
                    PluginName, ItemName, Amount, Count = Parts[0], Parts[1], Parts[2], Parts[3]
                    ItemStack = ToolUtils.createItemStack(" ".join(Parts[0:2]))
                    if ItemStack:
                        MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.WokContent"),
                            {"ItemName": ToolUtils.getItemDisplayName(ItemStack), "ItemAmount": Amount, "Count": Count})
            MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.WokDown"), {"Count": TotalCount})
            MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.WokHeatControl"), {"Heat": HeatLevel})
            EventUtils.setCancelled(Event, EventType, True)
            return True
        else:
            MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
            EventUtils.setCancelled(Event, EventType, True)
            return True
    elif EventUtils.isLeftClick(Event, EventType):
        if not EventUtils.getPermission(ClickPlayer, "cookiecooking.wok.stirfry"):
            MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
            EventUtils.setCancelled(Event, EventType, True)
            return False
        MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
        if MainHandItem and MainHandItem.getType() != Material.AIR:
            toolMaterials = ToolUtils.getToolMaterials(Config, "Wok", "Spatula")
            isToolValid = False
            for material in toolMaterials:
                if ToolUtils.isToolItem(MainHandItem, Config, "Wok", "Spatula", material):
                    isToolValid = True
                    break
            if isToolValid:
                if not hasExistingDisplay or not ItemList:
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
                    EventUtils.setCancelled(Event, EventType, True)
                    return True
                LastStirTime = Data.getLong("Wok." + FileKey + ".LastStirTime", 0)
                StirCount = Data.getInt("Wok." + FileKey + ".Count", 0)
                CurrentTime = System.currentTimeMillis()
                if StirCount != 0 and CurrentTime - LastStirTime > Config.getInt("Setting.Wok.TimeOut") * 1000:
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.BurntFood"))
                    EventUtils.setCancelled(Event, EventType, True)
                    return True
                StirFriedTime = Data.getLong("Wok." + FileKey + ".StirFriedTime", 0)
                if StirFriedTime != 0 and CurrentTime - StirFriedTime < Config.getInt("Setting.Wok.Delay") * 1000:
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.StirFriedTooQuickly"))
                    EventUtils.setCancelled(Event, EventType, True)
                    return True
                ParticleLocation = ClickBlock.getLocation().add(0.5, 1.1, 0.5)
                EventUtils.sendParticle("WokStirItem", ParticleLocation)
                Data.set("Wok." + FileKey + ".StirFriedTime", System.currentTimeMillis())
                Data.set("Wok." + FileKey + ".LastStirTime", System.currentTimeMillis())
                StirCount += 1
                if MainHandItem.getDurability() < MainHandItem.getType().getMaxDurability():
                    MainHandItem.setDurability(MainHandItem.getDurability() + 1)
                    ClickPlayer.getInventory().setItemInMainHand(MainHandItem)
                Data.set("Wok." + FileKey + ".Count", StirCount)
                UpdatedItemList = []
                for ItemEntry in ItemList:
                    Parts = ItemEntry.split(" ")
                    if len(Parts) >= 4:
                        ItemType = Parts[0]
                        ItemID = Parts[1]
                        Quantity = int(Parts[2])
                        StirTimes = int(Parts[3]) + 1
                        UpdatedEntry = "{} {} {} {}".format(ItemType, ItemID, Quantity, StirTimes)
                        UpdatedItemList.append(UpdatedEntry)

                Data.set("Wok." + FileKey + ".Items", UpdatedItemList)
                Data.save()
                MiniMessageUtils.sendActionBar(
                    ClickPlayer, Config.getString("Messages.ActionBar.StirCount"), {"Count": StirCount})
                MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.WokStirItem"))
                EventUtils.setCancelled(Event, EventType, True)
                return True
        NeedBowl = Config.getBoolean("Setting.Wok.NeedBowl")
        ShouldAttemptServe = False
        if NeedBowl and MainHandItem and MainHandItem.getType() == Material.BOWL:
            if ToolUtils.getItemIdentifier(MainHandItem) == "minecraft BOWL":
                ShouldAttemptServe = True
        elif not NeedBowl and (not MainHandItem or MainHandItem.getType() == Material.AIR):
            ShouldAttemptServe = True
        if ShouldAttemptServe:
            if not EventUtils.getPermission(ClickPlayer, "cookiecooking.wok.serveout"):
                MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                EventUtils.setCancelled(Event, EventType, True)
                return False
            if GetWokOutput(Data, FileKey, ClickPlayer, ClickBlock, HeatLevel):
                EventUtils.setCancelled(Event, EventType, True)
                return True
        if MainHandItem and MainHandItem.getType() != Material.AIR:
            CurrentItemIdentifier = ToolUtils.getItemIdentifier(MainHandItem)
            if hasExistingDisplay:
                NeedAddItem = False
                DisplayLocation = CalculateDisplayLocation(ClickBlock, "Wok", MainHandItem)
                NearbyDisplays = FindNearbyDisplay(DisplayLocation)
                for Index, ItemEntry in enumerate(ItemList):
                    Parts = ItemEntry.split(" ")
                    if len(Parts) >= 2:
                        ItemTypeID = Parts[0] + " " + Parts[1]
                        if ItemTypeID == CurrentItemIdentifier:
                            CurrentAmount = int(Parts[2]) + 1
                            StirCount = int(Parts[3])
                            ItemList[Index] = ItemTypeID + " " + str(CurrentAmount) + " " + str(StirCount)
                            NeedAddItem = True
                            for Display in NearbyDisplays:
                                if Display and not Display.isDead():
                                    DisplayItem = Display.getItemStack()
                                    if DisplayItem and ToolUtils.getItemIdentifier(DisplayItem) == CurrentItemIdentifier:
                                        DisplayItem.setAmount(CurrentAmount)
                                        Display.setItemStack(DisplayItem)
                                        break
                            break
                if not NeedAddItem:
                    ItemListLength = len(ItemList)
                    ExtraOffset = 0.0001 * ItemListLength
                    ItemList.append(CurrentItemIdentifier + " 1 0")
                    DisplayItem = MainHandItem.clone()
                    DisplayLocation = CalculateDisplayLocation(ClickBlock, "Wok", MainHandItem, ExtraOffset)
                    CreateItemDisplay(DisplayLocation, DisplayItem, "Wok")
                Data.set("Wok." + FileKey + ".Items", list(ItemList))
                Data.save()
            else:
                if not BottomBlockType in HeatControl:
                    return False
                SaveValue = CurrentItemIdentifier + " 1 0"
                Data.set("Wok." + FileKey + ".Items", [SaveValue])
                Data.set("Wok." + FileKey + ".Count", 0)
                Data.save()
                DisplayItem = MainHandItem.clone()
                DisplayLocation = CalculateDisplayLocation(ClickBlock, "Wok", MainHandItem)
                CreateItemDisplay(DisplayLocation, DisplayItem, "Wok")
            MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokAddItem"),
                {"Material": ToolUtils.getItemDisplayName(MainHandItem)})
            RemoveItemToPlayer(ClickPlayer, MainHandItem)
            MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.WokAddItem"))
            EventUtils.setCancelled(Event, EventType, True)
            return True
        else:
            StirCount = Data.getInt("Wok." + FileKey + ".Count", 0)
            if StirCount > 0 and Config.getBoolean("Setting.Wok.Damage.Enable"):
                DamageValue = Config.getInt("Setting.Wok.Damage.Value")
                ClickPlayer.damage(DamageValue)
                MiniMessageUtils.playSound(ClickPlayer, Config.get("Setting.Sound.WokScald"))
                MiniMessageUtils.sendTitle(
                    ClickPlayer, Config.getString("Messages.Title.Scald.MainTitle"),
                    Config.getString("Messages.Title.Scald.SubTitle"), {"Damage": str(DamageValue)})
            if not hasExistingDisplay or not ItemList:
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
                EventUtils.setCancelled(Event, EventType, True)
                return True
            LastItemEntry = ItemList[-1]
            Parts = LastItemEntry.split(" ")
            if len(Parts) < 4:
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
                EventUtils.setCancelled(Event, EventType, True)
                return True
            ItemType = Parts[0]
            ItemID = Parts[1]
            Quantity = int(Parts[2])
            StirTimes = int(Parts[3])
            ItemToGive = ToolUtils.createItemStack(" ".join([ItemType, ItemID]))
            if ItemToGive:
                GiveItemToPlayer(ClickPlayer, ItemToGive)
            Quantity -= 1
            if Quantity <= 0:
                ItemList.pop()
                if not ItemList:
                    Data.set("Wok." + FileKey, None)
                else:
                    Data.set("Wok." + FileKey + ".Items", ItemList)
                DisplayLocation = CalculateDisplayLocation(ClickBlock, "Wok", ItemToGive)
                NearbyDisplays = FindNearbyDisplay(DisplayLocation)
                if NearbyDisplays:
                    TargetIdentifier = ToolUtils.getItemIdentifier(ItemToGive)
                    for display in NearbyDisplays:
                        if display and not display.isDead():
                            displayItem = display.getItemStack()
                            if displayItem and ToolUtils.getItemIdentifier(displayItem) == TargetIdentifier:
                                display.remove()
                                break
            else:
                ItemList[-1] = "{} {} {} {}".format(ItemType, ItemID, Quantity, StirTimes)
                Data.set("Wok." + FileKey + ".Items", ItemList)
                DisplayLocation = CalculateDisplayLocation(ClickBlock, "Wok", ItemToGive)
                NearbyDisplays = FindNearbyDisplay(DisplayLocation)
                if NearbyDisplays:
                    TargetIdentifier = ToolUtils.getItemIdentifier(ItemToGive)
                    for display in NearbyDisplays:
                        if display and not display.isDead():
                            displayItem = display.getItemStack()
                            if displayItem and ToolUtils.getItemIdentifier(displayItem) == TargetIdentifier:
                                displayItem.setAmount(Quantity)
                                display.setItemStack(displayItem)
                                break
            Data.save()
            EventUtils.setCancelled(Event, EventType, True)
            return True
    return False

def GetWokOutput(DataFile, FileKey, ClickPlayer, ClickBlock, HeatLevel=0):

    MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
    DataStirFryAmount = DataFile.getInt("Wok." + FileKey + ".Count")
    if DataStirFryAmount == 0:
        return False
    ItemList = DataFile.getStringList("Wok." + FileKey + ".Items")
    if not ItemList:
        MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.WokNoItem"))
        return False
    RecipeKeys = WokRecipe.getKeys(False)
    for RecipeKey in RecipeKeys:
        RecipePermission = WokRecipe.getString(RecipeKey + ".Permission")
        if RecipePermission and not EventUtils.getPermission(ClickPlayer, RecipePermission):
            continue
        RecipeHeat = WokRecipe.getInt(RecipeKey + ".HeatControl", 0)
        if RecipeHeat != int(HeatLevel) and int(HeatLevel) != 0:
            continue
        RecipeItemList = WokRecipe.getStringList(RecipeKey + ".Item")
        if len(ItemList) != len(RecipeItemList):
            continue
        Match = True
        GreaterThan = 0
        LessThan = 0
        Tolerance = WokRecipe.getInt(RecipeKey + ".FaultTolerance", 0)
        Amount = 0
        for Idx in range(len(ItemList)):
            ItemEntry = ItemList[Idx].split(" ")
            RecipeEntry = RecipeItemList[Idx].split(" ")
            if len(ItemEntry) >= 2 and len(RecipeEntry) >= 2:
                item_namespace = ItemEntry[0]
                item_id = ItemEntry[1]
                recipe_namespace = RecipeEntry[0]
                recipe_id = RecipeEntry[1]
                if item_namespace.lower() == "minecraft" and recipe_namespace.lower() == "minecraft":
                    if item_id.lower() != recipe_id.lower():
                        Match = False
                        break
                else:
                    if item_namespace != recipe_namespace or item_id != recipe_id:
                        Match = False
                        break
            else:
                if ItemList[Idx] != RecipeItemList[Idx]:
                    Match = False
                    break
            RecipeStirFry = RecipeEntry[3] if len(RecipeEntry) >= 4 else "0"
            ItemStirFry = int(ItemEntry[3]) if len(ItemEntry) >= 4 else 0
            if "-" in RecipeStirFry:
                try:
                    MinValue, MaxValue = map(int, RecipeStirFry.split("-"))
                    if ItemStirFry < MinValue:
                        LessThan += 1
                        Amount += 1
                    elif ItemStirFry > MaxValue:
                        GreaterThan += 1
                        Amount += 1
                except ValueError:
                    pass
            else:
                try:
                    RequiredStirFry = int(RecipeStirFry)
                    if ItemStirFry < RequiredStirFry:
                        LessThan += 1
                        Amount += 1
                    elif ItemStirFry > RequiredStirFry:
                        GreaterThan += 1
                        Amount += 1
                except ValueError:
                    pass
            if Amount > Tolerance:
                Match = False
                break
        if Match:
            RemoveItemToPlayer(ClickPlayer, MainHandItem)
            StirFryAmount = WokRecipe.get(RecipeKey + ".Count")
            if isinstance(StirFryAmount, basestring) and "-" in StirFryAmount:
                try:
                    minValue, maxValue = map(int, StirFryAmount.split("-"))
                    MaxValue = max(minValue, maxValue)
                    MinValue = min(minValue, maxValue)
                except ValueError:
                    MaxValue = WokRecipe.getInt(RecipeKey + ".Count")
                    MinValue = MaxValue
            else:
                MaxValue = WokRecipe.getInt(RecipeKey + ".Count")
                MinValue = MaxValue
            LastStirTime = DataFile.getLong("Wok." + FileKey + ".LastStirTime", 0)
            CurrentTime = System.currentTimeMillis()
            if CurrentTime - LastStirTime > Config.getInt("Setting.Wok.TimeOut") * 1000:
                BurntItem = WokRecipe.getString(RecipeKey + ".BURNT")
                OutputWokItem(RecipeKey, BurntItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.BurntFood"))
                return True
            if DataStirFryAmount < MinValue:
                RawItem = WokRecipe.getString(RecipeKey + ".RAW")
                OutputWokItem(RecipeKey, RawItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.RawFood"))
                return True
            elif DataStirFryAmount > MaxValue:
                BurntItem = WokRecipe.getString(RecipeKey + ".BURNT")
                OutputWokItem(RecipeKey, BurntItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.BurntFood"))
                return True
            if Config.getBoolean("Setting.Wok.Failure.Enable"):
                Chance = Config.getInt("Setting.Wok.Failure.Chance")
                if random.randint(1, 100) <= Chance:
                    ErrorRecipe = Config.getString("Setting.Wok.Failure.Type")
                    OutputWokItem(RecipeKey, ErrorRecipe, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                    MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.FailureRecipe"))
                    return True
            if Amount <= Tolerance:
                OutputWokItem(RecipeKey, RecipeKey, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.SuccessRecipe"))
                return True
            elif GreaterThan > LessThan:
                BurntItem = WokRecipe.getString(RecipeKey + ".BURNT")
                OutputWokItem(RecipeKey, BurntItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.BurntFood"))
                return True
            elif LessThan > GreaterThan:
                RawItem = WokRecipe.getString(RecipeKey + ".RAW")
                OutputWokItem(RecipeKey, RawItem, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
                MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.RawFood"))
                return True
        if not Match:
            MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Debug.ItemIdMismatch"),
                {"Prefix": Prefix, "ItemNamespace": item_namespace, "ItemId": item_id, "RecipeNamespace": recipe_namespace, "RecipeId": recipe_id})
    if Config.getBoolean("Setting.Wok.Failure.Enable"):
        RemoveItemToPlayer(ClickPlayer, MainHandItem)
        ErrorRecipe = Config.getString("Setting.Wok.Failure.Type")
        OutputWokItem("Invalid", ErrorRecipe, WokRecipe, ClickPlayer, DataFile, FileKey, ClickBlock)
        MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.ErrorRecipe"))
        return True
    return False

def OutputWokItem(RecipeKey, Item, RecipeConfig, ClickPlayer, DataFile, FileKey, ClickBlock):

    GiveAmount = RecipeConfig.getInt(RecipeKey + ".Amount", 1)
    ITEM = ToolUtils.createItemStack(Item, GiveAmount)
    if ITEM is None:
        return
    if Config.getBoolean("Setting.Wok.Drop"):
        DropLocation = ClickBlock.getLocation().add(0.5, 1.0, 0.5)
        ItemEntity = ClickBlock.getWorld().dropItem(DropLocation, ITEM)
        ItemEntity.setPickupDelay(20)
    else:
        GiveItemToPlayer(ClickPlayer, ITEM)
    DataFile.set("Wok." + FileKey, None)
    DataFile.save()
    DisplayLocation = CalculateDisplayLocation(ClickBlock, "Wok")
    NearbyDisplays = FindNearbyDisplay(DisplayLocation)
    if NearbyDisplays:
        for display in NearbyDisplays:
            if display and not display.isDead():
                display.remove()

GrinderTask = None

def GrinderInteraction(Event, EventType):

    ClickPlayer = EventUtils.getPlayer(Event, EventType)
    ClickBlock = EventUtils.getInteractionBlock(Event, EventType)
    MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
    if not ClickBlock or not MainHandItem or MainHandItem.getType() == Material.AIR: return False
    if not EventUtils.isLeftClick(Event, EventType) or not EventUtils.isSneaking(ClickPlayer, "Grinder"): return False
    if not EventUtils.isTargetBlock(ClickBlock, "Grinder"): return False
    FileKey = GetFileKey(ClickBlock)
    if Data.contains("Grinder." + FileKey):
        MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.OnRunGrinder"))
        EventUtils.setCancelled(Event, EventType, True)
        return True
    ItemIdentifier = ToolUtils.getItemIdentifier(MainHandItem)
    RecipeKey = ToolUtils.matchConfigKey(GrinderRecipe, ItemIdentifier)
    if not RecipeKey:
        MiniMessageUtils.sendActionBar(ClickPlayer, Config.getString("Messages.ActionBar.NoGrinderReplace"))
        EventUtils.setCancelled(Event, EventType, True)
        return False
    RecipePermission = GrinderRecipe.getString(RecipeKey + ".Permission")
    if not EventUtils.getPermission(ClickPlayer, "cookiecooking.grinder.interaction"):
        MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
        EventUtils.setCancelled(Event, EventType, True)
        return False
    if RecipePermission and not EventUtils.getPermission(ClickPlayer, RecipePermission):
        EventUtils.setCancelled(Event, EventType, True)
        MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
        return False
    RemoveItemToPlayer(ClickPlayer, MainHandItem)
    GrindTime = GrinderRecipe.getInt(RecipeKey + ".GrindingTime", 5)
    CurrentTime = System.currentTimeMillis()
    Data.set("Grinder." + FileKey + ".StartTime", CurrentTime)
    Data.set("Grinder." + FileKey + ".Input", RecipeKey)
    Data.set("Grinder." + FileKey + ".Player", ClickPlayer.getName())
    Data.save()
    MainTitle = Config.getString("Messages.Title.Grinder.MainTitle")
    SubTitle = Config.getString("Messages.Title.Grinder.SubTitle")
    MiniMessageUtils.sendTitle(ClickPlayer, MainTitle, SubTitle, {"Time": GrindTime})
    StartGrinderCheckTask()
    EventUtils.setCancelled(Event, EventType, True)
    return True

def StartGrinderCheckTask():

    global GrinderTask
    if GrinderTask is not None:
        try:
            ps.scheduler.stopTask(GrinderTask)
        except:
            pass
        GrinderTask = None
    grinderSection = Data.getConfigurationSection("Grinder")
    if grinderSection is None:
        return
    grinderKeys = grinderSection.getKeys(False)
    if not grinderKeys:
        return
    CheckDelay = Config.getInt("Setting.Grinder.CheckDelay", 20)
    GrinderTask = ps.scheduler.scheduleRepeatingTask(CheckAllGrinders, CheckDelay, CheckDelay)

def CheckAllGrinders():

    global GrinderTask
    grinderSection = Data.getConfigurationSection("Grinder")
    if grinderSection is None:
        if GrinderTask is not None:
            try:
                ps.scheduler.stopTask(GrinderTask)
            except:
                pass
            GrinderTask = None
        return
    grinderKeys = grinderSection.getKeys(False)
    if not grinderKeys:
        if GrinderTask is not None:
            try:
                ps.scheduler.stopTask(GrinderTask)
            except:
                GrinderTask = None
        return
    for grinderKey in grinderKeys:
        CheckSingleGrinder(grinderKey)

def CheckSingleGrinder(FileKey):

    if not Data.contains("Grinder." + FileKey):
        return
    InputItem = Data.getString("Grinder." + FileKey + ".Input")
    if not InputItem:
        Data.set("Grinder." + FileKey, None)
        Data.save()
        return
    GrindTime = GrinderRecipe.getInt(InputItem + ".GrindingTime", 5)
    OutputItems = GrinderRecipe.getStringList(InputItem + ".Output")
    StartTime = Data.getLong("Grinder." + FileKey + ".StartTime")
    CurrentTime = System.currentTimeMillis()
    Parts = FileKey.split(",")
    BlockX = int(Parts[0])
    BlockY = int(Parts[1])
    BlockZ = int(Parts[2])
    WorldName = Parts[3]
    World = Bukkit.getWorld(WorldName)
    BlockLocation = Location(World, BlockX, BlockY, BlockZ)
    PlayerName = Data.getString("Grinder." + FileKey + ".Player")
    Player = Bukkit.getPlayer(PlayerName)
    if CurrentTime - StartTime >= GrindTime * 1000:
        if len(Parts) < 4:
            Data.set("Grinder." + FileKey, None)
            Data.save()
            return
        if World is None:
            Data.set("Grinder." + FileKey, None)
            Data.save()
            return
        for OutputItem in OutputItems:
            if ToolUtils.processReward(OutputItem, Player):
                continue
        Data.set("Grinder." + FileKey, None)
        Data.save()
    else:
        EventUtils.sendParticle("GrinderStart", BlockLocation.add(0.5, 1.0, 0.5))
        SoundName = Config.getString("Setting.Sound.GrinderStart")
        SoundLocation = BlockLocation.add(0.5, 0.5, 0.5)
        MiniMessageUtils.playSound(SoundLocation, SoundName)

CheckAllGrinders()

SteamerTempData = {}
SteamerInventories = {}
SteamerTask = None
SteamerProcessingData = {}

def SteamerInteraction(Event, EventType):

    ClickPlayer = EventUtils.getPlayer(Event, EventType)
    ClickBlock = EventUtils.getInteractionBlock(Event, EventType)
    if not ClickBlock:  return False
    if EventUtils.isTargetBlock(ClickBlock, "Steamer"):
        if not EventUtils.isMainHand(Event, EventType):  return False
        if not EventUtils.isRightClick(Event, EventType):  return False
        if not EventUtils.isSneaking(ClickPlayer, "Steamer"):    return False
        BottomBlock = ClickBlock.getRelative(BlockFace.DOWN)
        if not isHeatSourceBlock(BottomBlock):
            return False
        if not EventUtils.getPermission(ClickPlayer, "cookiecooking.steamer.interaction"):
            MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
            EventUtils.setCancelled(Event, EventType, True)
            return True
        EventUtils.setCancelled(Event, EventType, True)
        OpenSteamerGUI(ClickPlayer, ClickBlock)
        return True


    elif isHeatSourceBlock(ClickBlock):
        TopBlock = ClickBlock.getRelative(BlockFace.UP)
        if not EventUtils.isTargetBlock(TopBlock, "Steamer"): return False
        MainHandItem = ClickPlayer.getInventory().getItemInMainHand()
        if (not MainHandItem or MainHandItem.getType() == Material.AIR) and EventUtils.isRightClick(Event, EventType):
            if not EventUtils.isSneaking(ClickPlayer, "Steamer"):  return False
            EventUtils.setCancelled(Event, EventType, True)
            SteamerFileKey = GetFileKey(TopBlock)
            return ShowSteamerInfo(ClickPlayer, SteamerFileKey)
        if not EventUtils.isMainHand(Event, EventType):  return False
        if not EventUtils.isRightClick(Event, EventType):  return False
        if not EventUtils.isSneaking(ClickPlayer, "Steamer"):  return False
        if not MainHandItem or MainHandItem.getType() == Material.AIR:
            EventUtils.setCancelled(Event, EventType, True)
            return True
        ItemIdentifier = ToolUtils.getItemIdentifier(MainHandItem)
        IsMoistureItem = False
        MoistureValue = 0
        OutputItem = None
        MoistureConfig = Config.getStringList("Setting.Steamer.Moisture")
        for moistureEntry in MoistureConfig:
            try:
                parts = moistureEntry.split(" & ")
                if len(parts) >= 3:
                    inputItem = parts[0].strip()
                    if inputItem.upper() == ItemIdentifier.upper():
                        IsMoistureItem = True
                        MoistureValue = int(parts[2].strip())
                        OutputItem = parts[1].strip() if len(parts) > 1 else "AIR"
                        break
                    ItemParts = ItemIdentifier.split(" ")
                    if len(ItemParts) >= 2:
                        ItemID = ItemParts[1]
                        configParts = inputItem.split(" ")
                        if len(configParts) >= 2:
                            configID = configParts[1]
                            if configID.upper() == ItemID.upper():
                                IsMoistureItem = True
                                MoistureValue = int(parts[2].strip())
                                OutputItem = parts[1].strip() if len(parts) > 1 else "AIR"
                                break
            except Exception as e:
                continue
        if IsMoistureItem:
            if not EventUtils.getPermission(ClickPlayer, "cookiecooking.steamer.addmoisture"):
                MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                EventUtils.setCancelled(Event, EventType, True)
                return True
            EventUtils.setCancelled(Event, EventType, True)
            SteamerFileKey = GetFileKey(TopBlock)
            return AddMoistureToSteamer(ClickPlayer, MainHandItem, MoistureValue, OutputItem, SteamerFileKey)
        IsValidFuel = False
        FuelDuration = 0
        FuelConfig = Config.getConfigurationSection("Setting.Steamer.Fuel")
        if FuelConfig:
            MatchedFuelKey = ToolUtils.matchConfigKey(FuelConfig, ItemIdentifier)
            if MatchedFuelKey:
                IsValidFuel = True
                FuelDuration = FuelConfig.getInt(MatchedFuelKey)
            else:
                ItemParts = ItemIdentifier.split(" ")
                if len(ItemParts) >= 2:
                    ItemIDOnly = ItemParts[1]
                    for fuelKey in FuelConfig.getKeys(False):
                        if ":" in fuelKey:
                            namespace, key_id = fuelKey.split(":", 1)
                            if key_id.upper() == ItemIDOnly.upper():
                                IsValidFuel = True
                                FuelDuration = FuelConfig.getInt(fuelKey)
                                break
                        else:
                            if fuelKey.upper() == ItemIDOnly.upper():
                                IsValidFuel = True
                                FuelDuration = FuelConfig.getInt(fuelKey)
                                break
        if IsValidFuel:
            if not EventUtils.getPermission(ClickPlayer, "cookiecooking.steamer.addfuel"):
                MiniMessageUtils.sendMessage(ClickPlayer, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                EventUtils.setCancelled(Event, EventType, True)
                return True
            EventUtils.setCancelled(Event, EventType, True)
            SteamerFileKey = GetFileKey(TopBlock)
            return AddFuelToHeatSource(ClickPlayer, MainHandItem, FuelDuration, SteamerFileKey, ClickBlock)
        EventUtils.setCancelled(Event, EventType, True)
        return True
    return False

def ShowSteamerInfo(Player, SteamerFileKey):

    try:
        CoolingTimePath = "Steamer." + SteamerFileKey + ".CoolingTime"
        MoisturePath = "Steamer." + SteamerFileKey + ".Moisture"
        SteamPath = "Steamer." + SteamerFileKey + ".Steam"
        CurrentTime = System.currentTimeMillis()
        CoolingTime = Data.getLong(CoolingTimePath, 0)
        Moisture = Data.getInt(MoisturePath, 0)
        Steam = Data.getInt(SteamPath, 0)
        RemainingBurnTime = 0
        if CoolingTime > CurrentTime:
            RemainingBurnTime = (CoolingTime - CurrentTime) // 1000
        ProgressStatus = CalculateCookingProgress(SteamerFileKey)
        Placeholders = {
            "BurningTime": RemainingBurnTime,
            "Moisture": Moisture,
            "Steam": Steam,
            "Progress": ProgressStatus
        }
        MiniMessageUtils.sendActionBar(Player, Config.getString("Messages.ActionBar.SteamerInfo"), Placeholders)
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def CalculateCookingProgress(SteamerFileKey):

    try:
        SlotsPath = "Steamer." + SteamerFileKey + ".Slots"
        CookingProgressPath = "Steamer." + SteamerFileKey + ".CookingProgress"
        SteamPath = "Steamer." + SteamerFileKey + ".Steam"
        CurrentSteam = Data.getInt(SteamPath, 0)
        if CurrentSteam <= 0:
            if not Data.contains(SlotsPath) or not Data.contains(CookingProgressPath):
                return Config.getString("Messages.NotStarted")
            Slots = Data.getStringList(SlotsPath)
            CookingProgress = Data.getIntegerList(CookingProgressPath)
            AllProgressZero = True
            for progress in CookingProgress:
                if progress > 0:
                    AllProgressZero = False
                    break
            if AllProgressZero:
                return Config.getString("Messages.NotStarted")
        if not Data.contains(SlotsPath) or not Data.contains(CookingProgressPath):
            return Config.getString("Messages.NotStarted")
        Slots = Data.getStringList(SlotsPath)
        CookingProgress = Data.getIntegerList(CookingProgressPath)
        if len(CookingProgress) < len(Slots):
            CookingProgress.extend([0] * (len(Slots) - len(CookingProgress)))
        elif len(CookingProgress) > len(Slots):
            CookingProgress = CookingProgress[:len(Slots)]
        TotalRequiredSteam = 0
        TotalCurrentProgress = 0
        HasValidIngredients = False
        AllItemsCompleted = True
        ActiveItemsCount = 0
        for i in range(len(Slots)):
            if i >= len(CookingProgress):
                continue
            itemIdentifier = Slots[i]
            if itemIdentifier == "AIR":
                continue
            currentItem = None
            isInputItem = False
            RecipeKey = ToolUtils.matchConfigKey(SteamerRecipe, itemIdentifier)
            if RecipeKey:
                isInputItem = True
                currentItem = RecipeKey
            isOutputItem = False
            originalInputItem = None
            if not isInputItem:
                for rKey in SteamerRecipe.getKeys(False):
                    outputItem = SteamerRecipe.getString(rKey + ".Output")
                    if outputItem and outputItem.upper() == itemIdentifier.upper():
                        isOutputItem = True
                        originalInputItem = rKey
                        break
            if not isInputItem and not isOutputItem:
                AllItemsCompleted = False
                continue
            ActiveItemsCount += 1
            HasValidIngredients = True
            TargetRecipeKey = currentItem if isInputItem else originalInputItem
            RecipeSteam = SteamerRecipe.getInt(TargetRecipeKey + ".Steam", 0)
            OutputItem = SteamerRecipe.getString(TargetRecipeKey + ".Output")
            if RecipeSteam <= 0 or not OutputItem:
                AllItemsCompleted = False
                continue
            TotalRequiredSteam += RecipeSteam
            if i < len(CookingProgress):
                CurrentProgress = CookingProgress[i]
                if isOutputItem:
                    TotalCurrentProgress += RecipeSteam
                else:
                    TotalCurrentProgress += min(CurrentProgress, RecipeSteam)
                if isOutputItem or CurrentProgress >= RecipeSteam:
                    pass
                else:
                    AllItemsCompleted = False
            else:
                AllItemsCompleted = False
        if not HasValidIngredients or ActiveItemsCount == 0:
            return Config.getString("Messages.NotStarted")
        if AllItemsCompleted and ActiveItemsCount > 0:
            return Config.getString("Messages.Completed")
        if CurrentSteam <= 0 and TotalCurrentProgress == 0:
            return Config.getString("Messages.NotStarted")
        if TotalRequiredSteam > 0:
            Percentage = (float(TotalCurrentProgress) / TotalRequiredSteam) * 100
            Percentage = max(0, min(100, Percentage))
            FormattedPercentage = "{:.2f}%".format(Percentage)
            return FormattedPercentage
        else:
            return "0.00%"
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return Config.getString("Messages.NotStarted")

def isHeatSourceBlock(Block):

    HeatControlList = Config.getStringList("Setting.Steamer.HeatControl")
    if not HeatControlList: return False
    BlockName = Block.getType().name()
    for heatSource in HeatControlList:
        if heatSource.upper() == BlockName:
            return True
    if CraftEngineAvailable:
        try:
            from net.momirealms.craftengine.bukkit.api import CraftEngineBlocks
            if CraftEngineBlocks.isCustomBlock(Block):
                BlockState = CraftEngineBlocks.getCustomBlockState(Block)
                CraftEngineKey = "craftengine " + str(BlockState)
                for heatSource in HeatControlList:
                    if heatSource == CraftEngineKey:
                        return True
        except:
            pass
    return False

def OpenSteamerGUI(Player, SteamerBlock):

    try:
        InventoryTypeStr = Config.getString("Setting.Steamer.OpenInventory.Type", "HOPPER")
        TitleText = Config.getString("Setting.Steamer.OpenInventory.Title", u"<dark_gray>Steamer")
        SlotCount = Config.getInt("Setting.Steamer.OpenInventory.Slot", 9)
        TargetInventoryType = None
        try:
            TargetInventoryType = InventoryType.valueOf(InventoryTypeStr)
        except:
            TargetInventoryType = InventoryType.HOPPER
        TitleComponent = MiniMessageUtils.processMessage(TitleText)
        if TargetInventoryType == InventoryType.CHEST:
            if SlotCount < 9: SlotCount = 9
            if SlotCount > 54: SlotCount = 54
            if SlotCount % 9 != 0:
                SlotCount = (SlotCount // 9) * 9
            if SlotCount < 9: SlotCount = 9
            Inventory = Bukkit.createInventory(None, SlotCount, TitleComponent)
        else:
            Inventory = Bukkit.createInventory(None, TargetInventoryType, TitleComponent)
            SlotCount = Inventory.getSize()
        SteamerKey = GetFileKey(SteamerBlock)
        PlayerUUID = Player.getUniqueId().toString()
        SteamerTempData[PlayerUUID] = {
            "steamerKey": SteamerKey,
            "block": SteamerBlock,
            "inventoryType": InventoryTypeStr,
            "slotCount": SlotCount
        }
        SteamerInventories[PlayerUUID] = Inventory
        LoadSteamerInventory(SteamerKey, Inventory)
        Player.openInventory(Inventory)
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def LoadSteamerInventory(SteamerKey, Inventory):

    try:
        SlotsPath = "Steamer." + SteamerKey + ".Slots"
        CookingProgressPath = "Steamer." + SteamerKey + ".CookingProgress"
        if Data.contains(SlotsPath):
            SlotItems = Data.getStringList(SlotsPath)
            CookingProgress = []
            if Data.contains(CookingProgressPath):
                CookingProgress = Data.getIntegerList(CookingProgressPath)
            else:
                CookingProgress = [0] * len(SlotItems)
            if len(CookingProgress) < len(SlotItems):
                CookingProgress.extend([0] * (len(SlotItems) - len(CookingProgress)))
            elif len(CookingProgress) > len(SlotItems):
                CookingProgress = CookingProgress[:len(SlotItems)]
            for i, itemIdentifier in enumerate(SlotItems):
                if i >= Inventory.getSize():
                    break
                if itemIdentifier != "AIR":
                    ItemStack = ToolUtils.createItemStack(itemIdentifier, 1)
                    if ItemStack:
                        Inventory.setItem(i, ItemStack)
            Data.set(CookingProgressPath, CookingProgress)
            Data.save()
        else:
            Data.set(CookingProgressPath, [])
            Data.save()
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def SteamerInventoryClose(Event):

    Player = Event.getPlayer()
    PlayerUUID = Player.getUniqueId().toString()
    if PlayerUUID not in SteamerTempData:
        return
    Inventory = Event.getInventory()
    SteamerData = SteamerTempData[PlayerUUID]
    SteamerKey = SteamerData["steamerKey"]
    ProcessExcessSteamerItems(Player, Inventory)
    SaveSteamerInventory(SteamerKey, Inventory)
    if PlayerUUID in SteamerTempData:
        del SteamerTempData[PlayerUUID]
    if PlayerUUID in SteamerInventories:
        del SteamerInventories[PlayerUUID]
    slotsPath = "Steamer." + SteamerKey + ".Slots"
    if Data.contains(slotsPath):
        slots = Data.getStringList(slotsPath)
        hasValidIngredients = False
        for itemIdentifier in slots:
            if itemIdentifier != "AIR" and SteamerRecipe.contains(itemIdentifier):
                hasValidIngredients = True
                break
        if hasValidIngredients:
            StartSteamerTimer()

ps.listener.registerListener(SteamerInventoryClose, InventoryCloseEvent)

def ProcessExcessSteamerItems(Player, Inventory):

    try:
        for slot in range(Inventory.getSize()):
            item = Inventory.getItem(slot)
            if item and item.getType() != Material.AIR and item.getAmount() > 1:
                excess_amount = item.getAmount() - 1
                excess_item = item.clone()
                excess_item.setAmount(excess_amount)
                item.setAmount(1)
                Inventory.setItem(slot, item)
                ReturnExcessItemsToPlayer(Player, excess_item)
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def ReturnExcessItemsToPlayer(Player, ExcessItem):

    try:
        if Player.getInventory().firstEmpty() != -1:
            Player.getInventory().addItem(ExcessItem)
        else:
            drop_location = Player.getLocation()
            Player.getWorld().dropItemNaturally(drop_location, ExcessItem)
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def SaveSteamerInventory(SteamerKey, Inventory):

    try:
        OldSlotsPath = "Steamer." + SteamerKey + ".Slots"
        OldCookingProgressPath = "Steamer." + SteamerKey + ".CookingProgress"

        OldSlots = []
        OldCookingProgress = []
        if Data.contains(OldSlotsPath):
            OldSlots = Data.getStringList(OldSlotsPath)
        if Data.contains(OldCookingProgressPath):
            OldCookingProgress = Data.getIntegerList(OldCookingProgressPath)
        NewSlotItems = []
        NewCookingProgress = []
        for i in range(Inventory.getSize()):
            Item = Inventory.getItem(i)
            if Item and Item.getType() != Material.AIR:
                ItemIdentifier = ToolUtils.getItemIdentifier(Item)
                NewSlotItems.append(ItemIdentifier)
                if i < len(OldCookingProgress) and i < len(OldSlots) and OldSlots[i] == ItemIdentifier:
                    NewCookingProgress.append(OldCookingProgress[i])
                else:
                    NewCookingProgress.append(0)
            else:
                NewSlotItems.append("AIR")
                NewCookingProgress.append(0)
        Data.set(OldSlotsPath, NewSlotItems)
        Data.set(OldCookingProgressPath, NewCookingProgress)
        Data.save()
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def AddFuelToHeatSource(Player, FuelItem, FuelDuration, SteamerFileKey, HeatSourceBlock):

    try:
        CurrentTime = System.currentTimeMillis()
        FuelDurationMs = FuelDuration * 1000
        CoolingTimePath = "Steamer." + SteamerFileKey + ".CoolingTime"
        CurrentCoolingTime = Data.getLong(CoolingTimePath, 0)
        if CurrentCoolingTime > CurrentTime:
            NewCoolingTime = CurrentCoolingTime + FuelDurationMs
        else:
            NewCoolingTime = CurrentTime + FuelDurationMs
        Data.set(CoolingTimePath, NewCoolingTime)
        Data.save()
        RemoveItemToPlayer(Player, FuelItem)
        RemainingSeconds = (NewCoolingTime - CurrentTime) // 1000
        IgniteHeatSourceBlock(HeatSourceBlock, RemainingSeconds)
        StartSteamerTimer()
        FuelName = ToolUtils.getItemDisplayName(FuelItem)
        MiniMessageUtils.sendActionBar(Player, Config.getString("Messages.ActionBar.AddFuel"),
            {"Item": FuelName, "Second": str(RemainingSeconds)})
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def AddMoistureToSteamer(Player, MoistureItem, MoistureValue, OutputItem, SteamerFileKey):

    try:
        MoisturePath = "Steamer." + SteamerFileKey + ".Moisture"
        CurrentMoisture = Data.getInt(MoisturePath, 0)
        NewMoisture = CurrentMoisture + MoistureValue
        Data.set(MoisturePath, NewMoisture)
        Data.save()
        RemoveItemToPlayer(Player, MoistureItem)
        if OutputItem and OutputItem != "AIR":
            OutputItemStack = ToolUtils.createItemStack(OutputItem, 1)
            if OutputItemStack:
                GiveItemToPlayer(Player, OutputItemStack)
        if NewMoisture > 0:
            StartSteamerTimer()
        ItemName = ToolUtils.getItemDisplayName(MoistureItem)
        MiniMessageUtils.sendActionBar(Player, Config.getString("Messages.ActionBar.AddMoisture"),
            {"Item": ItemName, "Moisture": str(MoistureValue), "Total": str(NewMoisture)})
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def IgniteHeatSourceBlock(HeatSourceBlock, RemainingSeconds):

    try:
        blockType = HeatSourceBlock.getType()
        if blockType == Material.CAMPFIRE or blockType == Material.SOUL_CAMPFIRE:
            blockData = HeatSourceBlock.getBlockData()
            if hasattr(blockData, 'setLit'):
                blockData.setLit(True)
                HeatSourceBlock.setBlockData(blockData)
        elif blockType in [Material.FURNACE, Material.BLAST_FURNACE, Material.SMOKER]:
            furnaceState = HeatSourceBlock.getState()
            if hasattr(furnaceState, 'setBurnTime'):
                furnaceState.setBurnTime(RemainingSeconds * 20)
                furnaceState.update()
        HeatSourceBlock.getState().update()
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def StartSteamerTimer():

    global SteamerTask
    if SteamerTask is not None:
        try:
            ps.scheduler.stopTask(SteamerTask)
        except:
            pass
    SteamerTask = ps.scheduler.scheduleRepeatingTask(ProcessAllSteamers, 20, 20)

def ProcessAllSteamers():

    global SteamerTask
    try:
        steamerSection = Data.getConfigurationSection("Steamer")
        if steamerSection is None:
            if SteamerTask is not None:
                try:
                    ps.scheduler.stopTask(SteamerTask)
                    SteamerTask = None
                except:
                    pass
            return
        steamerKeys = steamerSection.getKeys(False)
        if not steamerKeys:
            if SteamerTask is not None:
                try:
                    ps.scheduler.stopTask(SteamerTask)
                    SteamerTask = None
                except:
                    pass
            return
        currentTime = System.currentTimeMillis()
        hasActiveSteamer = False
        for steamerKey in steamerKeys:
            coolingTimePath = "Steamer." + steamerKey + ".CoolingTime"
            coolingTime = Data.getLong(coolingTimePath, 0)
            if coolingTime > 0 and currentTime >= coolingTime:
                ExtinguishHeatSource(steamerKey)
                Data.set(coolingTimePath, 0)
                Data.save()
            if coolingTime > currentTime:
                if ProcessSteamProduction(steamerKey):
                    hasActiveSteamer = True
            if ProcessSteamConsumptionAndCooking(steamerKey):
                hasActiveSteamer = True
        if not hasActiveSteamer and SteamerTask is not None:
            try:
                ps.scheduler.stopTask(SteamerTask)
                SteamerTask = None
            except:
                pass
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))

def ProcessSingleSteamer(steamerKey, currentTime):

    try:
        coolingTimePath = "Steamer." + steamerKey + ".CoolingTime"
        coolingTime = Data.getLong(coolingTimePath, 0)
        shouldExtinguish = False
        if coolingTime > 0 and currentTime >= coolingTime:
            ExtinguishHeatSource(steamerKey)
            Data.set(coolingTimePath, 0)
            Data.save()
            shouldExtinguish = True
        isActive = False
        if coolingTime > currentTime:
            if ProcessSteamProduction(steamerKey):
                isActive = True
        if ProcessSteamConsumptionAndCooking(steamerKey):
            isActive = True
        steamPath = "Steamer." + steamerKey + ".Steam"
        currentSteam = Data.getInt(steamPath, 0)
        if shouldExtinguish and currentSteam > 0:
            isActive = True
        return isActive
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def ProcessSteamConsumptionAndCooking(steamerKey):

    try:
        steamPath = "Steamer." + steamerKey + ".Steam"
        currentSteam = Data.getInt(steamPath, 0)
        resetToZero = Config.getBoolean("Setting.Steamer.ResetToZero", True)
        DataChanged = False
        if currentSteam <= 0 and resetToZero:
            return False
        steamConversionEfficiency = Config.getInt("Setting.Steamer.SteamConversionEfficiency", 1)
        steamConsumptionEfficiency = Config.getInt("Setting.Steamer.SteamConsumptionEfficiency", 1)
        slotsPath = "Steamer." + steamerKey + ".Slots"
        cookingProgressPath = "Steamer." + steamerKey + ".CookingProgress"
        if not Data.contains(slotsPath):
            newSteam = max(0, currentSteam - steamConsumptionEfficiency)
            if newSteam != currentSteam:
                Data.set(steamPath, newSteam)
                Data.save()
            return newSteam > 0
        slots = Data.getStringList(slotsPath)
        cookingProgress = []
        if Data.contains(cookingProgressPath):
            cookingProgress = Data.getIntegerList(cookingProgressPath)
        else:
            cookingProgress = [0] * len(slots)
            DataChanged = True
        if len(cookingProgress) < len(slots):
            cookingProgress.extend([0] * (len(slots) - len(cookingProgress)))
            DataChanged = True
        elif len(cookingProgress) > len(slots):
            cookingProgress = cookingProgress[:len(slots)]
            DataChanged = True
        validIngredients = 0
        totalIngredientConsumption = 0
        for i, itemIdentifier in enumerate(slots):
            if itemIdentifier != "AIR":
                RecipeKey = ToolUtils.matchConfigKey(SteamerRecipe, itemIdentifier)
                if RecipeKey:
                    validIngredients += 1
                    totalIngredientConsumption += steamConversionEfficiency
        totalSteamConsumption = steamConsumptionEfficiency + totalIngredientConsumption
        if currentSteam < totalSteamConsumption:
            availableForIngredients = max(0, currentSteam - steamConsumptionEfficiency)
            if availableForIngredients <= 0:
                newSteam = 0
                Data.set(steamPath, newSteam)
                Data.save()
                return False
            actualIngredientConsumption = min(availableForIngredients, totalIngredientConsumption)
            newSteam = max(0, currentSteam - steamConsumptionEfficiency - actualIngredientConsumption)
            Data.set(steamPath, newSteam)
            DataChanged = True
            if totalIngredientConsumption > 0:
                progressRatio = float(actualIngredientConsumption) / float(totalIngredientConsumption)
                for i, itemIdentifier in enumerate(slots):
                    if i >= len(cookingProgress): continue
                    if itemIdentifier != "AIR":
                        RecipeKey = ToolUtils.matchConfigKey(SteamerRecipe, itemIdentifier)
                        if RecipeKey:
                            additionalProgress = int(steamConversionEfficiency * progressRatio)
                            MaxSteam = SteamerRecipe.getInt(RecipeKey + ".Steam", 0)
                            NewProgress = min(cookingProgress[i] + additionalProgress, MaxSteam)
                            if cookingProgress[i] != NewProgress:
                                cookingProgress[i] = NewProgress
                                DataChanged = True
        else:
            newSteam = currentSteam - totalSteamConsumption
            Data.set(steamPath, newSteam)
            DataChanged = True
            for i in range(len(slots)):
                if i >= len(cookingProgress): continue
                itemIdentifier = slots[i]
                if itemIdentifier == "AIR": continue
                RecipeKey = ToolUtils.matchConfigKey(SteamerRecipe, itemIdentifier)
                if not RecipeKey: continue
                recipeSteam = SteamerRecipe.getInt(RecipeKey + ".Steam", 0)
                outputItem = SteamerRecipe.getString(RecipeKey + ".Output")
                if recipeSteam <= 0 or not outputItem: continue
                currentProgress = cookingProgress[i]
                newProgress = currentProgress + steamConversionEfficiency
                if newProgress >= recipeSteam:
                    slots[i] = outputItem
                    cookingProgress[i] = 0
                else:
                    cookingProgress[i] = newProgress
                DataChanged = True
        if DataChanged:
            Data.set(slotsPath, slots)
            Data.set(cookingProgressPath, cookingProgress)
            Data.save()
        return validIngredients > 0 or newSteam > 0
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def ExtinguishHeatSource(SteamerFileKey):

    try:
        parts = SteamerFileKey.split(",")
        if len(parts) < 4:
            return False
        x = int(parts[0])
        y = int(parts[1])
        z = int(parts[2])
        worldName = parts[3]
        world = Bukkit.getWorld(worldName)
        if not world:
            return False
        steamerLocation = Location(world, x, y, z)
        heatSourceBlock = steamerLocation.getBlock().getRelative(BlockFace.DOWN)
        if not isHeatSourceBlock(heatSourceBlock):
            return False
        if heatSourceBlock.getType() in [Material.CAMPFIRE, Material.SOUL_CAMPFIRE]:
            blockData = heatSourceBlock.getBlockData()
            if hasattr(blockData, 'setLit'):
                blockData.setLit(False)
                heatSourceBlock.setBlockData(blockData)
        elif heatSourceBlock.getType() in [Material.FURNACE, Material.BLAST_FURNACE, Material.SMOKER]:
            furnaceState = heatSourceBlock.getState()
            if hasattr(furnaceState, 'setBurnTime'):
                furnaceState.setBurnTime(0)
                furnaceState.update()
        heatSourceBlock.getState().update()
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def ProcessSteamProduction(steamerKey):

    try:
        moisturePath = "Steamer." + steamerKey + ".Moisture"
        steamPath = "Steamer." + steamerKey + ".Steam"
        currentMoisture = Data.getInt(moisturePath, 0)
        currentSteam = Data.getInt(steamPath, 0)
        if currentMoisture <= 0:
            return False
        productionEfficiency = Config.getInt("Setting.Steamer.SteamProductionEfficiency", 10)
        steamProduced = min(currentMoisture, productionEfficiency)
        newMoisture = max(0, currentMoisture - steamProduced)
        newSteam = currentSteam + steamProduced
        Data.set(moisturePath, newMoisture)
        Data.set(steamPath, newSteam)
        Data.save()
        return True
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def ProcessSteamConsumption(steamerKey):

    try:
        steamPath = "Steamer." + steamerKey + ".Steam"
        currentSteam = Data.getInt(steamPath, 0)
        if currentSteam <= 0:
            return False
        consumptionEfficiency = Config.getInt("Setting.Steamer.SteamConsumptionEfficiency", 1)
        totalConsumption = consumptionEfficiency
        newSteam = max(0, currentSteam - totalConsumption)
        Data.set(steamPath, newSteam)
        Data.save()
        return newSteam > 0
    except Exception as e:
        MiniMessageUtils.sendMessage(Console, str(e))
        return False

def GiveItemToPlayer(Player, Item):

    if not Player or not Item:
        return
    if Player.getInventory().firstEmpty() != -1:
        Player.getInventory().addItem(Item)
    else:
        dropLocation = Player.getLocation()
        ItemEntity = Player.getWorld().dropItemNaturally(dropLocation, Item)
        ItemEntity.setPickupDelay(0)

def RemoveItemToPlayer(Player, Item):

    if not Player or not Item or Item.getType() == Material.AIR:
        return
    if Item.getAmount() > 1:
        newItem = Item.clone()
        newItem.setAmount(Item.getAmount() - 1)
        Player.getInventory().setItemInMainHand(newItem)
    else:
        Player.getInventory().setItemInMainHand(None)

def CreateItemDisplay(Location, Item, Target):

    ItemDisplayEntity = Location.getWorld().spawn(Location, ItemDisplay)
    DisplayItem = Item.clone()
    DisplayItem.setAmount(1)
    ItemDisplayEntity.setItemStack(DisplayItem)
    ItemIdentifier = ToolUtils.getItemIdentifier(Item)
    ConfigKey = "Setting." + Target + ".DisplayEntity." + ItemIdentifier
    if not Config.contains(ConfigKey + ".Scale"):
        Type = ToolUtils.isBlockMaterialType(Item)
        ConfigKey = "Setting." + Target + ".DisplayEntity." + Type
    Scale = Config.getDouble(ConfigKey + ".Scale")
    ScaleVector = Vector3f(Scale, Scale, Scale)
    RotX = Config.getDouble(ConfigKey + ".Rotation.X")
    RotY = Config.getDouble(ConfigKey + ".Rotation.Y")
    RotZConfig = Config.get(ConfigKey + ".Rotation.Z")
    RotZ = 0.0
    if isinstance(RotZConfig, basestring):
        if "-" in RotZConfig:
            try:
                MinValue, MaxValue = map(float, RotZConfig.split("-"))
                RotZ = random.uniform(MinValue, MaxValue)
            except ValueError:
                RotZ = 0.0
        else:
            try:
                RotZ = float(RotZConfig)
            except ValueError:
                RotZ = 0.0
    else:
        try:
            RotZ = float(RotZConfig)
        except ValueError:
            RotZ = 0.0
    RadX = math.radians(RotX)
    RadY = math.radians(RotY)
    RadZ = math.radians(RotZ)
    Rotation = Quaternionf().rotationXYZ(RadX, RadY, RadZ)
    New_Transform = Transformation(
        Vector3f(),
        Rotation,
        ScaleVector,
        Quaternionf())
    ItemDisplayEntity.setTransformation(New_Transform)
    ItemDisplayEntity.setInvulnerable(True)
    ItemDisplayEntity.setSilent(True)
    ItemDisplayEntity.setPersistent(True)
    ItemDisplayEntity.setGravity(False)
    ItemDisplayEntity.setCustomNameVisible(False)
    return ItemDisplayEntity

def FindNearbyDisplay(Location):

    FoundEntities = []
    Radius = Config.getDouble("Setting.General.SearchRadius")
    for entity in Location.getWorld().getNearbyEntities(Location, Radius, Radius, Radius):
        if entity.getType() == EntityType.ITEM_DISPLAY: FoundEntities.append(entity)
    return FoundEntities if FoundEntities else None

def GetFileKey(Block):

    return "{},{},{},{}".format(Block.getX(), Block.getY(), Block.getZ(), Block.getWorld().getName())

def CalculateDisplayLocation(Block, Target, Item=None, ExtraOffset=0):

    if Item:
        ItemIdentifier = ToolUtils.getItemIdentifier(Item)
        ConfigKey = "Setting." + Target + ".DisplayEntity." + ItemIdentifier
    else:
        ConfigKey = "Setting." + Target + ".DisplayEntity.Item"
    if not Config.contains(ConfigKey + ".Offset.X"):
        Type = ToolUtils.isBlockMaterialType(Item) if Item else "Item"
        ConfigKey = "Setting." + Target + ".DisplayEntity." + Type
    Offset_X = Config.getDouble(ConfigKey + ".Offset.X")
    Offset_Y = Config.getDouble(ConfigKey + ".Offset.Y")
    Offset_Z = Config.getDouble(ConfigKey + ".Offset.Z")
    return Location(
        Block.getWorld(),
        Block.getX() + Offset_X,
        Block.getY() + Offset_Y + ExtraOffset,
        Block.getZ() + Offset_Z)

ps.listener.registerListener(InteractionVanillaBlock, PlayerInteractEvent)
ps.listener.registerListener(BreakVanillaBlock, BlockBreakEvent)

def CommandExecute(sender, label, args):

    if len(args) == 0: return False
    if args[0] == "reload":
        if isinstance(sender, Player):
            if not sender.hasPermission("cookiecooking.command.reload"):
                MiniMessageUtils.sendMessage(sender, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                return False
        ReloadPlugin(sender)
        MiniMessageUtils.sendMessage(sender, Config.getString("Messages.Reload.LoadPlugin"), {"Prefix": Prefix})
        return True
    if isinstance(sender, Player):
        if args[0] == "clear":
            if sender.hasPermission("cookiecooking.command.clear"):
                for Entity in sender.getWorld().getNearbyEntities(sender.getLocation(), 0.5, 0.5, 0.5):
                    if Entity.getType() == EntityType.ITEM_DISPLAY:
                        Entity.remove()
                        return True
            else:
                MiniMessageUtils.sendMessage(sender, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                return False
        if args[0] == "hand":
            if sender.hasPermission("cookiecooking.command.hand"):
                HandItem = sender.getInventory().getItemInMainHand()
                if HandItem.getType() == Material.AIR:
                    MiniMessageUtils.sendMessage(sender, Config.getString("Messages.Command.NoItemInHand"))
                    return True
                ItemDisplay = HandItem.displayName()
                ItemDisplay.hoverEvent(HandItem.asHoverEvent())
                MiniMessageUtils.sendMessage(sender, ItemDisplay)
                return True
            else:
                MiniMessageUtils.sendMessage(sender, Config.getString("Messages.NoPermission"), {"Prefix": Prefix})
                return False
        return False
    return False

def ReloadPlugin(Target = Console):
    global Config, Prefix, ChoppingBoardRecipe, WokRecipe, Data, GrinderRecipe, SteamerRecipe
    ConfigManager.reloadAll()
    Config = ConfigManager.getConfig()
    Prefix = ConfigManager.getPrefix()
    ChoppingBoardRecipe = ConfigManager.getChoppingBoardRecipe()
    WokRecipe = ConfigManager.getWokRecipe()
    GrinderRecipe = ConfigManager.getGrinderRecipe()
    SteamerRecipe = ConfigManager.getSteamerRecipe()
    Data = ConfigManager.getData()
    ChoppingBoardRecipeAmount = ChoppingBoardRecipe.getKeys(False).size()
    WokRecipeAmount = WokRecipe.getKeys(False).size()
    GrinderRecipeAmount = GrinderRecipe.getKeys(False).size()
    SteamerRecipeAmount = SteamerRecipe.getKeys(False).size()
    MiniMessageUtils.sendMessage(Target, Config.getString("Messages.Reload.LoadChoppingBoardRecipe"),
                                 {"Prefix": Prefix, "Amount": int(ChoppingBoardRecipeAmount)})
    MiniMessageUtils.sendMessage(Target, Config.getString("Messages.Reload.LoadWokRecipe"),
                                 {"Prefix": Prefix, "Amount": int(WokRecipeAmount)})
    MiniMessageUtils.sendMessage(Target, Config.getString("Messages.Reload.LoadGrinderRecipe"),
                                 {"Prefix": Prefix, "Amount": int(GrinderRecipeAmount)})
    MiniMessageUtils.sendMessage(Target, Config.getString("Messages.Reload.LoadSteamerRecipe"),
                                 {"Prefix": Prefix, "Amount": int(SteamerRecipeAmount)})

def TabCommandExecute(sender, label, args):

    if isinstance(sender, Player):
        return ["reload", "clear", "hand"]
    return ["reload"]

ps.command.registerCommand(CommandExecute, TabCommandExecute, "cookiecooking", ["cook"], "")


def InitializePlugin():

    global PlaceholderAPIAvailable
    ServerPluginLoad()
    if not PlaceholderAPIAvailable:
        MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Startup.NoPlaceholderAPI"), {"Prefix": Prefix})
        MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Startup.Failed"), {"Prefix": Prefix})
        return False
    steamerSection = Data.getConfigurationSection("Steamer")
    if steamerSection:
        steamerKeys = steamerSection.getKeys(False)
        currentTime = System.currentTimeMillis()
        for steamerKey in steamerKeys:
            coolingTime = Data.getLong("Steamer." + steamerKey + ".CoolingTime", 0)
            moisture = Data.getInt("Steamer." + steamerKey + ".Moisture", 0)
            steam = Data.getInt("Steamer." + steamerKey + ".Steam", 0)
            if (coolingTime > currentTime) or (moisture > 0) or (steam > 0):
                StartSteamerTimer()
                break
    MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Load"), {"Version": "v1.3.12", "Prefix": Prefix})
    MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Startup.Discord"), {"Prefix": Prefix})
    MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Startup.QQGroup"), {"Prefix": Prefix})
    MiniMessageUtils.sendMessage(Console, Config.getString("Messages.Startup.Wiki"), {"Prefix": Prefix})
    ReloadPlugin()
    return True

PluginInitialization = InitializePlugin()

if not PluginInitialization:
    ps.script.unloadScript("CookieCooking.py")
