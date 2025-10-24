# Rutgers Marketplace

Students often face difficulties buying and selling items such as furniture, bikes, and textbooks when moving in or out of on-campus/off-campus housing. Current solutions (e.g., Facebook groups, Whatsapp groups, word-of-mouth) are unorganized and filled with scammers. This results in wasted time, unfair pricing and items left unsold.
This app offers a simple student-to-student marketplace for Rutgers to solve this problem

### How the app works:

Students can post items they want to sell by adding details like images, price, and category, and other students can browse these listings and place bids. The seller can then accept the highest bid or choose a buyer, completing the transaction in a safe, organized way.

### ✨ Features

- Rutgers-only auth (email pattern check) with PBKDF2 password hashing
- Post items with image upload (stored under uploads/ — S3-ready later)
- Browse with search, category filters, pagination, inline item detail (+ Back button)
- Auction bidding (no self-bids; no bids on inactive items) & Fixed price (Buy Now)
- My Listings for sellers: view bids, Close, Mark Sold (to highest)

### 🧱 Tech Stack

- Frontend: Streamlit (Python)
- Backend: Python, SQLAlchemy
- DB: PostgreSQL 18 + extensions pgcrypto, pg_trgm
- Auth: PBKDF2-SHA256 (passlib)
- Config: .env (DATABASE_URL, UPLOAD_DIR)
