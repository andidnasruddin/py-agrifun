### The Agri-Sim Engine

This chart visualizes the game as four primary interconnected layers, creating a dynamic feedback loop that drives gameplay:

1.  **The Player's Command Center (Top Layer):** This is the meta-layer, representing *you*, the manager. It's where your permanent legacy (**Grit**) and your in-run tactical abilities (**Ingenuity**) reside. This layer doesn't manage the farm directly; it provides global buffs, unlocks new possibilities, and offers emergency interventions, influencing every other aspect of the game.

2.  **The Strategic & Expansion Layer (CEO View):** This is where you make the big-picture, long-term decisions. You manage the empire's **Finances**, plan your growth across the **Multi-Farm World Map**, and steer your long-term competitive advantage through **Research & Technology**. This layer sets the grand strategy.

3.  **The Core Farm Operations (Manager View):** This is the heart of the simulation—the hands-on, day-to-day management of your farms. It includes managing **Employees** and their needs, maintaining the **Fleet** of equipment and tools, handling the physical **Water**, **Processing, and Storage** of goods. This layer is where your grand strategy is executed.

4.  **The Living World (External Forces):** This layer represents the forces outside of your direct control that constantly challenge you and create opportunities. Aggressive **Rivals** compete for every resource, while **Dynamic Events & Scenarios** can upend your best-laid plans or offer unexpected windfalls. This layer ensures that no two games are ever the same.

**The Intertwined Loop:** The **Living World** creates problems and opportunities. The player uses their **Strategic Layer** to plan a response, which is then executed by the **Core Operations Layer**. The success or failure of these operations feeds back into the Strategic Layer (as profit/loss) and ultimately provides the experience that fuels the **Player's Command Center** for future runs.

---

### Master Systems Integration Mermaid Chart

```mermaid
graph TD
    %% Define subgraph styles for clarity
    classDef player fill:#fff8e1,stroke:#f57f17,stroke-width:3px
    classDef strategic fill:#e0f7fa,stroke:#006064,stroke-width:3px
    classDef core fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px
    classDef world fill:#ffcdd2,stroke:#b71c1c,stroke-width:3px

    %% ===== 1. The Player's Command Center (Meta Layer) =====
    subgraph "<b><big>👑 The Player's Command Center</big></b>"
        PLAYER_LEGACY["⭐ Global Player Progression (Grit)<br/><i>Permanent unlocks, new content, innate talents.</i>"]
        PLAYER_INSTANCE["💡 Instance Player Progression (Ingenuity)<br/><i>Run-specific 'miracle' actions.</i>"]
    end

    %% ===== 2. Strategic & Expansion Layer (CEO View) =====
    subgraph "<b><big>📈 Strategic & Expansion Layer</big></b>"
        FINANCIAL["💰 Financial System<br/><i>Loans, credit, assets, cash flow.</i>"]
        MULTI_FARM["🗺️ Multi-Farm & World System<br/><i>Acquisition, delegation, logistics.</i>"]
        RESEARCH["🔬 Research & Technology<br/><i>R&D tech trees, unlocking new methods.</i>"]
    end

    %% ===== 3. Core Farm Operations (Manager View) =====
    subgraph "<b><big>⚙️ Core Farm Operations</big></b>"
        EMPLOYEE["👥 Employee System (Hiring & Needs)<br/><i>The human capital of the farm.</i>"]
        FLEET["🚜 Fleet Management (Equipment & Tools)<br/><i>The machinery and tools of the trade.</i>"]
        PROCESSING["🏭 Processing & Storage System<br/><i>Adding value and managing inventory.</i>"]
        WATER["💧 Water Management<br/><i>The lifeblood of the crops.</i>"]
    end

    %% ===== 4. The Living World (External Forces) =====
    subgraph "<b><big>🌍 The Living World</big></b>"
        RIVALS["🤖 Rival AI System<br/><i>Competitors with unique personalities.</i>"]
        EVENTS["🌪️ Dynamic Events & Scenarios<br/><i>Narrative challenges and opportunities.</i>"]
    end

    %% A. CORE CONNECTIONS (The Engine)
    EMPLOYEE -- Operates --> FLEET
    FLEET -- Works the Land --> WATER
    WATER -- Grows Crops for --> PROCESSING
    PROCESSING -- Generates Products & Revenue --> FINANCIAL
    
    %% B. STRATEGIC LAYER <--> CORE OPERATIONS (Command & Execution)
    STRATEGIC_LAYER((Strategic Layer))
    CORE_OPERATIONS((Core Operations))
    
    FINANCIAL -- Funds / Constrains --> EMPLOYEE & FLEET & PROCESSING & WATER
    MULTI_FARM -- Sets Goals for --> CORE_OPERATIONS
    RESEARCH -- Unlocks Upgrades for --> FLEET & PROCESSING & WATER
    CORE_OPERATIONS -.->|Provides Data & Capital| STRATEGIC_LAYER

    %% C. THE LIVING WORLD (External Pressure)
    LIVING_WORLD((The Living World))
    
    RIVALS -- Competes for --> MULTI_FARM & EMPLOYEE
    RIVALS -- Affects --> FINANCIAL
    EVENTS -- Creates Problems for --> CORE_OPERATIONS & STRATEGIC_LAYER

    %% D. PLAYER'S COMMAND CENTER (The Overlord)
    PLAYER_COMMAND((Player's Command Center))
    
    PLAYER_LEGACY -.->|Provides Permanent Buffs & Unlocks| STRATEGIC_LAYER & CORE_OPERATIONS
    PLAYER_INSTANCE -.->|Offers Emergency Actions| CORE_OPERATIONS & STRATEGIC_LAYER
    
    %% Hiding the abstract nodes
    style STRATEGIC_LAYER display:none
    style CORE_OPERATIONS display:none
    style LIVING_WORLD display:none
    style PLAYER_COMMAND display:none
    
    %% Link the abstract nodes to the subgraphs
    FINANCIAL & MULTI_FARM & RESEARCH --- STRATEGIC_LAYER
    EMPLOYEE & FLEET & PROCESSING & WATER --- CORE_OPERATIONS
    RIVALS & EVENTS --- LIVING_WORLD
    PLAYER_LEGACY & PLAYER_INSTANCE --- PLAYER_COMMAND
    
    %% Apply styles
    class PLAYER_LEGACY,PLAYER_INSTANCE player
    class FINANCIAL,MULTI_FARM,RESEARCH strategic
    class EMPLOYEE,FLEET,PROCESSING,WATER core
    class RIVALS,EVENTS world
```