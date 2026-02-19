#!/usr/bin/env python3
"""
教训提取算法 - 完整评估版
包含：召回率 + 精确率 + F1 + 误报率 + 评分分布
"""

import json
import re
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple

class LessonExtractor:
    def __init__(self, time_decay_factor: float = 0.1, threshold: float = 0.3):
        self.time_decay = time_decay_factor
        self.threshold = threshold

    def semantic_similarity(self, trigger: str, lesson: str) -> float:
        """关键词重叠度"""
        trigger_words = set(trigger.lower().split())
        lesson_words = set(lesson.lower().split())
        overlap = len(trigger_words & lesson_words)
        return min(overlap / max(len(trigger_words), 1) * 2, 1.0)

    def calculate_score(self, trigger: str, lesson: str,
                       frequency: int, cost_factor: float) -> float:
        """复合评分"""
        semantic_weight = self.semantic_similarity(trigger, lesson)
        frequency_score = min(frequency * 0.5, 3.0)
        cost_score = min(cost_factor * 0.3, 2.0)

        return (semantic_weight * 0.4 +
                frequency_score * 0.3 +
                cost_score * 0.2 +
                self.time_decay * 0.1)

    def extract_from_logs(self, log_text: str,
                         lessons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从日志中提取候选教训事件"""
        candidates = []
        for lesson in lessons:
            trigger = lesson.get('trigger', '')
            # 简单匹配：触发词出现在日志中
            if re.search(re.escape(trigger), log_text, re.IGNORECASE):
                score = self.calculate_score(
                    trigger=trigger,
                    lesson=lesson.get('lesson', ''),
                    frequency=2,
                    cost_factor=1.5
                )
                if score >= self.threshold:
                    candidates.append({
                        'id': lesson.get('id'),
                        'trigger': trigger,
                        'score': round(score, 3),
                        'lesson_id': lesson.get('id')
                    })
        return candidates

    def load_lessons(self, filepath: str) -> List[Dict[str, Any]]:
        """加载种子教训"""
        lessons = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    lessons.append(json.loads(line))
        return lessons

    def evaluate_full(self, candidates: List[Dict[str, Any]],
                     ground_truth: List[str]) -> Dict[str, Any]:
        """
        完整评估
        ground_truth: 真实教训 ID 列表
        """
        # 提取候选 ID
        candidate_ids = [c['lesson_id'] for c in candidates]

        # 计算各项指标
        tp = len(set(candidate_ids) & set(ground_truth))  # 真正例
        fp = len(set(candidate_ids) - set(ground_truth))  # 假正例
        fn = len(set(ground_truth) - set(candidate_ids))  # 假负例

        # 召回率、精确率、F1
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        # 误报率
        false_positive_rate = fp / len(candidates) if candidates else 0

        # 评分分布
        scores = [c['score'] for c in candidates]
        score_distribution = {
            'min': min(scores) if scores else 0,
            'max': max(scores) if scores else 0,
            'avg': sum(scores) / len(scores) if scores else 0,
            'count': len(scores)
        }

        return {
            'metrics': {
                'recall': round(recall, 3),
                'precision': round(precision, 3),
                'f1': round(f1, 3),
                'false_positive_rate': round(false_positive_rate, 3),
                'tp': tp,
                'fp': fp,
                'fn': fn
            },
            'score_distribution': score_distribution,
            'candidates': candidates
        }

def main():
    extractor = LessonExtractor(threshold=0.3)

    # 加载种子教训
    lessons = extractor.load_lessons('memory/lessons.jsonl')
    ground_truth = [l['id'] for l in lessons]

    print("📊 Memory Lab - 完整评估")
    print("=" * 60)
    print(f"种子数据：{len(lessons)} 条")
    print(f"阈值：{extractor.threshold}\n")

    # 模拟测试：用种子数据作为日志（简化测试）
    # 实际 Phase 2 会用真实 30 天日志
    test_log = "\n".join([l['trigger'] + " - " + l.get('lesson', '')
                          for l in lessons])

    # 提取候选
    candidates = extractor.extract_from_logs(test_log, lessons)

    # 完整评估
    eval_result = extractor.evaluate_full(candidates, ground_truth)

    # 输出
    print("📈 评估指标：")
    metrics = eval_result['metrics']
    print(f"  召回率 (Recall): {metrics['recall'] * 100}%")
    print(f"  精确率 (Precision): {metrics['precision'] * 100}%")
    print(f"  F1 分数: {metrics['f1']:.3f}")
    print(f"  误报率 (FPR): {metrics['false_positive_rate'] * 100}%")
    print(f"\n  真正例 (TP): {metrics['tp']}")
    print(f"  假正例 (FP): {metrics['fp']}")
    print(f"  假负例 (FN): {metrics['fn']}")

    print("\n📊 评分分布：")
    dist = eval_result['score_distribution']
    print(f"  最小值: {dist['min']}")
    print(f"  最大值: {dist['max']}")
    print(f"  平均值: {dist['avg']:.3f}")
    print(f"  数量: {dist['count']}")

    # 保存
    os.makedirs('ai-collab-log/reports', exist_ok=True)
    with open('ai-collab-log/reports/phase1_full_metrics.json', 'w') as f:
        json.dump(eval_result, f, indent=2, ensure_ascii=False)
    print("\n💾 完整结果已保存到 ai-collab-log/reports/phase1_full_metrics.json")

if __name__ == '__main__':
    main()
