### A Deep and Scalable Rival Farm AI System

### Pillar 1: The AI Persona - Giving the Rival a "Brain"

Each major rival NPC in the world is assigned a Persona. This persona is a collection of weighted priorities that governs all their strategic decisions. They aren't just trying to "make money"; they are trying to achieve specific goals based on their personality.

| Persona                | Core Goal                 | Preferred Strategy                                                                  | Strengths                                                        | Weaknesses                                                                   | Player Interaction                                                              |
| ---------------------- | ------------------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| **The Old-Timer**      | Preserve their legacy     | Diversified, traditional farming. Very slow to adopt new technology.                | High-quality crops, very high local reputation, financially stable. | Inefficient, vulnerable to new market trends, won't expand aggressively.       | A potential mentor. Can be a reliable partner for local contracts.              |
| **The Expansionist**   | Land & Market Share       | Aggressively buys land and uses high-volume, low-margin strategies (e.g., grain).   | Rapid growth, huge production volume, economies of scale.        | Often over-leveraged (high debt), low employee morale, average crop quality.   | Your primary competitor in land auctions and for large export contracts.        |
| **The Innovator**      | Technological Superiority | Rushes the R&D tech tree, invests heavily in automation and high-tech equipment.    | Extremely efficient, high-yield GMO crops, low labor costs.        | Prone to cash-flow problems due to high R&D/equipment costs, low reputation.   | Will try to poach your high-skill employees. A good source for buying used tech. |
| **The Boutique Farmer** | Quality & Brand           | Focuses on high-value niche markets (organics, specialty produce, farm-to-table).   | Highest quality goods, massive profit margins, very high brand loyalty. | Low production volume, vulnerable to blights/pests (no chemical use).          | Competes with you for the same premium restaurant and supermarket contracts.    |
| **The Penny-Pincher**  | Maximize Profit           | Ruthlessly minimizes all costs. Buys used equipment, pays low wages, avoids insurance. | Extremely high profit margins, very resilient during economic downturns. | High employee turnover, frequent equipment breakdowns, vulnerable to disasters. | Might try to undercut your prices on the open market, starting a price war.     |

**How it Works:** The AI uses these personas to make decisions. The Expansionist will *always* bid on adjacent land. The Innovator will *always* prioritize funding their R&D lab. The Old-Timer will *never* take a high-interest loan.

### Pillar 2: The Action Toolbox - What Rivals Can *Do*

Rivals don't just generate numbers; they take actions on the world map that directly affect the player.

*   **Market Actions:**
    *   **Price Undercutting:** A rival can flood the market with a specific crop to temporarily drive down prices, hurting your profits.
    *   **Exclusive Contracts:** A rival can outbid you for an exclusive supply contract with a major buyer, locking you out of that market for a year.
    *   **Reputation Smear:** A rival with low reputation might start a smear campaign, temporarily reducing your standing with a certain faction.
*   **Espionage & Poaching:**
    *   **Poaching Employees:** Rivals will make offers to your high-skill employees. The chance of acceptance depends on your employee's morale, loyalty, and ambition.
    *   **Scouting Your Farm:** You might see a rival's truck driving past your farm. They are gathering intel on what you're planting, which might inform their strategy next season.
*   **Direct Competition:**
    *   **Land Auctions:** Rivals will actively bid against you for new farm plots. An Expansionist will bid aggressively, while a Penny-Pincher will drop out early.
    *   **County Fair:** Rivals will enter their best produce/livestock into the annual fair, creating direct competition for awards and reputation bonuses.

### Pillar 3: The Difficulty Scaler - Tailoring the Challenge

This is how we implement your desired difficulty levels. The difficulty setting changes two things: the **Starting Conditions** of the rivals and their **Behavioral Modifiers**.

*   **Peaceful:** No rival farms are generated. The world is yours to conquer.
*   **Easy:**
    *   **Starting:** Rivals start with less cash and smaller farms than the player.
    *   **Behavior:** AI is less aggressive. They won't engage in price wars and will rarely poach employees. They expand slowly.
*   **Medium (The Way It's Meant to Be Played):**
    *   **Starting:** Rivals start on a level playing field with the player.
    *   **Behavior:** AI uses their full range of personas and actions. Competition is fair but constant.
*   **Hard:**
    *   **Starting:** Rivals start with a slight cash and land advantage.
    *   **Behavior:** AI is more aggressive and opportunistic. They get a small bonus to their efficiency (simulating them being "better" managers). They will actively exploit your weaknesses (e.g., if you're in debt, they might start a price war).
*   **Realism (Randomized):**
    *   **Starting:** This is the most interesting mode. The world is generated with a completely random assortment of rivals. One might be a massive, established "Expansionist" empire from the start. Another might be a "Boutique" farmer just starting out like you. Another could be a "Penny-Pincher" who is ruthless from day one.
    *   **Behavior:** All rivals act according to their "Hard" mode AI.
    *   **The Result:** Every "Realism" run is a unique strategic puzzle. Your starting position in the world and your proximity to different rival types will completely dictate your early-game strategy.

### Pillar 4: The Sandbox Mode - The Player as God

Sandbox mode gives the player direct control over the Rival AI system via a special "World Generation" menu.

*   **Rival Spawner:**
    *   Choose how many of each rival persona you want in the world (e.g., "1 Expansionist, 2 Old-Timers, 0 Innovators").
    *   Set their starting cash, land size, and initial tech level.
*   **Behavior Toggles:**
    *   Enable/disable specific rival actions ("Allow Employee Poaching: [Yes/No]").
    *   Adjust aggression levels with a slider ("Market Aggression: [Low/Medium/High]").
*   **World & Economic Modifiers:**
    *   Set global crop prices, event frequency, land costs, etc.

This allows players to create their own custom scenarios, from a hyper-competitive "battle royale" against three Expansionist rivals to a chill game focused on building next to friendly Old-Timers.

---

### Mermaid Chart: The Rival AI System

```mermaid
flowchart TD
    %% Player Settings
    subgraph "<b>Game Setup & Difficulty</b>"
        A[Difficulty Setting]
        A --> PEACEFUL["Peaceful<br/>(No Rivals)"]
        A --> EASY["Easy<br/>(Rivals start weak, are passive)"]
        A --> MEDIUM["Medium<br/>(Rivals are balanced)"]
        A --> HARD["Hard<br/>(Rivals start strong, are aggressive)"]
        A --> REALISM["Realism<br/>(Randomized rival power levels)"]
        A --> SANDBOX["Sandbox Mode<br/>(Player customizes everything)"]
    end
    
    %% AI Core
    subgraph "<b>Rival AI Core Engine</b>"
        B[Rival Farm Entity] -- Assigned an --> C[<b>AI Persona</b><br/>- Old-Timer<br/>- Expansionist<br/>- Innovator<br/>- etc.]
        C -- Dictates --> D[Strategic Priorities<br/>(e.g., 'Acquire Land' vs 'Maximize Quality')]
        D -- Selects from --> E[<b>Action Toolbox</b>]
    end

    %% AI Actions
    subgraph "<b>E. Action Toolbox (What Rivals Can Do)</b>"
        direction LR
        MARKET["Market Actions<br/>- Price Wars<br/>- Exclusive Contracts"]
        ESPIONAGE["Espionage & Poaching<br/>- Steal Employees<br/>- Scout Your Farm"]
        COMPETITION["Direct Competition<br/>- Land Auctions<br/>- County Fair"]
    end
    
    E --> MARKET & ESPIONAGE & COMPETITION

    %% Impact on Player
    subgraph "<b>Impact on the Player's Game</b>"
        F[Player's Farm Empire]
        MARKET -.->|Affects Prices & Contracts| F
        ESPIONAGE -.->|Affects Employees & Strategy| F
        COMPETITION -.->|Affects Expansion & Reputation| F
    end

    %% Connections
    A -- Determines --> B
    B -- Acts upon the --> WORLD[🗺️ The World Map]
    WORLD -- Contains --> F
    
```