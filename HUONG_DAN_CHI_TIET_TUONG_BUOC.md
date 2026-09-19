# HƯỚNG DẪN CHI TIẾT TỪNG BƯỚC THỰC HIỆN LAB 7 (K4-L3A)
## Nền Tảng Dữ Liệu: Embedding & Vector Store (Truy Xuất Quy Định Đại Học)

---

## BƯỚC 1: THIẾT LẬP MÔI TRƯỜNG & KIỂM TRA BAN ĐẦU

### 1.1 Khởi tạo môi trường ảo Python 3.11
Mở terminal tại thư mục gốc của dự án (`d:\vinuni AI\lab7\K4-L3A-Data-Foundations`) và chạy:

```bash
# Tạo virtual environment với Python 3.11
py -3.11 -m venv .venv

# Kích hoạt môi trường trên Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### 1.2 Kiểm tra bộ test ban đầu
Chạy bộ test để xác nhận các tính năng chưa hoàn thành (sẽ có nhiều test bị `FAILED` hoặc `NotImplementedError`):

```bash
pytest tests/ -v
```

---

## BƯỚC 2: LẬP TRÌNH CỐT LÕI TRONG GÓI `src/` (CÁ NHÂN)

Dưới đây là chi tiết mã nguồn chính xác cho từng TODO cần hoàn thiện.

---

### 2.1 Hoàn thiện `src/chunking.py`

Mở file [`src/chunking.py`](file:///d:/vinuni%20AI/lab7/K4-L3A-Data-Foundations/src/chunking.py) và cập nhật các lớp/hàm sau:

#### 1. Class `SentenceChunker`
```python
class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Tách câu dựa trên ranh giới . ! ? hoặc .\n
        # Regex tìm vị trí kết thúc câu: (?<=[.!?])(?=\s+|\n+|$)
        raw_sentences = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
        sentences = [s.strip() for s in raw_sentences if s.strip()]

        if not sentences:
            return []

        chunks: list[str] = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[i : i + self.max_sentences_per_chunk]
            chunk_str = " ".join(group)
            chunks.append(chunk_str)

        return chunks
```

#### 2. Class `RecursiveChunker` & Phương thức `_split`
```python
class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if not current_text:
            return []
        if len(current_text) <= self.chunk_size:
            return [current_text]
        if not remaining_separators:
            # Fallback nếu hết dấu phân cách: cắt theo chunk_size
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        sep = remaining_separators[0]
        next_seps = remaining_separators[1:]

        if sep == "":
            return [current_text[i : i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]

        splits = current_text.split(sep)
        final_chunks: list[str] = []
        accumulated = ""

        for part in splits:
            item = part if not accumulated else sep + part
            if len(accumulated) + len(item) <= self.chunk_size:
                accumulated += item
            else:
                if accumulated:
                    final_chunks.append(accumulated)
                    accumulated = ""
                
                # Nếu phần nhỏ này vẫn lớn hơn chunk_size, gọi đệ quy với separator tiếp theo
                if len(part) > self.chunk_size:
                    sub_chunks = self._split(part, next_seps)
                    final_chunks.extend(sub_chunks)
                else:
                    accumulated = part

        if accumulated:
            final_chunks.append(accumulated)

        return final_chunks
```

#### 3. Hàm `compute_similarity`
```python
def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot_val = sum(x * y for x, y in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(x * x for x in vec_a))
    mag_b = math.sqrt(sum(y * y for y in vec_b))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot_val / (mag_a * mag_b)
```

#### 4. Class `ChunkingStrategyComparator`
```python
class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed = FixedSizeChunker(chunk_size=chunk_size, overlap=20).chunk(text)
        sentences = SentenceChunker(max_sentences_per_chunk=3).chunk(text)
        recursive = RecursiveChunker(chunk_size=chunk_size).chunk(text)

        def get_stats(chunks: list[str]) -> dict:
            cnt = len(chunks)
            avg_len = sum(len(c) for c in chunks) / cnt if cnt > 0 else 0.0
            return {"count": cnt, "avg_length": avg_len, "chunks": chunks}

        return {
            "fixed_size": get_stats(fixed),
            "by_sentences": get_stats(sentences),
            "recursive": get_stats(recursive),
        }
```

---

### 2.2 Hoàn thiện `src/store.py`

Mở file [`src/store.py`](file:///d:/vinuni%20AI/lab7/K4-L3A-Data-Foundations/src/store.py) và cập nhật các phương thức sau:

```python
from __future__ import annotations
from typing import Any, Callable
from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document

class EmbeddingStore:
    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

    def _make_record(self, doc: Document) -> dict[str, Any]:
        embedding = self._embedding_fn(doc.content)
        meta = dict(doc.metadata) if doc.metadata else {}
        meta["doc_id"] = doc.id
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": meta,
            "embedding": embedding,
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if not records:
            return []
        
        query_vec = self._embedding_fn(query)
        scored_records = []
        for r in records:
            score = _dot(query_vec, r["embedding"])
            scored_records.append({
                "id": r["id"],
                "content": r["content"],
                "metadata": r["metadata"],
                "score": float(score),
            })
        
        # Sắp xếp giảm dần theo điểm tương đồng score
        scored_records.sort(key=lambda x: x["score"], reverse=True)
        return scored_records[:top_k]

    def add_documents(self, docs: list[Document]) -> None:
        for doc in docs:
            rec = self._make_record(doc)
            self._store.append(rec)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        if not metadata_filter:
            return self.search(query, top_k=top_k)

        # Lọc các record thỏa mãn điều kiện metadata_filter
        filtered_records = []
        for r in self._store:
            meta = r.get("metadata", {})
            match = True
            for k, v in metadata_filter.items():
                if meta.get(k) != v:
                    match = False
                    break
            if match:
                filtered_records.append(r)

        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        initial_count = len(self._store)
        self._store = [
            r for r in self._store
            if r.get("id") != doc_id and r.get("metadata", {}).get("doc_id") != doc_id
        ]
        return len(self._store) < initial_count
```

---

### 2.3 Hoàn thiện `src/agent.py`

Mở file [`src/agent.py`](file:///d:/vinuni%20AI/lab7/K4-L3A-Data-Foundations/src/agent.py) và cập nhật:

```python
from typing import Callable
from .store import EmbeddingStore

class KnowledgeBaseAgent:
    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        context_blocks = [r["content"] for r in results]
        context_text = "\n---\n".join(context_blocks)

        prompt = (
            f"Use the following context to answer the question.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Question: {question}\nAnswer:"
        )

        return self.llm_fn(prompt)
```

---

## BƯỚC 3: CHẠY & XÁC MINH TEST SUITE (`pytest`)

Chạy lệnh kiểm thử để đảm bảo tất cả các hàm và phương thức vừa viết đạt 100%:

```bash
pytest tests/ -v
```

**Kỳ vọng:** Output hiển thị **`42 passed`** mà không có lỗi nào.

---

## BƯỚC 4: THỰC HIỆN BÀI TẬP CÁ NHÂN & ĐIỀN `report/REPORT_CANHAN.md`

Mở file [`report/REPORT_CANHAN.md`](file:///d:/vinuni%20AI/lab7/K4-L3A-Data-Foundations/report/REPORT_CANHAN.md) và điền các mục sau:

### 4.1 Điền Mục 1 — Khởi động (Warm-up)

#### Bài tập 1.1 (Cosine Similarity):
- **Độ tương tự cosine cao nghĩa là gì?**: Hai đoạn văn bản có các hướng vector biểu diễn ngữ cảnh rất gần nhau trong không gian vector (cùng hướng), nghĩa là chúng có ngữ nghĩa tương đồng nhau cao bất kể độ dài ngắn của câu.
- **Ví dụ có độ tương tự CAO**:
  - *Câu A*: "Sinh viên được quyền đăng ký tối đa 24 tín chỉ mỗi học kỳ."
  - *Câu B*: "Hạn mức đăng ký học phần tối đa đối với sinh viên là 24 tín chỉ/kỳ."
  - *Tại sao tương đồng*: Cùng truyền tải một quy định học vụ về số tín chỉ tối đa.
- **Ví dụ có độ tương tự THẤP**:
  - *Câu A*: "Sinh viên được quyền đăng ký tối đa 24 tín chỉ mỗi học kỳ."
  - *Câu B*: "Thư viện mở cửa phục vụ từ 8 giờ sáng đến 10 giờ đêm."
  - *Tại sao khác*: Một câu nói về quy định học phần, một câu nói về giờ mở cửa thư viện.
- **Tại sao Cosine Similarity được ưu tiên hơn khoảng cách Euclid cho text embeddings?**: Khoảng cách Euclid bị ảnh hưởng bởi độ dài (magnitude) của vector (câu dài chứa nhiều từ sẽ có vector dài hơn). Cosine similarity chỉ đo góc giữa 2 vector, bỏ qua ảnh hưởng của độ dài văn bản, giúp so sánh chính xác ngữ nghĩa giữa văn bản ngắn và dài.

#### Bài tập 1.2 (Bài toán tính toán Chunking):
- **Phép tính số lượng chunk**:
  - Độ dài tài liệu $L = 10,000$, `chunk_size` $C = 500$, `overlap` $O = 50$.
  - Bước dịch chuyển (step) $= C - O = 500 - 50 = 450$.
  - Số lượng chunk $= \lceil \frac{L - O}{C - O} \rceil = \lceil \frac{10000 - 50}{450} \rceil = \lceil \frac{9950}{450} \rceil = \lceil 22.11 \rceil = 23$ chunks.
  - *Đáp án*: **23 chunks**.
- **Khi overlap tăng lên 100**:
  - Bước dịch chuyển $= 500 - 100 = 400$.
  - Số lượng chunk $= \lceil \frac{10000 - 100}{400} \rceil = \lceil \frac{9900}{400} \rceil = \lceil 24.75 \rceil = 25$ chunks.
  - *Giải thích*: Khi tăng overlap, số lượng chunk tăng lên (từ 23 lên 25). Ta muốn độ chồng chéo nhiều hơn để tránh việc thông tin quan trọng bị ngắt đôi ở ranh giới giữa 2 chunk liên tiếp, giúp giữ lại ngữ cảnh liên tục cho RAG.

---

### 4.2 Điền Mục 2 & 3 — Hướng tiếp cận & Kết quả test
- Điền mô tả ngắn gọn về cách bạn viết `SentenceChunker`, `RecursiveChunker`, `EmbeddingStore`, `KnowledgeBaseAgent`.
- Copy & dán kết quả `pytest tests/ -v` (báo 42 passed) vào khung code block.

---

### 4.3 Điền Mục 4 — Dự đoán độ tương tự (5 cặp câu)

Tạo một file script nhỏ trong thư mục `scratch/test_sim.py` để tính điểm thực tế cho 5 cặp câu:

```python
from src.chunking import compute_similarity
from src.embeddings import _mock_embed

pairs = [
    ("Sinh viên đăng ký học phần qua hệ thống trực tuyến.", "Học viên đăng ký môn học trên portal trường."),
    ("Sinh viên phải hoàn thành học phí trước tuần 4.", "Sinh viên chưa nộp học phí sẽ bị khóa tài khoản."),
    ("Ký túc xá đóng cửa lúc 23:00 hàng ngày.", "Thư viện cung cấp không gian tự học 24/7."),
    ("Quy trình xin phúc khảo bài thi kết thúc học phần.", "Đơn phúc khảo điểm được gửi về phòng Đào tạo."),
    ("Lập trình Python và Xử lý Ngôn ngữ Tự nhiên.", "Món phở truyền thống Việt Nam rất nổi tiếng.")
]

for idx, (a, b) in enumerate(pairs, 1):
    va = _mock_embed(a)
    vb = _mock_embed(b)
    sim = compute_similarity(va, vb)
    print(f"Pair {idx}: {sim:.4f}")
```

Chạy script trên và ghi kết quả vào bảng trong `REPORT_CANHAN.md`.

---

## BƯỚC 5: THỰC HIỆN NHIỆM VỤ NHÓM (K4-L3A) & ĐIỀN `report/REPORT_NHOM.md`

---

### 5.1 Thu thập tài liệu quy định đại học vào `data/university/`

Nhóm thu thập thêm 3-5 tài liệu `.md` thuộc chủ đề quy định/dịch vụ đại học (ví dụ: `tuition-policy.md`, `scholarship-rules.md`, `dormitory-regulations.md`, `re-examination-process.md`).

Ví dụ cấu trúc metadata được nhúng ở đầu file hoặc lưu trong code ingest:
- `source_url`: `"https://university.edu.vn/rules/tuition"`
- `retrieved_at`: `"2026-09-19"`
- `document_version`: `"v2025.1"`
- `audience`: `"student"` (hoặc `"faculty"`, `"staff"`)
- `department`: `"academic_affairs"` (Phòng Đào Tạo)

---

### 5.2 Xây dựng 5 Câu Hỏi Đánh Giá (Benchmark Queries) & Gold Answers

Thống nhất 5 câu hỏi của nhóm (đặc biệt **có ít nhất 1 câu yêu cầu lọc `audience="student"`**):

| # | Câu hỏi (Query) | Lọc Metadata (Metadata Filter) | Câu trả lời chuẩn (Gold Answer) | Document / Chunk chứa thông tin |
|---|----------------|--------------------------------|-------------------------------|----------------------------------|
| 1 | Thời gian đăng ký học phần đợt 1 diễn ra khi nào? | N/A | Đợt 1 diễn ra từ tuần thứ 2 đến tuần thứ 4 của kỳ học. | `course-registration.md` |
| 2 | Sinh viên cần lưu ý gì về quy định rút học phần? | `{"audience": "student"}` | Sinh viên chỉ được rút học phần trước tuần thứ 6 và không được hoàn lại 100% học phí. | `course-registration.md` |
| 3 | Quy định gia hạn mượn sách thư viện như thế nào? | N/A | Sách được gia hạn tối đa 2 lần, mỗi lần 7 ngày nếu không có người đặt trước. | `library-services.md` |
| 4 | Điều kiện để xét nhận học bổng khuyến khích học tập là gì? | `{"audience": "student"}` | Đạt ĐTB từ 3.2 trở lên, không nợ môn và điểm rèn luyện đạt loại Tốt trở lên. | `scholarship-rules.md` |
| 5 | Quy trình nộp đơn phúc khảo bài thi kết thúc học phần? | N/A | Sinh viên nộp đơn trong vòng 7 ngày làm việc kể từ khi công bố điểm tại Phòng Khảo thí. | `re-examination-process.md` |

---

### 5.3 Thử nghiệm chiến lược Custom Section Chunker (K4-L3A)

Ít nhất 1 thành viên viết chiến lược cắt theo Tiêu đề (`#`, `##`) của sổ tay/quy định đại học:

```python
class HeadingSectionChunker:
    """Chia nhỏ tài liệu quy định đại học theo các tiêu đề Markdown (#, ##, ###)."""
    def chunk(self, text: str) -> list[str]:
        lines = text.split("\n")
        chunks = []
        current_chunk = []
        for line in lines:
            if line.startswith("#") and current_chunk:
                chunks.append("\n".join(current_chunk).strip())
                current_chunk = [line]
            else:
                current_chunk.append(line)
        if current_chunk:
            chunks.append("\n".join(current_chunk).strip())
        return [c for c in chunks if c]
```

---

### 5.4 Chạy so sánh giữa các thành viên & Phân tích lỗi (Failure Analysis)

Các thành viên chạy 5 câu hỏi benchmark trên chiến lược của mình (FixedSize vs Sentence vs Recursive vs HeadingSection) và tổng hợp kết quả vào `REPORT_NHOM.md`.

Chỉ ra 1 case thất bại (Failure Case):
- *Ví dụ*: Khi dùng `FixedSizeChunker(chunk_size=100)`, điều kiện gia hạn sách thư viện bị ngắt đôi sang 2 chunk khác nhau $\rightarrow$ Agent không tổng hợp đủ câu trả lời.
- *Giải pháp*: Chuyển sang `HeadingSectionChunker` hoặc `RecursiveChunker` giữ trọn vẹn mục quy định.

---

### 5.5 Điền hoàn tất `report/REPORT_NHOM.md`
Điền toàn bộ các mục:
1. Lựa chọn tài liệu & Danh sách Data Inventory.
2. Cấu trúc Metadata Schema & Lý do thiết kế.
3. Bảng so sánh chiến lược giữa các thành viên.
4. Bảng 5 Benchmark queries + Gold answers + Kết quả truy xuất top-3.
5. Bài học rút ra & phần tự đánh giá.

---

## BƯỚC 6: KIỂM TRA ĐIỀU KIỆN NỘP BÀI (SUBMISSION CHECKLIST)

Chạy các lệnh kiểm tra trước khi hoàn tất:

```bash
# 1. Kiểm tra bộ test
pytest tests/ -v

# 2. Kiểm tra các file báo cáo đã được điền thông tin đầy đủ
python -c "
import os
for path in ['report/REPORT_CANHAN.md', 'report/REPORT_NHOM.md']:
    assert os.path.exists(path), f'Missing {path}'
    print(f'Checked {path}: OK')
"
```

Chúc mừng! Bạn đã hoàn thành toàn bộ yêu cầu dự án Lab 7 (K4-L3A).
