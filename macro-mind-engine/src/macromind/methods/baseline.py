"""Provisional scenario baselines without turning unknowns into negative facts."""

from html import escape
from typing import Literal

from pydantic import Field, model_validator

from macromind.methods.prototype import Model


class WorkingBaseline(Model):
    id: str
    topic: str
    source_case: str
    evidence_cutoff: str
    coverage: Literal["selected_excerpts", "systematic_observation"]
    evidence_scope: str = Field(min_length=1)
    evidence_state: Literal["unknown"] = "unknown"
    working_judgment: str = Field(min_length=1)
    consequences: list[str] = Field(min_length=1)
    alternative: str = Field(min_length=1)
    upgrade_triggers: list[str] = Field(min_length=1)
    downgrade_triggers: list[str] = Field(min_length=1)
    review_horizon: str = Field(min_length=1)
    observation_window: str | None = None
    expected_signal: str | None = None
    absence_used_as_counterevidence: bool = False
    absence_implies_nonexistence: Literal[False] = False
    status: Literal["PROVISIONAL_WORKING_JUDGMENT"] = "PROVISIONAL_WORKING_JUDGMENT"
    monitoring_active: Literal[False] = False

    @model_validator(mode="after")
    def distinguish_missing_and_observed_absence(self):
        if self.absence_used_as_counterevidence and (
            self.coverage != "systematic_observation"
            or not self.observation_window
            or not self.expected_signal
        ):
            raise ValueError(
                "Absence counterevidence requires a defined observation window and expected signal"
            )
        return self


def render_baselines(items):
    rows = [WorkingBaseline.model_validate(x) for x in items]
    if not rows or len({x.id for x in rows}) != len(rows):
        raise ValueError("Baseline IDs must be nonempty and unique")

    def esc(s):
        return escape(str(s), quote=True)

    def listing(xs):
        return "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in xs) + "</ul>"

    cards = []
    for b in rows:
        cards.append(
            f'<article id="{esc(b.id)}"><h3>{esc(b.topic)}</h3>'
            f'<p class="tag">当前基础判断（暂定）：{esc(b.working_judgment)}</p>'
            f"<h4>据此如何继续推演</h4>{listing(b.consequences)}"
            f"<details><summary>展开备选情景、更新条件与观察范围</summary>"
            f"<h4>备选情景</h4><p>{esc(b.alternative)}</p>"
            f"<h4>何时调整主情景</h4>{listing(b.upgrade_triggers)}"
            f"<h4>什么会削弱备选解释</h4>{listing(b.downgrade_triggers)}"
            f"<p>材料截止：{esc(b.evidence_cutoff)}。范围：{esc(b.evidence_scope)}</p>"
            f"<p>复核安排：{esc(b.review_horizon)}</p>"
            "<p>当前未开启自动监控；选段没有提到，不等于持续观察后应有动作仍未出现。</p>"
            "</details></article>"
        )
    return (
        '<section id="working-baselines"><h2>证据未齐，也要明确当前按什么推演</h2><p>以下是历史示例的暂定分析基线，不是对现实政策的最新判断，也不声称措施不存在。</p>'
        + "".join(cards)
        + "</section>"
    )
