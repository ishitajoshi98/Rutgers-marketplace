from sqlalchemy import text
from app.db import engine, Session
from app.models import User, Category, Item
from app.security import hash_password

def run():
    # 1) Connectivity check
    with engine.begin() as conn:
        now = conn.execute(text("SELECT now()")).scalar_one()
        print("DB time:", now)

    s = Session()
    try:
        # 2) Ensure a demo user exists
        user = s.query(User).filter_by(email="demo@scarletmail.edu").first()
        if not user:
            user = User(
                name="Demo Seller",
                email="demo@scarletmail.edu",
                password_hash=hash_password("demo1234"),
            )
            s.add(user)
            s.flush()  # ensures user.id is available

        # 3) Ensure a category exists
        cat = s.query(Category).filter_by(name="Books").first()
        if not cat:
            cat = Category(name="Books")
            s.add(cat)
            s.flush()

        # 4) Ensure a sample item exists
        item = s.query(Item).filter_by(title="CLRS Algorithms").first()
        if not item:
            item = Item(
                seller_id=user.id,
                title="CLRS Algorithms",
                description="3rd edition, good condition",
                price=25.00,
                category_id=cat.id,
                status="active",
                listing_type="auction",
            )
            s.add(item)

        s.commit()

        # 5) Read it back with a join (raw SQL for clarity)
        with engine.begin() as conn:
            rows = conn.execute(text("""
                SELECT i.title, i.price, c.name AS category, u.email AS seller
                FROM items i
                LEFT JOIN categories c ON c.id = i.category_id
                JOIN users u ON u.id = i.seller_id
                WHERE i.status = 'active'
                ORDER BY i.created_at DESC
                LIMIT 5
            """)).mappings().all()

        print("\nRecent active items:")
        for r in rows:
            print(f"- {r['title']} (${r['price']}) [{r['category']}] by {r['seller']}")

    finally:
        s.close()

if __name__ == "__main__":
    run()
