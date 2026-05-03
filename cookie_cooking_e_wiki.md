# CookieCooking Wiki

Welcome to the official **CookieCooking** Wiki! This is a cooking plugin built on **PySpigot**, delivering a highly immersive role-playing cooking experience with 4 interactive Cooking Stations using Holograms and GUI.

---

## 🌟 1. System Overview

CookieCooking supports deep integration with custom item plugins. You can use items from:
* **Vanilla Minecraft** (`minecraft ITEM_ID`)
* **MMOItems** (`mmoitems TYPE:ID`)
* **CraftEngine** (`craftengine KEY:ID`)
* **NeigeItems** (`neigeitems ID`)

The system provides 4 main workstations:
1. **Chopping Board:** Use a knife to cut ingredients.
2. **Wok:** Stir-fry ingredients with different heat levels; food can burn or stay raw.
3. **Grinder:** Grind items in real time.
4. **Steamer:** Steam food using Moisture and Fuel mechanics.

---

## 🛠️ 2. Setup & Basic Commands

### Commands
All commands start with `/cookiecooking` or `/cooking`.

* `/cooking reload`: Reload configuration (Config.yml) and all recipes.
* `/cooking clear`: Remove bugged Item Display entities near the player (radius 0.5 block).
* `/cooking hand`: View NBT data of the item in hand (useful for debugging/recipes).

### Permissions
You need to assign these permissions to players or staff:

* **Admin Commands:**
  * `cookiecooking.command.reload`
  * `cookiecooking.command.clear`
  * `cookiecooking.command.hand`
* **Station Interactions:**
  * `cookiecooking.choppingboard.interaction`
  * `cookiecooking.choppingboard.cut`
  * `cookiecooking.wok.interaction`
  * `cookiecooking.wok.stirfry`
  * `cookiecooking.wok.serveout`
  * `cookiecooking.grinder.interaction`
  * `cookiecooking.steamer.interaction`
  * `cookiecooking.steamer.addmoisture`
  * `cookiecooking.steamer.addfuel`
* **Recipe Permissions:** You can assign custom permissions per recipe in YAML files (e.g., `chop.use`, `fry.use`).

---

## 🔪 3. Chopping Board

**Default Block:** `OAK_LOG`
**Required Tool:** `IRON_AXE` (acts as a knife)

**Mechanics:**
1. Hold ingredient (e.g., Beef) → `Shift + Left Click` on board to place it.
2. Hold knife (`IRON_AXE`) → `Shift + Left Click` repeatedly to cut.
3. After enough cuts, the output item drops.
4. *Note:* There is a chance to injure yourself (lose health)! Right-click empty hand to retrieve items.

**Recipe Example (ChoppingBoard.yml):**
```yaml
minecraft BEEF:
  Count: 5
  Output:
  - minecraft COOKED_BEEF 1 90
  - minecraft BONE 1 15
  Durability: 2
  Permission: "chop.use"
  Damage:
    Chance: 12
    Value: 2
```

---

## 🍳 4. Wok

**Default Block:** `IRON_BLOCK`
**Tool:** `IRON_SHOVEL` (spatula)
**Heat Sources:** Level 1 (`CAMPFIRE`), Level 2 (`MAGMA_BLOCK`), Level 3 (`LAVA`)

**Mechanics:**
1. Hold ingredient → `Shift + Right Click` to add.
2. Hold spatula → `Shift + Left Click` to stir.
3. When done, use Bowl → `Shift + Right Click` to collect.
4. *Note:* If not stirred in time, food burns (`BURNT`). If undercooked, result is `RAW`.

**Recipe Example (Wok.yml):**
```yaml
minecraft COOKED_BEEF:
  Count: "10-14"
  HeatControl: 2
  Amount: 2
  FaultTolerance: 2
  Item:
  - minecraft BEEF 1 5-7
  - minecraft CARROT 1 3-4
  RAW: minecraft BEEF
  BURNT: minecraft CHARCOAL
  Permission: "fry.use"
```

---

## ⚙️ 5. Grinder

**Default Block:** `GRINDSTONE`

**Mechanics:**
1. Hold ingredient → `Shift + Left Click` to insert.
2. Machine runs automatically with particles and sound.
3. After time ends, items drop.

**Recipe Example (Grinder.yml):**
```yaml
minecraft WHEAT:
  Output:
  - minecraft SUGAR 2 100
  GrindingTime: 5
  Permission: "grinder.use"
```

---

## 🫕 6. Steamer

**Default Block:** `BARREL`
**Heat Source:** `FURNACE` or `SMOKER`

**Mechanics:**
Requires **Moisture** and **Steam**:
1. Add fuel → `Shift + Right Click` furnace.
2. Add water → `Shift + Right Click` steamer.
3. Moisture converts to Steam when heated.
4. Check stats via furnace interaction.
5. Insert food via GUI and wait for cooking.

**Recipe Example (Steamer.yml):**
```yaml
minecraft POTATO:
  Output: minecraft BAKED_POTATO
  Steam: 60
  Permission: "steam.use"
```

---

## 📝 7. Notes for Admin/Dev

1. **Namespace:** Always include namespace (e.g., `minecraft APPLE`).
2. **Reload Plugin:** Use `/cooking reload` after editing YAML files.
3. **Hologram Bugs:** Use `/cooking clear` if floating text remains.
4. **Localization:** Messages and holograms can be customized using MiniMessage format in `Config.yml`.

