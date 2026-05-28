"""评测脚本：对知识库检索进行量化评估"""

import json
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
import torch
from rag.knowledge_base import KnowledgeBase


def load_eval_questions(path: str = "data/eval_questions.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _unique_standards(items: list) -> list:
    """Deduplicate while preserving first-occurrence order."""
    seen = set()
    result = []
    for item in items:
        if item not in seen and item:
            seen.add(item)
            result.append(item)
    return result


def recall_at_k(retrieved: list, relevant: list, k: int) -> float:
    """相关问题中，Top-K 去重后命中了几个 / 总相关数"""
    if not relevant:
        return 1.0
    unique_retrieved = _unique_standards(retrieved[:k])
    hits = sum(1 for s in unique_retrieved if s in relevant)
    return hits / len(relevant)


def precision_at_k(retrieved: list, relevant: list, k: int) -> float:
    """Top-K 去重结果中，几个是真正相关的"""
    unique_retrieved = _unique_standards(retrieved[:k])
    if not unique_retrieved:
        return 0.0
    hits = sum(1 for s in unique_retrieved if s in relevant)
    return hits / len(unique_retrieved)


def mrr(retrieved: list, relevant: list) -> float:
    """第一个正确答案的排位倒数"""
    unique = _unique_standards(retrieved)
    for i, s in enumerate(unique, 1):
        if s in relevant:
            return 1.0 / i
    return 0.0


def ndcg_at_k(retrieved: list, relevant: list, k: int) -> float:
    """考虑排序位置的 DCG / IDCG"""
    import math
    unique = _unique_standards(retrieved[:k])

    def dcg(items):
        return sum((1.0 / math.log2(i + 2)) if item in relevant else 0.0
                   for i, item in enumerate(items))

    dcg_val = dcg(unique)
    # Ideal: all relevant standards at top (up to k)
    ideal = list(relevant)[:len(unique)]
    idcg_val = dcg(ideal)
    return dcg_val / idcg_val if idcg_val > 0 else 0.0


def run_eval(kb: KnowledgeBase, questions: list, k: int = 5):
    results = []
    metrics = defaultdict(list)

    for q in questions:
        retrieved = kb.search(q["query"], top_k=k)
        retrieved_codes = [
            r.get("metadata", {}).get("standard_code", "")
            for r in retrieved
        ]
        relevant = q.get("relevant_standards", [])

        recall = recall_at_k(retrieved_codes, relevant, k)
        precision = precision_at_k(retrieved_codes, relevant, k)
        mrr_val = mrr(retrieved_codes, relevant)
        ndcg = ndcg_at_k(retrieved_codes, relevant, k)

        metrics["recall"].append(recall)
        metrics["precision"].append(precision)
        metrics["mrr"].append(mrr_val)
        metrics["ndcg"].append(ndcg)

        results.append({
            "id": q["id"],
            "query": q["query"],
            "recall": round(recall, 3),
            "precision": round(precision, 3),
            "mrr": round(mrr_val, 3),
            "ndcg": round(ndcg, 3),
            "retrieved": retrieved_codes[:k],
            "relevant": relevant,
        })

    # Aggregate
    avg = {key: round(sum(vals) / len(vals), 3) for key, vals in metrics.items()}
    return results, avg


def print_report(results: list, avg: dict):
    print("=" * 70)
    print("  园规通 检索评测报告")
    print("=" * 70)
    print(f"  评测问题数: {len(results)}")
    print(f"  Recall@5  (查全率): {avg['recall']:.1%}")
    print(f"  Precision@5 (查准率): {avg['precision']:.1%}")
    print(f"  MRR      (首命中): {avg['mrr']:.3f}")
    print(f"  NDCG@5   (排序质量): {avg['ndcg']:.3f}")
    print("-" * 70)

    # Per-question detail
    perfect = [r for r in results if r["recall"] >= 0.5]
    zero = [r for r in results if r["recall"] == 0]
    print(f"  有效命中(Recall≥0.5): {len(perfect)}/{len(results)}")
    print(f"  完全未命中(Recall=0): {len(zero)}/{len(results)}")

    if zero:
        print("-" * 70)
        print("  未命中问题：")
        for r in zero:
            print(f"    [{r['id']}] {r['query']}")
            print(f"        预期标准: {r['relevant']}")
            print(f"        实际检索: {r['retrieved']}")

    print("=" * 70)


if __name__ == "__main__":
    questions = load_eval_questions()
    kb = KnowledgeBase()
    results, avg = run_eval(kb, questions, k=5)
    print_report(results, avg)

    # Save detailed results
    with open("data/eval_results.json", "w", encoding="utf-8") as f:
        json.dump({"summary": avg, "details": results}, f, ensure_ascii=False, indent=2)
    print("\n详细结果已保存到 data/eval_results.json")
