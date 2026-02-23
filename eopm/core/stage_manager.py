"""Stage Manager for Double Diamond Workflow.

This module implements the state machine that manages the PM workflow through
the four stages of the Double Diamond model:
- Discovery: Market/Competitor analysis, User Personas, Pain Points
- Definition: Value Proposition, User Journey Map, MVP Scope
- Ideation: Feature prioritization, Technical options
- Delivery: Detailed specifications, API contracts, Implementation details
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Stage(str, Enum):
    """The four stages of the Double Diamond model."""

    DISCOVERY = "discovery"
    DEFINITION = "definition"
    IDEATION = "ideation"
    DELIVERY = "delivery"
    COMPLETE = "complete"


@dataclass
class UserPersona:
    """A user persona card."""

    name: str
    age: str | None = None
    role: str = ""
    description: str = ""
    pain_points: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    scenarios: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Format the persona as Markdown."""
        md = f"### {self.name}\n\n"
        if self.age:
            md += f"**Age:** {self.age}  \n"
        if self.role:
            md += f"**Role:** {self.role}  \n"
        md += f"\n{self.description}\n\n"
        if self.pain_points:
            md += "**Pain Points:**\n"
            for point in self.pain_points:
                md += f"- {point}\n"
            md += "\n"
        if self.goals:
            md += "**Goals:**\n"
            for goal in self.goals:
                md += f"- {goal}\n"
            md += "\n"
        if self.scenarios:
            md += "**Key Scenarios:**\n"
            for scenario in self.scenarios:
                md += f"- {scenario}\n"
        return md


@dataclass
class Competitor:
    """A competitor analysis entry."""

    name: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    usp: str = ""  # Unique Selling Proposition comparison

    def to_markdown(self) -> str:
        """Format the competitor as Markdown."""
        md = f"### {self.name}\n\n"
        if self.strengths:
            md += "**Strengths:**\n"
            for s in self.strengths:
                md += f"- {s}\n"
            md += "\n"
        if self.weaknesses:
            md += "**Weaknesses:**\n"
            for w in self.weaknesses:
                md += f"- {w}\n"
            md += "\n"
        if self.usp:
            md += f"**Our Differentiation:** {self.usp}\n"
        return md


@dataclass
class Feature:
    """A feature with priority."""

    name: str
    priority: str  # P0 (Must-have), P1 (Should-have), P2 (Could-have)
    description: str = ""
    effort: str = ""  # t-shirt sizing: S, M, L, XL
    category: str = ""

    def to_markdown(self) -> str:
        """Format the feature as Markdown."""
        priority_emoji = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(self.priority, "⚪")
        md = f"- {priority_emoji} **{self.name}** ({self.priority})"
        if self.effort:
            md += f" - Effort: {self.effort}"
        md += f"\n  {self.description}\n"
        return md


@dataclass
class WorkflowState:
    """The complete state of the PM workflow."""

    current_stage: Stage = Stage.DISCOVERY
    project_vision: str = ""
    product_vision_statement: str = ""

    # Discovery stage artifacts
    user_personas: list[UserPersona] = field(default_factory=list)
    competitors: list[Competitor] = field(default_factory=list)

    # Definition stage artifacts
    user_journey_map: str = ""
    value_proposition: str = ""
    mvp_features: list[Feature] = field(default_factory=list)

    # Ideation stage artifacts
    tech_options: list[str] = field(default_factory=list)
    tech_recommendation: str = ""

    # Delivery stage artifacts
    api_contracts: str = ""
    data_model: str = ""
    implementation_notes: str = ""

    # User confirmation flags
    personas_confirmed: bool = False
    competitors_confirmed: bool = False
    mvp_confirmed: bool = False
    tech_confirmed: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "current_stage": self.current_stage.value,
            "project_vision": self.project_vision,
            "product_vision_statement": self.product_vision_statement,
            "user_personas": [
                {
                    "name": p.name,
                    "age": p.age,
                    "role": p.role,
                    "description": p.description,
                    "pain_points": p.pain_points,
                    "goals": p.goals,
                    "scenarios": p.scenarios,
                }
                for p in self.user_personas
            ],
            "competitors": [
                {
                    "name": c.name,
                    "strengths": c.strengths,
                    "weaknesses": c.weaknesses,
                    "usp": c.usp,
                }
                for c in self.competitors
            ],
            "user_journey_map": self.user_journey_map,
            "value_proposition": self.value_proposition,
            "mvp_features": [
                {
                    "name": f.name,
                    "priority": f.priority,
                    "description": f.description,
                    "effort": f.effort,
                    "category": f.category,
                }
                for f in self.mvp_features
            ],
            "tech_options": self.tech_options,
            "tech_recommendation": self.tech_recommendation,
            "api_contracts": self.api_contracts,
            "data_model": self.data_model,
            "implementation_notes": self.implementation_notes,
            "personas_confirmed": self.personas_confirmed,
            "competitors_confirmed": self.competitors_confirmed,
            "mvp_confirmed": self.mvp_confirmed,
            "tech_confirmed": self.tech_confirmed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorkflowState:
        """Create from dictionary for JSON deserialization."""
        state = cls(current_stage=Stage(data.get("current_stage", Stage.DISCOVERY.value)))
        state.project_vision = data.get("project_vision", "")
        state.product_vision_statement = data.get("product_vision_statement", "")

        state.user_personas = [
            UserPersona(
                name=p["name"],
                age=p.get("age"),
                role=p.get("role", ""),
                description=p.get("description", ""),
                pain_points=p.get("pain_points", []),
                goals=p.get("goals", []),
                scenarios=p.get("scenarios", []),
            )
            for p in data.get("user_personas", [])
        ]

        state.competitors = [
            Competitor(
                name=c["name"],
                strengths=c.get("strengths", []),
                weaknesses=c.get("weaknesses", []),
                usp=c.get("usp", ""),
            )
            for c in data.get("competitors", [])
        ]

        state.user_journey_map = data.get("user_journey_map", "")
        state.value_proposition = data.get("value_proposition", "")
        state.mvp_features = [
            Feature(
                name=f["name"],
                priority=f.get("priority", "P2"),
                description=f.get("description", ""),
                effort=f.get("effort", ""),
                category=f.get("category", ""),
            )
            for f in data.get("mvp_features", [])
        ]
        state.tech_options = data.get("tech_options", [])
        state.tech_recommendation = data.get("tech_recommendation", "")
        state.api_contracts = data.get("api_contracts", "")
        state.data_model = data.get("data_model", "")
        state.implementation_notes = data.get("implementation_notes", "")

        state.personas_confirmed = data.get("personas_confirmed", False)
        state.competitors_confirmed = data.get("competitors_confirmed", False)
        state.mvp_confirmed = data.get("mvp_confirmed", False)
        state.tech_confirmed = data.get("tech_confirmed", False)

        return state


class StageManager:
    """Manages the PM workflow through the Double Diamond stages."""

    def __init__(self, state: WorkflowState | None = None) -> None:
        """Initialize the stage manager."""
        self.state = state or WorkflowState()

    @property
    def current_stage(self) -> Stage:
        """Get the current stage."""
        return self.state.current_stage

    def can_advance(self) -> bool:
        """Check if we can advance to the next stage."""
        stage = self.current_stage

        if stage == Stage.DISCOVERY:
            return self.state.personas_confirmed and self.state.competitors_confirmed
        if stage == Stage.DEFINITION:
            return self.state.mvp_confirmed
        if stage == Stage.IDEATION:
            return self.state.tech_confirmed
        if stage == Stage.DELIVERY:
            return True  # Can always mark as complete
        return False

    def advance(self) -> Stage:
        """Advance to the next stage if possible."""
        if not self.can_advance():
            raise RuntimeError(
                f"Cannot advance from {self.current_stage.value}. "
                "Please complete the required confirmations first."
            )

        stage_order = [
            Stage.DISCOVERY,
            Stage.DEFINITION,
            Stage.IDEATION,
            Stage.DELIVERY,
            Stage.COMPLETE,
        ]

        current_idx = stage_order.index(self.current_stage)
        if current_idx < len(stage_order) - 1:
            self.state.current_stage = stage_order[current_idx + 1]

        return self.current_stage

    def get_stage_prompt(self) -> str:
        """Get the system prompt for the current stage."""
        stage = self.current_stage

        base = f"You are currently in the **{stage.value.upper()}** stage of the Double Diamond workflow.\n\n"

        if stage == Stage.DISCOVERY:
            return base + """Your focus is on understanding the problem space.

IMPORTANT: Ask any scoping/clarifying questions using @CHOICE blocks FIRST and wait for answers before producing personas and competitors. Never list questions as plain text and immediately show the stage confirmation — those answers will be lost.

Workflow:
1. Use @CHOICE to collect key scoping decisions (target users, job categories, platform, etc.)
2. After receiving answers, produce 2-3 competitor analyses and 1-2 user personas
3. Only then present the @CHOICE:confirm for stage completion

Do NOT show the stage completion confirmation until scoping questions are answered."""
        elif stage == Stage.DEFINITION:
            return base + """Your focus is on defining the solution scope:

1. **Product Vision Statement**: Craft a single, compelling sentence that captures:
   - Who the product is for
   - What problem it solves
   - What makes it different

2. **User Journey Map**: Create a visual flow using Mermaid syntax showing:
   - User entry points
   - Key decision points
   - Core actions
   - Success criteria

3. **Feature Prioritization (MoSCoW)**: Create a feature matrix with:
   - P0 (Must-have): Critical for MVP
   - P1 (Should-have): Important but not critical
   - P2 (Could-have): Nice to have
   - Include effort estimates (S/M/L/XL)

Focus on defining MVP boundaries. Ask the user to confirm the feature scope before proceeding."""
        elif stage == Stage.IDEATION:
            return base + """Your focus is on technical exploration:

1. **Technology Options**: Explore 2-3 different architectural approaches:
   - Different stack options (e.g., monolith vs microservices)
   - Database choices
   - Third-party service integrations
   - Trade-offs (pros/cons of each)

2. **Technical Recommendation**: Based on requirements, recommend:
   - Primary technology stack
   - Key architectural decisions
   - Justification for choices

3. **Risk Assessment**: Identify:
   - Technical risks
   - Implementation challenges
   - Areas needing spike/POC

Ask the user to confirm the technical direction before proceeding."""
        elif stage == Stage.DELIVERY:
            return base + """Your focus is on high-level implementation specs (consumed by senior engineers + Claude Code):

1. **Data Model**: Core entities and relationships only — no field-level definitions or schemas.

2. **API Surface**: Endpoint list with one-line descriptions — no request/response bodies.

3. **Implementation Milestones**: Break work into M1/M2/M3... chunks with concrete deliverables.

4. **Key Decisions & Open Questions**: Architectural decisions made, and unresolved questions.

Keep output concise and structural. Avoid TypeScript interfaces, detailed schemas, or field lists."""
        else:  # COMPLETE
            return "All stages complete. The product is ready for development handoff."

    def get_stage_context(self) -> str:
        """Get context about accumulated artifacts for the current stage."""
        if self.current_stage == Stage.DISCOVERY:
            context = ""
            if self.state.user_personas:
                context += "\n**Current Personas:**\n"
                for p in self.state.user_personas:
                    context += f"- {p.name}\n"
            if self.state.competitors:
                context += "\n**Current Competitors:**\n"
                for c in self.state.competitors:
                    context += f"- {c.name}\n"
            return context

        elif self.current_stage == Stage.DEFINITION:
            context = "\n**Validated Personas:**\n"
            for p in self.state.user_personas:
                context += f"- {p.name}: {p.role}\n"
            context += "\n**Competitor Landscape:**\n"
            for c in self.state.competitors:
                context += f"- {c.name}: {c.usp or 'Analyzed'}\n"
            return context

        elif self.current_stage == Stage.IDEATION:
            context = f"\n**Product Vision:** {self.state.product_vision_statement}\n\n"
            context += "**MVP Features (P0):**\n"
            p0_features = [f for f in self.state.mvp_features if f.priority == "P0"]
            for f in p0_features:
                context += f"- {f.name} ({f.effort})\n"
            return context

        elif self.current_stage == Stage.DELIVERY:
            context = f"\n**Tech Stack:** {self.state.tech_recommendation}\n\n"
            context += "**All MVP Features:**\n"
            for f in self.state.mvp_features:
                context += f"- {f.name} ({f.priority})\n"
            return context

        return ""

    def needs_confirmation(self) -> bool:
        """Check if the current stage needs user confirmation."""
        stage = self.current_stage

        if stage == Stage.DISCOVERY:
            return not (self.state.personas_confirmed and self.state.competitors_confirmed)
        if stage == Stage.DEFINITION:
            return not self.state.mvp_confirmed
        if stage == Stage.IDEATION:
            return not self.state.tech_confirmed
        return False

    def get_confirmation_prompt(self) -> str:
        """Get the confirmation prompt for the current stage."""
        stage = self.current_stage

        if stage == Stage.DISCOVERY:
            if not self.state.personas_confirmed:
                return "Please review the user personas above. Do these accurately represent your target users? (Reply 'confirm' or request changes)"
            if not self.state.competitors_confirmed:
                return "Please review the competitor analysis above. Is this analysis accurate and helpful? (Reply 'confirm' or request changes)"

        elif stage == Stage.DEFINITION:
            if not self.state.mvp_confirmed:
                return "Please review the MVP feature list above. Does this represent the right scope for v1? (Reply 'confirm' or request changes)"

        elif stage == Stage.IDEATION:
            if not self.state.tech_confirmed:
                return "Please review the technical recommendation above. Does this approach work for your team/context? (Reply 'confirm' or request changes)"

        return ""
