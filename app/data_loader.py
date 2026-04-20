from __future__ import annotations

from typing import List, Tuple

from app.domain_detector.types import DomainSample


def build_default_training_data() -> Tuple[List[str], List[DomainSample], List[DomainSample]]:
    domain_docs = [
        "核心网体验策略包括时延优化、切片保障、拥塞控制和QoS等级管理",
        "面向5G SA核心网的策略控制需要结合PCF、SMF和UPF协同调度",
        "体验保障策略关注语音掉线率、视频卡顿率、会话建立成功率",
    ]
    semantic_samples = [
        DomainSample("核心网策略如何降低跨省漫游时延", 1),
        DomainSample("UPF拥塞后如何进行体验分级保障", 1),
        DomainSample("如何设置PCF策略实现VIP用户优先", 1),
        DomainSample("今晚篮球比赛直播时间", 0),
        DomainSample("推荐几款降噪耳机", 0),
        DomainSample("北京明天的天气怎么样", 0),
    ]
    fusion_samples = [
        DomainSample("核心网体验策略里切片优先级怎么配置", 1),
        DomainSample("语音业务在5G核心网中如何做QoS保障", 1),
        DomainSample("会话建立失败率高应如何调整SMF策略", 1),
        DomainSample("帮我写一个旅游攻略", 0),
        DomainSample("这家餐厅评价如何", 0),
        DomainSample("怎么学习python爬虫", 0),
    ]
    return domain_docs, semantic_samples, fusion_samples
