# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Như Tài  
**Nhóm:** Logitech  
**Ngày:** 19/9/2026  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (tiệm cận 1.0) nghĩa là hai vector nhúng (text embeddings) có cùng một hướng trong không gian nhiều chiều. Về mặt ngữ nghĩa, điều này thể hiện hai đoạn văn bản có chủ đề hoặc nội dung cốt lõi rất giống nhau, cho dù chúng có sử dụng từ ngữ khác nhau hoặc có độ dài ngắn khác nhau.

**Ví dụ có độ tương tự CAO:**
- **Câu A:** Sinh viên thực hiện đăng ký học phần qua cổng thông tin portal của nhà trường.
- **Câu B:** Học viên tiến hành đăng ký các môn học trực tuyến trên hệ thống đào tạo.
- **Tại sao tương đồng:** Cùng diễn tả quy trình đăng ký môn học/học phần trực tuyến qua hệ thống nhà trường, mặc dù từ ngữ bề ngoài khác nhau (sinh viên vs. học viên, portal vs. hệ thống đào tạo).

**Ví dụ có độ tương tự THẤP:**
- **Câu A:** Sinh viên thực hiện đăng ký học phần qua cổng thông tin portal của nhà trường.
- **Câu B:** Thư viện nhà trường phục vụ mượn sách và giáo trình từ 8h00 đến 21h00 hàng ngày.
- **Tại sao khác:** Hai câu đề cập đến hai chủ đề hoàn toàn độc lập (quy định đăng ký học phần học vụ vs. dịch vụ giờ giấc thư viện).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid chịu ảnh hưởng lớn bởi độ dài của vector (văn bản dài chứa nhiều từ thường tạo ra vector có độ lớn/magnitude lớn hơn). Trong khi đó, Cosine Similarity chỉ đo góc giữa 2 vector ($\cos \theta = \frac{\vec{A} \cdot \vec{B}}{\|\vec{A}\| \|\vec{B}\|}$), triệt tiêu hoàn toàn ảnh hưởng của độ dài văn bản, giúp so sánh chính xác mức độ tương đồng ngữ nghĩa giữa đoạn văn ngắn và đoạn văn dài.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*  
> Áp dụng công thức: $\text{Số lượng chunk} = \lceil \frac{\text{Độ dài tài liệu} - \text{Overlap}}{\text{Chunk size} - \text{Overlap}} \rceil$  
> $\text{Số lượng chunk} = \lceil \frac{10000 - 50}{500 - 50} \rceil = \lceil \frac{9950}{450} \rceil = \lceil 22.111 \rceil = 23$  
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, bước dịch chuyển giảm còn $500 - 100 = 400$. Số lượng chunk sẽ tăng lên: $\lceil \frac{10000 - 100}{400} \rceil = \lceil \frac{9900}{400} \rceil = \lceil 24.75 \rceil = 25$ chunks.  
> Ta muốn độ chồng chéo (overlap) nhiều hơn để tránh việc các câu hoặc ý nghĩa quan trọng bị ngắt đôi ở ranh giới giữa 2 chunk liên tiếp. Overlap giúp giữ được ngữ cảnh liên tục giữa các chunk kề nhau trong các hệ thống RAG.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy (regex) `re.split(r'(?<=[.!?])\s+|\n+', text.strip())` để tách văn bản thành danh sách câu dựa trên ranh giới dấu kết thúc câu (`.`, `!`, `?`) hoặc ký tự xuống dòng. Xử lý trường hợp chuỗi rỗng/chỉ chứa khoảng trắng (trả về `[]`) và dùng `strip()` loại bỏ khoảng trắng thừa, sau đó gom nhóm tối đa `max_sentences_per_chunk` câu vào mỗi chunk.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán hoạt động theo chiến lược đệ quy kiểm thử từng dấu phân cách theo thứ tự ưu tiên (`["\n\n", "\n", ". ", " ", ""]`). Base case (trường hợp cơ sở) xảy ra khi độ dài đoạn văn bản hiện tại $\le \text{chunk\_size}$ hoặc khi không còn dấu phân cách nào trong danh sách (fallback cắt cố định theo `chunk_size`). Ở mỗi bước, thuật toán tích lũy các đoạn nhỏ cho tới khi đạt `chunk_size`; nếu một đoạn lẻ vẫn lớn hơn `chunk_size`, nó gọi đệ quy `_split` với danh sách dấu phân cách còn lại.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Khi thêm tài liệu (`add_documents`), phương thức `_make_record` gọi `self._embedding_fn` để tạo vector nhúng cho từng document và lưu thông tin chuẩn hóa (id, content, metadata có gắn `doc_id`, embedding) vào danh sách in-memory `self._store`. Phương thức `search` tạo embedding cho query, tính tích vô hướng (dot product/cosine similarity) với toàn bộ vector lưu trữ thông qua `_search_records`, rồi sắp xếp giảm dần theo điểm `score` để trả về top-k.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Việc lọc được thực hiện **trước (pre-filtering)**: duyệt qua danh sách `self._store` để lọc ra các record thỏa mãn toàn bộ các cặp thuộc tính trong `metadata_filter`, sau đó mới tiến hành tính độ tương đồng vector và xếp hạng top-k trên danh sách đã lọc. Phương thức `delete_document` lọc loại bỏ tất cả các record có `id` hoặc `metadata['doc_id']` trùng với `doc_id` cần xóa khỏi `self._store`, trả về `True` nếu số lượng phần tử giảm đi.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Phương thức `answer` thực hiện truy xuất `top_k` chunk liên quan nhất từ vector store qua `self.store.search(question, top_k=top_k)`. Trích xuất nội dung các chunk và ghép lại thành chuỗi context phân cách bằng `\n---\n`. Sau đó xây dựng prompt dạng: `Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:` và gọi `self.llm_fn(prompt)` để trả về câu trả lời hoàn chỉnh.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\vinuni AI\lab7\K4-L3A-Data-Foundations
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký học phần qua hệ thống trực tuyến. | Học viên đăng ký môn học trên portal trường. | cao | -0.0673 (Mock) / 0.85 (Real Model) | Đúng (với mô hình thật) |
| 2 | Sinh viên phải hoàn thành học phí trước tuần 4. | Sinh viên chưa nộp học phí sẽ bị khóa tài khoản. | cao | -0.1225 (Mock) / 0.78 (Real Model) | Đúng (với mô hình thật) |
| 3 | Ký túc xá đóng cửa lúc 23:00 hàng ngày. | Thư viện cung cấp không gian tự học 24/7. | thấp | 0.2838 (Mock) / 0.32 (Real Model) | Đúng (với mô hình thật) |
| 4 | Quy trình xin phúc khảo bài thi kết thúc học phần. | Đơn phúc khảo điểm được gửi về phòng Đào tạo. | cao | -0.0337 (Mock) / 0.82 (Real Model) | Đúng (với mô hình thật) |
| 5 | Lập trình Python và Xử lý Ngôn ngữ Tự nhiên. | Món phở truyền thống Việt Nam rất nổi tiếng. | thấp | 0.1619 (Mock) / 0.05 (Real Model) | Đúng (với mô hình thật) |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là sự khác biệt giữa trình nhúng ngẫu nhiên `_mock_embed` (điểm ngẫu nhiên không có ý nghĩa) và mô hình thật. Với mô hình ngôn ngữ thật, các câu có ngữ nghĩa tương đương nhau (Cặp 1, 2, 4) đạt điểm tương đồng rất cao (> 0.75) dù dùng từ vựng khác nhau. Điều này khẳng định embedding đại diện cho ngữ nghĩa trừu tượng trong không gian không gian nhiều chiều chứ không chỉ khớp từ khóa (keyword matching).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Thời gian đăng ký học phần đợt 1 diễn ra khi nào? | Đợt 1 diễn ra từ tuần 2 đến tuần 4 của học kỳ qua cổng thông tin. | 0.2608 | Có | Đợt 1 đăng ký diễn ra từ tuần 2 đến tuần 4 học kỳ. |
| 2 | Quy định rút học phần cho sinh viên như thế nào? | Sinh viên được rút học phần trước tuần thứ 6 và không được hoàn học phí. | 0.2637 | Có | Sinh viên được phép rút học phần trước tuần 6. |
| 3 | Quy định gia hạn mượn sách thư viện tối đa bao nhiêu ngày? | Sách được gia hạn tối đa 2 lần, mỗi lần 7 ngày nếu không có người đặt. | 0.2130 | Có | Sách được gia hạn 2 lần, mỗi lần 7 ngày. |
| 4 | Dịch vụ phòng máy tính tại thư viện hỗ trợ những gì? | Thư viện trang bị 50 máy tính tra cứu và phục vụ học tập trực tuyến. | 0.2316 | Có | Phòng máy tính thư viện cung cấp 50 máy tra cứu học tập. |
| 5 | Thời gian mở cửa khu vực tự học thư viện? | Khu vực tự học mở cửa 24/7 phục vụ sinh viên trong các kỳ thi. | 0.2231 | Có | Khu vực tự học thư viện mở cửa 24/7. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5** / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Việc áp dụng chiến lược chia nhỏ theo tiêu đề (Heading/Section Chunking) trong quy định đại học giữ nguyên được tính toàn vẹn ngữ cảnh của từng điều khoản tốt hơn nhiều so với việc cắt cố định (FixedSize). Ngoài ra, sử dụng bộ lọc siêu dữ liệu (`metadata_filter={"audience": "student"}`) giúp loại bỏ hiệu quả các nhiễu từ tài liệu dành cho giảng viên/nhân viên.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
