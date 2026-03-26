import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="MediStore",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",

)

# ─── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    [data-testid="stSidebar"] {
        background-color: #0f172a;
        padding-top: 1rem;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: transparent;
        border: none;
        text-align: left;
        padding: 10px 14px;
        border-radius: 8px;
        color: #cbd5e1;
        font-size: 14px;
        transition: background 0.2s;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #1e293b;
        color: #fff;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] span {
        color: #e2e8f0;
    }
    .active-report button {
        background: #1e293b !important;
        color: #fff !important;
        border-left: 3px solid #3b82f6 !important;
    }
    .upload-btn > button {
        background: #3b82f6 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        margin-bottom: 8px;
    }
    .chat-user {
        background: #eff6ff;
        border-radius: 12px 12px 4px 12px;
        padding: 12px 16px;
        margin: 8px 0 8px 60px;
        color: #1e3a5f;
        font-size: 15px;
    }
    .chat-bot {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px 12px 12px 4px;
        padding: 12px 16px;
        margin: 8px 60px 8px 0;
        color: #1e293b;
        font-size: 15px;
        line-height: 1.6;
    }
    .chat-label-user {
        text-align: right;
        font-size: 12px;
        color: #94a3b8;
        margin-bottom: 2px;
        margin-right: 4px;
    }
    .chat-label-bot {
        font-size: 12px;
        color: #94a3b8;
        margin-bottom: 2px;
        margin-left: 4px;
    }
    .summary-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
        color: #14532d;
        font-size: 15px;
        line-height: 1.7;
    }
    .main .block-container {
        padding-top: 2rem;
        max-width: 860px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Session State ──────────────────────────────────────────────
for key, default in {
    "token": None,
    "page": "login",
    "selected_file_id": None,
    "selected_file_name": None,
    "show_upload": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


# ═══════════════════════════════════════════════════════════════
# AUTH PAGE
# ═══════════════════════════════════════════════════════════════
def show_auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## 🏥 MediStore")
        st.markdown("##### AI-Powered Medical Report Analyzer")
        st.divider()

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login →", type="primary", key="btn_login", use_container_width=True):
                if email and password:
                    with st.spinner("Logging in..."):
                        res = requests.post(f"{BASE_URL}/login",
                                            json={"email": email, "password": password})
                    if res.status_code == 200:
                        st.session_state.token = res.json().get("access_token")
                        st.session_state.page = "main"
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Login failed"))
                else:
                    st.warning("Please fill all fields")

        with tab2:
            name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_pass = st.text_input("Password", type="password", key="reg_pass")
            if st.button("Create Account →", type="primary", key="btn_register", use_container_width=True):
                if name and reg_email and reg_pass:
                    with st.spinner("Creating account..."):
                        res = requests.post(f"{BASE_URL}/register",
                                            json={"name": name, "email": reg_email, "password": reg_pass})
                    if res.status_code == 200:
                        st.success("Account created! Please login.")
                    else:
                        st.error(res.json().get("detail", "Registration failed"))
                else:
                    st.warning("Please fill all fields")


# ═══════════════════════════════════════════════════════════════
# MAIN PAGE — Claude-style layout
# ═══════════════════════════════════════════════════════════════
def show_main_page():

    # ── SIDEBAR ──────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 🏥 MediStore")
        st.divider()

        st.markdown('<div class="upload-btn">', unsafe_allow_html=True)
        if st.button("➕  Upload New Report", use_container_width=True):
            st.session_state.show_upload = True
            st.session_state.selected_file_id = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<small style='color:#64748b'>MY REPORTS</small>", unsafe_allow_html=True)

        res = requests.get(f"{BASE_URL}/my/files", headers=auth_headers())
        files = res.json() if res.status_code == 200 else []

        if not files:
            st.markdown("<small style='color:#475569'>No reports yet</small>", unsafe_allow_html=True)
        else:
            for f in files:
                label = f.get("file_name", f"Report #{f['id']}")
                display = label[:28] + "..." if len(label) > 28 else label
                is_active = st.session_state.selected_file_id == f["id"]

                col_a, col_b = st.columns([5, 1])
                with col_a:
                    if is_active:
                        st.markdown('<div class="active-report">', unsafe_allow_html=True)
                    if st.button(f"📄 {display}", key=f"file_{f['id']}", use_container_width=True):
                        st.session_state.selected_file_id = f["id"]
                        st.session_state.selected_file_name = label
                        st.session_state.show_upload = False
                        st.rerun()
                    if is_active:
                        st.markdown('</div>', unsafe_allow_html=True)
                with col_b:
                    if st.button("🗑", key=f"del_{f['id']}"):
                        del_res = requests.delete(
                            f"{BASE_URL}/delete/files",
                            params={"file_id": f["id"]},
                            headers=auth_headers()
                        )
                        if del_res.status_code == 200:
                            if st.session_state.selected_file_id == f["id"]:
                                st.session_state.selected_file_id = None
                            st.rerun()

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.page = "login"
            st.rerun()

    # ── MAIN AREA ─────────────────────────────────────────────

    # 1. UPLOAD VIEW
    if st.session_state.show_upload:
        st.markdown("## Upload Medical Report")
        st.markdown("Upload a PDF and MediStore will analyze it instantly.")
        st.divider()

        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        if uploaded_file:
            st.info(f"📎 **{uploaded_file.name}** — {round(uploaded_file.size/1024, 1)} KB")
            if st.button("🔍 Analyze Report", type="primary"):
                with st.spinner("Analyzing report... ⏳ This may take a moment"):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    res = requests.post(
                        f"{BASE_URL}/summarize/document",
                        files=files,
                        headers=auth_headers()
                    )
                if res.status_code == 200:
                    data = res.json()
                    st.success("✅ Report analyzed!")
                    st.markdown("### Summary")
                    st.markdown(
                        f'<div class="summary-box">{data.get("summary", "Summary not available.")}</div>',
                        unsafe_allow_html=True
                    )
                    fid = data.get("file_id") or data.get("id")
                    if fid:
                        if st.button("💬 Start Asking Questions"):
                            st.session_state.selected_file_id = fid
                            st.session_state.selected_file_name = uploaded_file.name
                            st.session_state.show_upload = False
                            st.rerun()
                else:
                    st.error(res.json().get("detail", "Upload failed."))

    # 2. CHAT VIEW
    elif st.session_state.selected_file_id:
        file_id = st.session_state.selected_file_id
        file_name = st.session_state.selected_file_name or f"Report #{file_id}"

        st.markdown(f"## 📄 {file_name}")

        with st.expander("📋 View Report Summary", expanded=False):
            sum_res = requests.get(f"{BASE_URL}/files/{file_id}", headers=auth_headers())
            if sum_res.status_code == 200:
                summary = sum_res.json().get("summary", "No summary available.")
                st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
            else:
                st.warning("Could not load summary.")

        st.divider()
        st.markdown("### 💬 Ask about this report")

        # Load and display chat history
        hist_res = requests.get(f"{BASE_URL}/chat/history/{file_id}", headers=auth_headers())
        history = hist_res.json() if hist_res.status_code == 200 else []

        if not history:
            st.markdown(
                "<div style='color:#94a3b8; text-align:center; padding:40px 0'>Ask your first question below 👇</div>",
                unsafe_allow_html=True
            )
        else:
            for msg in history:
                q = msg.get("question") or (msg.get("content") if msg.get("role") == "user" else None)
                a = msg.get("answer") or (msg.get("content") if msg.get("role") == "assistant" else None)
                if q:
                    st.markdown('<div class="chat-label-user">You</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="chat-user">{q}</div>', unsafe_allow_html=True)
                if a:
                    st.markdown('<div class="chat-label-bot">🏥 MediStore</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="chat-bot">{a}</div>', unsafe_allow_html=True)

        # Question input
        st.divider()
        question = st.text_area(
            "question",
            placeholder="e.g. What is the patient's hemoglobin level? Any abnormal values?",
            height=80,
            label_visibility="collapsed"
        )
        if st.button("Send ➤", type="primary"):
            if question.strip():
                with st.spinner("Getting answer..."):
                    res = requests.post(
                        f"{BASE_URL}/ask/document",
                        json={"question": question, "file_id": file_id},
                        headers=auth_headers()
                    )
                if res.status_code == 200:
                    st.rerun()
                else:
                    st.error(res.json().get("detail", "Could not get answer."))
            else:
                st.warning("Please enter a question.")

    # 3. DEFAULT — nothing selected
    else:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='text-align:center; color:#94a3b8; padding: 80px 0'>
                <div style='font-size: 48px'>🏥</div>
                <div style='font-size: 22px; font-weight: 600; color:#1e293b; margin: 12px 0'>MediStore</div>
                <div style='font-size: 15px'>Select a report from the sidebar<br>or upload a new one to get started</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ═══════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════
if st.session_state.token is None:
    show_auth_page()
else:
    show_main_page()
