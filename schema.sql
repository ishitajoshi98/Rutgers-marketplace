-- ---- Lookup types as CHECKs (more flexible than ENUMs for class projects) ----
-- item status: active (listed), closed (no longer accepting bids), sold (winner chosen)
-- listing type: auction or fixed (buy-now only)
-- NOTE: keep as CHECKs so you can add more values later without ALTER TYPE hassles.

-- ---- USERS ----
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  is_admin BOOLEAN NOT NULL DEFAULT FALSE,
  email_verified BOOLEAN NOT NULL DEFAULT FALSE,
  join_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ, 
  CONSTRAINT chk_rutgers_email CHECK (email ~* '@(rutgers\.edu|scarletmail\.edu)$') 
--enforce Rutgers-only at DB level (you can also do it in app
); 

-- ---- CATEGORIES ----
CREATE TABLE IF NOT EXISTS categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT UNIQUE NOT NULL
);

-- ---- ITEMS (listings) ----
CREATE TABLE IF NOT EXISTS items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  seller_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
  category_id UUID REFERENCES categories(id),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','closed','sold')),
  listing_type TEXT NOT NULL DEFAULT 'auction' CHECK (listing_type IN ('auction','fixed')),
  buy_now_price NUMERIC(10,2) CHECK (buy_now_price IS NULL OR buy_now_price >= 0),
  pickup_location TEXT,
  pickup_lat DOUBLE PRECISION,
  pickup_lng DOUBLE PRECISION,
  auction_end_at TIMESTAMPTZ,
  chosen_bid_id UUID, -- FK added after bids table exists
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

-- keep items.updated_at fresh
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_items_set_updated_at ON items;
CREATE TRIGGER trg_items_set_updated_at
  BEFORE UPDATE ON items FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---- ITEM IMAGES (multi-image, future S3 ready) ----
CREATE TABLE IF NOT EXISTS item_images (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  image_path TEXT NOT NULL,         -- e.g., 'uploads/uuid.jpg' or S3 URL later
  is_primary BOOLEAN NOT NULL DEFAULT FALSE,
  sort_order INT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_item_images_item ON item_images(item_id);
CREATE INDEX IF NOT EXISTS idx_item_images_primary ON item_images(item_id, is_primary);

-- ---- BIDS ----
CREATE TABLE IF NOT EXISTS bids (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
  bidder_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount NUMERIC(10,2) NOT NULL CHECK (amount > 0),
  placed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bids_item_time ON bids(item_id, placed_at DESC);
CREATE INDEX IF NOT EXISTS idx_bids_item_amount ON bids(item_id, amount DESC);

-- Back-reference (winning bid) once bids exists
ALTER TABLE items
  DROP CONSTRAINT IF EXISTS fk_items_chosen_bid,
  ADD CONSTRAINT fk_items_chosen_bid
    FOREIGN KEY (chosen_bid_id) REFERENCES bids(id) ON DELETE SET NULL;

-- ---- Optional safety trigger: prevent bids on non-active items ----
CREATE OR REPLACE FUNCTION prevent_bids_on_inactive() RETURNS TRIGGER AS $$
DECLARE s TEXT;
BEGIN
  SELECT status INTO s FROM items WHERE id = NEW.item_id;
  IF s IS DISTINCT FROM 'active' THEN
    RAISE EXCEPTION 'Cannot bid on item with status %', s;
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_bids_only_on_active ON bids;
CREATE TRIGGER trg_bids_only_on_active
  BEFORE INSERT ON bids FOR EACH ROW EXECUTE FUNCTION prevent_bids_on_inactive();

-- ---- Optional safety trigger: seller cannot bid on own item ----
CREATE OR REPLACE FUNCTION prevent_self_bidding() RETURNS TRIGGER AS $$
DECLARE seller UUID;
BEGIN
  SELECT seller_id INTO seller FROM items WHERE id = NEW.item_id;
  IF seller = NEW.bidder_id THEN
    RAISE EXCEPTION 'Seller cannot bid on own item';
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_no_self_bids ON bids;
CREATE TRIGGER trg_no_self_bids
  BEFORE INSERT ON bids FOR EACH ROW EXECUTE FUNCTION prevent_self_bidding();

-- ---- Helpful indexes for common queries ----
CREATE INDEX IF NOT EXISTS idx_items_active_recent
  ON items (status, created_at DESC);

-- Trigram index for simple search (future)
CREATE INDEX IF NOT EXISTS idx_items_trgm_title
  ON items USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_items_trgm_desc
  ON items USING gin (description gin_trgm_ops);

-- ---- Convenience view: current highest bid per item (for fast UI) ----
CREATE OR REPLACE VIEW item_highest_bids AS
SELECT b.item_id, MAX(b.amount) AS highest_bid
FROM bids b
GROUP BY b.item_id;
