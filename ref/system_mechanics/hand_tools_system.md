### Integrating Hand Tools into Fleet Management

The core philosophy remains the same: **"Treat every tool as an asset with its own lifecycle and quirks."** We'll apply the same pillars (Lifecycle, Maintenance, Operator Impact, and Failure) but scaled down appropriately.

The main difference is that hand tools will be managed from a new building: the **Tool Shed / Workshop Bench**, which is a smaller, cheaper precursor to the full Machinery Workshop.

### Pillar 1: The Lifecycle of Hand Tools

*   **Acquisition:**
    *   **Hardware Store (New):** Players can buy new, reliable hand tools. They come in different quality tiers:
        *   **Standard Grade:** Cheap, but wear out faster.
        *   **Professional Grade:** 2-3x the cost, but much more durable and might offer a small efficiency bonus (+5% speed).
    *   **Yard Sales / Flea Market (Used):** Similar to the Used Equipment Auction, but for hand tools. A rusty old shovel might be a bargain, or it could have a hidden "Brittle Handle" quirk and snap on the first day. This makes even the first $50 purchase a strategic choice.

*   **Depreciation & Loss:**
    *   Hand tools are too small to have complex depreciation. Instead, they have a **Condition Meter** that, when depleted, means the tool is broken.
    *   **The "Misplaced Tool" Mechanic:** Low-skill or "Disorganized" employees have a small chance of *losing* a tool after a task. It might be left out in the field. This creates a new mini-task: "Find the Missing Shovel." If not found before it rains, the tool's condition will degrade rapidly. This is a simple, realistic, and engaging problem.

### Pillar 2: The Workshop Bench - A Hub of Tool Care

The Workshop Bench is where tool maintenance happens. A dedicated Mechanic isn't required initially; a regular employee with a decent "Mechanically Inclined" trait can perform these tasks, albeit more slowly.

*   **Component-Based Wear (Simplified):**
    *   Instead of complex engine parts, hand tools have 2-3 key components.
        *   **Shovel/Hoe:** `Handle` and `Head`. A worn handle reduces efficiency (flexes too much). A worn head is less effective at tilling.
        *   **Watering Can:** `Body` and `Nozzle`. A dented body holds less water. A clogged nozzle has a smaller watering radius.
        *   **Hand Drill/Saw:** `Motor/Body` and `Bit/Blade`.
    *   **Repairing vs. Replacing:** When a component breaks, the player has a choice. Do you just replace the broken shovel handle for $10, or do you spend $40 on a new "Professional Grade" shovel? This is a classic early-game economic decision.

*   **Sharpening & Oiling (Maintenance Task):**
    *   For tools with blades (hoes, sickles, pruners), a new recurring task appears: **"Sharpen Tools."** A sharp tool works 15-20% faster than a dull one.
    *   Similarly, **"Clean and Oil Tools"** prevents them from rusting and degrading while in storage, especially during the off-season like winter. Neglecting this means your tools start the spring with lower condition.

### Pillar 3: The Operator - The Human Element Scaled Down

The impact of the employee is even more pronounced with physical tools.

*   **Stamina and Tool Choice:** Using a heavy "Standard Grade" sledgehammer will drain an employee's stamina much faster than using a lighter, better-balanced "Professional Grade" one. This makes investing in better tools a way to improve employee efficiency.
*   **Skill and Tool Damage:**
    *   A **low-skill** employee trying to pry a rock with a shovel has a high chance of breaking the handle.
    *   A **high-skill** employee knows the tool's limits and causes minimal wear.
    *   The **"Weak"** or **"Clumsy"** employee traits dramatically increase the rate of tool degradation and the chance of a critical failure (snapping a tool).

### Pillar 4: The Breakdown - A Snap, Not a Sputter

Failure for hand tools is simpler but no less disruptive.

*   **Critical Failure (The Snap!):** When a tool's condition is low, there's a chance it will break catastrophically during a task.
*   **The Disruption:** The employee immediately stops their task. They are now "Idle - Broken Tool." They cannot continue until they walk back to the Tool Shed, get a replacement tool (if one is available), and walk back to the field. This can waste hours of a workday.
*   **Strategic Consequence:** Imagine you only own one Seeder. It breaks during the last day of the optimal planting window. The hardware store is closed. You just lost a day, which could impact your entire harvest. This makes having a few backup tools a very wise, player-driven strategy.

---

### Updated Mermaid Chart: Integrating Hand Tools

Here is the revised chart, now incorporating the full spectrum of equipment from a simple hoe to a complex tractor.

```mermaid
flowchart TD
    subgraph "1. Acquisition"
        style A fill:#f9fbe7,stroke:#827717
        style C fill:#f1f8e9,stroke:#33691e
        
        A["🛒 Equipment Market"] --> B{Player Choice}
        A --> USED_MACHINERY["Used Machinery Auction<br/>(Risk/Reward)"]
        A --> NEW_MACHINERY["Dealership<br/>(Expensive/Reliable)"]
        A --> HARDWARE_STORE["Hardware Store<br/>(Standard/Pro Hand Tools)"]
        A --> FLEA_MARKET["Flea Market<br/>(Used Hand Tools)"]

        USED_MACHINERY --> B
        NEW_MACHINERY --> B
        HARDWARE_STORE --> B
        FLEA_MARKET --> B
    end

    subgraph "2. Operation & Wear"
        B -- Assign to --> D[🚜 Equipment & Tools]
        D -- Operated by --> E[👤 Operator Employee]
        E -- Traits affect --> F["Component Wear &<br/>Risk of Loss (Tools)"] & G["Fuel / Stamina Drain"]
        F -- Leads to --> H{Potential Failure?}
    end

    subgraph "3. Maintenance & Strategy"
        style K fill:#e3f2fd,stroke:#0d47a1
        style WORKBENCH fill:#e3f2fd,stroke:#0d47a1

        H -- Yes --> I[🚨 FAILURE EVENT<br/>Breakdown / Snapped Tool<br/>Causes work stoppage]
        H -- No --> J[Preventive Maintenance]
        
        K["🔧 Machinery Workshop"]
        WORKBENCH["🛠️ Workshop Bench<br/>(Tool Maintenance)"]

        J --> K & WORKBENCH

        I -- Heavy Machinery --> K
        I -- Hand Tools --> WORKBENCH

        K -- Staffed by --> L[🛠️ Mechanic Employee]
        WORKBENCH -- Staffed by --> L
        L -- Skill affects --> M[Repair Cost & Speed] & N[Diagnostic Accuracy] & O[Customization Options]
    end
    
    subgraph "4. End of Life / Disposal"
       D -- Degrades over time --> P["Depreciation (Machines)<br/>Condition (Tools)"]
       P --> Q{Dispose, Sell, or Overhaul?}
       Q -- Sell Machine --> USED_MACHINERY
       Q -- Scrap/Sell Tool --> |Cash| ECONOMY_SYS[💰]
       Q -- Overhaul Machine --> K
    end

    classDef event fill:#ffcdd2,stroke:#c62828,stroke-width:2px
    class I event
```

This integrated system ensures that from Day 1, when the player is deciding between a $15 shovel and a $40 one, they are engaging in the same thought process they'll use in the late game when deciding on a $500,000 combine. It scales beautifully and adds immense strategic depth.