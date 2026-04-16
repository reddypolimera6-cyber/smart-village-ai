"""
╔══════════════════════════════════════════════════════╗
║          SmartVillage AI - Complete App              ║
║   Authentication + Dashboard + Feature Modules       ║
╚══════════════════════════════════════════════════════╝

Run with:  streamlit run app.py
"""

import streamlit as st
import sqlite3
import hashlib
import os
import re
from datetime import datetime

# ─────────────────────────────────────────────
# 1. PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SmartVillage AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 2. GLOBAL CSS STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Nunito', sans-serif;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 50%, #f0fdf4 100%);
    background-attachment: fixed;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #14532d 0%, #166534 60%, #15803d 100%) !important;
}
section[data-testid="stSidebar"] * {
    color: #f0fdf4 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.15) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 12px !important;
    width: 100%;
    font-size: 15px;
    padding: 10px;
    margin-bottom: 6px;
    transition: all 0.2s;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.25) !important;
    transform: translateX(4px);
}

/* ── Primary buttons ── */
div.stButton > button {
    background: linear-gradient(135deg, #16a34a, #15803d) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    padding: 12px 28px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 14px rgba(22,163,74,0.35) !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(22,163,74,0.45) !important;
}

/* ── Input fields ── */
.stTextInput > div > div > input,
.stTextInput > div > div > input:focus {
    border-radius: 10px !important;
    border: 2px solid #bbf7d0 !important;
    font-size: 16px !important;
    padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #16a34a !important;
    box-shadow: 0 0 0 3px rgba(22,163,74,0.15) !important;
}

/* ── Cards ── */
.sv-card {
    background: white;
    border-radius: 20px;
    padding: 28px 24px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    border: 1px solid #dcfce7;
    margin-bottom: 16px;
    text-align: center;
    cursor: pointer;
}
.sv-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 32px rgba(0,0,0,0.12);
}
.sv-card .card-icon  { font-size: 48px; margin-bottom: 12px; }
.sv-card .card-title { font-size: 19px; font-weight: 800; color: #14532d; margin-bottom: 6px; }
.sv-card .card-desc  { font-size: 14px; color: #6b7280; line-height: 1.5; }

/* ── Auth panel ── */
.auth-panel {
    background: white;
    border-radius: 24px;
    padding: 40px 36px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.12);
    border: 1px solid #dcfce7;
    max-width: 440px;
    margin: 0 auto;
}
.auth-title {
    text-align: center;
    font-size: 28px;
    font-weight: 800;
    color: #14532d;
    margin-bottom: 4px;
}
.auth-sub {
    text-align: center;
    color: #6b7280;
    font-size: 15px;
    margin-bottom: 28px;
}
.brand-logo {
    text-align: center;
    font-size: 56px;
    margin-bottom: 8px;
}
.welcome-banner {
    background: linear-gradient(135deg, #16a34a, #059669);
    color: white;
    border-radius: 18px;
    padding: 22px 28px;
    margin-bottom: 28px;
    box-shadow: 0 6px 20px rgba(22,163,74,0.3);
}
.welcome-banner h2 { color: white; font-size: 24px; margin: 0 0 4px 0; }
.welcome-banner p  { color: rgba(255,255,255,0.85); margin: 0; font-size: 15px; }

/* ── Section headers ── */
.section-header {
    font-size: 20px;
    font-weight: 800;
    color: #14532d;
    margin: 28px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 3px solid #bbf7d0;
}
.password-hint { font-size: 13px; color: #9ca3af; margin-top: -8px; margin-bottom: 12px; }
.error-msg   { background: #fef2f2; border: 1px solid #fca5a5; border-radius: 10px; padding: 12px 16px; color: #dc2626; font-size: 14px; }
.success-msg { background: #f0fdf4; border: 1px solid #86efac; border-radius: 10px; padding: 12px 16px; color: #16a34a; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 3. DATABASE SETUP  (SQLite, single file)
# ─────────────────────────────────────────────
DB_PATH = "smartvillage_users.db"

def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    """Create the users table if it doesn't already exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            created  TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Return a SHA-256 hex digest of the password (+ salt prefix)."""
    salt = "smartvillage_salt_2024"          # simple static salt
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

def create_user(username: str, password: str) -> tuple[bool, str]:
    """
    Insert a new user.
    Returns (True, '') on success or (False, error_message) on failure.
    """
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO users (username, password, created) VALUES (?, ?, ?)",
            (username.strip().lower(), hash_password(password), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return True, ""
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another."
    except Exception as e:
        return False, f"Database error: {e}"

def verify_user(username: str, password: str) -> bool:
    """Return True if username + password match a stored record."""
    conn = get_connection()
    row = conn.execute(
        "SELECT password FROM users WHERE username = ?",
        (username.strip().lower(),)
    ).fetchone()
    conn.close()
    return row is not None and row[0] == hash_password(password)

# ─────────────────────────────────────────────
# 4. SESSION-STATE HELPERS
# ─────────────────────────────────────────────
def init_session():
    """Ensure all required session-state keys exist."""
    defaults = {
        "logged_in":      False,
        "username":       "",
        "active_page":    "dashboard",   # which dashboard tab is active
        "auth_tab":       "login",       # login | signup
        "chat_messages":  [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def login(username: str):
    """Mark the user as logged in."""
    st.session_state.logged_in  = True
    st.session_state.username   = username.strip().lower()
    st.session_state.active_page = "dashboard"

def logout():
    """Clear session and redirect to login."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session()

# ─────────────────────────────────────────────
# 5. PASSWORD VALIDATION
# ─────────────────────────────────────────────
def validate_password(pw: str) -> list[str]:
    """
    Returns a list of unmet requirements.
    Empty list = password is valid.
    """
    errors = []
    if len(pw) < 6:
        errors.append("At least 6 characters")
    if not re.search(r"[A-Z]", pw):
        errors.append("At least one uppercase letter")
    if not re.search(r"\d", pw):
        errors.append("At least one number")
    return errors

# ─────────────────────────────────────────────
# 6. AUTH PAGE  (Login / Sign Up)
# ─────────────────────────────────────────────
def render_auth():
    """Renders the full-screen authentication page."""
    # Centre the panel
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        # Brand header
        st.markdown('<div class="brand-logo">🌾</div>', unsafe_allow_html=True)
        st.markdown('<h1 style="text-align:center;color:#14532d;font-size:32px;font-weight:900;margin:0">SmartVillage AI</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;color:#6b7280;margin-bottom:28px">Empowering Farmers with Smart Technology</p>', unsafe_allow_html=True)

        # Tab switcher
        tab_login, tab_signup = st.tabs(["🔑  Login", "✨  Sign Up"])

        # ── LOGIN TAB ──────────────────────────────────
        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_user", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Login  →", key="btn_login", use_container_width=True):
                if not username or not password:
                    st.markdown('<div class="error-msg">⚠️ Please fill in both fields.</div>', unsafe_allow_html=True)
                elif verify_user(username, password):
                    login(username)
                    st.rerun()
                else:
                    st.markdown('<div class="error-msg">❌ Incorrect username or password. Please try again.</div>', unsafe_allow_html=True)

        # ── SIGN UP TAB ────────────────────────────────
        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            new_user = st.text_input("Choose a Username", key="reg_user", placeholder="e.g. ramu_farmer")
            new_pass = st.text_input("Create Password", type="password", key="reg_pass", placeholder="Min 6 chars, 1 uppercase, 1 number")
            st.markdown('<p class="password-hint">🔒 Min 6 characters · 1 uppercase · 1 number</p>', unsafe_allow_html=True)
            confirm  = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Re-enter password")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account  →", key="btn_signup", use_container_width=True):
                if not new_user or not new_pass or not confirm:
                    st.markdown('<div class="error-msg">⚠️ All fields are required.</div>', unsafe_allow_html=True)
                elif new_pass != confirm:
                    st.markdown('<div class="error-msg">❌ Passwords do not match.</div>', unsafe_allow_html=True)
                else:
                    pw_errors = validate_password(new_pass)
                    if pw_errors:
                        st.markdown(f'<div class="error-msg">❌ Password must have: {", ".join(pw_errors)}.</div>', unsafe_allow_html=True)
                    else:
                        ok, msg = create_user(new_user, new_pass)
                        if ok:
                            st.markdown('<div class="success-msg">✅ Account created! Please switch to Login.</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="error-msg">❌ {msg}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 7. SIDEBAR  (shown only when logged in)
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center;padding:20px 0 12px 0">
            <div style="font-size:48px">🌾</div>
            <div style="font-size:20px;font-weight:800;color:white">SmartVillage AI</div>
            <div style="font-size:13px;color:rgba(255,255,255,0.7);margin-top:4px">
                👤 {st.session_state.username}
            </div>
        </div>
        <hr style="border-color:rgba(255,255,255,0.2);margin:0 0 16px 0">
        """, unsafe_allow_html=True)

        # Navigation buttons
        nav_items = [
            ("🏠", "Dashboard",        "dashboard"),
            ("🌿", "Crop Advisory",    "crop"),
            ("🚜", "Equipment Booking","equipment"),
            ("🌦️", "Weather Info",     "weather"),
            ("💬", "Community Chat",   "chat"),
        ]
        for icon, label, page_key in nav_items:
            if st.button(f"{icon}  {label}", key=f"nav_{page_key}"):
                st.session_state.active_page = page_key
                st.rerun()

        st.markdown("<br>" * 4, unsafe_allow_html=True)
        st.markdown('<hr style="border-color:rgba(255,255,255,0.2)">', unsafe_allow_html=True)

        # Sign Out
        if st.button("🚪  Sign Out", key="btn_signout"):
            logout()
            st.rerun()

# ─────────────────────────────────────────────
# 8. DASHBOARD HOME
# ─────────────────────────────────────────────
def render_dashboard_home():
    # Welcome banner
    now = datetime.now()
    greeting = "Good Morning" if now.hour < 12 else ("Good Afternoon" if now.hour < 17 else "Good Evening")
    st.markdown(f"""
    <div class="welcome-banner">
        <h2>🌾 {greeting}, {st.session_state.username.capitalize()}!</h2>
        <p>Welcome back to SmartVillage AI — your smart farming companion.</p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    st.markdown('<div class="section-header">⚡ Quick Access</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    features = [
        ("🌿", "Crop Advisory",     "crop",      "Upload crop images and get instant AI-powered disease & care advice."),
        ("🚜", "Equipment Booking", "equipment", "Book tractors, sprayers and farming tools from your village network."),
        ("🌦️", "Weather Info",      "weather",   "Check today's forecast and plan your farming activities smartly."),
        ("💬", "Community Chat",    "chat",      "Talk to fellow farmers, share tips and ask questions anytime."),
    ]
    for col, (icon, title, page, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
            <div class="sv-card">
                <div class="card-icon">{icon}</div>
                <div class="card-title">{title}</div>
                <div class="card-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {title}", key=f"home_{page}"):
                st.session_state.active_page = page
                st.rerun()

    # Stats row
    st.markdown('<div class="section-header">📊 Today\'s Summary</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("🌡️ Temperature", "31 °C", "+2°C")
    with s2:
        st.metric("💧 Humidity", "68%", "-5%")
    with s3:
        st.metric("☁️ Weather", "Partly Cloudy", "")
    with s4:
        st.metric("📅 Today", now.strftime("%d %b %Y"), "")

# ─────────────────────────────────────────────
# 9. FEATURE PAGES
# ─────────────────────────────────────────────

# ── 9a. Crop Advisory ─────────────────────────
def render_crop_advisory():
    st.markdown('<h2 style="color:#14532d">🌿 AI Crop Advisory</h2>', unsafe_allow_html=True)
    st.markdown("Upload a photo of your crop and get instant analysis and care recommendations.")
    st.markdown("---")

    uploaded = st.file_uploader(
        "📸 Upload crop image (JPG / PNG)",
        type=["jpg", "jpeg", "png"],
        help="Take a clear photo of the affected leaves or the whole plant"
    )

    if uploaded:
        col1, col2 = st.columns([1, 1.4])
        with col1:
            st.image(uploaded, caption="Your uploaded crop image", use_container_width=True)
        with col2:
            with st.spinner("🔍 Analysing your crop..."):
                import time; time.sleep(1.5)   # simulates API call
            st.success("✅ Analysis Complete!")
            st.markdown("""
            **🌾 Detected Crop:** Tomato plant  
            **⚠️ Issue Detected:** Early Blight (*Alternaria solani*)

            **💊 Recommended Treatment:**
            - Remove and destroy infected leaves immediately
            - Apply **Mancozeb 75% WP** fungicide (2g per litre of water)
            - Spray every 7 days for 3 weeks
            - Ensure proper spacing for air circulation

            **🌱 Preventive Tips:**
            - Water at the base, avoid wetting leaves
            - Use certified disease-resistant seeds next season
            - Rotate crops yearly
            """)
            st.info("📞 Contact your local Krishi Vigyan Kendra (KVK) for further help.")
    else:
        st.markdown("""
        <div style="background:#f0fdf4;border:2px dashed #86efac;border-radius:16px;
                    padding:40px;text-align:center;color:#6b7280">
            📸 Upload a crop image above to get AI-powered advice
        </div>
        """, unsafe_allow_html=True)

# ── 9b. Equipment Booking ─────────────────────
def render_equipment_booking():
    st.markdown('<h2 style="color:#14532d">🚜 Equipment Booking</h2>', unsafe_allow_html=True)
    st.markdown("Book farming equipment available in your village.")
    st.markdown("---")

    equipment_list = [
        {"name": "Tractor (35 HP)",     "owner": "Ram Babu",    "rate": "₹800/day",  "available": True},
        {"name": "Power Sprayer",        "owner": "Suresh K.",   "rate": "₹200/day",  "available": True},
        {"name": "Seed Drill Machine",   "owner": "Lakshmi D.",  "rate": "₹600/day",  "available": False},
        {"name": "Rotavator",            "owner": "Venkat R.",   "rate": "₹700/day",  "available": True},
        {"name": "Paddy Thresher",       "owner": "Ramu G.",     "rate": "₹400/day",  "available": False},
    ]

    for eq in equipment_list:
        badge = "🟢 Available" if eq["available"] else "🔴 Booked"
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([2.5, 2, 1.5, 1.5, 1.5])
            c1.markdown(f"**{eq['name']}**")
            c2.markdown(f"👤 {eq['owner']}")
            c3.markdown(f"💰 {eq['rate']}")
            c4.markdown(badge)
            if eq["available"]:
                if c5.button("Book Now", key=f"book_{eq['name']}"):
                    st.success(f"✅ Booking request sent for **{eq['name']}**! The owner will contact you.")
            else:
                c5.markdown("—")
            st.markdown('<hr style="margin:6px 0;border-color:#e5e7eb">', unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("➕ List Your Own Equipment"):
        e_name  = st.text_input("Equipment Name")
        e_rate  = st.text_input("Daily Rate (₹)")
        e_phone = st.text_input("Your Contact Number")
        if st.button("Submit Listing"):
            if e_name and e_rate and e_phone:
                st.success(f"✅ '{e_name}' listed successfully! Others can now book it.")
            else:
                st.warning("Please fill all fields.")

# ── 9c. Weather Info ──────────────────────────
def render_weather():
    st.markdown('<h2 style="color:#14532d">🌦️ Weather Information</h2>', unsafe_allow_html=True)
    st.markdown("Local weather forecast to plan your farming activities.")
    st.markdown("---")

    location = st.text_input("📍 Enter your village / city name", value="Tirupati, Andhra Pradesh")
    if st.button("🔍 Get Weather"):
        with st.spinner("Fetching weather..."):
            import time; time.sleep(1)

        st.markdown(f"### 📍 Weather for: {location}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🌡️ Temperature", "31°C", "+2°C from yesterday")
        c2.metric("💧 Humidity",    "68%",  "-5%")
        c3.metric("💨 Wind Speed",  "14 km/h", "")
        c4.metric("🌧️ Rain Chance", "20%",  "")

        st.markdown("---")
        st.markdown("#### 📅 5-Day Forecast")
        forecast = [
            ("Today",     "⛅ Partly Cloudy", "31°C", "24°C"),
            ("Tomorrow",  "🌧️ Light Rain",    "28°C", "22°C"),
            ("Wednesday", "☀️ Sunny",          "33°C", "25°C"),
            ("Thursday",  "⛅ Overcast",       "29°C", "23°C"),
            ("Friday",    "🌦️ Showers",        "27°C", "21°C"),
        ]
        fc_cols = st.columns(5)
        for col, (day, condition, hi, lo) in zip(fc_cols, forecast):
            with col:
                st.markdown(f"""
                <div style="background:white;border-radius:14px;padding:16px 10px;
                            text-align:center;box-shadow:0 2px 10px rgba(0,0,0,0.08)">
                    <div style="font-weight:700;color:#14532d;font-size:14px">{day}</div>
                    <div style="font-size:28px;margin:8px 0">{condition.split()[0]}</div>
                    <div style="font-size:13px;color:#6b7280">{condition.split(' ',1)[1]}</div>
                    <div style="margin-top:8px;font-size:13px">
                        <span style="color:#ef4444">▲{hi}</span> &nbsp;
                        <span style="color:#3b82f6">▼{lo}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.info("🌾 **Farming Tip:** Light rain expected tomorrow — ideal day to apply basal fertiliser before sowing.")

# ── 9d. Community Chat ────────────────────────
def render_community_chat():
    st.markdown('<h2 style="color:#14532d">💬 Community Chat</h2>', unsafe_allow_html=True)
    st.markdown("Share knowledge, ask questions and connect with fellow farmers.")
    st.markdown("---")

    # Pre-populated demo messages
    if not st.session_state.chat_messages:
        st.session_state.chat_messages = [
            {"user": "ramu_farmer",  "msg": "Namaste everyone! Any tips for managing tomato blight?",          "time": "09:12"},
            {"user": "lakshmi_d",    "msg": "Use Mancozeb spray every week. Works great for me!",              "time": "09:18"},
            {"user": "suresh_k",     "msg": "Also try neem oil — it is natural and very effective.",           "time": "09:25"},
            {"user": "venkat_r",     "msg": "When is the best time to sow rabi crops this year?",             "time": "10:05"},
            {"user": "agri_advisor", "msg": "October 15–November 10 is ideal for rabi sowing in Andhra.",     "time": "10:30"},
        ]

    # Display messages
    chat_container = st.container()
    with chat_container:
        for m in st.session_state.chat_messages:
            is_me = m["user"] == st.session_state.username
            align = "flex-end" if is_me else "flex-start"
            bg    = "#16a34a" if is_me else "#f3f4f6"
            color = "white"   if is_me else "#111827"
            name_display = "You" if is_me else m["user"]
            st.markdown(f"""
            <div style="display:flex;justify-content:{align};margin-bottom:12px">
                <div style="max-width:65%;background:{bg};color:{color};border-radius:16px;
                            padding:12px 16px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
                    <div style="font-size:11px;opacity:0.75;margin-bottom:4px">
                        👤 {name_display} · {m['time']}
                    </div>
                    <div style="font-size:15px">{m['msg']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        new_msg = st.text_input("Type your message…", key="chat_input", label_visibility="collapsed")
    with col_btn:
        send = st.button("Send 📨")

    if send and new_msg.strip():
        st.session_state.chat_messages.append({
            "user": st.session_state.username,
            "msg":  new_msg.strip(),
            "time": datetime.now().strftime("%H:%M"),
        })
        st.rerun()

# ─────────────────────────────────────────────
# 10. MAIN ROUTER
# ─────────────────────────────────────────────
def main():
    init_db()
    init_session()

    if not st.session_state.logged_in:
        # Show auth page (no sidebar)
        render_auth()
    else:
        # Show sidebar navigation
        render_sidebar()

        # Route to the selected page
        page = st.session_state.active_page
        if page == "dashboard":
            render_dashboard_home()
        elif page == "crop":
            render_crop_advisory()
        elif page == "equipment":
            render_equipment_booking()
        elif page == "weather":
            render_weather()
        elif page == "chat":
            render_community_chat()

if __name__ == "__main__":
    main()
