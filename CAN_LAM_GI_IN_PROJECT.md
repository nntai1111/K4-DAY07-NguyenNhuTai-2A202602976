# TỔNG QUAN YÊU CẦU DỰ ÁN (PROJECT OVERVIEW)
## Lab 7 (Biến thể K4-L3A): Nền Tảng Dữ Liệu, Embedding & Vector Store
### Chủ đề chuyên biệt K4-L3A: Truy Xuất Dịch Vụ & Quy Định Đại Học

---

## 1. Tóm Tắt Mục Tiêu & Cấu Trúc Dự Án

Dự án này là bài thực hành **Lab 7** dành cho lớp **K4-L3A**. Mục tiêu chính là xây dựng hệ thống **RAG (Retrieval-Augmented Generation)** từ nền tảng: chia nhỏ văn bản (chunking), tạo vector nhúng (embedding), lưu trữ & tìm kiếm trong Vector Store, và kết nối với LLM Agent.

Dự án được chia thành **2 Giai Đoạn chính** (Tổng điểm: **100 điểm**):

| Giai Đoạn | Bản Chất | Trọng Tâm | Điểm | File Báo Cáo |
| :--- | :--- | :--- | :---: | :--- |
| **Giai Đoạn 1** | **Cá Nhân** | Lập trình toàn bộ các hàm TODO trong gói `src/`, vượt qua bài test, làm bài tập lý thuyết & dự đoán | **60 điểm** | `report/REPORT_CANHAN.md` |
| **Giai Đoạn 2** | **Nhóm** | Thu thập 5–10 tài liệu quy định đại học (K4-L3A), thiết kế metadata, tạo 5 câu hỏi benchmark, so sánh chiến lược chunking & trình bày demo | **40 điểm** | `report/REPORT_NHOM.md` |

---

## 2. Chi Tiết Nhiệm Vụ Cần Làm

### PHẦN 1: NHIỆM VỤ CÁ NHÂN (GIAI ĐOẠN 1 — 60 ĐIỂM)

Bạn cần hoàn thành **3 công việc chính**:

#### Công việc 1.1: Lập trình toàn bộ các TODO trong gói `src/` (30 điểm)
Cần hoàn thiện 3 file Python chính:
1. **`src/chunking.py`**:
   - `SentenceChunker`: Tách văn bản thành các câu và gom lại thành từng chunk theo số câu tối đa (`max_sentences_per_chunk`).
   - `RecursiveChunker` & `_split`: Cắt văn bản đệ quy theo thứ tự ưu tiên của dấu phân cách (`["\n\n", "\n", ". ", " ", ""]`) sao cho các chunk không vượt quá `chunk_size`.
   - `compute_similarity`: Tính độ tương tự Cosine (Cosine Similarity) giữa 2 vector, có bảo vệ chống chia cho 0.
   - `ChunkingStrategyComparator`: Chạy so sánh cả 3 chiến lược (`fixed_size`, `by_sentences`, `recursive`) trên một văn bản và trả về thống kê (`count`, `avg_length`, `chunks`).

2. **`src/store.py`**:
   - `EmbeddingStore.__init__`: Khởi tạo lưu trữ vector (hỗ trợ ChromaDB nếu có, hoặc fallback về In-Memory list).
   - `_make_record`: Tạo dict lưu trữ chuẩn hóa cho 1 Document/Chunk gồm id, content, metadata, embedding.
   - `_search_records`: Tìm kiếm độ tương đồng vector in-memory và trả về top-k.
   - `add_documents`: Tạo embedding cho danh sách tài liệu và lưu trữ.
   - `search`: Tìm kiếm top-k chunk liên quan nhất cho query.
   - `get_collection_size`: Trả về tổng số chunk đang lưu trữ.
   - `search_with_filter`: Lọc chunk theo `metadata_filter` trước, sau đó mới tính tương đồng vector để lấy top-k.
   - `delete_document`: Xóa tất cả các chunk thuộc về 1 `doc_id`.

3. **`src/agent.py`**:
   - `KnowledgeBaseAgent.__init__`: Khởi tạo agent nhận `store` và `llm_fn`.
   - `KnowledgeBaseAgent.answer`: Truy xuất top-k chunk liên quan từ store $\rightarrow$ Tạo prompt chứa context $\rightarrow$ Gọi `llm_fn` để trả lời câu hỏi.

> **Tiêu chuẩn hoàn thành:** Chạy lệnh `pytest tests/ -v` đạt **42/42 tests Pass**.

---

#### Công việc 1.2: Làm các bài tập lý thuyết & tính toán (5 điểm)
Trả lời các bài tập trong `exercises.md` (Phần 1):
- **Bài tập 1.1 (Cosine Similarity)**: Giải thích ý nghĩa cosine similarity cao/thấp, cho ví dụ cụ thể, giải thích lý do cosine similarity được ưu tiên hơn khoảng cách Euclid cho text embedding.
- **Bài tập 1.2 (Tính số lượng Chunk)**: Phép tính số chunk cho tài liệu 10,000 ký tự (`chunk_size=500, overlap=50`), phân tích sự thay đổi khi `overlap=100`.

---

#### Công việc 1.3: Thực hiện dự đoán & chạy đánh giá cá nhân (15 điểm)
- **Bài tập 3.3 (Dự đoán độ tương tự - 5 điểm)**: Chạy `compute_similarity` trên 5 cặp câu, đưa ra dự đoán trước khi chạy và so sánh với điểm số thực tế.
- **Điền báo cáo cá nhân `report/REPORT_CANHAN.md` (10 điểm)**:
  - Ghi hướng tiếp cận lập trình cho từng hàm/lớp trong `src/`.
  - Dán kết quả chạy `pytest tests/ -v`.
  - Điền bảng dự đoán độ tương tự.
  - Chạy 5 câu hỏi benchmark của nhóm trên code cá nhân và điền bảng kết quả truy xuất (top-1 chunk, score, relevance, câu trả lời agent).

---

### PHẦN 2: NHIỆM VỤ NHÓM (GIAI ĐOẠN 2 — 40 ĐIỂM)

Nhóm làm việc chung để thu thập dữ liệu, thử nghiệm chiến lược và trình bày báo cáo.

#### Các Quy Tắc Bắt Buộc Riêng Cho Lớp K4-L3A (`K4_VARIANT.md`):
1. **Chủ đề dữ liệu**: Phải về **Dịch vụ hoặc Quy định Đại học** (Đăng ký học phần, học phí, học bổng, ký túc xá, thư viện, quy chế học vụ, phúc khảo...).
2. **Số lượng tài liệu**: Thu thập **5 – 10 tài liệu** định dạng `.md` hoặc `.txt` lưu vào thư mục `data/university/`.
3. **Cấu trúc Metadata bắt buộc**:
   - Trường K4-L3A bắt buộc: `audience` (`student` / `faculty` / `staff` / `all`).
   - Ít nhất 1 trường bổ sung: `department`, `category`, `language`...
   - 3 trường quản trị bắt buộc: `source_url`, `retrieved_at` (ngày lấy), `document_version` (phiên bản/ngày hiệu lực).
4. **Yêu cầu đối với 5 Câu Hỏi Đánh Giá (Benchmark Queries)**:
   - Viết đúng **5 câu hỏi** kèm **câu trả lời chuẩn (Gold Answer)** trích xuất trực tiếp từ tài liệu đã thu thập (không tự suy đoán).
   - **BẮT BUỘC**: Ít nhất **1 câu hỏi** phải dùng lọc siêu dữ liệu `metadata_filter={"audience": "student"}` để không bị lẫn thông tin dành cho giảng viên/nhân viên.
5. **Thử nghiệm chiến lược Chunking**:
   - Ít nhất 1 thành viên trong nhóm phải thử chiến lược **chia nhỏ theo Tiêu đề/Mục (Heading/Section Chunking)** của sổ tay/quy định học vụ (ví dụ cắt theo các mục `#`, `##`).
   - Mỗi thành viên thử 1 chiến lược riêng trên cùng bộ 5 câu hỏi benchmark để so sánh hiệu quả.
6. **Phân tích lỗi (Failure Analysis)**:
   - Phân tích ít nhất 1 trường hợp truy xuất thất bại (do chunk quá to/nhỏ, thiếu metadata, query mơ hồ...).

---

## 3. Thang Điểm & Sản Phẩm Cần Nộp (Submission Deliverables)

### Bảng Phân Bổ Điểm Chi Tiết

```
TỔNG ĐIỂM: 100 ĐIỂM
│
├── I. PHẦN CÁ NHÂN (60 điểm) — File: report/REPORT_CANHAN.md & src/
│   ├── 1. Khởi động (Lý thuyết & Tính toán)         : 5 điểm
│   ├── 2. Hướng tiếp cận lập trình (My Approach)    : 10 điểm
│   ├── 3. Hoàn thiện Code (`src/` pass 42 tests)   : 30 điểm
│   ├── 4. Dự đoán độ tương tự (5 cặp câu)           : 5 điểm
│   └── 5. Kết quả truy xuất cá nhân (5 benchmark q): 10 điểm
│
└── II. PHẦN NHÓM (40 điểm) — File: report/REPORT_NHOM.md & data/university/
    ├── 1. Lựa chọn tài liệu & Schema Metadata (K4-L3A): 10 điểm
    ├── 2. Thiết kế & So sánh chiến lược Chunking    : 15 điểm
    ├── 3. Chất lượng truy xuất 5 Benchmark Queries  : 10 điểm
    └── 4. Thuyết trình (Demo) & Bài học rút ra      : 5 điểm
```

### Danh Sách Các File Cần Nộp Trực Tiếp Trong Repository:
1. `src/chunking.py`, `src/store.py`, `src/agent.py` (Đã hoàn thiện code).
2. `data/university/*.md` hoặc `*.txt` (5–10 file quy định đại học kèm metadata).
3. `report/REPORT_CANHAN.md` (Điền đầy đủ thông tin báo cáo cá nhân).
4. `report/REPORT_NHOM.md` (Điền đầy đủ thông tin báo cáo nhóm).

---

## 4. Danh Sách Kiểm Tra Nhanh (Checklist)

- [ ] Môi trường ảo Python 3.11 đã được kích hoạt.
- [ ] Lệnh `pytest tests/ -v` báo `42 passed`.
- [ ] Thư mục `data/university/` chứa 5–10 file quy định đại học.
- [ ] Tất cả tài liệu có metadata `audience`, `source_url`, `retrieved_at`, `document_version`.
- [ ] Đã xây dựng 5 câu hỏi benchmark + gold answers, có ít nhất 1 câu hỏi test `metadata_filter={"audience": "student"}`.
- [ ] Có ít nhất 1 custom chunker chia theo Heading/Section (`#`, `##`).
- [ ] File `report/REPORT_CANHAN.md` được hoàn thành 100%.
- [ ] File `report/REPORT_NHOM.md` được hoàn thành 100%.
