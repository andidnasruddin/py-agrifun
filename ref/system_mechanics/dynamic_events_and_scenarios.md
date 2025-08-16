### The Critical Flaw of Basic Event Systems

Most games implement events as simple, one-off notifications with a binary choice:
*   "A storm is coming! Pay $5,000 to protect your crops? [Yes/No]"
*   "Fuel prices have increased by 20% for 3 days."

**Critique:** These are shallow. They are temporary stat modifiers, not engaging scenarios. They don't tell a story, offer creative solutions, or have lasting consequences. The player's agency is limited to a simple financial calculation.

Our goal is to create a **Narrative Event System** where events are multi-stage problems that require the player to leverage their entire farm operation to solve. They should feel like a season's main plotline, not a random pop-up.

---

### An In-Depth Dynamic Events & Scenarios System

We'll structure this system into three layers: Event Triggers (what starts them), Event Categories (what they are about), and The Scenario Structure (how they play out).

### 1. Event Triggers: The "Why"

Events don't just happen randomly. They are triggered by a combination of world state, player actions, and a small dose of RNG.

*   **Time-Based:** Seasonal events (first frost, spring thaw), annual events (county fair, tax season).
*   **Player-Action Based:** Taking on a huge amount of debt might trigger a "Bank Audit." Expanding into a new region might trigger a "Territorial Dispute" with a rival NPC.
*   **Performance-Based:** Achieving a record-breaking harvest might trigger a "Feature in a Farming Magazine" scenario, boosting reputation. Conversely, a major crop failure could trigger a "Pest Outbreak Investigation."
*   **World-State Based:** A global "Economic Boom" or "Recession" can trigger long-term changes in market prices and demand.

### 2. Event Categories: The "What"

These are the flavors of the challenges the player will face.

| Category             | Description                                                                                             | Simple Event Example                             | **In-Depth Scenario Example**                                                                                                                                                                                                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Environmental**    | Challenges from the natural world.                                                                      | "Heatwave: Crop growth -10%"                     | **Scenario: "The Hundred-Year Flood"** <br>1. Early Warning: News predicts massive rainfall. <br>2. The Choice: Do you harvest unripe crops now, or build costly levees? <br>3. Aftermath: Fields are flooded, soil quality is damaged, and a government relief grant becomes available (requires paperwork).           |
| **Economic**         | Shifts in the financial landscape.                                                                      | "Fertilizer prices up 5%"                        | **Scenario: "The Supply Chain Collapse"** <br>1. The Trigger: A distant port strike is announced. <br>2. The Squeeze: Spare parts for machinery become "Rare" and 3x the price. <br>3. The Opportunity: A local NPC offers to fabricate parts at low quality for a high price. Do you risk it?                          |
| **Social/Political** | Events involving people, communities, and regulations.                                                    | "New farm subsidy available."                    | **Scenario: "The Rezoning Dispute"** <br>1. The Letter: The local council proposes rezoning the land next to your farm for a housing development. <br>2. The Campaign: Do you spend money and time lobbying against it (improves local rep, angers developers), or support it for a payout? <br>3. The Outcome: Lasting reputation changes. |
| **Mechanical**       | Events related to your equipment and infrastructure.                                                    | "Tractor #3 has a flat tire."                      | **Scenario: "The Bad Batch"** <br>1. The Problem: A new harvester breaks down catastrophically. The mechanic diagnoses a faulty part. <br>2. The Investigation: You discover the part is from a bad batch. Do you issue a public recall (costly, but reputation boost) or handle repairs quietly?             |
| **Personal**         | Stories focused on your player character and key employees.                                               | "Employee #5 is sick for a day."                 | **Scenario: "The Protégé"** <br>1. The Request: Your most talented young employee asks you to fund their advanced degree. <br>2. The Investment: It's expensive and they'll be gone for a whole season. <br>3. The Return: They come back as a high-skill specialist, but a rival farm immediately tries to poach them with a huge offer. |
| **Opportunity**      | Unexpected positive events that require quick action to capitalize on.                                  | "A buyer offers +10% for wheat this week."         | **Scenario: "The Celebrity Chef"** <br>1. The Visit: A famous TV chef is in town and wants to source "the best local ingredients." <br>2. The Trial: You must deliver a small batch of your highest-quality produce on a tight deadline. <br>3. The Contract: If successful, you unlock a permanent "Gourmet Restaurant" buyer who pays S-Tier prices. |

### 3. The Scenario Structure: The "How"

This is how we make events feel like a narrative arc. Each scenario follows a three-act structure.

*   **Act 1: The Inciting Incident**
    *   The event begins. The player is presented with the initial situation and the stakes are established. This is the "Flood Warning" or the "Letter from the Council."

*   **Act 2: The Crossroads & The Chain of Choices**
    *   This is the core of the scenario. The player isn't given one choice, but a **series of choices** over time.
    *   These choices are not just buttons; they are **Tasks and Projects**. To "Lobby the Council," you must assign an employee (or yourself) to a project that takes a week. To "Build Levees," you must create work orders for your construction team.
    *   This makes the solution resource-based (money, time, employee skill) rather than a simple click.

*   **Act 3: The Resolution & The Lasting Consequences**
    *   The scenario concludes. The results of your choices are revealed.
    *   **The key:** The consequences are not just a one-time cash reward/penalty. They create a **permanent or long-lasting change** to the game state.
        *   The flood permanently reduces soil quality in one field but unlocks a new government grant you can apply for annually.
        *   The rezoning dispute changes your community reputation forever.
        *   The celebrity chef becomes a permanent, high-value buyer on the world map.

---

### Mermaid Chart: The Dynamic Event System & Its Impact

This chart shows how a scenario is triggered, how it unfolds, and how its resolution radiates outwards to affect every other core system in your game.

```mermaid
flowchart TD
    %% Main System
    EVENT_SYSTEM["<big>🌪️ Dynamic Events & Scenarios System</big>"]

    %% Triggers
    subgraph "<b>1. Event Triggers</b>"
        TRIGGERS[Triggers]
        PLAYER_ACTIONS[Player Actions<br/>(e.g., Taking Debt)] --> TRIGGERS
        WORLD_STATE[World State<br/>(e.g., Economy)] --> TRIGGERS
        TIME_SEASON[Time & Season<br/>(e.g., Winter)] --> TRIGGERS
    end

    EVENT_SYSTEM -- Initiated by --> TRIGGERS

    %% Scenario Structure
    subgraph "<b>2. The Scenario Narrative Arc</b>"
        direction LR
        ACT1[<b>Act 1: Inciting Incident</b><br/>The problem is presented]
        ACT2[<b>Act 2: Crossroads</b><br/>A series of choices & tasks over time]
        ACT3[<b>Act 3: Resolution</b><br/>The outcome is revealed]
        
        ACT1 --> ACT2 --> ACT3
    end
    
    TRIGGERS --> ACT1

    %% Consequences
    CONSEQUENCES["<big>✨ Lasting Consequences</big><br/>(Permanent or long-term changes to the game world)"]
    ACT3 --> CONSEQUENCES
    
    %% Impact on Other Systems
    subgraph "<b>3. Ripple Effects on Core Game Systems</b>"
        CONSEQUENCES -- Affects --> FINANCE["💰 <b>Finance System</b><br/>- Unlocks/Loses Grants<br/>- New Loan Types<br/>- Market Price Volatility"]
        CONSEQUENCES -- Affects --> MULTI_FARM["🗺️ <b>Multi-Farm & World</b><br/>- Adds/Removes Buyers<br/>- Changes Road Networks<br/>- Alters Land Value/Terroir"]
        CONSEQUENCES -- Affects --> EMPLOYEES["👥 <b>Employee System</b><br/>- Creates Unique Hiring Opps<br/>- Morale/Stress Shocks<br/>- Triggers Personal Storylines"]
        CONSEQUENCES -- Affects --> REPUTATION["🤝 <b>Reputation System</b><br/>- Major Shifts in Faction Standing<br/>- Boosts/Damages Buyer Loyalty<br/>- Changes Rival Farm Behavior"]
        CONSEQUENCES -- Affects --> FLEET["🚜 <b>Fleet & Processing</b><br/>- Creates Parts Scarcity<br/>- Damages/Destroys Equipment<br/>- Unlocks New Tech Blueprints"]
        CONSEQUENCES -- Affects --> AGRICULTURE["🌾 <b>Agricultural System</b><br/>- Introduces New Diseases<br/>- Permanently Alters Soil<br/>- Creates Demand for New Crops"]
    end
    
    %% Visual Links
    linkStyle 0 stroke-width:3px,stroke:orange
    linkStyle 7 stroke-width:2px,stroke:#c62828,stroke-dasharray: 5 5
    linkStyle 8 stroke-width:2px,stroke:#0d47a1,stroke-dasharray: 5 5
    linkStyle 9 stroke-width:2px,stroke:#4a148c,stroke-dasharray: 5 5
    linkStyle 10 stroke-width:2px,stroke:#1b5e20,stroke-dasharray: 5 5
    linkStyle 11 stroke-width:2px,stroke:#283593,stroke-dasharray: 5 5
    linkStyle 12 stroke-width:2px,stroke:#e65100,stroke-dasharray: 5 5
```