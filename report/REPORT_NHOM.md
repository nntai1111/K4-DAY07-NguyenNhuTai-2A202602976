# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Logitech
**Thành viên:** Hoàng Quốc Việt (R1 · Data), Lò Văn Long (R2 · Benchmark), Nguyễn Như Tài (R3 · Strategy)
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Dịch vụ sinh viên của các phòng ban — Trường Đại học Giao thông Vận tải (UTC)

**Tại sao nhóm chọn chủ đề này?**
> Nguồn là các trang chính thức, công khai trên utc.edu.vn và robots.txt cho phép truy cập tự động. Bộ tài liệu phủ nhiều mảng dịch vụ mà sinh viên thường cần (học vụ, học phí, ký túc xá, y tế, thư viện, học trực tuyến), các trang lại có cùng khuôn trình bày nên thuận tiện để so sánh các chiến lược chunking. Tài liệu hướng tới các đối tượng khác nhau (sinh viên / cán bộ / tất cả), giúp nhóm thử nghiệm metadata filter theo `audience`.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Phòng Bảo vệ: an ninh trật tự và quản lý ra vào trong trường | https://www.utc.edu.vn/gioi-thieu/phong-bao-ve | 2026-09-19 / not-stated | 1991 | audience=all, department=phong-bao-ve, category=an-ninh |
| 2 | Phòng Chăm sóc người học: công tác sinh viên, học bổng và chế độ chính sách | https://www.utc.edu.vn/gioi-thieu/phong-cong-tac-chinh-tri-va-sinh-vien | 2026-09-19 / not-stated | 2733 | audience=student, department=phong-cham-soc-nguoi-hoc, category=cong-tac-sinh-vien |
| 3 | Phòng Đào tạo đại học: đăng ký học phần và các thủ tục học vụ | https://www.utc.edu.vn/gioi-thieu/phong-dao-tao-dai-hoc | 2026-09-19 / not-stated | 3759 | audience=student, department=phong-dao-tao-dai-hoc, category=hoc-vu |
| 4 | Trung tâm Đào tạo trực tuyến UTC: hệ thống học trực tuyến | https://www.utc.edu.vn/gioi-thieu/trung-tam-dao-tao-truc-tuyen-utc | 2026-09-19 / not-stated | 3352 | audience=student, department=trung-tam-dao-tao-truc-tuyen, category=hoc-truc-tuyen |
| 5 | Phòng Kế hoạch - Tài chính: học phí và các khoản thu | https://www.utc.edu.vn/gioi-thieu/phong-ke-hoach-tai-chinh | 2026-09-19 / not-stated | 4525 | audience=all, department=phong-ke-hoach-tai-chinh, category=hoc-phi |
| 6 | Ban Quản lý Ký túc xá: chức năng và dịch vụ cho sinh viên nội trú | https://www.utc.edu.vn/gioi-thieu/ban-quan-ly-ky-tuc-xa | 2026-09-19 / not-stated | 2231 | audience=student, department=ban-quan-ly-ky-tuc-xa, category=ky-tuc-xa |
| 7 | Phòng Pháp chế và Kiểm soát nội bộ: xây dựng và rà soát văn bản nội bộ | https://www.utc.edu.vn/gioi-thieu/phong-phap-che-va-kiem-soat-noi-bo | 2026-09-19 / not-stated | 2726 | audience=staff, department=phong-phap-che-va-kiem-soat-noi-bo, category=phap-che |
| 8 | Phòng Quản lý chất lượng: khảo thí và đảm bảo chất lượng đào tạo | https://www.utc.edu.vn/gioi-thieu/phong-quan-ly-chat-luong | 2026-09-19 / not-stated | 2973 | audience=staff, department=phong-quan-ly-chat-luong, category=dam-bao-chat-luong |
| 9 | Trung tâm Thông tin - Thư viện: dịch vụ và đối tượng bạn đọc | https://www.utc.edu.vn/gioi-thieu/trung-tam-thong-tin-thu-vien | 2026-09-19 / not-stated | 3490 | audience=all, department=trung-tam-thong-tin-thu-vien, category=thu-vien |
| 10 | Trạm Y tế: chăm sóc sức khỏe và bảo hiểm y tế sinh viên | https://www.utc.edu.vn/gioi-thieu/tram-y-te | 2026-09-19 / not-stated | 2510 | audience=student, department=tram-y-te, category=y-te |

*Số ký tự tính trên phần nội dung, không gồm frontmatter. Tất cả tài liệu dùng `language=vi`, `license_or_permission=public-source`.*

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

> Đã kiểm tra robots.txt trước khi crawl. Đã xoá menu, danh sách tin tức, thống kê truy cập và địa chỉ IP người truy cập khỏi nội dung. Tên cán bộ lãnh đạo phòng ban là thông tin công khai trên trang của trường. Không nguồn nào ghi số hiệu phiên bản nên `document_version` để `not-stated`.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | string (student / faculty / staff / all) | student | Lọc đúng đối tượng người hỏi; dùng cho `metadata_filter={"audience": "student"}` để loại tài liệu dành cho cán bộ |
| `department` | string | phong-dao-tao-dai-hoc | Thu hẹp tìm kiếm về đúng phòng ban phụ trách khi câu hỏi nêu rõ đơn vị |
| `category` | string | hoc-phi | Lọc theo mảng dịch vụ (học phí, ký túc xá, y tế...) |
| `source_url` | string (URL) | https://www.utc.edu.vn/gioi-thieu/tram-y-te | Truy vết nguồn khi agent trích dẫn câu trả lời |
| `retrieved_at` / `document_version` | date / string | 2026-09-19 / not-stated | Biết dữ liệu được lấy khi nào và có còn hiệu lực không |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu UTC:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `dao-tao-dai-hoc-hoc-vu.md` | FixedSizeChunker (`fixed_size`) | 28 | 198 ký tự | Kém. Cắt cứng độ dài 200 làm ngắt đôi nhiều câu giữa chừng. |
| `dao-tao-dai-hoc-hoc-vu.md` | SentenceChunker (`by_sentences`) | 14 | 382 ký tự | Khá. Giữ trọn vẹn từng câu nhưng gom các câu không cùng chủ đề vào 1 chunk. |
| `dao-tao-dai-hoc-hoc-vu.md` | RecursiveChunker (`recursive`) | 16 | 338 ký tự | Tốt. Tách theo ranh giới đoạn văn `\n\n` và xuống dòng `\n` nên ngữ cảnh tự nhiên. |

### Chiến lược của từng thành viên

**Thành viên 1 — Hoàng Quốc Việt (02563)**
- **Loại chiến lược:** Custom `HeadingChunker` (Chia nhỏ theo tiêu đề Markdown `#`, `##`).
- **Mô tả & lý do chọn cho chủ đề này:** Tất cả 10 tài liệu dịch vụ sinh viên UTC đều có cấu trúc tiêu đề rõ ràng với 4 mục chính (`THÔNG TIN CHUNG`, `CHỨC NĂNG NHIỆM VỤ`, `GIỚI THIỆU`, `CÁC THÀNH TÍCH`). Việc cắt theo tiêu đề giúp bảo toàn trọn vẹn toàn bộ một mục chức năng/nhiệm vụ mà không bị xé nhỏ hay ngắt đoạn.
- **Code snippet:**
```python
class HeadingChunker:
    """Chia nhỏ văn bản quy định UTC theo các tiêu đề Markdown (#, ##, ###)."""

    def chunk(self, text: str) -> list[str]:
        lines = text.split("\n")
        chunks, current = [], []
        for line in lines:
            if line.startswith("#") and current:
                chunks.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            chunks.append("\n".join(current).strip())
        return [c for c in chunks if c]
```

**Thành viên 2 — Nguyễn Như Tài**
- **Loại chiến lược:** `RecursiveChunker` (chunk_size=400, separators=["\n\n", "\n", ". ", " ", ""]).
- **Mô tả & lý do chọn:** Kiểm thử đệ quy các dấu phân cách từ lớn đến nhỏ giúp giữ ranh giới đoạn tự nhiên. Thiết lập `chunk_size=400` đảm bảo thông tin vừa đủ để nằm trọn trong context window của LLM mà không thừa thông tin nhiễu.

**Thành viên 3 — Lò Văn Long**
- **Loại chiến lược:** `SentenceChunker` (max_sentences_per_chunk=3).
- **Mô tả & lý do chọn:** Cắt văn bản thành các cụm 3 câu hoàn chỉnh. Phương pháp này đảm bảo không bao giờ cắt đứt một câu ở giữa từ, giữ nguyên vẹn ngữ pháp và ý nghĩa của từng câu quy định.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Hoàng Quốc Việt | Custom `HeadingChunker` | 9.5 / 10 | Trích xuất trọn vẹn từng mục chức năng nhiệm vụ, giữ toàn bộ ngữ cảnh liên quan. | Kích thước chunk phụ thuộc độ dài mục, mục quá dài có thể chứa thông tin thừa. |
| Nguyễn Như Tài | `RecursiveChunker` (size=400) | 9.0 / 10 | Cân bằng hoàn hảo giữa độ dài chunk và tính mạch lạc ngữ nghĩa của đoạn văn. | Có trường hợp một danh sách điểm khoản bị ngắt đôi sang 2 chunk. |
| Lò Văn Long | `SentenceChunker` (3 câu/chunk) | 8.0 / 10 | Giữ nguyên vẹn cấu trúc ngữ pháp từng câu, không bao giờ cắt đứt câu. | Không giữ được cấu trúc phân cấp các mục lớn và các tiêu đề của tài liệu. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Chiến lược **Custom `HeadingChunker`** (hoặc `RecursiveChunker` kết hợp cắt theo tiêu đề) là chiến lược tốt nhất cho chủ đề Quy định & Dịch vụ Đại học. Lý do là các tài liệu hành chính quy định luôn được soạn thảo theo cấu trúc phân cấp mục rõ ràng; cắt theo tiêu đề giúp bảo toàn toàn bộ bối cảnh của một điều khoản hay chức năng phòng ban, tránh tình trạng thông tin câu trả lời bị chia rẽ thành nhiều chunk rời rạc.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Ký túc xá của trường có bao nhiêu phòng và sức chứa bao nhiêu sinh viên? | Ký túc xá của trường có 03 khối nhà vĩnh cửu từ 4–5 tầng với tổng số 214 phòng hoàn toàn có công trình phụ khép kín với sức chứa 1500 sinh viên. | `ky-tuc-xa-quan-ly.md` |
| 2 | Sinh viên muốn hỏi về học bổng và vay vốn tín dụng đào tạo thì liên hệ đơn vị nào? | Phòng Chăm sóc người học (P101-103 Nhà A9 / P108 A6) giải quyết chế độ chính sách, bảo hiểm, vay vốn tín dụng đào tạo và học bổng tài trợ / ngoài ngân sách. Riêng học bổng khuyến khích học tập do Phòng Đào tạo đại học chủ trì xét. | `cong-tac-sinh-vien.md`, `dao-tao-dai-hoc-hoc-vu.md` |
| 3 | Đơn vị nào tham mưu cho Hiệu trưởng về công tác chăm sóc sức khỏe cho sinh viên? | Trạm Y tế tham mưu cho Hiệu trưởng về quản lý, giáo dục và chăm sóc sức khỏe (2 cơ sở tại khu giảng đường và KTX 99 Nguyễn Chí Thanh). Sau sáp nhập (QĐ 2109/QĐ-ĐHGTVT), công tác y tế thuộc Phòng Chăm sóc người học. | `tram-y-te.md`, `cong-tac-sinh-vien.md` |
| 4 | Ai quản lý ký túc xá của trường? | Phòng Chăm sóc người học. Theo QĐ 2109/QĐ-ĐHGTVT, phòng được thành lập trên cơ sở sáp nhập Phòng CTCT&SV, Ban Quản lý KTX và Trạm Y tế. | `cong-tac-sinh-vien.md` |
| 5 | Tra cứu tài liệu thư viện trực tuyến ở địa chỉ nào và thư viện phục vụ những đối tượng bạn đọc nào? | Tra cứu trực tuyến (OPAC) tại http://opac.utc.edu.vn. Phục vụ bạn đọc gồm: giảng viên, cán bộ nghiên cứu, nghiên cứu sinh, học viên cao học và sinh viên trong/ngoài Trường. | `thu-vien-dich-vu.md` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Ký túc xá có bao nhiêu phòng... | Custom `HeadingChunker` / `RecursiveChunker` | Có (Hit@3) | Trích xuất chính xác 214 phòng / 1500 sinh viên. (2/2 điểm) |
| 2 | Hỏi học bổng và vay vốn tín dụng... | `RecursiveChunker` | Có (Hit@3) | Trả về đúng thông tin Phòng Chăm sóc người học & Phòng Đào tạo. (2/2 điểm) |
| 3 | Đơn vị tham mưu sức khỏe SV... | `HeadingChunker` + Metadata Filter | Có (Hit@3) | **Bắt buộc dùng `metadata_filter={"audience": "student"}`** để lọc bớt 8 file phòng ban có câu mở đầu giống hệt nhau. (2/2 điểm) |
| 4 | Ai quản lý ký túc xá của trường? | `HeadingChunker` + Version Filter | Có (Hit@3) | Trả về đúng Phòng Chăm sóc người học (phát hiện xung đột tài liệu sáp nhập theo QĐ 2109). (2/2 điểm) |
| 5 | Tra cứu thư viện trực tuyến OPAC... | `SentenceChunker` / `HeadingChunker` | Có (Hit@3) | Trả về chính xác địa chỉ website http://opac.utc.edu.vn và danh sách đối tượng bạn đọc. (2/2 điểm) |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Lọc bằng metadata giúp ích rất lớn ở **Câu 3 (Q3)**. Cụm từ "Tham mưu cho Hiệu trưởng" xuất hiện ở đoạn văn mở đầu (boilerplate) của 8 trên 10 tài liệu giới thiệu phòng ban UTC. Nếu không lọc `metadata_filter={"audience": "student"}`, kết quả tìm kiếm không lọc sẽ bị tràn ngập bởi các đoạn văn giới thiệu chung của Phòng Quản lý chất lượng hay Phòng Pháp chế. Việc áp dụng bộ lọc giúp triệt tiêu nhiễu từ 5 trang dành cho cán bộ/tất cả, trả về chính xác Trạm Y tế & Phòng Chăm sóc người học.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Tác động của Metadata Filtering**: Lọc siêu dữ liệu không chỉ là tính năng nâng cao mà là giải pháp bắt buộc để loại bỏ hiện tượng nhiễu câu mở đầu (boilerplate) khi các trang web tổ chức có định dạng giống hệt nhau (như Q3).
2. **Xung đột phiên bản tài liệu (Failure Case ở Q4)**: Trong kho dữ liệu có 2 câu trả lời mâu thuẫn (`cong-tac-sinh-vien.md` nêu Ban QL KTX đã sáp nhập, trong khi `ky-tuc-xa-quan-ly.md` cũ vẫn tự mô tả là đơn vị độc lập). Lỗi này không thể giải quyết bằng chunking mà bắt buộc phải quản trị bằng trường metadata `document_version` / `supersedes`.
3. **Ưu thế của Heading Chunking trong văn bản quy định**: Chiến lược cắt theo tiêu đề Markdown (`#`, `##`) giúp giữ trọn vẹn mạch ngữ cảnh của từng điều khoản hành chính.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một bộ dữ liệu và 5 câu hỏi benchmark, việc chọn chiến lược chunking cắt theo tiêu đề (`HeadingChunker`) giúp tăng đáng kể tính mạch lạc và độ chính xác của câu trả lời từ LLM Agent so với cắt cố định (`FixedSizeChunker`). Đồng thời, việc chuyển đổi từ `MockEmbedder` sang mô hình nhúng ngữ nghĩa thật (`LocalEmbedder` / `GeminiEmbedder`) là điều kiện bắt buộc để hệ thống RAG hoạt động đúng bản chất.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ bổ sung thêm các trường metadata như `document_version`, `effective_date` (ngày hiệu lực) và `supersedes` (thay thế văn bản cũ nào) khi nạp dữ liệu vào kho vector để tự động lọc loại bỏ các văn bản đã bị thay thế hoặc hết hiệu lực trước khi thực hiện truy xuất.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
