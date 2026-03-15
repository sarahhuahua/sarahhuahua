from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from assistant.agents import (
    DietAgent,
    ExerciseAgent,
    HealthManagementAgent,
    MedicalAdviceAgent,
    NanjingCareGuideAgent,
    TriageGuardrailAgent,
)


@dataclass
class AssistantResponse:
    summary: str
    actions_today: List[str]
    when_to_seek_care: str
    local_guide: str
    risk_level: str


def _extract_metrics(user_input: str) -> Dict[str, Any]:
    # 支持输入："空腹8.7"、"餐后 11.2"、"血糖2.9"
    glucose_match = re.search(r"(\d+(?:\.\d+)?)", user_input)
    glucose = float(glucose_match.group(1)) if glucose_match else None

    period = "随机"
    if "空腹" in user_input:
        period = "空腹"
    elif "餐后" in user_input:
        period = "餐后"

    return {"glucose": glucose, "period": period}


class NanjingDiabetesAssistant:
    def __init__(self, hospitals_path: str = "data/nanjing_hospitals.json") -> None:
        hospitals = json.loads(Path(hospitals_path).read_text(encoding="utf-8"))
        self.guardrail = TriageGuardrailAgent()
        self.medical = MedicalAdviceAgent()
        self.diet = DietAgent()
        self.exercise = ExerciseAgent()
        self.management = HealthManagementAgent()
        self.local_guide = NanjingCareGuideAgent(hospitals)

    def chat(self, user_input: str, profile: Dict[str, Any]) -> AssistantResponse:
        metrics = _extract_metrics(user_input)

        guardrail_out = self.guardrail.run(user_input, profile, metrics)
        if guardrail_out.meta["route"] == "emergency":
            return AssistantResponse(
                summary=guardrail_out.advice,
                actions_today=["停止剧烈活动", "联系家属协助", "尽快前往急诊或呼叫120"],
                when_to_seek_care="立即就医，不延迟。",
                local_guide="如在南京，优先选择最近有急诊能力的三甲医院。",
                risk_level="high",
            )

        outputs = [
            self.medical.run(user_input, profile, metrics),
            self.diet.run(user_input, profile, metrics),
            self.exercise.run(user_input, profile, metrics),
            self.management.run(user_input, profile, metrics),
            self.local_guide.run(user_input, profile, metrics),
        ]

        summary = outputs[0].advice
        actions_today = [outputs[1].advice, outputs[2].advice, "睡前复测血糖并记录。"]
        when_to_seek_care = "若血糖持续>16.7 mmol/L或出现明显不适（呕吐、胸痛、意识异常），请立即就医。"
        local_guide = outputs[4].advice

        return AssistantResponse(
            summary=summary,
            actions_today=actions_today,
            when_to_seek_care=when_to_seek_care,
            local_guide=local_guide,
            risk_level=guardrail_out.meta["risk_level"],
        )
