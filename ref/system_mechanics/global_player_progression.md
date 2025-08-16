### The Critical Flaw of Traditional Progression vs. Your Roguelite Idea

*   **Traditional Problem:** In a standard sim, failure is a dead end. You reload an old save, losing hours of progress, or you quit. There's no forward momentum *through* failure. Success is the only path.
*   **Your Solution's Strength:** Your concept reframes "Game Over" as "**Chapter Over**." The failure of the *business* is not a failure of the *player*. It's a learning experience for your persistent manager character, making them wiser and better equipped for their next venture. This is psychologically brilliant.

However, we must be critical of the potential pitfalls of a roguelite loop in a long-form game:

*   **Pitfall 1: The Grind.** If a run takes 15+ hours, the meta-progression rewards *must* be substantial and game-changing. A "+2% Crop Yield" bonus is insulting after that much time.
*   **Pitfall 2: Trivializing the Early Game.** If the meta-upgrades are too powerful, the tense, challenging early game of survival is completely removed on subsequent runs, which can be boring.

Our design will focus on making the meta-progression provide more **options and interesting starting scenarios**, rather than just making the player generically more powerful.

---

### A Deep Dive: The Manager's Legacy System

Our philosophy is: **"The business is temporary; the experience is permanent."**

### Pillar 1: The End of a Chapter - The Debriefing

When a run ends (either by bankruptcy or a successful "retirement"), the player is taken to a special "Career Debriefing" screen. This is where the rewards are calculated.

*   **Introducing "Grit": The Meta-Currency**
    *   Instead of generic XP, you earn **Grit**. Grit is a measure of the hard-won experience your manager has accumulated.
    *   **Grit Calculation:**
        *   +1 Grit for every year in business.
        *   +1 Grit for every $100,000 of peak net worth achieved.
        *   +5 Grit for every "Major Scenario" successfully navigated.
        *   **The "Hard Knocks" Bonus:** If you went bankrupt, you get a **massive Grit bonus** based on how deep in debt you were. This is crucial—it rewards spectacular failure and encourages risky plays.
        *   **The "Golden Handshake" Bonus:** If you succeed (e.g., reach a $10 million net worth and choose to sell the farm), you get the largest Grit reward, solidifying success as the optimal, but not only, path to progression.

### Pillar 2: The Career Legacy Hub - Spending Your Grit

This is the meta-game menu, accessible between runs. Here you spend Grit on permanent, account-wide unlocks that will affect all future playthroughs. The skill tree is divided into three distinct branches.

#### Branch 1: "Starting Advantage" (Head Starts)
*   These are straightforward bonuses to ease the start of the next run. They should be useful but carefully balanced to not break the early game.
    *   **Favorable Loan:** Start with a pre-approved, low-interest line of credit.
    *   **The Heirloom Tool:** Choose one hand tool from your previous run to bring to the next. That "Professional Grade" shovel you loved is now a permanent part of your legacy.
    *   **Old Connections:** Start with a +10 loyalty rating with one buyer of your choice.
    *   **Inherited Machinery:** Start with a single, well-used but functional small tractor. A huge early-game boost.
    *   **Seed Capital:** Begin with a slightly larger pool of starting cash.

#### Branch 2: "New Horizons" (Unlocking Content)
*   This is the most important branch for replayability. These unlocks don't make you stronger, they make the *game bigger* by adding new content to the procedural generation pools.
    *   **Unlock New Crops:** Spend Grit to add rare or complex crops to the world (e.g., Saffron, Hops, Grapes for winemaking).
    *   **Unlock New Business Ventures:** Permanently unlock the ability to build advanced buildings like a Bakery, a Dairy, or even the coveted **Farm-to-Table Restaurant**.
    *   **Unlock New Employee Traits:** Add rare, powerful, or quirky traits to the pool of potential hires (e.g., "Prodigy," "Logistics Whiz," "Incorruptible").
    *   **Unlock New Regions:** Add entirely new, challenging biomes to the world generation (e.g., "The Volcanic Fields," "The Marshlands").
    *   **Unlock New Scenarios:** Add more complex and difficult dynamic scenarios to the event pool. This is for players who want more challenge, not less.

#### Branch 3: "Innate Talents" (The Manager's Skills)
*   These are permanent skills your player character has learned. They are subtle global buffs that reflect your manager's growing expertise.
    *   **The Negotiator's Tongue:** A permanent 2% discount on all supply purchases and a 2% bonus on all crop sales.
    *   **The Agronomist's Eye:** Soil quality information is slightly more detailed from the start.
    *   **The Leader's Presence:** New hires start with slightly higher morale.
    *   **The Mechanic's Knack:** Any machine the *player character* personally operates degrades 10% slower.
    *   **The Survivor:** Your farm can sustain a negative cash flow for a slightly longer period before triggering the insolvency spiral.

### Pillar 3: A New Beginning - The Next Venture

The "New Game" screen is now the "Found a New Venture" screen.

*   **Choose Your Starting Conditions:** After spending your Grit, you set up your next run. The procedural generation creates a new world.
*   **Challenge Modifiers:** For expert players, you can now add self-imposed challenges for a Grit multiplier on the next run.
    *   **"Starting from Scratch":** No starting loan or equipment. (+50% Grit earned).
    *   **"The Barren Land":** Start in a region with universally poor soil quality. (+75% Grit earned).
    *   **"Hostile Market":** All crop prices are permanently reduced by 15%. (+100% Grit earned).
*   **The Narrative Link:** The game acknowledges your past. The news report on Day 1 might read: "Famed agriculturalist [Player Name], who previously built and sold the lucrative Grainsville operation, has been spotted setting up a new venture in the Oak Valley region."

---

### Mermaid Chart: The Player's Career Legacy Loop

```mermaid
flowchart TD
    %% The Live Game Loop
    subgraph "<b>The Current Venture (A Single Playthrough)</b>"
        A[🌱 Start New Farm] --> B[Manage & Grow Empire]
        B --> C{Run Ends?}
    end

    C -- Success! --> D_WIN[🏆 Voluntary Retirement<br/>(Sell the Farm)]
    C -- Failure! --> D_FAIL[💥 Bankruptcy<br/>(Empire Collapses)]
    
    %% The Meta-Game Loop
    subgraph "<b>Meta-Progression: The Manager's Legacy</b>"
        style E fill:#fff8e1,stroke:#f57f17
        style F fill:#e0f7fa,stroke:#006064
        style G fill:#f3e5f5,stroke:#4a148c

        D_WIN & D_FAIL --> E[<b>Career Debriefing</b><br/>Calculate 'Grit' Earned<br/>(Success gives more, Failure gives a bonus)]
        
        E --> F[<b>Legacy Hub: Spend Grit</b>]
        F --> F1[<u>Branch 1: Head Starts</u><br/>- Better Loans<br/>- Heirloom Tool<br/>- Inherited Tractor]
        F --> F2[<u>Branch 2: New Horizons</u><br/>- Unlock Crops<br/>- Unlock Buildings<br/>- Unlock Traits & Scenarios]
        F --> F3[<u>Branch 3: Innate Talents</u><br/>- The Negotiator<br/>- The Leader<br/>- The Survivor]
    end

    %% The Loop Back
    G[<b>A New Beginning</b><br/>- New Procedurally Generated World<br/>- Choose Starting Bonuses<br/>- Add Optional Challenges]
    F --> G
    G -- Start a new chapter --> A

    %% Visual Styling
    linkStyle 2 stroke-width:3px,stroke:green
    linkStyle 3 stroke-width:3px,stroke:red
    linkStyle 4 stroke-width:2px,stroke-dasharray: 5 5
    linkStyle 5 stroke-width:2px,stroke-dasharray: 5 5
```