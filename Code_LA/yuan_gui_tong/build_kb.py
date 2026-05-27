"""一键构建知识库脚本"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag.knowledge_base import KnowledgeBase

print("=" * 60)
print("  园规通 — 知识库构建")
print("=" * 60)

kb = KnowledgeBase()
kb.build(pdf_dir="data/standards")

print()
print("=" * 60)
stats = kb.get_stats()
print(f"  构建完成!")
print(f"  总条款数: {stats['total_clauses']}")
print(f"  强制性条文: {stats['mandatory_count']}")
print(f"  规范分布:")
for code, count in sorted(stats['standards'].items()):
    print(f"    {code}: {count} 条")
print("=" * 60)

# 测试检索
print("\n测试检索...")
results = kb.search("居住区绿地率要求", top_k=3)
for i, r in enumerate(results, 1):
    print(f"\n  [{i}] 相似度: {r.get('similarity', 0):.3f}")
    print(f"      规范: {r.get('metadata', {}).get('standard_name', '?')}")
    print(f"      条款: {r.get('metadata', {}).get('clause_number', '?')}")
    content_preview = r.get('content', '')[:100].replace('\n', ' ')
    print(f"      内容: {content_preview}...")