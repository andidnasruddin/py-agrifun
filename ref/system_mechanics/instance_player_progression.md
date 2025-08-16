### The "Ingenuity" System

We'll introduce a new, **run-specific currency** that is related to Grit but distinct from it. Let's call it **Ingenuity**.

**How it Works:**

*   **Ingenuity (💡):** A temporary, in-run resource. You earn it during your current playthrough. You spend it during your current playthrough. It does not carry over directly.
*   **Grit (⭐):** The permanent, meta-resource. You earn it at the end of a run. You spend it between runs.

This separation is the key. It prevents the "Death Spiral Trap." A player can spend all their Ingenuity and still fail, but they will never lose their permanent Grit progression.

### Pillar 1: Earning Ingenuity (Rewarding Good Play)

You earn Ingenuity by playing well and overcoming minor challenges within the current run. It's a reward for being a good manager.

*   **+1💡:** Successfully navigating a "Minor" or "Moderate" dynamic event.
*   **+1💡:** Achieving a record high for single-day profit.
*   **+2💡:** An employee levels up to a milestone (e.g., Level 10).
*   **+3💡:** Winning an award at the County Fair.
*   **+5💡:** Paying off a major loan ahead of schedule.

### Pillar 2: Spending Ingenuity (The "Miracle" Menu)

At any point, the player can pause and access the "Manager's Ingenuity" menu. Here, they can spend their 💡 on powerful, one-time actions that are framed as your manager having a "stroke of genius" or "calling in an old favor."

These are not cheap bailouts; they are expensive, strategic interventions.

*   **"Pull an All-Nighter" (Cost: 3💡):** For the next 24 hours, all employees' Stamina needs are frozen. Perfect for pushing through a critical harvest before a storm.
*   **"Call in a Favor" (Cost: 5💡):** Instantly source a single, critically needed item that is otherwise unavailable (e.g., a rare spare part, a bag of special seeds off-season).
*   **"Inspiring Speech" (Cost: 4💡):** Instantly grant a moderate morale boost to all employees on one farm. Can be used to prevent a mass quit event.
*   **"Resourceful Solution" (Cost: 8💡):** Instantly complete the final 25% of any single construction or repair project.
*   **"Market Insight" (Cost: 10💡):** Receive a highly accurate, one-time tip about a massive price spike or crash for a specific commodity in the coming week.

### Pillar 3: The End of the Chapter - The Conversion

This is where the two systems connect and create a beautiful loop. At the Career Debriefing screen, any **unspent Ingenuity** is converted into permanent Grit.

*   **Conversion Rate:** For example, **5💡 = 1⭐**.
*   **The Strategic Choice:** This creates the *exact* dilemma you wanted, but in a healthier way.
    *   Do I spend my Ingenuity now to make this run easier and more likely to succeed?
    *   Or do I hoard my Ingenuity, making this run harder, knowing that it will convert into more permanent Grit for my future legacy?
*   **Rewarding Prudence:** This system directly rewards players who can solve problems without resorting to "miracles," accelerating their meta-progression.

---

### Updated Mermaid Chart: The Two-Tiered Progression Loop

This chart shows the two distinct loops: the inner, run-specific **Ingenuity Loop**, and the outer, permanent **Legacy Loop**.

```mermaid
flowchart TD
    %% Outer Loop Start
    LEGACY_HUB[<b>⭐ Legacy Hub</b><br/>Spend Grit on Permanent Unlocks] --> NEW_GAME[🌱 Start New Venture]

    %% The Live Game Loop
    subgraph "<b>The Current Venture (A Single Playthrough)</b>"
        style INNER_LOOP fill:#e3f2fd,stroke:#0d47a1
        
        NEW_GAME --> GAMEPLAY[Manage & Grow Farm]
        GAMEPLAY -- Good Play / Overcome Challenges --> EARN_INGENUITY[+💡 Earn Ingenuity]
        
        EARN_INGENUITY --> INGENUITY_POOL[💡 Ingenuity Pool<br/>(Run-Specific Currency)]
        
        GAMEPLAY -- Face a Crisis --> PLAYER_CHOICE{Use Ingenuity?}
        
        PLAYER_CHOICE -- Yes --> SPEND_INGENUITY[Spend 💡 on<br/>'Miracle' Actions]
        SPEND_INGENUITY --> GAMEPLAY
        
        PLAYER_CHOICE -- No --> GAMEPLAY

        GAMEPLAY --> RUN_ENDS{Run Ends?}

        INNER_LOOP(Inner Loop: The Ingenuity Cycle)
    end

    RUN_ENDS -- Success or Failure --> DEBRIEFING

    %% The Meta-Game Loop
    subgraph "<b>Meta-Progression: The Manager's Legacy</b>"
        style DEBRIEFING fill:#fff8e1,stroke:#f57f17
        
        DEBRIEFING[<b>Career Debriefing</b>]
        
        DEBRIEFING -- Calculate --> GRIT_EARNED[Earn ⭐ Grit<br/>(Based on Performance)]
        INGENUITY_POOL -- Any unspent 💡? --> CONVERT[Convert 💡 to ⭐<br/>(e.g., 5-to-1)]
        CONVERT --> GRIT_EARNED
        
        GRIT_EARNED --> LEGACY_HUB
    end

    %% Visual Styling
    linkStyle 0 stroke-width:3px,stroke:purple
    linkStyle 10 stroke-width:3px,stroke:purple
    linkStyle 3 stroke-width:2px,stroke:#0d47a1,stroke-dasharray: 5 5
    linkStyle 6 stroke-width:2px,stroke:#0d47a1,stroke-dasharray: 5 5
    linkStyle 7 stroke-width:2px,stroke:#0d47a1,stroke-dasharray: 5 5
```