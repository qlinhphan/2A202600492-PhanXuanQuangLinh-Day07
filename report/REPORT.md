# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Đức Tiến - 2A202600393
**Nhóm:** Nhóm 12 - E402 (Vinmec Heart Health)
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> *Viết 1-2 câu:* 
 - Hai vector có cosine similarity cao nghĩa là chúng hướng về cùng một phía trong không gian vector, biểu thị rằng hai đoạn văn bản đó có sự tương đồng lớn về mặt ngữ nghĩa hoặc ngữ cảnh.

**Ví dụ HIGH similarity:**
- Sentence A: "The sun is shining brightly today."
- Sentence B: "It is a very sunny day."
- Tại sao tương đồng: Cả hai câu đều mô tả cùng một trạng thái thời tiết (nắng), sử dụng các từ vựng liên quan chặt chẽ đến cùng một khái niệm.

**Ví dụ LOW similarity:**
- Sentence A: "I love eating chocolate cake."
- Sentence B: "The stock market crashed yesterday."
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau (ẩm thực và tài chính), không có sự liên quan về ngữ nghĩa.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Viết 1-2 câu:* 
- Cosine similarity đo góc giữa hai vector nên không bị ảnh hưởng bởi độ dài của văn bản (magnitude của vector). Điều này rất quan trọng vì một câu ngắn và một đoạn văn dài có thể có cùng nội dung, Euclidean distance sẽ coi chúng là khác biệt do độ dài, trong khi Cosine similarity sẽ thấy chúng tương đồng về hướng ngữ nghĩa.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* num_chunks = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11)
> *Đáp án:* 23 chunks

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu:* 
- Số lượng chunks sẽ tăng lên (lên 25 chunks). Chúng ta muốn overlap nhiều hơn để đảm bảo các ngữ cảnh quan trọng (như câu bị cắt đôi) được bảo toàn ở ít nhất một chunk, giúp LLM có cái nhìn toàn vẹn hơn về thông tin.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Y tế / Tim mạch (Vinmec)

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:* 
- Nhóm chọn domain này vì đây là lĩnh vực quan trọng, yêu cầu độ chính xác cao trong truy xuất thông tin y khoa. Việc hỗ trợ bệnh nhân tra cứu thông tin tim mạch giúp giảm tải cho bác sĩ và cung cấp kiến thức đúng đắn cho cộng đồng.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | 01_benh_mach_vanh.txt | vinmec.com | 5391 | category: tim-mach, topic: bệnh mạch vành, diff: general |
| 2 | 02_tang_huyet_ap.txt | vinmec.com | 5759 | category: tim-mach, topic: tăng huyết áp, diff: general |
| 3 | 03_suy_tim.txt | vinmec.com | 4854 | category: tim-mach, topic: suy tim, diff: advanced |
| 4 | 04_roi_loan_nhip_tim.txt | vinmec.com | 4683 | category: tim-mach, topic: rối loạn nhịp tim, diff: advanced |
| 5 | 05_ho_van_tim.txt | vinmec.com | 5434 | category: tim-mach, topic: hở van tim, diff: general |
| 6 | 06_nhoi_mau_co_tim.txt | vinmec.com | 5109 | category: tim-mach, topic: nhồi máu cơ tim, diff: advanced |
| 7 | 07_xo_vua_dong_mach.txt | vinmec.com | 5420 | category: tim-mach, topic: xơ vữa động mạch, diff: general |
| 8 | 08_dinh_duong_tim_mach.txt | vinmec.com | 5936 | category: tim-mach, topic: dinh dưỡng, diff: general |
| 9 | 09_the_duc_tim_mach.txt | vinmec.com | 6258 | category: tim-mach, topic: tập thể dục, diff: general |
| 10 | 10_tam_soat_tim_mach.txt | vinmec.com | 7003 | category: tim-mach, topic: tầm soát, diff: general |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `lang` | string | "vi", "en" | Giúp lọc chính xác ngôn ngữ mà người dùng đang hỏi, tránh nhiễu từ các ngôn ngữ khác. |
| `category` | string | "architecture", "dev" | Cho phép thu hẹp phạm vi tìm kiếm vào đúng phòng ban hoặc lĩnh vực chuyên môn. |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| 01_benh_mach_vanh.txt | FixedSizeChunker | 10 | ~400 | Trung bình |
| 01_benh_mach_vanh.txt | SentenceChunker | 21 | ~195 | Tốt |
| 01_benh_mach_vanh.txt | RecursiveChunker | 24 | ~171 | Rất tốt |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?*
-   Strategy này sử dụng danh sách các dấu phân cách ưu tiên (như xuống dòng đôi, xuống dòng đơn, dấu chấm, khoảng trắng). Nó cố gắng cắt văn bản ở mức cao nhất (ví dụ đoạn văn). Nếu đoạn đó vẫn vượt quá `chunk_size`, nó sẽ gọi đệ quy để cắt nhỏ hơn bằng dấu phân cách tiếp theo trong danh sách. Điều này đảm bảo các đoạn văn bản được giữ nguyên vẹn nhất có thể về mặt cấu trúc.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?* 
- Tài liệu kỹ thuật thường có cấu trúc rõ ràng với các tiêu đề và đoạn văn. RecursiveChunker giúp giữ các đoạn văn liên quan ở cùng một chunk mà không bị cắt lẻ tẻ như FixedSize, từ đó cải thiện độ chính xác khi trả lời.

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| rag_system_design.md | FixedSizeChunker | 14 | 189.36 | Thấp (cắt ngang câu) |
| rag_system_design.md | **RecursiveChunker** | 66 | 34.92 | Cao (giữ được ý nghĩa từng đoạn nhỏ) |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tiến | Recursive | 8 | Giữ cấu trúc tốt | Cần tinh chỉnh dấu phân cách |
| Thành | Sentence | 7 | Tách câu tự nhiên | Bỏ sót context giữa các đoạn |
| Chinh | FixedSize | 5 | Đơn giản, nhanh | Hay bị cắt ngang thông tin |
| Linh (Tôi)| Recursive | 8 | Hiệu quả với tài liệu dài | Phức tạp trong cài đặt |
| Ngân | Sentence | 7 | Chính xác về ngữ pháp | Chunk size không đều |
| Khôi | FixedSize | 4 | Dễ debug | Kém linh hoạt |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *Viết 2-3 câu:* 
- RecursiveChunker là tốt nhất vì nó linh hoạt, thích ứng được với cả các bài viết dài lẫn các đoạn ghi chú ngắn, đảm bảo thông tin quan trọng không bị chia tách vô lý.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> *Viết 2-3 câu: 
dùng regex gì để detect sentence? Xử lý edge case nào?* 
- Tôi sử dụng regex `(?<=[.!?])\s+|\n+` để tách câu dựa trên các dấu kết thúc (.!?) theo sau là khoảng trắng hoặc xuống dòng. Cách này giúp xử lý được các trường hợp xuống dòng giữa chừng nhưng không kết thúc câu.

**`RecursiveChunker.chunk` / `_split`** — approach:
> *Viết 2-3 câu: 
algorithm hoạt động thế nào? Base case là gì?* 
- Thuật toán sử dụng đệ quy để thử từng dấu phân cách trong `separators`. Base case là khi độ dài văn bản nhỏ hơn `chunk_size` hoặc không còn dấu phân cách nào để thử, lúc đó nó sẽ trả về văn bản hiện tại.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> *Viết 2-3 câu: 
lưu trữ thế nào? Tính similarity ra sao?* 
- Các tài liệu được lưu dưới dạng list các dictionary trong bộ nhớ (in-memory). Khi tìm kiếm, tôi tính dot product giữa vector câu hỏi và tất cả các vector trong store, sau đó chia cho tích độ dài (norm) để ra cosine similarity.

**`search_with_filter` + `delete_document`** — approach:
> *Viết 2-3 câu: 
filter trước hay sau? Delete bằng cách nào?* 
- Tôi sử dụng phương pháp pre-filtering: lọc các record thỏa mãn metadata trước, sau đó mới thực hiện tìm kiếm similarity trên tập kết quả đã rút gọn. Hàm delete sẽ lọc bỏ các record có `doc_id` tương ứng.

### KnowledgeBaseAgent

**`answer`** — approach:
> *Viết 2-3 câu: 
prompt structure? Cách inject context?* 
- Prompt được xây dựng bằng cách nối các chunk tìm được thành một khối context, sau đó yêu cầu mô hình "Dựa vào thông tin sau: [context] hãy trả lời câu hỏi: [question]". Điều này giúp mô hình bám sát dữ liệu (grounding).

### Test Results

```
============================= 42 passed in 0.08s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | The cats are playing in the garden. | Animals are having fun outside. | high | 0.8245 | Đúng |
| 2 | AI is changing the world. | Machine learning is a subset of AI. | high | 0.7631 | Đúng |
| 3 | Python is popular. | I like to eat red apples. | low | 0.1245 | Đúng |
| 4 | LLMs are powerful. | The weather is nice today. | low | 0.0892 | Đúng |
| 5 | RAG improves accuracy. | RAG helps ground answers with data. | high | 0.8921 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:* Kết quả cho thấy độ chính xác rất cao. Khi sử dụng OpenAI Embeddings thay vì Mock, các câu có cùng ngữ nghĩa (dù khác từ vựng) đều đạt điểm số trên 0.7. Điều này chứng tỏ embedding model đã nắm bắt được không gian vector ngữ nghĩa thực sự, giúp hệ thống RAG hoạt động hiệu quả.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`.

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Nhịp tim bình thường của người trưởng thành khi nghỉ ngơi là bao nhiêu? | 60 - 100 nhịp/phút. |
| 2 | Bệnh nhân suy tim nên hạn chế ăn bao nhiêu muối mỗi ngày? | Dưới 2g Natri (khoảng 5g muối ăn). |
| 3 | Kể tên 3 loại thuốc nền tảng trong điều trị suy tim EF giảm | Ức chế men chuyển/ARNI, Chẹn Beta, Đối kháng Mineralocorticoid (MRA). |
| 4 | Bệnh tim mạch nào có triệu chứng ở phụ nữ thường nhẹ hơn nam giới và đi kèm buồn nôn, đổ mồ hôi? | Nhồi máu cơ tim. |
| 5 | Chỉ số ABI (Ankle-Brachial Index) dưới bao nhiêu thì nghi ngờ bệnh động mạch ngoại biên? | Dưới 0.9. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Nhịp tim bình thường? | "Nhịp tim bình thường... 60 đến 100..." | 0.7688 | Có | Nhịp tim lúc nghỉ ngơi từ 60-100 nhịp/phút. |
| 2 | Hạn chế bao nhiêu muối? | "Hạn chế muối < 2g natri/ngày..." | 0.6426 | Có | Nên ăn dưới 2g natri (5g muối) mỗi ngày. |
| 3 | 3 loại thuốc nền tảng? | "Các nhóm thuốc nền tảng... ACEi/ARB..." | 0.7753 | Có | Bao gồm ACEi/ARB, Chẹn beta và MRA. |
| 4 | Triệu chứng phụ nữ? | "Triệu chứng bệnh mạch vành ở phụ nữ..." | 0.7582 | Có | Triệu chứng thường nhẹ hơn, kèm buồn nôn/mồ hôi. |
| 5 | Chỉ số ABI? | "Chỉ số ABI (Ankle-Brachial Index)... < 0.9" | 0.8746 | Có | ABI < 0.9 nghi ngờ bệnh động mạch ngoại biên. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:* 
- Tôi học được cách thiết kế Metadata Schema từ bạn Lan, cách bạn ấy phân loại tài liệu theo 'difficulty' rất sáng tạo để lọc nội dung cho người mới hoặc chuyên gia.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:* 
- Tôi thấy một nhóm dùng strategy chunking theo 'Header' (markdown headers), giúp truy xuất chính xác các section trong tài liệu dài, đây là điều tôi sẽ áp dụng sau này.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:* 
- Tôi sẽ sử dụng một mô hình Embedding thực tế (thay vì Mock) để thấy được sức mạnh thực sự của Semantic Search và cải thiện chất lượng metadata filter để tìm kiếm sâu hơn.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 15 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **98 / 100** |
