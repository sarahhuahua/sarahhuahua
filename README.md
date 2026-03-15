# 南京地区多智能体糖尿病助手（可运行原型）

这是一个可直接运行的 Python 原型，实现了“多智能体 + 安全分流 + 南京本地就医导航”的基础流程。

## 功能
- 糖尿病咨询建议（基于血糖文本提取）
- 饮食与运动指导（含南京饮食习惯提示）
- 健康管理提醒（随访与并发症筛查）
- 南京本地医院就医建议（按区推荐）
- 高风险守卫（低血糖/急症信号时紧急分流）

## 快速启动
```bash
python app.py --district 鼓楼区 --insulin
```

启动后输入问题，例如：
- `我今天空腹8.7，昨晚吃面比较多`
- `头晕出汗手抖，血糖2.9`

输入 `quit` 退出。

## 一次性调用（用于集成）
可以在 Python 中调用：

```python
from app import run_one_shot
print(run_one_shot("餐后11.2怎么办", district="鼓楼区", insulin=False))
```

## 目录结构
- `app.py`：CLI 入口与一次性调用函数
- `assistant/agents.py`：各子智能体
- `assistant/engine.py`：编排器与响应结构
- `data/nanjing_hospitals.json`：南京本地医院示例数据
- `design.md`：完整架构设计文档

## 说明
- 本项目为原型，不替代医生面诊或急诊处理。
- 如出现胸痛、呼吸困难、意识异常、严重低血糖等情况，请立即就医。
