### What Kinds of Needs Do Employees Have During Work?

Needs are states that decay over time or with exertion, and if ignored, they impose penalties. Fulfilling them provides temporary buffs and keeps employees functional.

1.  **Stamina/Energy (Your "Energy"):**
    *   **Decays with:** Physical labor (tilling, harvesting), carrying heavy loads, working in extreme weather (heat/cold).
    *   **Fulfilled by:** Taking breaks in a **Common Room**, sitting on a bench, or a full night's rest.
    *   **Penalty for Low:** Movement and work speed drastically slow down. Increased chance of accidents or mistakes. At 0, the employee will stop working and seek a place to rest.

2.  **Hunger:**
    *   **Decays:** Over the course of the workday, faster with heavy labor.
    *   **Fulfilled by:** Eating a meal at the **Canteen** or a packed lunch at a designated break area.
    *   **Penalty for Low:** Stamina drains faster, morale drops, and minor work speed penalty.

3.  **Thirst:**
    *   **Decays:** Constantly, but much faster in hot weather or during heavy exertion.
    *   **Fulfilled by:** Drinking from a **Water Cooler**, a tap in the Canteen, or a personal water bottle.
    *   **Penalty for Low:** Massive work speed penalty (especially in summer), stamina drains much faster.

4.  **Bladder:**
    *   **Decays:** After drinking. A simple, realistic need.
    *   **Fulfilled by:** Using a **Bathroom** or outhouse.
    *   **Penalty for Low:** A severe "distracted" debuff, causing slower work and a huge morale drop. If it hits zero, they will stop everything and run to the nearest facility.

5.  **Social:**
    *   **Decays:** When working alone for long periods. Different traits affect the decay rate ("Introvert" vs. "Extrovert").
    *   **Fulfilled by:** Chatting with colleagues in the **Common Room**, during lunch at the Canteen, or during collaborative tasks.
    *   **Penalty for Low:** Morale drain. For "Extrovert" types, it can also lead to them stopping work to find someone to talk to.

### What Other Aspects Would Make Sense? (Expanding the Profile)

Your default stats are a great baseline for *physical capabilities*. Let's add layers for *progression, personality, and well-being*.

1.  **Experience Points (XP) & Levels:**
    *   Employees gain XP for every task they complete.
    *   Upon leveling up, they gain a small boost to a relevant stat (e.g., leveling up from farming tasks could slightly increase their movement speed or carry weight).
    *   At milestone levels (e.g., 5, 10), they might unlock a new **Perk**, which is like a minor, earned Trait (e.g., "Efficient Harvester" or "Tireless Walker"). This creates a rewarding progression loop for each employee.

2.  **Age & Career Stage:**
    *   Employees age over the years. This isn't just a number; it affects their capabilities.
        *   **Young (18-25):** High stamina, fast, but lower starting skills and more prone to mistakes.
        *   **Prime (26-45):** The best balance of physical stats and experience.
        *   **Veteran (46-60):** Physical stats begin to slowly decline (- movement speed), but their high skill level compensates with efficiency. May gain a "Mentor" trait that helps nearby junior employees gain XP faster.
        *   **Senior (>60):** Significant physical penalties, but their vast experience makes them excellent for supervisory or highly specialized, low-exertion roles (like an R&D Scientist).

3.  **Stress Meter:**
    *   Different from Morale. This measures their mental strain.
    *   **Increases with:** Being overworked (low Stamina for too long), working with clashing personalities (Rivals), failing at tasks, or being micromanaged.
    *   **Decreases with:** Successful task completion, getting a raise, relaxing in the Common Room.
    *   **High Stress leads to:** Higher chance of mistakes, faster morale drain, and can eventually lead to a "Burnout" state where the employee is ineffective for several days.

4.  **Ambition (Hidden Trait):**
    *   This dictates an employee's career goals.
        *   **Highly Ambitious:** Their morale will plummet if they aren't promoted, trained, or given a raise regularly. They are driven but high-maintenance.
        *   **Content:** They are happy performing the same roles for years as long as they are paid fairly. Reliable and stable.
        *   **Wanderer:** Prone to quitting after a few years to "seek new opportunities," regardless of morale. Great for the short-term, but not a long-term investment.

---

### Revised and Expanded Mermaid Chart

This chart now includes the detailed Employee Profile, clearly breaking down their stats and needs, and showing how those needs link to the farm's infrastructure.

```mermaid
flowchart TD
    %% Main System Title
    EMPLOYEE_MGMT[<big>👥 Employee Management System</big>]
    EMPLOYEE_MGMT --> SOURCING

    %% ===== 1. SOURCING & RECRUITMENT =====
    subgraph "1. Sourcing & Recruitment"
        direction LR
        SOURCING[Start: Find Talent] --> JOB_BOARD[📍 Community Job Board] & AGENCY[🏢 Recruitment Agency] & HEADHUNT[🎯 Headhunting]
        JOB_BOARD & AGENCY & HEADHUNT --> APPLICANT_POOL[<br/>👨‍🌾<br/>Applicant Pool]
    end

    %% ===== 2. THE INTERVIEW =====
    subgraph "2. The Interview & Vetting Process"
        APPLICANT_POOL --> HIRING_UI[Hiring UI Screen<br/><b>Visible:</b> Skills, Salary, History<br/><b>Hidden:</b> All Traits]
        HIRING_UI --> INTERVIEW_MINIGAME{Begin Interview w/ Limited IP}
        INTERVIEW_MINIGAME --> REVEAL_TRAITS[✨ Trait Discovery]
        REVEAL_TRAITS --> OFFER[📝 Create Job Offer]
    end

    %% ===== 3. ONBOARDING =====
    subgraph "3. Onboarding & Contracts"
        OFFER --> ACCEPT_REJECT{Applicant Accepts Offer?}
        ACCEPT_REJECT -- Yes --> HIRED[✅ Employee Hired!]
        ACCEPT_REJECT -- No --> APPLICANT_POOL
    end

    %% ===== THE EMPLOYEE PROFILE (CORE ASSET) =====
    subgraph "<b>The Employee Profile (Core Asset)</b>"
        style EMPLOYEE_PROFILE fill:#fff8e1,stroke:#f57f17,stroke-width:4px
        HIRED --> EMPLOYEE_PROFILE[👤 Employee's Full Profile]
        
        EMPLOYEE_PROFILE --> P_IDENTITY[📜 Identity & Career<br/><b>Age/Career Stage</b><br/><b>Ambition</b> (Hidden)<br/>Contract Details]
        EMPLOYEE_PROFILE --> P_ATTRIBUTES[🧠 Attributes<br/><b>Skills</b> (Trainable)<br/><b>Traits</b> (Innate)<br/><b>Perks</b> (Earned)]
        EMPLOYEE_PROFILE --> P_PROGRESSION[📈 Progression<br/><b>XP & Level</b><br/>Certifications]
        EMPLOYEE_PROFILE --> P_DYNAMICS[❤️ Dynamic Stats<br/><b>Morale</b> (Happiness)<br/><b>Stress</b> (Strain)<br/><b>Loyalty</b>]
        EMPLOYEE_PROFILE --> P_PHYSICAL[💪 Physical Stats<br/><b>Movement Speed</b><br/><b>Carry Weight</b><br/><b>Carry Slots</b><br/><b>Tool Capacity</b>]
        EMPLOYEE_PROFILE --> P_NEEDS[❤️ Needs System]
        
        P_NEEDS --> N_STAMINA[⚡ Stamina]
        P_NEEDS --> N_HUNGER[🍔 Hunger]
        P_NEEDS --> N_THIRST[💧 Thirst]
        P_NEEDS --> N_BLADDER[🚽 Bladder]
        P_NEEDS --> N_SOCIAL[💬 Social]
    end

    %% ===== 4. MANAGEMENT & DEVELOPMENT =====
    subgraph "4. Management & Development"
        EMPLOYEE_PROFILE --> DAILY_TASKS[🔨 Daily Farm Tasks]
        DAILY_TASKS -- Gains --> P_PROGRESSION
        INVEST[Player Investment Decisions] --> TRAINING[📚 Send to School] & RAISES[Give Raise]
        TRAINING -- Unlocks --> P_PROGRESSION
        RAISES -- Boosts --> P_DYNAMICS
    end
    
    %% ===== 5. SEPARATION =====
    subgraph "5. Separation & Repercussions"
        P_DYNAMICS -- Low Morale/Loyalty --> QUIT[⚠️ Employee Quits!]
        PLAYER_CHOICE[Player Decision] --> FIRE[🔥 Fire Employee]
        QUIT & FIRE --> CONSEQUENCES[🚨 Consequences]
    end

    %% ===== 6. KEY SYSTEM INTEGRATIONS =====
    subgraph "🔗 Key System Integrations"
        direction TB
        style AMENITIES fill:#e8f5e9,stroke:#1b5e20
        
        N_HUNGER & N_THIRST & N_SOCIAL -- Fulfilled By --> AMENITIES[Canteen / Common Room]
        N_BLADDER -- Fulfilled By --> BATHROOM[Bathroom Facilities]
        N_STAMINA -- Fulfilled By --> BREAK_AREAS[Break Areas / Benches]
        
        AMENITIES & BATHROOM & BREAK_AREAS -- Part of --> BUILDING_SYS[🏢 Building System]

        P_PHYSICAL -.->|Affects Task Time| TASK_MGMT[📋 Task Management]
        P_ATTRIBUTES -.->|Affects Wear & Tear| FLEET_MGMT[🚜 Fleet Management]
        P_DYNAMICS -.->|Affects Overall Efficiency| ECONOMY_SYS[💰 Economy System]
    end

    %% Styling
    classDef sourcing fill:#e0f7fa,stroke:#006064,stroke-width:2px
    classDef interviewing fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef onboarding fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef management fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef separation fill:#ffcdd2,stroke:#b71c1c,stroke-width:2px
    classDef integration fill:#f1f8e9,stroke:#33691e,stroke-width:2px

    class SOURCING,JOB_BOARD,AGENCY,HEADHUNT,APPLICANT_POOL sourcing
    class HIRING_UI,INTERVIEW_MINIGAME,REVEAL_TRAITS,OFFER interviewing
    class ACCEPT_REJECT,HIRED onboarding
    class INVEST,DAILY_TASKS,TRAINING,RAISES management
    class QUIT,FIRE,CONSEQUENCES,PLAYER_CHOICE separation
```

flowchart TD
    %% Main System Title
    EMPLOYEE_MGMT[<big>👥 Employee Management System</big>]

    %% Link to the start of the lifecycle
    EMPLOYEE_MGMT --> SOURCING

    %% ===== 1. SOURCING & RECRUITMENT =====
    subgraph "1. Sourcing & Recruitment"
        direction LR
        SOURCING[Start: Find Talent] --> JOB_BOARD[📍 Community Job Board<br/><i>Locals, Low Skill, No Fees<br/>Short-Term / Seasonal Focus</i>]
        SOURCING --> AGENCY[🏢 Recruitment Agency<br/><i>Specialists, Career-Focused<br/>Requires Hiring & Relocation Fees</i>]
        SOURCING --> HEADHUNT[🎯 Headhunting<br/><i>Poach from NPC Farms<br/>High Risk, High Reward, Expensive</i>]
        
        JOB_BOARD --> APPLICANT_POOL
        AGENCY --> APPLICANT_POOL
        HEADHUNT --> APPLICANT_POOL

        APPLICANT_POOL[<br/>👨‍🌾<br/>Applicant Pool]
    end

    %% ===== 2. THE INTERVIEW & VETTING PROCESS =====
    subgraph "2. The Interview & Vetting Process"
        APPLICANT_POOL --> HIRING_UI[Hiring UI Screen<br/><b>Visible:</b> Skills, Salary, History<br/><b>Hidden:</b> All Traits]
        HIRING_UI --> INTERVIEW_MINIGAME{Begin Interview}
        
        INTERVIEW_MINIGAME --> IP[💧 Interview Points<br/><i>Limited resource per interview</i>]
        
        IP --> Q_BACKGROUND["Background Questions<br/><i>(Costs 1 IP)</i>"]
        IP --> Q_SITUATIONAL["Situational Questions<br/><i>(Costs 2 IP)</i>"]
        IP --> Q_REFERENCE["Reference Check<br/><i>(Costs 3 IP)</i>"]
        
        Q_BACKGROUND --> REVEAL_TRAITS[✨ Trait Discovery]
        Q_SITUATIONAL --> REVEAL_TRAITS
        Q_REFERENCE --> REVEAL_TRAITS

        REVEAL_TRAITS --> BLUFF{Potential Lie?<br/><i>Certain traits may deceive</i>}
        BLUFF -- Yes --> DECEPTION[Deception Attempted!]
        BLUFF -- No --> HONESTY[Honest Answer Given]
    end

    %% ===== 3. ONBOARDING & CONTRACTS =====
    subgraph "3. Onboarding & Contracts"
        HONESTY --> OFFER[📝 Create Job Offer]
        DECEPTION --> OFFER

        OFFER --> O_SALARY[Salary Negotiation]
        OFFER --> O_CONTRACT_TYPE[Contract Type<br/>Seasonal vs. Full-Time]
        OFFER --> O_BENEFITS[Benefits Package<br/>Housing, Health, etc.]
        OFFER --> O_BONUS[Signing Bonus]
        
        OFFER --> ACCEPT_REJECT{Applicant Accepts Offer?}
        ACCEPT_REJECT -- Yes --> HIRED[✅ Employee Hired!]
        ACCEPT_REJECT -- No --> APPLICANT_POOL
    end

    %% ===== THE EMPLOYEE PROFILE (CORE ASSET) =====
    subgraph "<b>The Employee Profile (Core Asset)</b>"
        style EMPLOYEE_PROFILE fill:#fff8e1,stroke:#f57f17,stroke-width:4px
        HIRED --> EMPLOYEE_PROFILE[👤 Employee's Full Profile]
        
        EMPLOYEE_PROFILE --> P_SKILLS[🔧 Skills (1-10)<br/><i>Trainable attributes like<br/>Farming, Mechanical, Agronomy</i>]
        EMPLOYEE_PROFILE --> P_TRAITS[🧠 Traits<br/><i>Innate personality quirks<br/>e.g., Diligent, Lazy, Fast Learner</i>]
        EMPLOYEE_PROFILE --> P_MORALE[❤️ Morale (0-100)<br/><i>Influenced by Pay, Workload, Amenities,<br/>Team Cohesion, Feeling Valued</i>]
        EMPLOYEE_PROFILE --> P_CERTIFICATIONS[🎓 Certifications<br/><i>Official licenses to use<br/>advanced tools & machinery</i>]
        EMPLOYEE_PROFILE --> P_CONTRACT[📄 Contract Details<br/><i>Salary, Type, Benefits</i>]
    end

    %% ===== 4. MANAGEMENT & DEVELOPMENT =====
    subgraph "4. Management & Development"
        EMPLOYEE_PROFILE --> DAILY_TASKS[🔨 Daily Farm Tasks]
        DAILY_TASKS -- Slow Gain --> P_SKILLS

        INVEST[Player Investment Decisions] --> TRAINING[📚 Send to School/Training<br/><i>Costs Time & Money</i>]
        TRAINING -- Fast Gain --> P_SKILLS
        TRAINING -- Unlocks --> P_CERTIFICATIONS
        INVEST --> RAISES[Give Raise / Promotion]
        RAISES -- Boosts --> P_MORALE
    end
    
    %% ===== 5. SEPARATION & REPERCUSSIONS =====
    subgraph "5. Separation & Repercussions"
        P_MORALE -- Reaches Zero --> QUIT[⚠️ Employee Quits!]
        PLAYER_CHOICE[Player Decision] --> FIRE[🔥 Fire Employee]

        QUIT --> QUIT_CONSEQUENCES[Consequences<br/>- Steals Tools<br/>- Leaves Bad Agency Review]
        FIRE --> FIRE_CONSEQUENCES[🚨 Consequences<br/>- Team Morale Drop<br/>- Pay Severance<br/>- Risk of Lawsuit Event]
    end

    %% ===== 6. KEY SYSTEM INTEGRATIONS =====
    subgraph "🔗 Key System Integrations"
        direction LR
        style EMPLOYEE_PROFILE_LINK fill:#fff8e1,stroke:#f57f17,stroke-width:2px
        
        EMPLOYEE_PROFILE_LINK[👤 Employee Profile]
        
        EMPLOYEE_PROFILE_LINK -.->|Affects Wear & Tear| FLEET_MGMT[🚜 Fleet Management]
        EMPLOYEE_PROFILE_LINK -.->|Affects Work Speed & Quality| TASK_MGMT[📋 Task Management]
        EMPLOYEE_PROFILE_LINK -.->|Required to Operate| MACHINERY_SYS[⚙️ Advanced Machinery]
        EMPLOYEE_PROFILE_LINK -.->|Drives Need for Amenities| BUILDING_SYS[🏢 Building System]
        EMPLOYEE_PROFILE_LINK -.->|Direct Financial Impact| ECONOMY_SYS[💰 Economy System]
        EMPLOYEE_PROFILE_LINK -.->|Requires Specialists| RESEARCH_SYS[🔬 Research System]
    end

    %% Styling
    classDef sourcing fill:#e0f7fa,stroke:#006064,stroke-width:2px
    classDef interviewing fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef onboarding fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef management fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef separation fill:#ffcdd2,stroke:#b71c1c,stroke-width:2px
    classDef integration fill:#f1f8e9,stroke:#33691e,stroke-width:2px

    class SOURCING,JOB_BOARD,AGENCY,HEADHUNT,APPLICANT_POOL sourcing
    class HIRING_UI,INTERVIEW_MINIGAME,IP,Q_BACKGROUND,Q_SITUATIONAL,Q_REFERENCE,REVEAL_TRAITS,BLUFF,DECEPTION,HONESTY interviewing
    class OFFER,O_SALARY,O_CONTRACT_TYPE,O_BENEFITS,O_BONUS,ACCEPT_REJECT,HIRED onboarding
    class INVEST,DAILY_TASKS,TRAINING,RAISES management
    class QUIT,FIRE,QUIT_CONSEQUENCES,FIRE_CONSEQUENCES,PLAYER_CHOICE separation
    class FLEET_MGMT,TASK_MGMT,MACHINERY_SYS,BUILDING_SYS,ECONOMY_SYS,RESEARCH_SYS integration