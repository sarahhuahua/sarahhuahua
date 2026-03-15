from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class AgentOutput:
    agent: str
    advice: str
    confidence: float
    meta: Dict[str, Any]


class TriageGuardrailAgent:
    """High-risk detector. If triggered, it can short-circuit regular flow."""

    emergency_keywords = ["胸痛", "呼吸困难", "意识", "昏迷", "抽搐", "呕吐", "腹痛", "糖尿病足", "感染"]
    hypo_keywords = ["手抖", "心慌", "出汗", "低血糖", "头晕"]

    def run(self, user_input: str, profile: Dict[str, Any], metrics: Dict[str, Any]) -> AgentOutput:
        glucose = metrics.get("glucose")
        text = user_input.lower()

        emergency = any(k in user_input for k in self.emergency_keywords)
        hypo_symptom = any(k in user_input for k in self.hypo_keywords)

        if glucose is not None and glucose <= 3.9 and hypo_symptom:
            return AgentOutput(
                agent="guardrail",
                advice=(
                    "检测到低血糖高风险。请立即执行15-15原则："
                    "立刻补充15g快速糖（葡萄糖片/含糖饮料），15分钟后复测血糖；"
                    "若仍<3.9 mmol/L，重复一次。若意识异常或无法进食，立即呼叫120。"
                ),
                confidence=0.99,
                meta={"risk_level": "high", "route": "emergency"},
            )

        if glucose is not None and glucose >= 16.7 and ("呕吐" in user_input or "腹痛" in user_input):
            emergency = True

        if emergency:
            return AgentOutput(
                agent="guardrail",
                advice="存在急症信号，请立即前往急诊或呼叫120，不要仅依赖线上建议。",
                confidence=0.97,
                meta={"risk_level": "high", "route": "emergency"},
            )

        return AgentOutput(
            agent="guardrail",
            advice="未识别到急症信号，继续常规管理建议。",
            confidence=0.80,
            meta={"risk_level": "normal", "route": "normal"},
        )


class MedicalAdviceAgent:
    def run(self, user_input: str, profile: Dict[str, Any], metrics: Dict[str, Any]) -> AgentOutput:
        glucose = metrics.get("glucose")
        period = metrics.get("period", "随机")
        if glucose is None:
            advice = "建议补充最近3天的空腹/餐后2小时血糖数据，再做更准确判断。"
            conf = 0.66
        elif period == "空腹" and glucose > 7.0:
            advice = "空腹血糖偏高，优先检查晚餐主食量、睡前加餐与作息，并按计划复诊评估。"
            conf = 0.84
        elif period == "餐后" and glucose > 10.0:
            advice = "餐后血糖偏高，建议减少精制碳水并增加餐后轻中强度步行20-30分钟。"
            conf = 0.84
        else:
            advice = "当前血糖在可管理范围，继续监测并保持饮食与运动稳定。"
            conf = 0.78

        return AgentOutput("medical", advice, conf, {"period": period})


class DietAgent:
    def run(self, user_input: str, profile: Dict[str, Any], metrics: Dict[str, Any]) -> AgentOutput:
        local_hint = "南京饮食建议：鸭血粉丝汤可选择小份+少粉丝；盐水鸭控制分量并搭配高纤蔬菜。"
        template = "每餐采用'1/2蔬菜+1/4优质蛋白+1/4主食'，主食优先全谷杂豆。"
        return AgentOutput("diet", f"{template} {local_hint}", 0.82, {"focus": "local_diet"})


class ExerciseAgent:
    def run(self, user_input: str, profile: Dict[str, Any], metrics: Dict[str, Any]) -> AgentOutput:
        insulin = profile.get("on_insulin", False)
        safety = "运动前血糖<5.6 mmol/L时先补充少量碳水。" if insulin else "运动前后记录血糖，避免空腹高强度训练。"
        plan = "每周150分钟中等强度有氧（快走/骑行）+2次抗阻训练。"
        return AgentOutput("exercise", f"{plan} {safety}", 0.80, {"insulin": insulin})


class HealthManagementAgent:
    def run(self, user_input: str, profile: Dict[str, Any], metrics: Dict[str, Any]) -> AgentOutput:
        return AgentOutput(
            "management",
            "建议建立每周管理清单：每日血糖记录、每3个月HbA1c、每年眼底和尿微量白蛋白筛查。",
            0.86,
            {"follow_up": "enabled"},
        )


class NanjingCareGuideAgent:
    def __init__(self, hospitals: List[Dict[str, Any]]) -> None:
        self.hospitals = hospitals

    def run(self, user_input: str, profile: Dict[str, Any], metrics: Dict[str, Any]) -> AgentOutput:
        district = profile.get("district", "鼓楼区")

        candidates = [h for h in self.hospitals if h.get("district") == district]
        if not candidates:
            candidates = self.hospitals[:2]

        top = candidates[0]
        advice = (
            f"建议优先前往{top['name']}（{top['district']}，{top['address']}）内分泌门诊；"
            f"可通过{top['registration']}挂号。"
        )
        return AgentOutput("nanjing_guide", advice, 0.88, {"district": district, "hospital": top["name"]})
