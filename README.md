"# Bản đồ Offline - Việt Nam, Hoàng Sa, Trường Sa

Ứng dụng bản đồ offline sử dụng Leaflet để hiển thị bản đồ Việt Nam, Quần đảo Hoàng Sa và Trường Sa **hoàn toàn không cần internet**.

## ✨ Tính năng

- ✅ **Hoạt động hoàn toàn offline** - không cần kết nối internet
- 🗺️ **Bao phủ đầy đủ**: Việt Nam đất liền, Hoàng Sa, Trường Sa
- 🔍 Tìm kiếm theo tọa độ (Vĩ độ, Kinh độ)
- 📍 Hiển thị dữ liệu KMZ/KML
- 🚫 **Tránh bị "Access blocked"** khi tải tiles

## 📦 Cài đặt

### Bước 1: Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

### Bước 2: Tải tiles bản đồ offline

Chạy script để tải tiles cho các vùng:

- Việt Nam đất liền (lat: 8-23.5°N, lon: 102-110°E)
- Quần đảo Hoàng Sa (lat: 15.5-17.5°N, lon: 111-113°E)
- Quần đảo Trường Sa (lat: 6-12°N, lon: 109.5-117.5°E)

```bash
python download_tiles.py
```

**Script sẽ:**

- Tải tiles từ zoom level 5-10 (có thể tùy chỉnh trong script)
- Sử dụng User-Agent để tránh bị chặn
- Có retry logic và delay hợp lý
- Lưu tiles vào thư mục `tiles/` theo cấu trúc: `tiles/{z}/{x}/{y}.png`

**Lưu ý:**

- Quá trình tải có thể mất vài phút đến vài giờ tùy zoom level
- Zoom level cao hơn = chi tiết hơn nhưng tải lâu hơn và tốn dung lượng
- Zoom 5-10: Khoảng vài trăm MB đến vài GB

### Bước 3: Mở bản đồ

Mở `index.html` trong trình duyệt. Bản đồ sẽ hoạt động **hoàn toàn offline**!

## 🚀 Triển khai với Docker

Triển khai ứng dụng như một website tĩnh với Nginx để public thư mục `tiles/`.

### Dùng Docker CLI

```powershell
# Chạy ở thư mục: d:\.ATIN\map\offlinemap\map
docker build -t offline-map .
docker run -d -p 8080:80 --name offline-map `
    -v ${PWD}\tiles:/usr/share/nginx/html/tiles:ro offline-map

# Mở trình duyệt
Start-Process http://localhost:8080/
```

### Dùng Docker Compose

```powershell
# Chạy ở thư mục: d:\.ATIN\map\offlinemap\map
docker compose up -d --build
Start-Process http://localhost:8080/
```

### Ghi chú

- Container Nginx sẽ phục vụ `index.html`, `lib/`, `biengioi.kmz` và `tiles/`.
- `tiles/` được mount read-only; cập nhật bên ngoài là phục vụ ngay.
- Public truy cập tại `http://localhost:8080/`. Có thể đổi port nếu cần.

## 🎯 Cách sử dụng

1. **Xem bản đồ**: Bản đồ sẽ hiển thị khu vực Việt Nam, Hoàng Sa, Trường Sa
2. **Tìm kiếm tọa độ**: Nhập tọa độ vào ô tìm kiếm
   - Ví dụ Hoàng Sa: `16.5, 112.0`
   - Ví dụ Trường Sạ: `10.0, 114.0`
   - Ví dụ Hà Nội: `21.0285, 105.8542`
3. **Xem dữ liệu KMZ**: Bản đồ tự động load file `data2.kmz` khi mở

## ⚙️ Tùy chỉnh

### Thay đổi zoom levels

Mở file `download_tiles.py` và chỉnh sửa:

```python
MIN_ZOOM = 5   # Zoom thấp nhất (xem toàn cảnh)
MAX_ZOOM = 10  # Zoom cao nhất (chi tiết)
```

**Khuyến nghị zoom levels:**

- Zoom 5-8: Xem tổng quan, nhẹ (vài trăm MB)
- Zoom 5-10: Cân bằng chi tiết và dung lượng (vài GB)
- Zoom 5-12: Chi tiết cao (hàng chục GB)

### Thay đổi vùng tải

Chỉnh sửa `REGIONS` trong `download_tiles.py`:

```python
REGIONS = {
    "custom_area": {
        "name": "Vùng tùy chỉnh",
        "bounds": {
            "min_lat": 10.0,
            "max_lat": 20.0,
            "min_lon": 105.0,
            "max_lon": 115.0
        }
    }
}
```

## 🔧 Xử lý lỗi

### Bị "Access blocked" khi tải tiles

Script đã có sẵn các biện pháp:

- ✅ User-Agent giống trình duyệt thật
- ✅ Delay giữa các requests (0.1s)
- ✅ Retry logic khi bị rate limit
- ✅ Số luồng download hợp lý (4 workers)

Nếu vẫn bị chặn:

1. Tăng `DELAY_BETWEEN_REQUESTS` trong script (ví dụ: 0.5)
2. Giảm `MAX_WORKERS` (ví dụ: 2)
3. Chạy script vào giờ thấp điểm

### Tiles không hiển thị

1. Kiểm tra thư mục `tiles/` đã có dữ liệu
2. Đảm bảo cấu trúc: `tiles/{z}/{x}/{y}.png`
3. Kiểm tra zoom level trong `index.html` khớp với script

## 📁 Cấu trúc thư mục

```
map/
├── index.html              # Trang bản đồ chính
├── download_tiles.py       # Script tải tiles offline
├── requirements.txt        # Python dependencies
├── README.md              # Tài liệu này
├── data.kmz               # Dữ liệu KMZ (tùy chọn)
├── data2.kmz              # Dữ liệu KMZ (tùy chọn)
├── lib/                   # Thư viện JavaScript
│   ├── leaflet.js
│   ├── leaflet.css
│   ├── jszip.min.js
│   └── togeojson.js
└── tiles/                 # Tiles bản đồ (tạo bởi script)
    └── {z}/
        └── {x}/
            └── {y}.png
```

## 🌐 Thư viện sử dụng

- **Leaflet**: Thư viện bản đồ JavaScript
- **JSZip**: Xử lý file KMZ
- **toGeoJSON**: Chuyển đổi KML sang GeoJSON
- **requests**: Tải tiles từ OpenStreetMap

## 📝 Tọa độ quan trọng

### Hoàng Sa (Paracel Islands)

- Trung tâm: `16.5°N, 112.0°E`
- Vùng: 15.5-17.5°N, 111-113°E

### Trường Sa (Spratly Islands)

- Trung tâm: `10.0°N, 114.0°E`
- Vùng: 6-12°N, 109.5-117.5°E

### Việt Nam đất liền

- Trung tâm: `16.0544°N, 108.2022°E`
- Vùng: 8-23.5°N, 102-110°E

## 📄 Giấy phép

Tiles bản đồ: © OpenStreetMap contributors
Code: MIT License

## 🤝 Đóng góp

Mở issue hoặc pull request nếu có đề xuất cải thiện!
"
