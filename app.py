import streamlit as st
import pandas as pd
import json
import bcrypt
import re
import requests
import io
from pathlib import Path

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="📚 Hafisu's Digital Library",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== BEAUTIFUL CUSTOM CSS ==========
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=yes">
    <style>
        /* Main background gradient */
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        /* Make main content area transparent to show gradient */
        .main .block-container {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(0px);
            border-radius: 30px;
            padding: 2rem 1.5rem !important;
            max-width: 1200px !important;
            margin: 1rem auto !important;
        }
        /* Custom card style for books */
        .book-card {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .book-card:hover {
            transform: translateY(-3px);
        }
        /* Buttons */
        .stButton > button {
            background: linear-gradient(90deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 30px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s;
        }
        .stButton > button:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        /* Headers */
        h1, h2, h3 {
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2d3748, #1a202c);
        }
        section[data-testid="stSidebar"] * {
            color: #f0f0f0;
        }
        /* Input fields */
        .stTextInput > div > div > input, .stTextArea > div > textarea {
            background-color: white;
            border-radius: 15px;
        }
        /* Expander header */
        .streamlit-expanderHeader {
            background-color: rgba(255,255,255,0.2);
            border-radius: 20px;
            color: white;
        }
        /* Footer */
        .footer {
            text-align: center;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255,255,255,0.3);
            color: rgba(255,255,255,0.8);
            font-size: 0.8rem;
        }
        .creator-badge {
            text-align: center;
            font-size: 1rem;
            font-weight: bold;
            color: gold;
            margin-bottom: 1rem;
        }
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255,255,255,0.2);
            border-radius: 20px 20px 0 0;
            color: white;
            font-weight: bold;
        }
        .stTabs [aria-selected="true"] {
            background-color: white;
            color: #667eea;
        }
    </style>
    <div class="creator-badge">✨ Created by <strong>Hafisu Mahamoud</strong> – University of Ghana, BSc Agriculture ✨</div>
""", unsafe_allow_html=True)

# ========== USER MANAGEMENT ==========
USER_FILE = Path("users.json")

def load_users():
    if USER_FILE.exists():
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed.encode())

def register_user(username, name, email, password):
    users = load_users()
    if username in users:
        return False, "Username already exists. Please choose another."
    users[username] = {
        "name": name,
        "email": email,
        "password": hash_password(password)
    }
    save_users(users)
    return True, "Registration successful! Please log in."

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False, "User not found. Please register first."
    if verify_password(password, users[username]["password"]):
        return True, users[username]["name"]
    return False, "Incorrect password."

# ========== SESSION STATE ==========
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# ========== LOGIN / REGISTRATION UI ==========
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>📚 Hafisu's Digital Library</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        with st.form("login_form"):
            login_user_input = st.text_input("Username", key="login_username")
            login_pass = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login")
            if submitted:
                ok, msg = login_user(login_user_input, login_pass)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.user_name = msg
                    st.rerun()
                else:
                    st.error(msg)

    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("Username", key="reg_username")
            new_name = st.text_input("Full name", key="reg_name")
            new_email = st.text_input("Email", key="reg_email")
            new_pass = st.text_input("Password", type="password", key="reg_password")
            confirm_pass = st.text_input("Confirm password", type="password", key="reg_confirm")
            submitted_reg = st.form_submit_button("Register")
            if submitted_reg:
                if not all([new_user, new_name, new_email, new_pass]):
                    st.error("All fields are required.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
                    st.error("Invalid email address.")
                else:
                    ok, msg = register_user(new_user, new_name, new_email, new_pass)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

# ========== MAIN LIBRARY (AFTER LOGIN) ==========
else:
    st.sidebar.image("https://img.icons8.com/fluency/96/books.png", width=80)
    st.sidebar.title("📚 Digital Library")
    st.sidebar.write(f"Welcome, **{st.session_state.user_name}**")
    if st.sidebar.button("🚪 Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.rerun()

    # 🔗 YOUR GOOGLE SHEETS CSV LINK (UPDATED)
    BOOKS_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSc1n79eu3nTL8bndupttgrNBKqIq0bh2sg5S-1KOzctS4tRrqqcDllDKDU9VWx8UxbYMTiyjKrvc22/pub?output=csv"

    @st.cache_data(ttl=600)
    def load_books():
        return pd.read_csv(BOOKS_CSV_URL)

    try:
        df = load_books()
    except Exception as e:
        st.error(f"Could not load books from Google Sheets. Please check your CSV link. Error: {e}")
        st.stop()

    st.markdown("<h1 style='text-align: center;'>📖 Your Digital Library</h1>", unsafe_allow_html=True)

    # Search & filter
    col1, col2 = st.columns([3,1])
    with col1:
        search = st.text_input("🔍 Search by title, author, or course", key="search_input")
    with col2:
        categories = ["All"] + list(df['Category'].unique())
        cat = st.selectbox("📂 Filter by category", categories, key="category_filter")

    filtered = df.copy()
    if search:
        filtered = filtered[
            filtered['Title'].str.contains(search, case=False) |
            filtered['Author'].str.contains(search, case=False) |
            filtered['Course'].str.contains(search, case=False)
        ]
    if cat != "All":
        filtered = filtered[filtered['Category'] == cat]

    st.subheader(f"📚 Available Books ({len(filtered)})")

    # Display each book as a card
    for idx, row in filtered.iterrows():
        with st.container():
            colA, colB = st.columns([4,1])
            with colA:
                st.markdown(f"<div class='book-card'><strong>{row['Title']}</strong><br><em>{row['Author']}</em><br>{row['Course']}</div>", unsafe_allow_html=True)
            with colB:
                if st.button("📖 Read", key=f"read_btn_{idx}"):
                    st.session_state['current_book_link'] = row['File_Link']
                    st.session_state['current_book_title'] = row['Title']
            st.markdown("<hr>", unsafe_allow_html=True)

    # Embedded reader
    if 'current_book_link' in st.session_state and st.session_state['current_book_link']:
        st.markdown(f"### Now Reading: {st.session_state['current_book_title']}")
        st.components.v1.html(st.session_state['current_book_link'], height=650, scrolling=True, key="reader_component")

    # ========== AUTO-FETCH BOOKS SECTION ==========
    with st.sidebar.expander("📚 Auto‑Fetch Books (Librarian Tool)", expanded=False):
        st.markdown("### Fetch free books from Project Gutenberg")
        subjects = {
            "Basic Sciences": "science",
            "Applied Sciences": "technology",
            "Mathematics": "mathematics",
            "Economics": "economics",
            "Geography": "geography",
            "Political Science": "political-science",
            "Computing": "computers",
            "Agriculture": "agriculture",
            "Biology": "biology",
            "Chemistry": "chemistry",
            "Physics": "physics"
        }
        selected = st.multiselect("Choose subjects", list(subjects.keys()), default=["Basic Sciences", "Mathematics"], key="fetch_subjects")
        num_books = st.slider("Number of books", 5, 100, 20, key="fetch_num")
        if st.button("🔍 Fetch Books from Gutenberg", key="fetch_btn"):
            topics = [subjects[s] for s in selected]
            topic_param = "&".join([f"topic={t}" for t in topics])
            url = f"https://gutendex.com/books?{topic_param}&limit={num_books}"
            with st.spinner(f"Fetching up to {num_books} books..."):
                try:
                    response = requests.get(url)
                    data = response.json()
                    books = data.get("results", [])
                    if not books:
                        st.warning("No books found for these topics.")
                    else:
                        fetched_books = []
                        for book in books:
                            authors = ", ".join([a["name"] for a in book.get("authors", [])]) if book.get("authors") else "Unknown"
                            formats = book.get("formats", {})
                            file_link = formats.get("text/plain; charset=utf-8") or formats.get("text/html") or formats.get("application/pdf") or ""
                            if not file_link:
                                continue
                            fetched_books.append({
                                "ID": f"G{book['id']}",
                                "Title": book["title"],
                                "Author": authors,
                                "Category": ", ".join(selected),
                                "Course": "Multiple",
                                "File_Link": file_link
                            })
                        if fetched_books:
                            df_fetched = pd.DataFrame(fetched_books)
                            st.success(f"✅ Fetched {len(fetched_books)} books")
                            st.dataframe(df_fetched[['Title', 'Author', 'Category']])
                            csv_buffer = io.StringIO()
                            df_fetched.to_csv(csv_buffer, index=False)
                            st.download_button(
                                label="📥 Download CSV to Import",
                                data=csv_buffer.getvalue(),
                                file_name="fetched_books.csv",
                                mime="text/csv",
                                key="download_csv_btn"
                            )
                            st.info("""
                                **How to import:**
                                1. Open your Google Sheet
                                2. Click **File → Import → Upload**
                                3. Select the CSV file
                                4. Choose **Append to current sheet**
                                5. Click **Import** – books will appear in your library
                            """)
                        else:
                            st.warning("No books with readable formats found.")
                except Exception as e:
                    st.error(f"Error fetching books: {e}")

    # Footer
    st.markdown("---")
    st.markdown("<div class='footer'>📢 This library is maintained by Hafisu Mahamoud – University of Ghana, BSc Agriculture – always free, always open.</div>", unsafe_allow_html=True)