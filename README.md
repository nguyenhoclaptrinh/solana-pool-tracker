# Solana Token Pool Tracker

Dự án web Flask cho phép người dùng nhập đến 100 địa chỉ token Solana (mint address), 
sau đó hiển thị thông tin pool của từng token từ 3 DEX: Raydium, Orca, Meteora.

## Cách chạy dự án

1. Cài thư viện:
   pip install -r requirements.txt

2. Chạy server:
   python app.py

3. Truy cập web:
   http://localhost:5000

## Tính năng

- Nhập token (mint, tên, symbol)
- Tự động lấy pool từ Raydium, Orca, Meteora
- Hiển thị bảng pool: tên token, DEX, địa chỉ pool, giá, volume
- Cập nhật realtime 

## Thư mục chính

- app.py               → Flask app chính
- templates/           → Giao diện HTML
- static/              → JS, CSS
- pool_fetcher/        → Code lấy dữ liệu từ các DEX
- data/tokens.json     → Danh sách token do người dùng nhập
- data/pools.json      → Danh sách pool cập nhật

