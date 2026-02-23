# Core Architecture Design

## 1. Directory Structure
```text
specforge/
├── __init__.py
├── main.py           # Entry point (Typer app)
├── config.py         # Env vars & constants
├── llm/
│   ├── client.py     # LiteLLM wrapper (supports Anthropic, OpenAI, Azure)
│   └── prompts.py    # System prompts & stage-specific prompts
├── core/
│   ├── session.py    # State management (Save/Load history + workflow state)
│   ├── stage_manager.py  # Double Diamond workflow state machine
│   ├── web.py        # URL content fetching
│   └── pdf.py        # PDF text extraction
└── ui/
    └── console.py    # Rich console utilities & stage-aware UI
```

## 2. Double Diamond Workflow Architecture

SpecForge implements the **Double Diamond** design methodology through a state machine:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Double Diamond Workflow                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  📋 DISCOVERY               🎯 DEFINITION                          │
│  ├─ Competitor Analysis     ├─ Product Vision Statement            │
│  ├─ User Personas           ├─ User Journey Map (Mermaid)          │
│  └─ Pain Points             └─ Feature Prioritization (MoSCoW)    │
│         ↓                           ↓                                │
│         └───────────┬─────────────────┘                            │
│                     ↓                                                  │
│                  💡 IDEATION              🚀 DELIVERY                │
│                  ├─ Tech Options          ├─ Data Model              │
│                  ├─ Stack Selection       ├─ API Contracts           │
│                  └─ Risk Assessment       └─ Implementation Notes    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.1 Stage Manager (specforge/core/stage_manager.py)

The `StageManager` class is the heart of the workflow:

```python
class Stage(str, Enum):
    DISCOVERY = "discovery"
    DEFINITION = "definition"
    IDEATION = "ideation"
    DELIVERY = "delivery"
    COMPLETE = "complete"

class StageManager:
    def can_advance(self) -> bool:
        """Check if all required confirmations are done"""

    def advance(self) -> Stage:
        """Move to next stage"""

    def get_stage_prompt(self) -> str:
        """Get stage-specific system prompt"""

    def get_stage_context(self) -> str:
        """Get accumulated artifacts as context"""
```

### 2.2 Workflow State Artifacts

Each stage accumulates specific artifacts:

```python
@dataclass
class WorkflowState:
    # Current stage
    current_stage: Stage

    # Discovery artifacts
    user_personas: list[UserPersona]
    competitors: list[Competitor]

    # Definition artifacts
    product_vision_statement: str
    user_journey_map: str
    mvp_features: list[Feature]  # with priority (P0/P1/P2)

    # Ideation artifacts
    tech_options: list[str]
    tech_recommendation: str

    # Delivery artifacts
    api_contracts: str
    data_model: str

    # Confirmation flags
    personas_confirmed: bool
    competitors_confirmed: bool
    mvp_confirmed: bool
    tech_confirmed: bool
```

## 3. User Interaction Flow

```
┌─────────────────────────────────────────────────────────────┐
│ User: "I want a crypto tracker app"                         │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ AI (DISCOVERY):                                             │
│ "Let me understand your problem space first..."             │
│ - Creates 2 user personas                                   │
│ - Analyzes 3 competitors                                    │
│ "Do these personas match your target users?"                │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ User: "confirm"                                              │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ AI (DEFINITION):                                            │
│ "Great! Now let's define your MVP..."                       │
│ - Product Vision Statement                                  │
│ - User Journey Map (Mermaid flowchart)                      │
│ - Feature Matrix (P0: 5 features, P1: 3, P2: 4)             │
│ "Is this the right scope for v1?"                           │
└─────────────────────────────────────────────────────────────┘
```

## 4. State Persistence

Session data is saved to `.specforge/session.json`:

```json
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "workflow_state": {
    "current_stage": "definition",
    "user_personas": [...],
    "competitors": [...],
    "mvp_features": [...],
    "personas_confirmed": true,
    "competitors_confirmed": true,
    "mvp_confirmed": false
  }
}
```

## 5. Command Reference

| Command | Action |
|---------|--------|
| `specforge new "idea"` | Start new session |
| `specforge new --fresh` | Start fresh (clear history) |
| `confirm` | Confirm current stage artifacts |
| `/status` | Show current stage and progress |
| `/export <dir>` | Export PRD + Tech Spec to directory |
| `exit` | Save and exit |
