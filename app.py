from __future__ import annotations

import argparse
import json

from assistant.engine import NanjingDiabetesAssistant


def format_response(resp: dict) -> str:
    actions = "\n".join([f"{i+1}. {a}" for i, a in enumerate(resp["actions_today"])])
    return (
        f"\n【当前判断】\n{resp['summary']}\n"
        f"\n【今天行动清单】\n{actions}\n"
        f"\n【何时就医】\n{resp['when_to_seek_care']}\n"
        f"\n【南京就医建议】\n{resp['local_guide']}\n"
        f"\n【风险等级】{resp['risk_level']}\n"
    )


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="南京多智能体糖尿病助手（可运行原型）")
    parser.add_argument("--district", default="鼓楼区", help="所在区，例如 鼓楼区/玄武区")
    parser.add_argument("--insulin", action="store_true", help="是否使用胰岛素")
    args = parser.parse_args()

    profile = {"district": args.district, "on_insulin": args.insulin}
    assistant = NanjingDiabetesAssistant()

    print("南京糖尿病多智能体助手已启动，输入 quit 退出。")
    while True:
        user_input = input("\n你：").strip()
        if user_input.lower() in {"quit", "exit", "q"}:
            print("已退出。")
            break

        response = assistant.chat(user_input, profile)
        print(format_response(response.__dict__))


def run_one_shot(message: str, district: str, insulin: bool) -> str:
    profile = {"district": district, "on_insulin": insulin}
    assistant = NanjingDiabetesAssistant()
    response = assistant.chat(message, profile)
    return json.dumps(response.__dict__, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    run_cli()
