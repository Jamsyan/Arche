"""Cost calculator for cloud training — pricing table and aggregation."""

from __future__ import annotations

from datetime import datetime

# 定价表（元/小时）
PRICING_TABLE: dict[str, dict[str, float]] = {
    "mock": {
        "A100": 15.0,
        "H100": 25.0,
        "V100": 8.0,
        "RTX4090": 5.0,
        "default": 10.0,
    },
    # 智星云
    "zhixingyun": {
        "A100": 12.5,
        "H100": 22.0,
        "V100": 7.5,
        "RTX4090": 4.5,
        "RTX3090": 3.5,
        "RTX3080": 3.0,
        "default": 10.0,
    },
    # 阿里云（待接入）
    "aliyun": {
        "A100": 16.0,
        "H100": 28.0,
        "default": 18.0,
    },
}


def calculate_rate(provider: str, gpu_type: str) -> float:
    """获取指定 Provider + GPU 类型的单价（元/小时）。"""
    provider_pricing = PRICING_TABLE.get(provider, PRICING_TABLE["mock"])
    return provider_pricing.get(gpu_type, provider_pricing.get("default", 10.0))


def calculate_instance_cost(
    started_at: datetime | None,
    stopped_at: datetime | None,
    provider: str,
    gpu_type: str,
) -> float:
    """计算单个实例的运行费用。"""
    if not started_at:
        return 0.0

    end = stopped_at or datetime.now(started_at.tzinfo)
    hours = (end - started_at).total_seconds() / 3600
    rate = calculate_rate(provider, gpu_type)
    return round(hours * rate, 2)


def aggregate_costs(instances: list[dict]) -> dict:
    """汇总多个实例的费用。

    Args:
        instances: [{provider, gpu_type, started_at, stopped_at}]

    Returns:
        {total_cost, breakdown: [{provider, gpu_type, cost}]}
    """
    breakdown = []
    total = 0.0

    for inst in instances:
        cost = calculate_instance_cost(
            started_at=inst.get("started_at"),
            stopped_at=inst.get("stopped_at"),
            provider=inst.get("provider", "mock"),
            gpu_type=inst.get("gpu_type", "A100"),
        )
        breakdown.append(
            {
                "instance_id": inst.get("instance_id", ""),
                "provider": inst.get("provider", "mock"),
                "gpu_type": inst.get("gpu_type", "A100"),
                "cost": cost,
            }
        )
        total += cost

    return {
        "total_cost": round(total, 2),
        "currency": "CNY",
        "instance_count": len(breakdown),
        "breakdown": breakdown,
    }
