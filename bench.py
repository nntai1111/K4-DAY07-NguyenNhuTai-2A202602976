from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Cấu hình UTF-8 cho Windows Terminal
sys.stdout.reconfigure(encoding="utf-8")

from src.agent import KnowledgeBaseAgent
from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker
from src.embeddings import _mock_embed
from src.models import Document
from src.store import EmbeddingStore


class HeadingChunker:
    """
    Chia nhỏ văn bản quy định theo tiêu đề Markdown (#, ##, ###).

    Nếu một section dài quá max_chunk_size, section đó được hạ xuống cắt tiếp
    bằng RecursiveChunker và gắn lại tiêu đề section vào từng mảnh con.
    """

    def __init__(self, max_chunk_size: int = 500) -> None:
        self.max_chunk_size = max_chunk_size
        self.fallback_chunker = RecursiveChunker(chunk_size=max_chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        lines = text.split("\n")
        sections: list[tuple[str, list[str]]] = []
        current_heading = ""
        current_lines: list[str] = []

        for line in lines:
            if line.startswith("#"):
                if current_lines or current_heading:
                    sections.append((current_heading, current_lines))
                current_heading = line.strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines or current_heading:
            sections.append((current_heading, current_lines))

        final_chunks: list[str] = []
        for heading, sec_lines in sections:
            sec_text = "\n".join(sec_lines).strip()
            if not sec_text:
                continue

            if len(sec_text) <= self.max_chunk_size:
                final_chunks.append(sec_text)
            else:
                # Nếu section quá dài, hạ xuống RecursiveChunker và gắn lại heading vào từng mảnh con
                sub_chunks = self.fallback_chunker.chunk(sec_text)
                for sub in sub_chunks:
                    if heading and not sub.startswith("#"):
                        attached_sub = f"{heading}\n{sub}"
                    else:
                        attached_sub = sub
                    final_chunks.append(attached_sub)

        return final_chunks


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Tách phần YAML frontmatter (nếu có) và trả về (metadata_dict, body_text)."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_yaml = parts[1].strip()
            body = parts[2].strip()
            metadata = {}
            for line in raw_yaml.split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    # Tách inline comment nếu có
                    if " #" in v:
                        v = v.split(" #", 1)[0].strip()
                    metadata[k] = v
            return metadata, body
    return {}, content.strip()


def run_benchmark(strategy: str = "heading") -> None:
    data_dir = Path("data/dich-vu-sinh-vien-utc")
    if not data_dir.exists() or not any(data_dir.glob("*.md")):
        data_dir = Path("data/university")

    print(f"=== Đang đọc dữ liệu từ: {data_dir} ===")

    # 1. Chọn chiến lược chia nhỏ (Chunking Strategy)
    if strategy == "fixed":
        chunker = FixedSizeChunker(chunk_size=500, overlap=50)
    elif strategy == "sentence":
        chunker = SentenceChunker(max_sentences_per_chunk=3)
    elif strategy == "recursive":
        chunker = RecursiveChunker(chunk_size=400)
    else:  # heading
        chunker = HeadingChunker(max_chunk_size=500)

    print(f"Chiến lược sử dụng: {strategy.upper()} ({chunker.__class__.__name__})\n")

    # 2. Đọc file, tách frontmatter và chunk phần thân
    stored_documents: list[Document] = []
    file_paths = sorted(list(data_dir.glob("*.md")))

    for path in file_paths:
        raw_text = path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(raw_text)

        # Mặc định audience và doc_id nếu frontmatter thiếu
        doc_id = frontmatter.get("doc_id", path.stem)
        audience = frontmatter.get("audience", "student" if "staff" not in doc_id else "staff")

        # Chunk phần thân
        chunks = chunker.chunk(body)

        for i, chunk_text in enumerate(chunks):
            # 2. Chunk phần thân, mỗi chunk thành một Document:
            # Document(id=f"{path.stem}#{i}", content=chunk, metadata={**frontmatter, "doc_id": path.stem, ...})
            meta = {
                **frontmatter,
                "doc_id": doc_id,
                "audience": audience,
                "source_url": frontmatter.get("source_url", f"https://utc.edu.vn/{doc_id}"),
            }
            stored_documents.append(
                Document(
                    id=f"{path.stem}#{i}",
                    content=chunk_text,
                    metadata=meta,
                )
            )

    print(f"Tổng số tài liệu đọc được: {len(file_paths)}")
    print(f"Tổng số chunks đã tạo: {len(stored_documents)}\n")

    # 3. Nạp vào EmbeddingStore
    store = EmbeddingStore("benchmark_store", embedding_fn=_mock_embed)
    store.add_documents(stored_documents)

    def simple_llm(prompt: str) -> str:
        lines = prompt.split("\n")
        ctx = [l.strip() for l in lines if l.strip() and not l.startswith("Use the") and not l.startswith("Context:") and not l.startswith("Question:")]
        preview = ctx[0][:100] if ctx else "Nội dung quy định"
        return f"Theo tài liệu: {preview}..."

    agent = KnowledgeBaseAgent(store=store, llm_fn=simple_llm)

    # 5 Benchmark Queries
    benchmark_queries = [
        {
            "id": "Q1",
            "query": "Ký túc xá của trường có bao nhiêu phòng và sức chứa bao nhiêu sinh viên?",
            "gold_answer": "214 phòng khép kín, sức chứa 1500 sinh viên.",
            "gold_doc_ids": ["ky-tuc-xa-quan-ly", "ban-quan-ly-ky-tuc-xa"],
            "metadata_filter": None,
        },
        {
            "id": "Q2",
            "query": "Sinh viên muốn hỏi về học bổng và vay vốn tín dụng đào tạo thì liên hệ đơn vị nào?",
            "gold_answer": "Phòng Chăm sóc người học (P101-103 Nhà A9 / P108 A6).",
            "gold_doc_ids": ["cong-tac-sinh-vien", "phong-cong-tac-chinh-tri-va-sinh-vien"],
            "metadata_filter": None,
        },
        {
            "id": "Q3",
            "query": "Đơn vị nào tham mưu cho Hiệu trưởng về công tác chăm sóc sức khỏe cho sinh viên?",
            "gold_answer": "Trạm Y tế (sau sáp nhập thuộc Phòng Chăm sóc người học).",
            "gold_doc_ids": ["tram-y-te", "cong-tac-sinh-vien"],
            "metadata_filter": {"audience": "student"},
        },
        {
            "id": "Q4",
            "query": "Ai quản lý ký túc xá của trường?",
            "gold_answer": "Phòng Chăm sóc người học (sáp nhập Ban QL KTX theo QĐ 2109).",
            "gold_doc_ids": ["cong-tac-sinh-vien", "ky-tuc-xa-quan-ly"],
            "metadata_filter": None,
        },
        {
            "id": "Q5",
            "query": "Tra cứu tài liệu thư viện trực tuyến ở địa chỉ nào và thư viện phục vụ những đối tượng bạn đọc nào?",
            "gold_answer": "Tra cứu tại http://opac.utc.edu.vn. Phục vụ giảng viên, cán bộ, NCS và sinh viên.",
            "gold_doc_ids": ["thu-vien-dich-vu", "trung-tam-thong-tin-thu-vien"],
            "metadata_filter": None,
        },
    ]

    print("================================================================================")
    print("                      CHẠY EVALUATION BENCHMARK (HIT@3)                         ")
    print("================================================================================\n")

    hit_count = 0
    for q_item in benchmark_queries:
        q_id = q_item["id"]
        query_str = q_item["query"]
        meta_filter = q_item["metadata_filter"]
        gold_docs = q_item["gold_doc_ids"]

        # 3. Nạp vào EmbeddingStore, chạy 5 query qua search_with_filter()
        if meta_filter:
            results = store.search_with_filter(query_str, top_k=3, metadata_filter=meta_filter)
        else:
            results = store.search(query_str, top_k=3)

        # Kiểm tra Hit@3
        retrieved_doc_ids = [r.get("metadata", {}).get("doc_id") for r in results]
        is_hit = any(g_id in retrieved_doc_ids for g_id in gold_docs)
        if is_hit:
            hit_count += 1

        print(f"[{q_id}] Câu hỏi: {query_str}")
        print(f"     Lọc Metadata: {meta_filter}")
        print(f"     Tài liệu chuẩn (Gold): {gold_docs}")
        print(f"     Kết quả Hit@3: {'✅ PASSED (Tìm thấy)' if is_hit else '❌ FAILED (Không tìm thấy)'}")
        print("     Top-3 Chunks thu được:")

        # 4. In top-3 kèm score và doc_id để đối chiếu với gold answer
        for idx, res in enumerate(results, start=1):
            chunk_doc_id = res.get("metadata", {}).get("doc_id", "N/A")
            score = res.get("score", 0.0)
            content_preview = res.get("content", "").replace("\n", " ")[:90]
            print(f"       Top {idx}: [Score: {score:.4f} | doc_id: {chunk_doc_id} | id: {res.get('id')}]")
            print(f"              Content: {content_preview}...")

        agent_answer = agent.answer(query_str, top_k=3)
        print(f"     Trả lời của Agent: {agent_answer[:120]}...\n")
        print("-" * 80)

    print(f"TỔNG KẾT HIT@3 SCORE: {hit_count} / {len(benchmark_queries)} ({(hit_count / len(benchmark_queries)) * 100:.1f}%)\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy công cụ đo Benchmark RAG")
    parser.add_argument(
        "--strategy",
        type=str,
        default="heading",
        choices=["fixed", "sentence", "recursive", "heading"],
        help="Chiến lược chia nhỏ văn bản (fixed, sentence, recursive, heading)",
    )
    args = parser.parse_args()
    run_benchmark(strategy=args.strategy)
