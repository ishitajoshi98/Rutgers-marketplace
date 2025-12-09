import os
from dotenv import load_dotenv
import streamlit as st


# --- ensure project root is on sys.path ---
import os, sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
# ------------------------------------------

from app.db import Session
from app.models import Item, ItemImage, Category
from app.utils import save_uploaded_image
    

import base64

def add_fullscreen_bg(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
            /* Remove Streamlit's default white header spacing */
            header[data-testid="stHeader"] {{
                display: none;
            }}

            html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main {{
                height: 100%;
                min-height: 100vh;
            }}

            [data-testid="stAppViewContainer"] {{
                background-image: url("data:image/jpeg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
                margin: 0;
                padding: 0;
            }}

            /* Overlay to control opacity */
            [data-testid="stAppViewContainer"]::before {{
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.4);
                z-index: 0;
            }}

            /* Keep content readable and centered */
            .block-container {{
                position: relative;
                z-index: 1;
                padding-top: 5vh;
                padding-bottom: 5vh;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )




# Load .env (for future DB use)
load_dotenv()

st.set_page_config(page_title="Rutgers Marketplace!", page_icon="🛒", layout="wide")

# # Force global font override in Streamlit
# st.markdown("""
#     <style>
#         /* Apply Book Antiqua for all text globally */
#         html, body, [class*="st-"], [data-testid="stAppViewContainer"] * {
#             font-family: 'Book Antiqua', 'Bookman Old Style', serif !important;
#         }

#         /* Make titles specifically use Bookman Old Style */
#         h1, h2, h3, .auth-title, .stMarkdown h2 {
#             font-family: 'Bookman Old Style', serif !important;
#             color: white !important;
#         }

#         /* Optional: make captions softer */
#         .auth-caption {
#             color: #dddddd !important;
#             font-family: 'Book Antiqua', serif !important;
#         }
#     </style>
# """, unsafe_allow_html=True)



# --- session bootstrap ---
if "user" not in st.session_state:
    st.session_state.user = None  # {"id": "...", "name": "...", "email": "..."}

# Try to import real auth functions if they exist (Step 2.2 will add them)
_auth_available = True
try:
    from app.auth import register_user, authenticate_user, is_rutgers_email
except Exception as e:
    _auth_available = False
    print("AUTH_IMPORT_ERROR: ", e)





#BOXED LAYOUT
def render_logged_out():
    # Hide sidebar when logged out for a cleaner look
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] { display: none !important; }

            .auth-title, h2.auth-title, div[data-testid="stMarkdownContainer"] h2.auth-title {
                text-align: center;
                margin-bottom: 6px;
                font-size: 40px !important;
                line-height: 0.5;
                color: #ffffff;
            }

            .auth-caption {
                text-align: center;
                margin-bottom: 18px;
                color: #ccc;
                font-size: 16px;
            }

            /* optional: soften the container look a bit */
            .boxed-inner {
                padding: 5px 32px 28px 32px;  /* top, right, bottom, left */
                max-width: 200px;                /* controls box width */
                margin: 0 auto;                  /* centers the box horizontally */
            }
        </style>
    """, unsafe_allow_html=True)




    # Center column layout: empty | content | empty
    left, center, right = st.columns([1, 2, 1])
    with center:
        # --- Native Streamlit container so tabs/forms are inside the SAME box ---
        with st.container(border=True):
            # Extra padding inside the bordered container
            st.markdown('<div class="boxed-inner">', unsafe_allow_html=True)

            # Title & caption (centered)
            st.markdown('<h2 class="auth-title">🛒 Welcome to Rutgers Marketplace</h2>', unsafe_allow_html=True)
            st.markdown('<div class="auth-caption">Rutgers-only, safe student-to-student marketplace</div>', unsafe_allow_html=True)

            st.divider()

            if not _auth_available:
                st.info("Auth backend not implemented yet (we'll add it in the next step). Buttons are disabled for now.")

            # Centered tabs INSIDE the same bordered box
            tab_login, tab_register = st.tabs(["🔑 Login", "🆕 Register"])

            with tab_login:
                with st.form("login_form", clear_on_submit=False):
                    email = st.text_input("Rutgers Email", placeholder="you@rutgers.edu")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Login", use_container_width=True)

                if submitted:
                    if not _auth_available:
                        st.error("Auth backend not loaded. Restart Streamlit from the project root.")
                    else:
                        user = authenticate_user(email, password)
                        if user:
                            st.session_state.user = {"id": str(user.id), "name": user.name, "email": user.email}
                            st.success("Logged in successfully.")
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")

            with tab_register:
                with st.form("register_form", clear_on_submit=False):
                    name = st.text_input("Full Name", placeholder="Jane Doe")
                    email_new = st.text_input(
                        "Rutgers Email (@rutgers.edu or @scarletmail.rutgers.edu)",
                        placeholder="netid@rutgers.edu"
                    )
                    password_new = st.text_input("Password (min 6 chars)", type="password")
                    submitted_r = st.form_submit_button("Create Account", use_container_width=True)

                if submitted_r:
                    if not _auth_available:
                        st.error("Auth backend not loaded. Restart Streamlit from the project root.")
                    else:
                        if not is_rutgers_email(email_new):
                            st.error("Please use a Rutgers email address.")
                        else:
                            ok, msg = register_user(name, email_new, password_new)
                            if ok:
                                st.success(msg)
                                st.info("Now switch to the Login tab to sign in.")
                            else:
                                st.error(msg)

            st.markdown('</div>', unsafe_allow_html=True)  # close .boxed-inner




# OG LAYOUT
# def render_logged_out():
#     # Hide sidebar when logged out for a cleaner look
#     st.markdown("""
#         <style>
#             section[data-testid="stSidebar"] { display: none !important; }
#             .auth-title, h2.auth-title, div[data-testid="stMarkdownContainer"] h2.auth-title {text-align: center;
#             margin-bottom: 6px; font-size: 60px !important; line-height: 1.2;} 
#             .auth-caption { text-align: center;  margin-bottom: 18px; }
#             .auth-tabs [data-baseweb="tab-list"] { justify-content: center; }
#         </style>
#     """, unsafe_allow_html=True)

#     #.auth-title { text-align: center; margin-bottom: 6px; font-size: 45px;}
#     #color: #6b7280;
    


#     # Center column layout: empty | content | empty
#     left, center, right = st.columns([1, 2, 1])
#     with center:
#         # Title & caption (centered)
#         st.markdown('<h2 class="auth-title">🛒 Rutgers Marketplace</h2>', unsafe_allow_html=True)
#         st.markdown('<div class="auth-caption">Rutgers-only, safe student-to-student marketplace</div>', unsafe_allow_html=True)

#         if not _auth_available:
#             st.info("Auth backend not implemented yet (we'll add it in the next step). Buttons are disabled for now.")

#         st.divider()

#         # Centered tabs
#         tab_login, tab_register = st.tabs(["🔑 Login", "🆕 Register"])
#         with tab_login:
#             with st.form("login_form", clear_on_submit=False):
#                 email = st.text_input("Rutgers Email", placeholder="you@rutgers.edu")
#                 password = st.text_input("Password", type="password")
#                 submitted = st.form_submit_button("Login", use_container_width=True)

#             if submitted:
#                 if not _auth_available:
#                     st.error("Auth backend not loaded. Restart Streamlit from the project root.")
#                 else:
#                     user = authenticate_user(email, password)
#                     if user:
#                         st.session_state.user = {"id": str(user.id), "name": user.name, "email": user.email}
#                         st.success("Logged in successfully.")
#                         st.rerun()
#                     else:
#                         st.error("Invalid email or password.")

#         with tab_register:
#             with st.form("register_form", clear_on_submit=False):
#                 name = st.text_input("Full Name", placeholder="Jane Doe")
#                 email_new = st.text_input("Rutgers Email (@rutgers.edu or @scarletmail.rutgers.edu)", placeholder="netid@rutgers.edu")
#                 password_new = st.text_input("Password (min 6 chars)", type="password")
#                 submitted_r = st.form_submit_button("Create Account", use_container_width=True)

#             if submitted_r:
#                 if not _auth_available:
#                     st.error("Auth backend not loaded. Restart Streamlit from the project root.")
#                 else:
#                     if not is_rutgers_email(email_new):
#                         st.error("Please use a Rutgers email address.")
#                     else:
#                         ok, msg = register_user(name, email_new, password_new)
#                         if ok:
#                             st.success(msg)
#                             st.info("Now switch to the Login tab to sign in.")
#                         else:
#                             st.error(msg)


# Before UI changes
# def render_logged_in():
#     # Sidebar nav ONLY when logged in
#     PAGES = ["Home", "Post Item", "My Listings", "My Purchases", "My Bids"]
#     if "selected_page" not in st.session_state:
#         st.session_state.selected_page = "Home"
#     st.sidebar.success(f"Logged in as {st.session_state.user['name']}")
#     if st.sidebar.button("Log out"):
#         st.session_state.user = None
#         st.rerun()

#     page = st.sidebar.radio("Navigation", PAGES, index=PAGES.index(st.session_state.selected_page))
#     st.session_state.selected_page = page

#     st.title("🛒 Rutgers Marketplace")
#     st.caption("Rutgers-only, safe student-to-student marketplace")

#     if page == "Home":
#         render_browse_items()

#     elif page == "Post Item":
#         render_post_item()

#     elif page == "My Listings":
#         render_my_listings()
    
#     elif page == "My Purchases":
#         render_my_purchases()
        
#     elif page == "My Bids":
#         render_my_bids()


def render_logged_in():
    

    # --- HEADER ---
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("app/rutgers_logo_final.png", width=350)

    with col2:
        st.markdown(
            '''
            <div style="text-align: right;">
                <h3 style="margin-bottom: 5px;">Welcome to your marketplace</h3>
                <input type="text" placeholder="Search..." 
                    style="width: 60%; padding: 8px; border-radius: 6px; border: 1px solid #ccc;">
            </div>
            ''',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --- NAV TABS ---
    tabs = ["Home", "Post Item", "My Listings", "My Purchases", "My Bids"]
    selected_tab = st.radio(
        label="Navigation",
        options=tabs,
        horizontal=True,
        label_visibility="collapsed"
    )

    # --- Custom CSS for Tabs ---
    st.markdown("""
        <style>
        div[data-baseweb="radio"] > div {
            justify-content: center;
        }
        div[data-baseweb="radio"] label {
            background-color: #CC0033;
            color: white;
            font-weight: bold;
            border-radius: 6px;
            padding: 10px 20px;
            margin-right: 10px;
            cursor: pointer;
            transition: 0.3s;
        }
        div[data-baseweb="radio"] input:checked + div {
            background-color: #800000 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render the selected page content
    if selected_tab == "Home":
        render_browse_items()
    elif selected_tab == "Post Item":
        render_post_item()
    elif selected_tab == "My Listings":
        render_my_listings()
    elif selected_tab == "My Purchases":
        render_my_purchases()
    elif selected_tab == "My Bids":
        render_my_bids()

    st.markdown("---")
    st.markdown(f"Logged in as **{st.session_state.user['name']}**")
    if st.button("Log out"):
        st.session_state.user = None
        st.rerun()




def render_post_item():
    import uuid
    from uuid import UUID

    st.subheader("Post an Item")

    # must be logged in
    user = st.session_state.user
    if not user:
        st.warning("You must be logged in to post an item.")
        return

    # load categories for the dropdown
    s = Session()
    try:
        cats = s.query(Category).order_by(Category.name).all()
        cat_options = {c.name: str(c.id) for c in cats}
    finally:
        s.close()

    if not cat_options:
        st.info("No categories found. Add some categories in the DB first (e.g., Books, Electronics, Furniture).")
        return

    with st.form("post_item_form", clear_on_submit=False):
        title = st.text_input("Title")
        description = st.text_area("Description", height=120)
        pickup_location = st.text_input("Pickup Location (e.g., College Ave, Livingston)", max_chars=100)
        nearest_campus = st.selectbox("Nearest Campus", ["Busch", "College Ave", "Livingston", "SoCam"])
        options_display = ["Auction", "Fixed"]
        mapping = {"Auction": "auction", "Fixed": "fixed"}
        choice = st.radio("Listing type", options_display, horizontal=True)
        listing_type = mapping[choice]
        #listing_type = st.radio("Listing type", ["auction", "fixed"], horizontal=True)
        if listing_type == "fixed":
            buy_now_price = st.number_input("Price (USD)", min_value=0.0, value=10.0, step=1.0)
            price = buy_now_price  # keep same var name used below
        else:
            price = st.number_input("Starting Price (USD)", min_value=0.0, value=10.0, step=1.0)
            buy_now_price = None

        category_name = st.selectbox("Category", list(cat_options.keys()))
        image = st.file_uploader("Main image", type=["jpg", "jpeg", "png", "webp"])
        submitted = st.form_submit_button("Create Listing", use_container_width=True)


    if submitted:
        # basic validation
        if not title.strip() or not description.strip():
            st.error("Title and description are required.")
            return
        if image is None:
            st.error("Please upload a main image.")
            return

        # save image
        upload_root = os.getenv("UPLOAD_DIR", "uploads")
        ok, rel_or_err = save_uploaded_image(image, upload_root, user["id"])
        if not ok:
            st.error(rel_or_err)
            return

        # insert into DB
        s = Session()
        try:
            cat_id = UUID(cat_options[category_name])

            item = Item(
                seller_id=UUID(user["id"]),
                title=title.strip(),
                description=description.strip(),
                price=price,
                category_id=cat_id,
                status="active",
                listing_type=listing_type,
                buy_now_price=buy_now_price,
                pickup_location=pickup_location.strip() or None,
                pickup_campus=nearest_campus,
                pickup_lat=None,  # for future
                pickup_lng=None   # for future
            )
            s.add(item)
            s.flush()  # get item.id

            img = ItemImage(
                item_id=item.id,
                image_path=rel_or_err,  # relative to UPLOAD_DIR
                is_primary=True,
                sort_order=0,
            )
            s.add(img)
            s.commit()

            st.success("Listing created!")
            abs_path = os.path.join(upload_root, rel_or_err).replace("\\", "/")
            st.image(abs_path, caption=title, use_container_width=True)
        except Exception as e:
            s.rollback()
            st.error(f"Failed to create listing: {e}")
        finally:
            s.close()


def render_browse_items():
    import math
    from sqlalchemy import text

    st.subheader("Browse Items")

    # Initialize pagination state
    if "browse_page" not in st.session_state:
        st.session_state.browse_page = 1


    # If we're viewing a specific item, render detail with a Back button
    viewing_id = st.session_state.get("viewing_item_id")
    if viewing_id:
        if st.button("← Back to results"):
            st.session_state.pop("viewing_item_id", None)
            st.rerun()
        # Render the detail view inline and return early
        render_item_detail(viewing_id)
        return



    # Filters row
    col1, col2, col3, col4 = st.columns([4, 3, 4, 2])

    # Load categories for dropdown
    s = Session()
    try:
        cats = s.query(Category).order_by(Category.name).all()
        cat_names = ["All categories"] + [c.name for c in cats]
        price_bounds = s.execute(text("SELECT MIN(price), MAX(price) FROM items WHERE status = 'active'")).first()
        price_min, price_max = price_bounds if price_bounds else (0, 100)
        # --- FIX: Ensure slider never breaks when min == max or DB is empty ---
        # Handle None values (empty table)
        if price_min is None:
            price_min = 0
        if price_max is None:
            price_max = 100
        # Avoid min == max which breaks Streamlit slider
        if price_min == price_max:
            price_min = 0
            price_max = float(price_max) + 50
    finally:
        s.close()


    with col1:
        selected_cat = st.selectbox("Category", cat_names)

    with col2:
        location = st.selectbox("Location", ["All", "Busch", "College Ave", "Livingston", "SoCam"])

    with col3:
        price_range = st.slider("Price Range (USD)", min_value=float(price_min or 0), max_value=float(price_max or 100), value=(float(price_min or 0), float(price_max or 100)), step = 50.0)

    with col4:
        page_size = st.selectbox("Page size", [6, 9, 12, 15, 20], index=1)

    # with col1:
    #     q = st.text_input("Search", placeholder="title or description…").strip()
    # with col2:
    #     selected_cat = st.selectbox("Category", cat_names, index=0)
    # with col3:
    #     page_size = st.selectbox("Page size", [6, 9, 12, 15, 20], index=1)
    # with col4:
    #     # page index in session so pagination persists on reruns
    #     if "browse_page" not in st.session_state:
    #         st.session_state.browse_page = 1

    # Build WHERE clause
    where = ["i.status = 'active'"]
    params = {}

    # if q:
    #     where.append("(i.title ILIKE :q OR i.description ILIKE :q)")
    #     params["q"] = f"%{q}%"

    if selected_cat != "All categories":
        where.append("c.name = :cat_name")
        params["cat_name"] = selected_cat

    if location != "All":
        where.append("i.pickup_campus = :location")
        params["location"] = location

    where.append("i.price BETWEEN :min_price AND :max_price")
    params["min_price"] = price_range[0]
    params["max_price"] = price_range[1]

    where_sql = " AND ".join(where) if where else "TRUE"

    # Count total for pagination
    count_sql = text(f"""
        SELECT COUNT(*)
        FROM items i
        LEFT JOIN categories c ON c.id = i.category_id
        JOIN users u ON u.id = i.seller_id
        WHERE {where_sql}
    """)

    # Fetch page of items (with one primary image if present)
    # Note: using COALESCE to pick any image_path if no primary is set
    list_sql = text(f"""
        WITH base AS (
            SELECT i.id, i.title, i.price, i.created_at,
                   COALESCE(ci.name, 'Uncategorized') AS category,
                   u.email AS seller_email,
                   i.pickup_location
            FROM items i
            LEFT JOIN categories ci ON ci.id = i.category_id
            JOIN users u ON u.id = i.seller_id
            WHERE i.status = 'active'
            {"AND ci.name = :cat_name" if selected_cat != "All categories" else ""}
            {"AND i.pickup_location = :location" if location != "All" else ""}
            AND i.price BETWEEN :min_price AND :max_price
            ORDER BY i.created_at DESC
        ),
        img AS (
            SELECT ii.item_id,
                   -- prefer primary image; else first by sort_order
                   (SELECT image_path
                    FROM item_images iix
                    WHERE iix.item_id = ii.item_id
                    ORDER BY iix.is_primary DESC, iix.sort_order ASC, iix.created_at ASC
                    LIMIT 1) AS image_path
            FROM item_images ii
            GROUP BY ii.item_id
        )
        SELECT b.id, b.title, b.price, b.category, b.seller_email, b.created_at,
               COALESCE(img.image_path, NULL) AS image_path,
               b.pickup_location
        FROM base b
        LEFT JOIN img ON img.item_id = b.id
        LIMIT :limit OFFSET :offset
    """)

    # Handle pagination controls
    col_prev, col_stat, col_next = st.columns([0.3, 3, 0.3])
    with col_prev:
        if st.button("⬅️ Prev", use_container_width=True, disabled=st.session_state.browse_page <= 1):
            st.session_state.browse_page = max(1, st.session_state.browse_page - 1)
            st.rerun()
    with col_next:
        # next button set after we know total
        pass

    # Run queries
    s = Session()
    try:
        total = s.execute(count_sql, params).scalar_one()
        total_pages = max(1, math.ceil(total / page_size))
        page = min(st.session_state.browse_page, total_pages)
        offset = (page - 1) * page_size

        rows = s.execute(list_sql, {**params, "limit": page_size, "offset": offset}).mappings().all()
    finally:
        s.close()

    # Update Next button now that we know total/pages
    with col_stat:
        st.write(f"Page {page} of {total_pages} • {total} result(s)")

    with col_next:
        if st.button("Next ➡️", use_container_width=True, disabled=page >= total_pages):
            st.session_state.browse_page = min(total_pages, page + 1)
            st.rerun()

    st.divider()

    if not rows:
        st.info("No items matched your filters yet.")
        return


    # Add uniform image sizing via CSS
    st.markdown("""
        <style>
            .uniform-img img {
                object-fit: cover;      /* Crop rather than stretch */
                width: 100%;            /* Fit column width */
                height: 350px;          /* Set consistent height */
                border-radius: 10px;     /* Optional: smooth corners */
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                margin-bottom: 12px;    /*  Adds gap below image */
            }
        </style>
    """, unsafe_allow_html=True)

    # Grid of cards
    cols_per_row = 3
    for i in range(0, len(rows), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(rows):
                break
            r = rows[idx]

            with col:
                # Thumbnail logic
                img_md = ""
                if r["image_path"]:
                    abs_path = os.path.join(os.getenv("UPLOAD_DIR", "uploads"), r["image_path"]).replace("\\", "/")
                    st.markdown(f"""
                        <div class="uniform-img">
                            <img src="data:image/jpeg;base64,{base64.b64encode(open(abs_path, "rb").read()).decode()}" />
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.caption("No image")

                st.markdown(f"**{r['title']}**")
                st.caption(f"{r['category']} • {r['seller_email']}")
                if r["pickup_location"]:
                    st.caption(f"📍 Pickup from: {r['pickup_location']}")
                st.write(f"${r['price']:.2f}")
                if st.button("View", key=f"view_{r['id']}"):
                    st.session_state.viewing_item_id = str(r["id"])  # stay on Browse, show detail inline
                    st.rerun()



def render_item_detail(item_id_str: str):
    from uuid import UUID
    from sqlalchemy import text

    st.subheader("Item Detail")

    # parse UUID
    try:
        item_id = UUID(item_id_str)
    except Exception:
        st.error("Invalid item ID.")
        return

    # fetch item, seller, category, images, highest bid
    s = Session()
    try:
        item_row = s.execute(text("""
            SELECT i.id, i.title, i.description, i.price, i.status, i.listing_type,
                   COALESCE(c.name, 'Uncategorized') AS category,
                   u.email AS seller_email, u.id AS seller_id,
                   i.pickup_location
            FROM items i
            LEFT JOIN categories c ON c.id = i.category_id
            JOIN users u ON u.id = i.seller_id
            WHERE i.id = :iid
        """), {"iid": str(item_id)}).mappings().first()

        if not item_row:
            st.error("Item not found.")
            return

        # primary image (if any) + all images (future gallery)
        imgs = s.execute(text("""
            SELECT image_path, is_primary, sort_order
            FROM item_images
            WHERE item_id = :iid
            ORDER BY is_primary DESC, sort_order ASC, created_at ASC
        """), {"iid": str(item_id)}).mappings().all()

        # highest bid
        hb = s.execute(text("""
            SELECT MAX(amount) AS highest FROM bids WHERE item_id = :iid
        """), {"iid": str(item_id)}).scalar()

    finally:
        s.close()

    # layout
    col_img, col_info = st.columns([3, 4], vertical_alignment="top")

    with col_img:
        if imgs:
            upload_root = os.getenv("UPLOAD_DIR", "uploads")
            main = imgs[0]["image_path"]
            abs_path = os.path.join(upload_root, main).replace("\\", "/")
            st.image(abs_path, use_container_width=True)
        else:
            st.caption("No image")

    with col_info:
        st.markdown(f"### {item_row['title']}")
        st.caption(f"{item_row['category']} • Seller: {item_row['seller_email']}")
        if item_row["pickup_location"]:
            st.caption(f"📍 Pickup from: {item_row['pickup_location']}")

        st.write(item_row["description"])
        st.write(f"**Price:** ${item_row['price']:.2f}")
        st.write(f"**Type:** {item_row['listing_type'].capitalize()}")

        user = st.session_state.user

        if item_row["listing_type"] == "auction":
            current_highest = float(hb) if hb is not None else 0.0
            st.markdown(f"**Current highest bid:** ${current_highest:.2f}")

            if item_row["status"] == "active":
                if not user:
                    st.warning("Log in to place a bid.")
                elif user["email"] == item_row["seller_email"]:
                    st.info("You are the seller; you cannot bid on your own item.")
                else:
                    if st.session_state.get("just_bid"):
                        st.session_state.pop("just_bid")
                        
                    with st.form("place_bid_form", clear_on_submit=False):
                        min_bid = max(current_highest + 1.00, 1.00)
                        default_bid = 0.0 if st.session_state.get("just_bid") else min_bid
                        bid_amount = st.number_input("Your bid (USD)", min_value=min_bid, value=default_bid, step=1.00)
                        placed = st.form_submit_button("Place Bid", use_container_width=True)

                    if placed:
                        sb = Session()
                        try:
                            res = sb.execute(text("""
                                INSERT INTO bids (item_id, bidder_id, amount)
                                VALUES (:iid, :bidder, :amt)
                                RETURNING id
                            """), {"iid": str(item_row["id"]), "bidder": user["id"], "amt": bid_amount})
                            bid_id = res.scalar_one()
                            sb.commit()
                            st.success("Bid placed successfully.")
                            st.session_state["just_bid"] = True
                            st.rerun()
                        except Exception as e:
                            sb.rollback()
                            st.error(f"Failed to place bid: {e}")
                        finally:
                            sb.close()
            else:
                st.info("Bidding is unavailable for this item.")

        elif item_row["listing_type"] == "fixed":
            # Fixed price purchase
            st.markdown(f"**Buy now price:** ${float(item_row['price']):.2f}")
            if item_row["status"] != "active":
                st.info("This item is not available for purchase.")
            else:
                if not user:
                    st.warning("Log in to purchase.")
                elif user["email"] == item_row["seller_email"]:
                    st.info("You are the seller; you cannot purchase your own item.")
                else:
                    sb = Session()
                    try:
                        # Check if user already placed an offer 
                        existing = sb.execute(text("""
                            SELECT id, status FROM bids
                            WHERE item_id = :iid AND bidder_id = :bidder
                        """), {"iid": str(item_row["id"]), "bidder": user["id"]}).mappings().first()

                        if existing:
                            if existing["status"] == "accepted":
                                st.success("Seller accepted your offer!")
                            else:
                                st.info("Your offer is already submitted. Waiting for seller to respond.")
                        else:
                            if st.button("Buy Now", type="primary", use_container_width=True):
                                sb.execute(text("""
                                    INSERT INTO bids (item_id, bidder_id, amount, status)
                                    VALUES (:iid, :bidder, :amt, 'not_accepted')
                                """), {
                                    "iid": str(item_row["id"]),
                                    "bidder": user["id"],
                                    "amt": float(item_row["price"])
                                })
                                sb.commit()
                                st.success("Offer submitted. Waiting for seller's response.")
                                st.rerun()
                    except Exception as e:
                        sb.rollback()
                        st.error(f"Error placing offer: {e}")
                    finally:
                        sb.close()


def render_my_listings():
    from uuid import UUID
    from sqlalchemy import text

    st.subheader("My Listings")

    user = st.session_state.user
    if not user:
        st.warning("Log in to view your listings.")
        return

    # filters for status
    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        status_display = ["All", "Active", "Closed"]
        status_internal = ["all", "active", "closed"]
        selected_display = st.selectbox("Status", status_display, index=0)
        status_filter = status_internal[status_display.index(selected_display)]
        #status_filter = st.selectbox("Status", ["all", "active", "closed"], index=0)
    with col_s2:
        page_size = st.selectbox("Page size", [5, 10, 15, 20], index=1)

    # maintain pagination state
    key_page = "my_listings_page"
    if key_page not in st.session_state:
        st.session_state[key_page] = 1

    where = ["i.seller_id = :sid"]
    params = {"sid": user["id"]}

    if status_filter != "all":
        if status_filter == "closed":
            where.append("i.status IN ('closed', 'sold')")
        else:
            where.append("i.status = :status")
            params["status"] = status_filter

    where_sql = " AND ".join(where)

    count_sql = text(f"""
        SELECT COUNT(*)
        FROM items i
        WHERE {where_sql}
    """)

    list_sql = text(f"""
        WITH base AS (
            SELECT i.id, i.title, i.price, i.status, i.listing_type, i.created_at,
                   COALESCE(c.name, 'Uncategorized') AS category
            FROM items i
            LEFT JOIN categories c ON c.id = i.category_id
            WHERE {where_sql}
            ORDER BY i.created_at DESC
        ),
        img AS (
            SELECT ii.item_id,
                   (SELECT image_path
                    FROM item_images iix
                    WHERE iix.item_id = ii.item_id
                    ORDER BY iix.is_primary DESC, iix.sort_order ASC, iix.created_at ASC
                    LIMIT 1) AS image_path
            FROM item_images ii
            GROUP BY ii.item_id
        ),
        hb AS (
            SELECT item_id, MAX(amount) AS highest_bid
            FROM bids
            GROUP BY item_id
        )
        SELECT b.id, b.title, b.price, b.status, b.listing_type, b.category, b.created_at,
               COALESCE(img.image_path, NULL) AS image_path,
               COALESCE(hb.highest_bid, 0) AS highest_bid
        FROM base b
        LEFT JOIN img ON img.item_id = b.id
        LEFT JOIN hb  ON hb.item_id  = b.id
        LIMIT :limit OFFSET :offset
    """)

    # run queries
    s = Session()
    try:
        total = s.execute(count_sql, params).scalar_one()
        import math
        total_pages = max(1, math.ceil(total / page_size))
        page = min(st.session_state[key_page], total_pages)
        offset = (page - 1) * page_size

        rows = s.execute(list_sql, {**params, "limit": page_size, "offset": offset}).mappings().all()
    finally:
        s.close()

    # pagination controls
    col_prev, col_stat, col_next = st.columns([0.3, 3, 0.3])
    with col_prev:
        if st.button("⬅️ Prev", use_container_width=True, disabled=page <= 1):
            st.session_state[key_page] = max(1, page - 1)
            st.rerun()
    with col_stat:
        st.write(f"Page {page} of {total_pages} • {total} listing(s)")
    with col_next:
        if st.button("Next ➡️", use_container_width=True, disabled=page >= total_pages):
            st.session_state[key_page] = min(total_pages, page + 1)
            st.rerun()

    st.divider()

    if not rows:
        st.info("You have no listings yet.")
        return

    # render cards
    upload_root = os.getenv("UPLOAD_DIR", "uploads")
    for r in rows:
        with st.container(border=True):
            c1, c2 = st.columns([1, 3])
            with c1:
                if r["image_path"]:
                    abs_path = os.path.join(upload_root, r["image_path"]).replace("\\", "/")
                    st.image(abs_path, use_container_width=True)
                else:
                    st.caption("No image")

            with c2:
                st.markdown(f"**{r['title']}**  —  ${float(r['price']):.2f}")
                st.caption(f"{r['category']} • {r['listing_type']} • status: {r['status']}")

                # bids preview
                with st.expander("View bids", expanded=False):
                    sb = Session()
                    try:
                        bid_rows = sb.execute(text("""
                            SELECT  b.id AS bid_id, b.amount, b.placed_at, u.email AS bidder, b.status
                            FROM bids b
                            JOIN users u ON u.id = b.bidder_id
                            WHERE b.item_id = :iid AND b.status != 'declined'
                            ORDER BY b.amount DESC, b.placed_at DESC
                        """), {"iid": str(r["id"])}).mappings().all()
                    finally:
                        sb.close()

                    if not bid_rows:
                        st.write("No bids yet.")
                    else:
                        for br in bid_rows[:20]:
                            st.write(f"- ${float(br['amount']):.2f} by {br['bidder']} at {br['placed_at']}")

                            if r["listing_type"] == "fixed" and r["status"] == "active":
                                if st.button("Accept this offer", key=f"accept_{br['bid_id']}"):
                                    sb2 = Session()
                                    try:
                                        # Mark this bid as accepted, others as not accepted
                                        sb2.execute(text("""
                                            UPDATE bids
                                            SET status = CASE
                                                WHEN bidder_id = (SELECT id FROM users WHERE email = :email) THEN 'accepted'
                                                ELSE 'not_accepted'
                                            END
                                            WHERE item_id = :iid
                                        """), {"iid": str(r["id"]), "email": br["bidder"]})

                                        # Update item status
                                        sb2.execute(text("""
                                            UPDATE items
                                            SET status = 'sold',
                                                chosen_bid_id = (
                                                    SELECT id FROM bids
                                                    WHERE item_id = :iid
                                                    AND bidder_id = (SELECT id FROM users WHERE email = :email)
                                                    LIMIT 1
                                                )
                                            WHERE id = :iid
                                        """), {"iid": str(r["id"]), "email": br["bidder"]})

                                        sb2.commit()
                                        st.success("Offer accepted. Item marked as sold.")
                                        st.rerun()
                                    except Exception as e:
                                        sb2.rollback()
                                        st.error(f"Failed to accept offer: {e}")

                            elif r["listing_type"] == "auction":

                                bidding_open = (r["status"] == "active")

                                if bidding_open:
                                    col1, col2 = st.columns(2)

                                    # ACCEPT BID
                                    with col1:
                                        if st.button("Accept", key=f"accept_auction_{br['bid_id']}"):
                                            sb2 = Session()
                                            try:
                                                # 1. Accept this bid
                                                sb2.execute(text("""
                                                    UPDATE bids
                                                    SET status = 'accepted'
                                                    WHERE id = :bid_id
                                                """), {"bid_id": str(br["bid_id"])})

                                                # 2. Decline all others
                                                sb2.execute(text("""
                                                    UPDATE bids
                                                    SET status = 'declined'
                                                    WHERE item_id = :iid AND id != :bid_id
                                                """), {"iid": str(r["id"]), "bid_id": str(br["bid_id"])})

                                                # 3. Update item
                                                sb2.execute(text("""
                                                    UPDATE items
                                                    SET status = 'sold',
                                                        chosen_bid_id = :bid_id
                                                    WHERE id = :iid
                                                """), {"iid": str(r["id"]), "bid_id": str(br["bid_id"])})

                                                sb2.commit()
                                                st.success("Bid accepted. Item marked as sold.")
                                                st.rerun()
                                            except Exception as e:
                                                sb2.rollback()
                                                st.error(f"Failed to accept bid: {e}")
                                            finally:
                                                sb2.close()

                                    # DECLINE BID
                                    with col2:
                                        if st.button("Decline", key=f"decline_auction_{br['bid_id']}"):
                                            sb2 = Session()
                                            try:
                                                sb2.execute(text("""
                                                    UPDATE bids
                                                    SET status = 'declined'
                                                    WHERE id = :bid_id
                                                """), {"bid_id": str(br["bid_id"])})

                                                sb2.commit()
                                                st.info("Bid declined.")
                                                st.rerun()
                                            except Exception as e:
                                                sb2.rollback()
                                                st.error(f"Failed to decline bid: {e}")
                                            finally:
                                                sb2.close()

                                else:
                                    st.caption("Bidding is closed for this item.")
                # actions
                colA, colB, colC = st.columns([1,1,3])
                with colA:
                    disable_close = (r["status"] != "active")
                    if st.button("Close listing", key=f"close_{r['id']}", disabled=disable_close, use_container_width=True):
                        sb = Session()
                        try:
                            sb.execute(text("UPDATE items SET status = 'closed' WHERE id = :iid"), {"iid": str(r["id"])})
                            sb.commit()
                            st.success("Listing closed.")
                            st.rerun()
                        except Exception as e:
                            sb.rollback()
                            st.error(f"Failed to close: {e}")
                        finally:
                            sb.close()


# ============================================================
# 🆕 FEATURE: View items the user has purchased
# ============================================================
def render_my_purchases():
    from sqlalchemy import text
    st.subheader("🛍️ My Purchases")

    user = st.session_state.user
    if not user:
        st.warning("Log in to view your purchases.")
        return

    s = Session()
    try:
        purchases = s.execute(text("""
            SELECT i.id, i.title, i.price, i.status,
                   u.email AS seller_email,
                   COALESCE(c.name, 'Uncategorized') AS category,
                   (SELECT image_path FROM item_images ii
                    WHERE ii.item_id = i.id
                    ORDER BY is_primary DESC, sort_order ASC
                    LIMIT 1) AS image_path
            FROM items i
            JOIN bids b ON b.id = i.chosen_bid_id
            JOIN users u ON u.id = i.seller_id
            LEFT JOIN categories c ON c.id = i.category_id
            WHERE b.bidder_id = :uid
            ORDER BY i.created_at DESC
        """), {"uid": user["id"]}).mappings().all()
    finally:
        s.close()

    if not purchases:
        st.info("You haven’t purchased any items yet.")
        return

    upload_root = os.getenv("UPLOAD_DIR", "uploads")
    for p in purchases:
        with st.container(border=True):
            c1, c2 = st.columns([1, 3])
            with c1:
                if p["image_path"]:
                    abs_path = os.path.join(upload_root, p["image_path"]).replace("\\", "/")
                    st.image(abs_path, use_container_width=True)
                else:
                    st.caption("No image")
            with c2:
                st.markdown(f"**{p['title']}** — ${float(p['price']):.2f}")
                st.caption(f"Category: {p['category']} • Seller: {p['seller_email']}")



# ============================================================
# 🆕 FEATURE: View items the user has bid on
# ============================================================
def render_my_bids():
    from sqlalchemy import text
    st.subheader("💸 My Bids")

    user = st.session_state.user
    if not user:
        st.warning("Log in to view your bids.")
        return

    s = Session()
    try:
        bid_rows = s.execute(text("""
            WITH my_bids AS (
                SELECT DISTINCT ON (b.item_id)
                    b.item_id, b.amount, b.placed_at,
                    b.status AS bid_status,
                    i.status, i.chosen_bid_id, i.title, i.price AS base_price,
                    (SELECT image_path FROM item_images ii
                     WHERE ii.item_id = i.id
                     ORDER BY is_primary DESC, sort_order ASC
                     LIMIT 1) AS image_path
                FROM bids b
                JOIN items i ON i.id = b.item_id
                WHERE b.bidder_id = :uid
                ORDER BY b.item_id, b.amount DESC, b.placed_at DESC
            )
            SELECT * FROM my_bids
            ORDER BY placed_at DESC
        """), {"uid": user["id"]}).mappings().all()
    finally:
        s.close()

    if not bid_rows:
        st.info("You haven’t placed any bids yet.")
        return

    upload_root = os.getenv("UPLOAD_DIR", "uploads")
    for b in bid_rows:
        # compute bid status dynamically (correct logic)
        item_status = b["status"]       # item-level status
        my_bid_status = b["bid_status"] # this specific user's bid status

        if item_status == "sold":
            if my_bid_status == "accepted":
                status_text = "✅ Seller accepted your offer"
            else:
                status_text = "❌ Seller accepted another buyer"

        elif item_status == "closed":
            status_text = "⚠️ Auction closed — no winning bid"

        elif item_status == "active":
            if my_bid_status == "accepted":
                status_text = "✅ Seller accepted your offer"
            elif my_bid_status == "declined":
                status_text = "❌ Seller did not accept your offer"
            else:
                status_text = "⏳ Awaiting seller response"

        else:
            status_text = "⏳ Waiting for seller"

        # # compute bid status dynamically
        # if b["status"] == "sold":
        #     if b["bid_status"] == "accepted":
        #         status_text = "✅ Seller accepted your offer"
        #     else:
        #         status_text = "❌ Seller accepted another buyer"



        # # if b["status"] == "sold" and b["chosen_bid_id"]:
        # #     s2 = Session()
        # #     try:
        # #         winner = s2.execute(text("SELECT bidder_id FROM bids WHERE id = :bid"),
        # #                             {"bid": str(b["chosen_bid_id"])}).scalar()
        # #         if winner == user["id"]:
        # #             status_text = "✅ Seller accepted your offer"
        # #         else:
        # #             status_text = "❌ Seller accepted another buyer"
        # #     finally:
        # #         s2.close()
        # elif b["status"] == "active":
        #     if b["status"] == "declined":
        #         status_text = "❌ Seller did not accept your offer"
        #     elif b["status"] == "accepted":
        #         status_text = "✅ Seller accepted your offer"
        #     else:
        #         status_text = "⏳ Awaiting seller response"

        with st.container(border=True):
            c1, c2 = st.columns([1, 3])
            with c1:
                if b["image_path"]:
                    abs_path = os.path.join(upload_root, b["image_path"]).replace("\\", "/")
                    st.image(abs_path, use_container_width=True)
                else:
                    st.caption("No image")
            with c2:
                st.markdown(f"**{b['title']}** — Your bid: ${float(b['amount']):.2f}")
                st.caption(status_text)
                #st.caption(f"Item status: {b['status']} • {status_text}")





# --- Gate the app ---
if st.session_state.user is None:
    # Signed-out view: ONLY show Login/Register (no sidebar nav)
    add_fullscreen_bg("app/Rutgersbg.jpg")
    render_logged_out()
else:
    # Signed-in view: full app with sidebar
    render_logged_in()
