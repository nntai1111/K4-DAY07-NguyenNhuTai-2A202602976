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

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

*`chunk_size=400` (cùng cỡ với benchmark), trên phần nội dung đã bỏ frontmatter; FixedSize dùng overlap = 40, SentenceChunker gom 3 câu/chunk.*

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `ky-tuc-xa-quan-ly` (2231 ký tự) | FixedSizeChunker (`fixed_size`) | 7 | 353 | Không — cắt giữa từ ("…khai th" / "uan ; tổ chức…") |
| | SentenceChunker (`by_sentences`) | 4 | 556 | Có theo câu, nhưng chunk dài gấp đôi mục tiêu và dính tiêu đề "CHỨC NĂNG NHIỆM VỤ" vào câu |
| | RecursiveChunker (`recursive`) | 9 | 246 | Tốt — mỗi chunk trọn một đoạn/câu |
| `cong-tac-sinh-vien` (2733 ký tự) | FixedSizeChunker (`fixed_size`) | 8 | 377 | Không — cắt giữa cụm ("tổ chức, học tập ng…") |
| | SentenceChunker (`by_sentences`) | 4 | 680 | Một phần — gộp nhiều mục a), b), c) vào một chunk rất dài |
| | RecursiveChunker (`recursive`) | 10 | 272 | Tốt — tách theo từng mục nhiệm vụ a) … g) |
| `thu-vien-dich-vu` (3490 ký tự) | FixedSizeChunker (`fixed_size`) | 10 | 385 | Không — cắt giữa câu ("trực thuộc Ba" / "n Giám hiệu") |
| | SentenceChunker (`by_sentences`) | 6 | 579 | Có theo câu, chunk dài |
| | RecursiveChunker (`recursive`) | 13 | 267 | Tốt — ranh giới theo đoạn |

> Nhận xét: dữ liệu viết theo đoạn và mục liệt kê a), b), c)… nên RecursiveChunker giữ ranh giới tự nhiên tốt nhất; FixedSize luôn cắt giữa từ; SentenceChunker bị lệ thuộc dấu câu (dòng tiêu đề không có dấu chấm nên dính vào câu sau) và sinh chunk dài.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Hoàng Quốc Việt**
- **Loại chiến lược:** FixedSize (`FixedSizeChunker`, có overlap)
- **Mô tả & lý do chọn cho chủ đề này:** `FixedSizeChunker(chunk_size=400, overlap=50)` cắt đều 400 ký tự, hai chunk liền kề chia sẻ 50 ký tự → 90 chunk, dài TB 381 ký tự. Làm baseline đơn giản nhất; overlap giúp một ý nằm ở ranh giới vẫn có cơ hội thứ hai lọt top-k, đổi lại chunk hay bắt đầu/kết thúc giữa từ.
- **Code snippet (nếu custom):** không (dùng chunker có sẵn)

**Thành viên 2 — Lò Văn Long**
- **Loại chiến lược:** Recursive (`RecursiveChunker`)
- **Mô tả & lý do chọn:** `RecursiveChunker(chunk_size=400)` tách theo `"\n\n" → "\n" → ". " → " "` rồi gom mảnh nhỏ liền kề tới sát 400 ký tự → 105 chunk, dài TB 287 ký tự. Các trang phòng ban viết theo đoạn và mục liệt kê a), b), c)…, nên cắt theo ranh giới đoạn/dòng giữ trọn từng nhiệm vụ trong một chunk, không cắt giữa câu.
- **Code snippet (nếu custom):** không (dùng chunker trong `src/chunking.py`)

**Thành viên 3 — Nguyễn Như Tài**
- **Loại chiến lược:** custom — chunk theo heading/section (`HeadingChunker(chunk_size=500)`) → 113 chunk, dài TB 275 ký tự
- **Mô tả & lý do chọn:** Mỗi trang phòng ban chia sẵn thành các mục do người soạn đặt tiêu đề (THÔNG TIN CHUNG, GIỚI THIỆU, CHỨC NĂNG NHIỆM VỤ…), nên tách tại dòng tiêu đề giữ trọn một đơn vị ngữ nghĩa. Data không có heading Markdown `##`, nên tiêu đề được nhận diện là dòng ngắn viết HOA toàn bộ. Section dài hơn 500 ký tự được hạ xuống `RecursiveChunker` và **gắn lại tiêu đề vào từng mảnh con**, để mảnh thứ hai trở đi không mất ngữ cảnh "đây là mục nói về cái gì".
- *Ghi chú minh bạch:* lần chạy đầu của Tài dùng MockEmbedder (máy chưa cài `sentence-transformers`) và gán nhầm `doc_id` = id chunk, nên kết quả 0/10 không hợp lệ. Số liệu trong báo cáo là lần chạy lại bằng phiên bản `HeadingChunker` dưới đây (nằm trong `bench.py`), cùng embedder thật và cùng pipeline với hai thành viên còn lại.
- **Code snippet (nếu custom):**
```python
class HeadingChunker:
    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size

    @staticmethod
    def _is_heading(line: str) -> bool:
        s = line.strip()
        if s.startswith("#"):
            return True
        return 0 < len(s) <= 80 and any(c.isalpha() for c in s) and s == s.upper()

    def chunk(self, text: str) -> list[str]:
        sections: list[tuple[str, list[str]]] = [("", [])]
        for line in text.split("\n"):
            if self._is_heading(line):
                sections.append((line.strip(), []))
            else:
                sections[-1][1].append(line)

        chunks: list[str] = []
        for heading, lines in sections:
            body = "\n".join(lines).strip()
            if not heading and not body:
                continue
            section = f"{heading}\n{body}".strip()
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue
            # Section quá dài: hạ xuống recursive, gắn lại tiêu đề vào từng mảnh con
            sub = RecursiveChunker(chunk_size=max(50, self.chunk_size - len(heading) - 1))
            chunks.extend(f"{heading}\n{piece}".strip() for piece in sub.chunk(body))
        return chunks
```

### So Sánh Giữa Các Thành Viên

*Cùng 10 tài liệu, cùng 5 câu hỏi, cùng embedder `paraphrase-multilingual-MiniLM-L12-v2`, top-3. Điểm truy xuất = điểm chấm theo nội dung (chuỗi đáp án có trong ngữ cảnh top-3), Q3 tính bản có filter.*

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Hoàng Quốc Việt | FixedSize (400, overlap 50) | 4 (doc_id: 5/5) | Chunk to hơn (TB 381) nên Q3 *không filter* vẫn kéo được chunk đáp án vào hạng 2 (A=1); lấy được nửa "học bổng khuyến khích học tập" của Q2 | Cắt giữa từ/câu (chunk bắt đầu bằng "iệc xét, cấp học bổng…"); mất nửa "vay vốn tín dụng đào tạo" của Q2 |
| Lò Văn Long | Recursive (400) | 4 (doc_id: 5/5) | Ranh giới sạch theo đoạn/mục; chunk top-1 Q1 chứa trọn đáp án; lấy được nửa "vay vốn tín dụng đào tạo" của Q2 | Chunk nhỏ (TB 287), không overlap → đáp án hai phần (Q2, Q5) bị tách, chỉ một phần lọt top-3; Q3 không filter = 0 |
| Nguyễn Như Tài | Heading/section (500) | **8** (doc_id: 5/5) | Mỗi chunk mang tiêu đề mục ("CHỨC NĂNG NHIỆM VỤ …") nên embedding "biết" chunk nói về nhiệm vụ của đơn vị → gom đủ hai nửa đáp án Q2 và Q5 | Q3 không filter vẫn 0 (trang staff chiếm top-3); Q4 vẫn thua trang KTX cũ; tiêu đề lặp giống nhau giữa các trang làm các chunk "CHỨC NĂNG NHIỆM VỤ" của nhiều phòng ban gần nhau |

*Lưu ý chấm điểm:* lần chấm đầu, chuỗi `trong và ngoài Trường` của Q5 không bao giờ khớp vì data crawl từ web dùng khoảng trắng không ngắt (`\xa0`) giữa "ngoài" và "Trường". `bench.py` đã được sửa để chuẩn hoá khoảng trắng trước khi so khớp và **chấm lại cả ba chiến lược**; điểm FixedSize và Recursive không đổi (4/10).

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **HeadingChunker thắng rõ (8/10 so với 4/10)**. Các trang phòng ban được người soạn chia sẵn theo mục, và mỗi nhiệm vụ nằm trọn trong một mục; chunk theo mục + gắn lại tiêu đề vào mảnh con giúp mỗi chunk vừa ngắn vừa mang ngữ cảnh "đây là chức năng nhiệm vụ của đơn vị X", nên câu hỏi kiểu "đơn vị nào phụ trách…" khớp đúng chunk nhiệm vụ. FixedSize và Recursive hòa 4/10 nhưng hỏng ở chỗ khác nhau: Recursive cho ranh giới sạch nhưng chunk nhỏ, không overlap nên tách rời đáp án hai phần (Q2, Q5); FixedSize cắt giữa từ nhưng chunk to + overlap nên đôi khi gom được thông tin vắt qua ranh giới (Q3 không filter: A=1). Không chiến lược nào sửa được Q4, vì lỗi nằm ở **dữ liệu** (trang KTX cũ còn trên web), không nằm ở cách cắt.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Ký túc xá có bao nhiêu phòng và sức chứa bao nhiêu sinh viên? | 03 khối nhà, 214 phòng, sức chứa 1500 sinh viên | `ky-tuc-xa-quan-ly` |
| 2 | Hỏi về học bổng và vay vốn tín dụng đào tạo thì liên hệ đơn vị nào? | Phòng Chăm sóc người học (vay vốn tín dụng đào tạo, học bổng tài trợ / ngoài ngân sách); học bổng khuyến khích học tập do Phòng Đào tạo đại học chủ trì | `cong-tac-sinh-vien` + `dao-tao-dai-hoc-hoc-vu` |
| 3 | Đơn vị nào tổ chức thi và đánh giá kết quả học tập? *(chạy với `metadata_filter={"audience": "student"}`)* | Phòng Đào tạo đại học — lập thời khóa biểu, lịch thi cho sinh viên và chủ trì việc đánh giá kết quả học tập của sinh viên theo quy chế | `dao-tao-dai-hoc-hoc-vu` |
| 4 | Ai quản lý ký túc xá của trường? | Phòng Chăm sóc người học, theo QĐ 2109/QĐ-ĐHGTVT sáp nhập Phòng CTCT&SV + Ban Quản lý KTX + Trạm Y tế | `cong-tac-sinh-vien` (bẫy: trang cũ `ky-tuc-xa-quan-ly`, QĐ 390/1981) |
| 5 | Tra cứu tài liệu thư viện trực tuyến ở đâu, phục vụ những đối tượng nào? | http://opac.utc.edu.vn; giảng viên, cán bộ nghiên cứu, nghiên cứu sinh, học viên cao học, sinh viên trong và ngoài Trường | `thu-vien-dich-vu` |

**Chuỗi đặc trưng dùng để chấm ở mức nội dung** (phải xuất hiện trong ngữ cảnh top-3, khớp đúng từng ký tự với data):

| # | Chuỗi kiểm tra | Mục đích của câu hỏi |
|---|---|---|
| 1 | `214 phòng`, `1500 sinh viên` | Câu đối chứng: trích số liệu. Sai câu này là pipeline hỏng, không phải do chiến lược |
| 2 | `vay vốn tín dụng đào tạo`, `học bổng khuyến khích học tập` | Hai đơn vị giữ hai nửa đáp án; "học bổng" xuất hiện ở 3 tài liệu nên chỉ lấy tài liệu đầu tiên thì chỉ được 1 điểm |
| 3 | `đánh giá kết quả học tập của sinh viên` | Câu bắt buộc dùng filter: Phòng Quản lý chất lượng (`audience=staff`) cũng mô tả "tổ chức các kỳ thi nội bộ và đánh giá kết quả học tập của người học" với từ vựng gần như trùng; không lọc thì trang staff chiếm top-3, lọc `audience=student` thì đơn vị phục vụ sinh viên nổi lên |
| 4 | `sáp nhập lại Phòng CTCT&SV` | Hai văn bản chính thức mâu thuẫn trong index; bẫy là trang cũ của Ban QL KTX (QĐ 390, 1981) vẫn còn trên website |
| 5 | `opac.utc.edu.vn`, `trong và ngoài Trường` | Đáp án hai phần trong cùng một tài liệu |

> *Ghi chú:* Q3 ban đầu ("Đơn vị nào tham mưu cho Hiệu trưởng về công tác chăm sóc sức khỏe cho sinh viên?") được thay vì khi chạy với embedder thật, kết quả có và không có filter giống hệt nhau — tức câu hỏi không thực sự cần filter.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Ký túc xá có bao nhiêu phòng, sức chứa? | Cả ba (2/2) | Có — top-1 chứa đủ "214 phòng", "1500 sinh viên" | Câu đối chứng đạt ở mọi chiến lược → pipeline hoạt động đúng |
| 2 | Học bổng và vay vốn liên hệ đơn vị nào? | **Heading (2/2)**; FixedSize 0, Recursive 0 | Có (Heading); một phần (hai chiến lược kia) | Heading lấy chunk nhiệm vụ của cả Phòng Đào tạo (học bổng KKHT) và Phòng CSNH (vay vốn); Recursive chỉ được nửa "vay vốn", FixedSize chỉ được nửa "học bổng" |
| 3 | Đơn vị nào tổ chức thi và đánh giá kết quả học tập? (filter `student`) | Cả ba khi có filter (2/2); không filter: FixedSize 1, Recursive 0, Heading 0 | Có (khi có filter) | Không filter, trang Phòng Quản lý chất lượng (staff) chiếm top-3 |
| 4 | Ai quản lý ký túc xá? | Không chiến lược nào (0/2) | Không | Trang Ban QL KTX cũ (QĐ 390/1981) luôn xếp hạng 1–2; chunk "sáp nhập" (QĐ 2109) không vào top-3 |
| 5 | Tra cứu thư viện trực tuyến ở đâu, phục vụ ai? | **Heading (2/2)**; FixedSize 0, Recursive 0 | Có (Heading); một phần (hai chiến lược kia) | Chunk "CHỨC NĂNG NHIỆM VỤ" của Heading chứa cả danh sách đối tượng bạn đọc lẫn địa chỉ OPAC; hai chiến lược kia chỉ có "opac.utc.edu.vn" |

*Tổng điểm nội dung: HeadingChunker 8/10, FixedSize 4/10, Recursive 4/10 (chấm theo doc_id cả ba đều 5/5).*

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, rõ nhất ở **Q3**: không filter, trang Phòng Quản lý chất lượng (`audience=staff`) — cũng viết "tổ chức các kỳ thi nội bộ và đánh giá kết quả học tập của người học" — chiếm cả top-3 với Recursive và Heading (điểm A=0) và 2/3 slot với FixedSize (A=1); lọc `audience=student` đưa Phòng Đào tạo đại học lên top-1 cho cả ba chiến lược (B=2). Cái giá là **recall**: filter loại hẳn một tài liệu có liên quan thật (Phòng QLCL cũng làm khảo thí), nên chỉ nên lọc khi biết chắc người hỏi là sinh viên. Q3 ban đầu (chăm sóc sức khỏe) cho kết quả A/B giống hệt nhau nên đã được thay.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Chấm theo doc_id thổi phồng kết quả:** cả ba chiến lược đều 5/5 câu có tài liệu gold trong top-3, nhưng chấm theo nội dung chỉ 4/10 (FixedSize, Recursive) và 8/10 (Heading) — đúng tài liệu, sai chunk. Chunk theo mục có gắn tiêu đề thắng vì mỗi chunk mang theo ngữ cảnh của mục.
> 2. **Failure case do dữ liệu (Q4):** trang Ban Quản lý KTX (QĐ 390/1981) vẫn còn trên website dù đơn vị đã sáp nhập vào Phòng Chăm sóc người học (QĐ 2109); từ vựng của trang cũ khớp câu hỏi hơn nên luôn thắng → agent trả lời sai đơn vị. Đề xuất sửa: gắn metadata hiệu lực (`document_version`/ngày ban hành, trạng thái còn hiệu lực) và loại hoặc hạ hạng văn bản đã bị thay thế.
> 3. **Filter là đánh đổi precision/recall (Q3):** lọc `audience=student` biến 0–1 điểm thành 2 điểm, nhưng đồng thời loại một đơn vị có liên quan thật (Phòng QLCL).

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng tài liệu, cùng câu hỏi, cách cắt quyết định *chunk nào* lọt top-3: Heading gấp đôi điểm hai chiến lược kia chỉ nhờ tôn trọng cấu trúc mục mà người soạn đã chia sẵn và gắn tiêu đề vào từng mảnh. FixedSize và Recursive cùng 4/10 nhưng hỏng ở chỗ khác nhau (Recursive tách rời đáp án hai phần; FixedSize cắt giữa từ nhưng nhờ overlap đôi khi gom được thông tin vắt ranh giới). Hai lỗi "hạ tầng" dạy nhóm nhiều nhất: một lần chạy sai môi trường (mock embedder, `doc_id` sai) cho 0/10, và một ký tự khoảng trắng không ngắt (`\xa0`) trong data làm chuỗi kiểm tra Q5 trượt với mọi chiến lược — so sánh chỉ có nghĩa khi cùng pipeline và bộ chấm được kiểm tra lại.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Chọn trang **quy định/dịch vụ** có con số và thủ tục cụ thể thay vì trang giới thiệu phòng ban (nhiều đoạn mở đầu, lịch sử, thành tích giống nhau giữa các trang), và chủ động thu các cặp tài liệu cùng chủ đề nhưng khác `audience` để filter có việc thật. Ghi `document_version`/ngày hiệu lực khi nguồn có nêu và loại trang đã lỗi thời như Ban QL KTX. Thống nhất môi trường (cài embedder thật, dùng chung `bench.py`) ngay từ đầu để kết quả của các thành viên so sánh được.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 7 / 10 |
| Thiết kế chiến lược (Strategy Design) | 13 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 7 / 10 |
| Thuyết trình (Demo) | 4 / 5 |
| **Tổng phần nhóm** | **31 / 40** |
