"""
Script để tải tiles bản đồ offline cho Việt Nam, Hoàng Sa và Trường Sa
Tránh bị "Access blocked" bằng cách sử dụng User-Agent và delay hợp lý
"""

import os
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

# Cấu hình
TILE_SERVER = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
TILES_DIR = "tiles"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
DELAY_BETWEEN_REQUESTS = 0.2  # Giây - tăng lên để an toàn hơn
MAX_WORKERS = 3  # Giảm số luồng để tránh bị chặn

# Zoom levels
MIN_ZOOM = 11
MAX_ZOOM = 11  # Tăng lên 11 hoặc 12 nếu cần chi tiết hơn

# Tọa độ vùng cần tải (Việt Nam + Hoàng Sa + Trường Sa)
REGIONS = {
    "vietnam_mainland": {
        "name": "Việt Nam đất liền",
        "bounds": {
            "min_lat": 8.0,    # Nam
            "max_lat": 23.5,   # Bắc
            "min_lon": 102.0,  # Tây
            "max_lon": 110.0   # Đông
        }
    },
    "hoang_sa": {
        "name": "Quần đảo Hoàng Sa (Paracel Islands)",
        "bounds": {
            "min_lat": 15.5,
            "max_lat": 17.5,
            "min_lon": 111.0,
            "max_lon": 113.0
        }
    },
    "truong_sa": {
        "name": "Quần đảo Trường Sa (Spratly Islands)",
        "bounds": {
            "min_lat": 6.0,
            "max_lat": 12.0,
            "min_lon": 109.5,
            "max_lon": 117.5
        }
    }
}

def deg2num(lat_deg, lon_deg, zoom):
    """Chuyển đổi tọa độ địa lý sang tile number"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def download_tile(z, x, y, session, retry_count=3):
    """Tải một tile với retry logic"""
    tile_path = Path(TILES_DIR) / str(z) / str(x) / f"{y}.png"
    
    # Nếu tile đã tồn tại, bỏ qua
    if tile_path.exists():
        return f"Skipped (exists): {z}/{x}/{y}"
    
    # Tạo thư mục nếu chưa có
    tile_path.parent.mkdir(parents=True, exist_ok=True)
    
    url = TILE_SERVER.format(z=z, x=x, y=y)
    
    for attempt in range(retry_count):
        try:
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                with open(tile_path, 'wb') as f:
                    f.write(response.content)
                return f"Downloaded: {z}/{x}/{y}"
            elif response.status_code == 404:
                # Tile không tồn tại (biển cả không có dữ liệu)
                return f"Not found (404): {z}/{x}/{y}"
            elif response.status_code == 403 or response.status_code == 429:
                # Bị chặn hoặc rate limit - chờ lâu hơn
                wait_time = 10 * (attempt + 1)  # Tăng dần thời gian chờ
                print(f"⚠️  Rate limited at {z}/{x}/{y}, waiting {wait_time}s... (attempt {attempt + 1}/{retry_count})")
                time.sleep(wait_time)
                continue
            else:
                print(f"⚠️  Error {response.status_code} for {z}/{x}/{y}")
                return f"Error {response.status_code}: {z}/{x}/{y}"
                
        except Exception as e:
            if attempt < retry_count - 1:
                time.sleep(3)
                continue
            return f"Failed: {z}/{x}/{y} - {str(e)}"
    
    return f"Failed after retries: {z}/{x}/{y}"

def get_tiles_for_region(region_bounds, zoom):
    """Lấy danh sách các tile cần tải cho một vùng"""
    min_x, max_y = deg2num(region_bounds["min_lat"], region_bounds["min_lon"], zoom)
    max_x, min_y = deg2num(region_bounds["max_lat"], region_bounds["max_lon"], zoom)
    
    tiles = []
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            tiles.append((zoom, x, y))
    
    return tiles

def download_tiles():
    """Hàm chính để tải tiles"""
    print("=" * 60)
    print("SCRIPT TẢI TILES BẢN ĐỒ OFFLINE - VIỆT NAM, HOÀNG SA, TRƯỜNG SA")
    print("=" * 60)
    print(f"Tile Server: {TILE_SERVER}")
    print(f"Zoom levels: {MIN_ZOOM} - {MAX_ZOOM}")
    print(f"Output directory: {TILES_DIR}/")
    print(f"Max workers: {MAX_WORKERS}")
    print("=" * 60)
    
    # Tạo session với headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': USER_AGENT,
        'Referer': 'https://www.openstreetmap.org/',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8'
    })
    
    # Thu thập tất cả tiles cần tải
    all_tiles = []
    for zoom in range(MIN_ZOOM, MAX_ZOOM + 1):
        print(f"\n📊 Calculating tiles for zoom level {zoom}...")
        
        for region_key, region_data in REGIONS.items():
            tiles = get_tiles_for_region(region_data["bounds"], zoom)
            all_tiles.extend(tiles)
            print(f"  • {region_data['name']}: {len(tiles)} tiles")
    
    print(f"\n✅ Total tiles to download: {len(all_tiles)}")
    
    # Hỏi xác nhận
    response = input("\n⚠️  Bạn có muốn tiếp tục? (y/n): ")
    if response.lower() != 'y':
        print("❌ Đã hủy.")
        return
    
    print(f"\n🚀 Starting download with {MAX_WORKERS} workers...")
    print("=" * 60)
    
    # Download tiles với thread pool
    downloaded = 0
    skipped = 0
    failed = 0
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit tất cả tasks
        futures = []
        for z, x, y in all_tiles:
            future = executor.submit(download_tile, z, x, y, session)
            futures.append(future)
            time.sleep(DELAY_BETWEEN_REQUESTS)  # Delay giữa các requests
        
        # Theo dõi tiến độ
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            
            if "Downloaded" in result:
                downloaded += 1
            elif "Skipped" in result or "Not found" in result:
                skipped += 1
            else:
                failed += 1
            
            # Hiển thị tiến độ mỗi 50 tiles
            if i % 50 == 0 or i == len(futures):
                elapsed = time.time() - start_time
                percent = (i / len(futures)) * 100
                print(f"Progress: {i}/{len(futures)} ({percent:.1f}%) | "
                      f"Downloaded: {downloaded} | Skipped: {skipped} | Failed: {failed} | "
                      f"Time: {elapsed:.1f}s")
    
    # Tổng kết
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("✅ HOÀN THÀNH!")
    print("=" * 60)
    print(f"📥 Downloaded: {downloaded} tiles")
    print(f"⏭️  Skipped: {skipped} tiles")
    print(f"❌ Failed: {failed} tiles")
    print(f"⏱️  Total time: {total_time:.1f}s")
    print(f"📁 Tiles saved to: {TILES_DIR}/")
    print("=" * 60)
    
    # Hướng dẫn tiếp theo
    print("\n📝 BƯỚC TIẾP THEO:")
    print("1. Kiểm tra thư mục tiles/ đã có dữ liệu")
    print("2. Mở index.html trong trình duyệt")
    print("3. Bản đồ sẽ hoạt động hoàn toàn offline!")
    print("\n💡 Nếu cần zoom levels cao hơn, chỉnh MAX_ZOOM và chạy lại script.")

if __name__ == "__main__":
    try:
        download_tiles()
    except KeyboardInterrupt:
        print("\n\n⚠️  Download bị gián đoạn bởi người dùng.")
    except Exception as e:
        print(f"\n❌ Lỗi: {str(e)}")
