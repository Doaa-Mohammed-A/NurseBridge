import streamlit as st
import os
import json
import io
import re
from openai import OpenAI

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NurseBridge: The Clinical Compass",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── OpenAI Client ─────────────────────────────────────────────────────────────
client = OpenAI(
    api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY"),
    base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL"),
)

# ─── PWA Injection ─────────────────────────────────────────────────────────────
st.markdown("""
<link rel="manifest" href="/app/static/manifest.json">
<meta name="theme-color" content="#008080">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="NurseBridge">
<link rel="apple-touch-icon" href="/app/static/icon-192.png">
<script>
(function() {
    // Inject manifest into <head> for proper PWA support
    if (!document.querySelector('link[rel="manifest"]')) {
        var link = document.createElement('link');
        link.rel = 'manifest';
        link.href = '/app/static/manifest.json';
        document.head.appendChild(link);
    }
    // Set theme-color
    if (!document.querySelector('meta[name="theme-color"]')) {
        var meta = document.createElement('meta');
        meta.name = 'theme-color';
        meta.content = '#008080';
        document.head.appendChild(meta);
    }
    // Register service worker
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/app/static/sw.js')
                .then(function(reg) { console.log('SW registered:', reg.scope); })
                .catch(function(err) { console.log('SW registration failed:', err); });
        });
    }
})();
</script>
""", unsafe_allow_html=True)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #000080 0%, #003366 50%, #004080 100%);
        padding: 0;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: #B0C4DE !important;
        font-size: 13px;
        font-weight: 500;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #FFFFFF !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        padding: 10px 16px !important;
        border-radius: 8px !important;
        margin-bottom: 4px !important;
        transition: background 0.2s ease !important;
        text-transform: none !important;
        letter-spacing: normal !important;
        display: block !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: rgba(0, 128, 128, 0.3) !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        background: rgba(0, 128, 128, 0.5) !important;
        border-left: 3px solid #00FFFF !important;
    }

    /* Main background */
    .stApp {
        background-color: #F0F4F8;
    }
    .main .block-container {
        padding: 2rem 2.5rem 3rem 2.5rem;
        max-width: 1200px;
    }

    /* Card container */
    .card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 28px 32px;
        margin-bottom: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0, 0, 80, 0.06);
    }

    /* Page title */
    .page-title {
        font-size: 28px;
        font-weight: 700;
        color: #000080;
        margin-bottom: 6px;
        letter-spacing: -0.3px;
    }
    .page-subtitle {
        font-size: 15px;
        color: #64748B;
        margin-bottom: 28px;
        font-weight: 400;
    }

    /* Section headings */
    .section-heading {
        font-size: 18px;
        font-weight: 600;
        color: #000080;
        padding-bottom: 8px;
        border-bottom: 2px solid #008080;
        margin-bottom: 16px;
    }

    /* Care plan boxes */
    .assessment-box {
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 16px;
        border-left: 4px solid;
    }
    .physical-box {
        background: #EBF8FF;
        border-color: #0284C7;
    }
    .psychiatric-box {
        background: #F0FDF4;
        border-color: #16A34A;
    }
    .assessment-box-title {
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .physical-box-title { color: #0284C7; }
    .psychiatric-box-title { color: #16A34A; }

    /* Result cards */
    .result-section {
        background: #F8FAFF;
        border-radius: 10px;
        padding: 20px 24px;
        margin-bottom: 16px;
        border: 1px solid #E2E8F0;
    }
    .result-section-title {
        font-size: 14px;
        font-weight: 700;
        color: #000080;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 12px;
    }

    /* Answer feedback */
    .correct-answer {
        background: #DCFCE7;
        border: 1px solid #16A34A;
        border-radius: 8px;
        padding: 14px 18px;
        color: #15803D;
        font-weight: 600;
        margin-top: 12px;
    }
    .incorrect-answer {
        background: #FEE2E2;
        border: 1px solid #DC2626;
        border-radius: 8px;
        padding: 14px 18px;
        color: #B91C1C;
        font-weight: 600;
        margin-top: 12px;
    }
    .rationale-box {
        background: #FFFBEB;
        border: 1px solid #F59E0B;
        border-radius: 8px;
        padding: 14px 18px;
        margin-top: 10px;
        color: #92400E;
        font-size: 14px;
        line-height: 1.6;
    }

    /* Specialty badge */
    .specialty-badge {
        display: inline-block;
        background: linear-gradient(135deg, #008080, #000080);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 16px;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
        border: none !important;
        padding: 10px 22px !important;
        font-size: 14px !important;
    }

    /* Primary button */
    .stButton > button[kind="primary"], .stButton > button:not([kind]) {
        background: linear-gradient(135deg, #008080, #006666) !important;
        color: white !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 128, 128, 0.3) !important;
    }

    /* Text areas and inputs */
    .stTextArea textarea, .stTextInput input {
        border-radius: 8px !important;
        border: 1.5px solid #CBD5E1 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        transition: border-color 0.2s ease !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #008080 !important;
        box-shadow: 0 0 0 3px rgba(0, 128, 128, 0.1) !important;
    }

    /* Selectbox */
    .stSelectbox [data-baseweb="select"] {
        border-radius: 8px !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #008080 !important;
        border-radius: 10px !important;
        background: #F0FAFA !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #008080 !important;
    }

    /* Info/success/error */
    .stAlert {
        border-radius: 8px !important;
    }

    /* Divider */
    hr {
        border-color: #E2E8F0;
        margin: 20px 0;
    }

    /* Tab icons in sidebar */
    .nav-icon {
        margin-right: 8px;
        font-size: 16px;
    }

    /* Footer */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: rgba(0, 0, 128, 0.92);
        backdrop-filter: blur(4px);
        padding: 8px 20px;
        text-align: center;
        color: rgba(255,255,255,0.75);
        font-size: 11.5px;
        font-style: italic;
        z-index: 999;
        letter-spacing: 0.2px;
    }

    /* Ensure main content doesn't get hidden behind footer */
    .main .block-container {
        padding-bottom: 60px !important;
    }

    /* Sidebar logo area */
    .sidebar-header {
        background: rgba(0,0,0,0.2);
        padding: 24px 20px 20px 20px;
        margin-bottom: 16px;
        text-align: center;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .sidebar-logo {
        font-size: 36px;
        margin-bottom: 6px;
    }
    .sidebar-title {
        font-size: 17px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.2px;
    }
    .sidebar-tagline {
        font-size: 11px;
        color: rgba(255,255,255,0.6);
        margin-top: 2px;
        font-style: italic;
    }

    /* ── Fix 1: Arabic RTL support ── */
    .arabic-content {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Noto Naskh Arabic', 'Scheherazade New', 'Arial', sans-serif !important;
        line-height: 2.2 !important;
        unicode-bidi: embed;
    }
    .arabic-content strong { font-weight: 700; }
    .arabic-content em { font-style: italic; }
    .arabic-content li { text-align: right; list-style-position: inside; }
    .arabic-content ul, .arabic-content ol { padding-right: 16px; padding-left: 0; }
    /* Strip raw asterisks – handled by format_ai_content() in Python */
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ─────────────────────────────────────────────────────────
def init_session_state():
    defaults = {
        "care_plan_result": None,
        "care_plan_type": "Physiological / Physical Problem",   # Fix 4
        "doc_text": None,
        "doc_explanation": None,
        "quiz_question": None,
        "quiz_answer": None,
        "quiz_submitted": False,
        "quiz_correct": None,
        "quiz_rationale": None,
        "ward_advice": None,
        "nclex_question": None,
        "nclex_options": None,
        "nclex_answer_revealed": False,
        "nclex_correct": None,
        "nclex_rationale": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

# ─── Fix 1: Markdown → HTML formatter (handles bold, italic, lists) ────────────
def format_ai_content(text: str) -> str:
    """Convert markdown syntax to safe HTML for rendering inside custom divs."""
    import html as html_lib
    text = html_lib.escape(text)                                          # sanitise first
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)  # bold+italic
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)        # bold
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)                    # italic
    # numbered list items  "1. item"
    text = re.sub(
        r'(?m)^(\d+)\.\s+(.+)$',
        r'<li style="margin-bottom:5px;"><span style="font-weight:600;">\1.</span> \2</li>',
        text,
    )
    # bullet items  "- item" or "• item"
    text = re.sub(
        r'(?m)^[-•]\s+(.+)$',
        r'<li style="margin-bottom:5px;">\1</li>',
        text,
    )
    text = text.replace('\n\n', '<br><br>')
    text = text.replace('\n', '<br>')
    return text

# ─── Helper: AI Call ───────────────────────────────────────────────────────────
def ask_ai(prompt: str, system: str = None, max_tokens: int = 2000) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="gpt-5.2",
        messages=messages,
        max_completion_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()

# ─── Helper: Extract PDF text ──────────────────────────────────────────────────
def extract_text_from_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    file_type = uploaded_file.type
    if file_type == "text/plain":
        return uploaded_file.read().decode("utf-8", errors="ignore")
    elif file_type == "application/pdf":
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            return f"[Error reading PDF: {e}]"
    return ""

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-logo">🏥</div>
        <div class="sidebar-title">NurseBridge</div>
        <div class="sidebar-tagline">The Clinical Compass</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### NAVIGATE")
    tab = st.radio(
        "Navigate",
        [
            "📋 NANDA-I Care Plan Generator",
            "📚 Smart Tutor & Document Q&A",
            "🏨 Ward Survival Guide",
            "📝 Licensing Exam Prep (NCLEX)",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:12px; color:rgba(255,255,255,0.5); padding:0 4px; line-height:1.6;">
        <strong style="color:rgba(255,255,255,0.7);">Powered by</strong><br>
        OpenAI GPT-5.2<br><br>
        <strong style="color:rgba(255,255,255,0.7);">Version</strong><br>
        1.0.0 Clinical Edition
    </div>
    """, unsafe_allow_html=True)

# ─── TAB 1: NANDA-I Care Plan Generator ───────────────────────────────────────
if tab == "📋 NANDA-I Care Plan Generator":
    st.markdown('<div class="page-title">📋 NANDA-I Care Plan Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Generate a comprehensive, evidence-based nursing care plan from a medical diagnosis or clinical presentation.</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">Clinical Input</div>', unsafe_allow_html=True)

        # ── Fix 4: Problem type radio ──────────────────────────────────────────
        st.markdown("**Select the Type of Problem / Condition:**")
        problem_type = st.radio(
            "Problem Type",
            ["Physiological / Physical Problem", "Psychiatric / Mental Health Problem"],
            key="problem_type_radio",
            horizontal=True,
            label_visibility="collapsed",
        )
        st.session_state.care_plan_type = problem_type

        st.markdown("<br>", unsafe_allow_html=True)
        if problem_type == "Physiological / Physical Problem":
            diagnosis_placeholder = "e.g., Type 2 Diabetes Mellitus with non-healing foot wound, uncontrolled blood glucose, fatigue and polyuria for 3 weeks..."
        else:
            diagnosis_placeholder = "e.g., Major Depressive Disorder, patient reports persistent sadness, anhedonia, insomnia, and passive suicidal ideation..."

        diagnosis = st.text_area(
            "Medical Diagnosis / Symptoms / Clinical Presentation",
            placeholder=diagnosis_placeholder,
            height=120,
            key="diagnosis_input",
        )
        col_btn1, col_btn2, _ = st.columns([1, 1, 4])
        with col_btn1:
            generate_btn = st.button("🚀 Generate Care Plan", type="primary", use_container_width=True)
        with col_btn2:
            clear_btn = st.button("🗑 Clear", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if clear_btn:
        st.session_state.care_plan_result = None
        st.rerun()

    if generate_btn and diagnosis.strip():
        with st.spinner("Generating your NANDA-I care plan... This may take a moment."):
            system_msg = (
                "You are an expert clinical nursing educator specializing in NANDA-I nursing diagnoses, "
                "NOC outcomes, and NIC interventions. Generate rigorous, evidence-based nursing care plans "
                "that are immediately useful in clinical practice."
            )

            # ── Fix 4: Conditional assessment section based on problem type ──
            is_physical = (problem_type == "Physiological / Physical Problem")
            if is_physical:
                assessment_section = """## CARE PLAN ASSESSMENT: PHYSICAL HEALTH DATA
List all relevant physical/physiological assessment data (vitals, lab values, physical findings, ADL status, pain level, mobility, nutrition, elimination, respiratory, cardiovascular, skin, wounds, etc.). Use detailed bullet points."""
            else:
                assessment_section = """## CARE PLAN ASSESSMENT: PSYCHIATRIC & MENTAL HEALTH DATA
List all relevant psychological and psychiatric assessment data (mood, affect, cognition, thought content, insight, judgment, anxiety level, coping mechanisms, sleep pattern, spiritual needs, social support system, behavioral concerns, substance use history, risk assessment). Use detailed bullet points."""

            prompt = f"""
Generate a comprehensive NANDA-I nursing care plan for the following:

CONDITION TYPE: {problem_type}
CLINICAL PRESENTATION: {diagnosis}

Structure the care plan EXACTLY as follows (use these exact section headers):

## NANDA-I NURSING DIAGNOSIS
State the most appropriate NANDA-I nursing diagnosis (include domain, class, definition, related factors, and defining characteristics).

{assessment_section}

## GOALS (NOC - Nursing Outcomes Classification)
List 3–5 SMART, measurable short-term and long-term goals with expected timeframes and NOC labels.

## NURSING INTERVENTIONS (NIC - Nursing Interventions Classification)
List at least 6 prioritized nursing interventions with NIC labels and specific action steps.

## SCIENTIFIC RATIONALES
For each intervention listed above, provide a corresponding scientific rationale based on current evidence and pathophysiology. Number them to match interventions.

## EVALUATION CRITERIA
Describe how you will evaluate achievement of goals and when to escalate care.
"""
            result = ask_ai(prompt, system_msg, max_tokens=3000)
            st.session_state.care_plan_result = result

    elif generate_btn and not diagnosis.strip():
        st.warning("Please enter a medical diagnosis or clinical presentation.")

    # Display care plan
    if st.session_state.care_plan_result:
        plan = st.session_state.care_plan_result
        sections = plan.split("## ")

        # Parse and display each section
        parsed = {}
        for section in sections:
            if section.strip():
                lines = section.strip().split("\n", 1)
                title = lines[0].strip()
                content = lines[1].strip() if len(lines) > 1 else ""
                parsed[title] = content

        st.markdown("---")
        st.markdown('<div class="section-heading">📄 Generated Care Plan</div>', unsafe_allow_html=True)

        for title, content in parsed.items():
            formatted = format_ai_content(content)   # Fix 1: convert markdown → HTML
            if "PHYSICAL HEALTH DATA" in title.upper():
                st.markdown(f"""
                <div class="assessment-box physical-box">
                    <div class="assessment-box-title physical-box-title">🫀 {title}</div>
                    <div style="font-size:14px; line-height:1.8; color:#1E3A5F;">{formatted}</div>
                </div>
                """, unsafe_allow_html=True)
            elif "PSYCHIATRIC" in title.upper() or "MENTAL HEALTH" in title.upper():
                st.markdown(f"""
                <div class="assessment-box psychiatric-box">
                    <div class="assessment-box-title psychiatric-box-title">🧠 {title}</div>
                    <div style="font-size:14px; line-height:1.8; color:#14532D;">{formatted}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-section">
                    <div class="result-section-title">{title}</div>
                    <div style="font-size:14px; line-height:1.8; color:#334155;">{formatted}</div>
                </div>
                """, unsafe_allow_html=True)

        # Action buttons
        st.markdown("---")
        col_a, col_b, _ = st.columns([1.2, 1.2, 3])
        with col_a:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                try:
                    import pyperclip
                    pyperclip.copy(st.session_state.care_plan_result)
                    st.success("✅ Copied to clipboard!")
                except Exception:
                    st.info("📋 To copy: select all text above and use Ctrl+C / Cmd+C")

        with col_b:
            if st.button("📥 Download as PDF", use_container_width=True):
                try:
                    from fpdf import FPDF
                    pdf = FPDF()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.add_page()
                    pdf.set_font("Helvetica", "B", 16)
                    pdf.set_text_color(0, 0, 128)
                    pdf.cell(0, 10, "NurseBridge: NANDA-I Care Plan", ln=True, align="C")
                    pdf.set_font("Helvetica", "", 9)
                    pdf.set_text_color(100, 100, 100)
                    pdf.cell(0, 6, f"Diagnosis: {diagnosis[:80]}", ln=True, align="C")
                    pdf.ln(4)
                    pdf.set_font("Helvetica", "", 10)
                    pdf.set_text_color(30, 30, 30)
                    for line in st.session_state.care_plan_result.split("\n"):
                        clean_line = line.replace("## ", "").replace("**", "")
                        if clean_line.startswith("#"):
                            pdf.set_font("Helvetica", "B", 11)
                            pdf.set_text_color(0, 0, 128)
                            pdf.cell(0, 7, clean_line.replace("#", "").strip(), ln=True)
                            pdf.set_font("Helvetica", "", 10)
                            pdf.set_text_color(30, 30, 30)
                        elif clean_line.strip():
                            try:
                                pdf.multi_cell(0, 5, clean_line.encode('latin-1', 'replace').decode('latin-1'))
                            except Exception:
                                pdf.multi_cell(0, 5, clean_line[:200])
                        else:
                            pdf.ln(2)
                    pdf_bytes = bytes(pdf.output())
                    st.download_button(
                        label="⬇️ Click to Save PDF",
                        data=pdf_bytes,
                        file_name="NurseBridge_CarePlan.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"PDF generation error: {e}")

# ─── TAB 2: Smart Tutor ────────────────────────────────────────────────────────
elif tab == "📚 Smart Tutor & Document Q&A":
    st.markdown('<div class="page-title">📚 Interactive Smart Tutor</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Upload a nursing document for AI-powered explanation and interactive quizzes tailored to your content.</div>', unsafe_allow_html=True)

    # ── Fix 2: File upload card — always visible, no extra containers ───────────
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">📂 Document Upload</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload your nursing document (PDF or TXT)",
        type=["pdf", "txt"],
        help="Upload lecture notes, textbook chapters, clinical guidelines, or any nursing document.",
    )
    if uploaded_file:
        text = extract_text_from_file(uploaded_file)
        if text and not text.startswith("[Error"):
            st.session_state.doc_text = text
            st.session_state.doc_explanation = None   # reset explanation on new upload
            st.session_state.quiz_question = None
            st.success(f"✅ Document loaded: **{uploaded_file.name}** ({len(text):,} characters)")
        else:
            st.error(f"Could not extract text from the file. {text}")
            st.session_state.doc_text = None
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Fix 2: All output sections ONLY appear after a file is successfully loaded
    if not st.session_state.doc_text:
        st.info("📂 Please upload a document above to begin your interactive learning session.")
    else:
        # ── Explanation section ────────────────────────────────────────────────
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">🌐 Document Explanation</div>', unsafe_allow_html=True)
        col_lang, col_btn = st.columns([2, 1])
        with col_lang:
            language = st.selectbox(
                "Explanation Language",
                ["English", "Arabic"],
                key="explain_lang",
            )
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            explain_btn = st.button("🔍 Explain Document", type="primary", use_container_width=True)

        if explain_btn:
            with st.spinner("Analyzing and explaining your document..."):
                # Fix 1: tell the AI to avoid markdown bold symbols in Arabic
                if language == "Arabic":
                    lang_instruction = (
                        "Respond entirely in Arabic (العربية). "
                        "Do NOT use markdown symbols like ** or *. "
                        "Use plain text only. Format lists with Arabic numerals (١، ٢، ٣) or dashes."
                    )
                else:
                    lang_instruction = "Respond in English."
                doc_preview = st.session_state.doc_text[:4000]
                prompt = f"""
{lang_instruction}

You are an expert nursing educator. Analyze the following nursing document and provide:
1. A concise summary (3-4 sentences)
2. Key clinical concepts covered
3. Important nursing implications and takeaways
4. Any critical safety points or clinical pearls

Document content:
{doc_preview}
"""
                explanation = ask_ai(prompt, max_tokens=1500)
                st.session_state.doc_explanation = explanation

        # ── Fix 1: Arabic RTL rendering ────────────────────────────────────────
        if st.session_state.doc_explanation:
            is_arabic = (language == "Arabic")
            formatted_expl = format_ai_content(st.session_state.doc_explanation)
            rtl_class = "arabic-content" if is_arabic else ""
            st.markdown(f"""
            <div class="result-section" style="margin-top:16px;">
                <div class="result-section-title">📖 Document Explanation</div>
                <div class="{rtl_class}" style="font-size:14px; line-height:1.9; color:#334155;">
                    {formatted_expl}
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Quiz section ───────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">🎯 Interactive Quiz</div>', unsafe_allow_html=True)

        col_qtype, col_qbtn = st.columns([2, 1])
        with col_qtype:
            q_type = st.selectbox(
                "Question Type",
                ["MCQ (Multiple Choice)", "True / False", "Essay (Short Answer)"],
                key="quiz_q_type",
            )
        with col_qbtn:
            st.markdown("<br>", unsafe_allow_html=True)
            gen_quiz_btn = st.button("🎲 Generate Question", type="primary", use_container_width=True)

        if gen_quiz_btn:
            with st.spinner("Generating a question from your document..."):
                doc_preview = st.session_state.doc_text[:4000]
                q_map = {
                    "MCQ (Multiple Choice)": "multiple choice question with 4 options (A, B, C, D). Return JSON: {\"question\": \"...\", \"options\": {\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"}, \"correct\": \"A\", \"rationale\": \"...\"}",
                    "True / False": "true or false question. Return JSON: {\"question\": \"...\", \"correct\": \"True\", \"rationale\": \"...\"}",
                    "Essay (Short Answer)": "open-ended short answer question. Return JSON: {\"question\": \"...\", \"sample_answer\": \"...\", \"key_points\": [\"...\", \"...\", \"...\"]}",
                }
                prompt = f"""
Based STRICTLY on the following nursing document, generate ONE challenging {q_map[q_type]}.
The question must test clinical understanding and critical thinking, not just recall.
Only return the JSON, nothing else.

Document:
{doc_preview}
"""
                raw = ask_ai(prompt, max_tokens=800)
                raw = raw.strip()
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                raw = raw.strip()
                try:
                    quiz_data = json.loads(raw)
                    st.session_state.quiz_question = quiz_data
                    st.session_state.quiz_answer = None
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_correct = None
                    st.session_state.quiz_rationale = None
                except Exception:
                    st.session_state.quiz_question = {"question": raw, "type": "parse_error"}

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Display quiz question ──────────────────────────────────────────────
        if st.session_state.quiz_question and "question" in st.session_state.quiz_question:
            qdata = st.session_state.quiz_question

            st.markdown(f"""
            <div class="card">
                <div class="result-section-title">❓ Question</div>
                <div style="font-size:16px; font-weight:600; color:#1A202C; line-height:1.6; margin-bottom:16px;">
                    {qdata.get("question", "Question unavailable")}
                </div>
            """, unsafe_allow_html=True)

            if "options" in qdata:
                options = qdata["options"]
                option_list = [f"{k}: {v}" for k, v in options.items()]
                selected = st.radio(
                    "Select your answer:",
                    option_list,
                    key="mcq_radio",
                    index=None,
                )
                st.session_state.quiz_answer = selected
                submit_btn = st.button("✅ Submit Answer", type="primary")
                if submit_btn and selected:
                    correct_key = qdata.get("correct", "A")
                    selected_key = selected.split(":")[0].strip()
                    st.session_state.quiz_submitted = True
                    st.session_state.quiz_correct = (selected_key == correct_key)
                    st.session_state.quiz_rationale = qdata.get("rationale", "")

            elif "correct" in qdata and qdata["correct"] in ["True", "False"]:
                selected_tf = st.radio("Your answer:", ["True", "False"], key="tf_radio", index=None)
                st.session_state.quiz_answer = selected_tf
                submit_tf = st.button("✅ Submit Answer", type="primary")
                if submit_tf and selected_tf:
                    st.session_state.quiz_submitted = True
                    st.session_state.quiz_correct = (selected_tf == qdata.get("correct"))
                    st.session_state.quiz_rationale = qdata.get("rationale", "")

            elif "sample_answer" in qdata or "key_points" in qdata:
                st.text_area("Your answer:", height=100, key="essay_answer")
                if st.button("🔑 Reveal Sample Answer", type="primary"):
                    sample = format_ai_content(qdata.get("sample_answer", ""))
                    key_points = qdata.get("key_points", [])
                    kp_html = "".join(f"<li>{p}</li>" for p in key_points)
                    st.markdown(f"""
                    <div class="rationale-box">
                        <strong>📝 Sample Answer:</strong><br>{sample}
                        {"<br><br><strong>Key Points:</strong><ul>" + kp_html + "</ul>" if key_points else ""}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="color:#64748B; font-size:13px;">{qdata.get("question","")}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.quiz_submitted and st.session_state.quiz_correct is not None:
                if st.session_state.quiz_correct:
                    st.markdown('<div class="correct-answer">✅ Correct! Well done!</div>', unsafe_allow_html=True)
                else:
                    correct_opt = qdata.get("correct", "")
                    options = qdata.get("options", {})
                    correct_text = options.get(correct_opt, correct_opt)
                    st.markdown(f'<div class="incorrect-answer">❌ Incorrect. The correct answer is: <strong>{correct_opt}: {correct_text}</strong></div>', unsafe_allow_html=True)

                if st.session_state.quiz_rationale:
                    formatted_rat = format_ai_content(st.session_state.quiz_rationale)
                    st.markdown(f'<div class="rationale-box"><strong>🔬 Scientific Rationale:</strong><br><br>{formatted_rat}</div>', unsafe_allow_html=True)

# ─── TAB 3: Ward Survival Guide ────────────────────────────────────────────────
elif tab == "🏨 Ward Survival Guide":
    st.markdown('<div class="page-title">🏨 Ward Survival Guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Instant, practical step-by-step clinical guidance for real-world hospital floor situations faced by interns and new graduate nurses.</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">🚨 Clinical Scenario Input</div>', unsafe_allow_html=True)

        # Quick scenario examples
        st.markdown("**Quick Scenarios (click to use):**")
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        scenario_input = ""

        quick_scenarios = [
            "Infiltrated IV line in patient's forearm",
            "Patient suddenly becomes unresponsive",
            "Angry, verbally aggressive patient refusing medication",
            "Chest pain in post-op patient",
        ]

        for i, (col, scenario) in enumerate(zip([col_s1, col_s2, col_s3, col_s4], quick_scenarios)):
            with col:
                if st.button(f"💡 {scenario[:25]}...", key=f"quick_{i}", use_container_width=True):
                    st.session_state["ward_scenario_text"] = scenario

        st.markdown("---")
        scenario = st.text_area(
            "Describe your clinical scenario in detail:",
            value=st.session_state.get("ward_scenario_text", ""),
            placeholder="e.g., My patient's IV has infiltrated — the arm is swollen, cool, and the patient is complaining of pain. What do I do right now?",
            height=120,
            key="ward_scenario",
        )

        col_ward1, col_ward2, _ = st.columns([1, 1, 4])
        with col_ward1:
            ward_btn = st.button("⚡ Get Immediate Guidance", type="primary", use_container_width=True)
        with col_ward2:
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.ward_advice = None
                st.session_state["ward_scenario_text"] = ""
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    if ward_btn and scenario.strip():
        with st.spinner("Consulting the clinical compass..."):
            system_msg = (
                "You are an experienced senior nurse with 20+ years of clinical experience in a busy hospital. "
                "You provide clear, immediate, practical, step-by-step guidance to interns and new graduate nurses "
                "who are facing real-world clinical challenges. Be direct, prioritize patient safety, and explain "
                "the reasoning behind each action. Use a calm, supportive, mentor-like tone."
            )
            prompt = f"""
A new nurse/intern needs immediate help with this clinical situation:

{scenario}

Provide:
## IMMEDIATE ACTIONS (First 2 Minutes)
Step-by-step what to do RIGHT NOW. Number each step.

## CLINICAL ASSESSMENT
What to assess/check to understand the situation better.

## NURSING INTERVENTIONS
Specific nursing actions to take (in priority order).

## WHEN TO ESCALATE
Clear criteria for when to call the physician/rapid response. What to say (SBAR format briefly).

## DOCUMENTATION
Key things to document in the nursing notes.

## CLINICAL PEARLS
1-2 tips from experienced nurses that will help in this situation.

Keep advice practical, specific, and immediately actionable.
"""
            advice = ask_ai(prompt, system_msg, max_tokens=2000)
            st.session_state.ward_advice = advice

    elif ward_btn and not scenario.strip():
        st.warning("Please describe your clinical scenario.")

    if st.session_state.ward_advice:
        st.markdown("---")
        advice = st.session_state.ward_advice
        sections = advice.split("## ")

        section_icons = {
            "IMMEDIATE": "🚨",
            "ASSESSMENT": "🔍",
            "INTERVENTIONS": "💊",
            "ESCALATE": "📞",
            "DOCUMENTATION": "📝",
            "PEARLS": "💎",
        }

        for section in sections:
            if section.strip():
                lines = section.strip().split("\n", 1)
                title = lines[0].strip()
                content = lines[1].strip() if len(lines) > 1 else ""

                icon = "📋"
                for key, ico in section_icons.items():
                    if key in title.upper():
                        icon = ico
                        break

                bg_colors = {
                    "🚨": "#FFF5F5",
                    "🔍": "#EBF8FF",
                    "💊": "#F0FDF4",
                    "📞": "#FFFBEB",
                    "📝": "#F8F4FF",
                    "💎": "#F0FAFA",
                    "📋": "#F8FAFF",
                }
                border_colors = {
                    "🚨": "#FCA5A5",
                    "🔍": "#7DD3FC",
                    "💊": "#86EFAC",
                    "📞": "#FCD34D",
                    "📝": "#C4B5FD",
                    "💎": "#5EEAD4",
                    "📋": "#93C5FD",
                }

                bg = bg_colors.get(icon, "#F8FAFF")
                border = border_colors.get(icon, "#93C5FD")

                st.markdown(f"""
                <div style="background:{bg}; border-left:4px solid {border}; border-radius:10px; padding:20px 24px; margin-bottom:16px;">
                    <div style="font-size:14px; font-weight:700; color:#000080; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:10px;">{icon} {title}</div>
                    <div style="font-size:14px; line-height:1.75; color:#334155; white-space:pre-wrap;">{content}</div>
                </div>
                """, unsafe_allow_html=True)

# ─── TAB 4: Licensing Exam Prep ────────────────────────────────────────────────
elif tab == "📝 Licensing Exam Prep (NCLEX)":
    st.markdown('<div class="page-title">📝 Licensing Exam Prep — NCLEX Style</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Practice with rigorous, scenario-based NCLEX-style questions across all major nursing specialties. Master the clinical reasoning behind every answer.</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-heading">🎯 Select Your Specialty</div>', unsafe_allow_html=True)

        specialties = [
            "Medical-Surgical Nursing",
            "Pediatric Nursing",
            "Maternal & Obstetric Nursing",
            "Psychiatric & Mental Health Nursing",
            "Critical Care / ICU Nursing",
            "Emergency & Trauma Nursing",
            "Pharmacology & Drug Calculations",
            "Community & Public Health Nursing",
            "Gerontological Nursing",
            "Oncology Nursing",
            "Cardiac / Cardiovascular Nursing",
            "Respiratory / Pulmonary Nursing",
            "Neurological Nursing",
            "Renal / Nephrology Nursing",
            "Endocrine & Metabolic Nursing",
        ]

        col_spec, col_diff = st.columns([2, 1])
        with col_spec:
            specialty = st.selectbox("Nursing Specialty", specialties, key="nclex_specialty")
        with col_diff:
            difficulty = st.selectbox("Difficulty Level", ["NCLEX-RN Level", "NCLEX-PN Level", "Advanced Practice (Graduate)"], key="nclex_diff")

        col_gen, col_clr, _ = st.columns([1.2, 1, 3])
        with col_gen:
            nclex_btn = st.button("🎲 Generate NCLEX Question", type="primary", use_container_width=True)
        with col_clr:
            if st.button("🔄 New Question", use_container_width=True):
                st.session_state.nclex_question = None
                st.session_state.nclex_options = None
                st.session_state.nclex_answer_revealed = False
                st.session_state.nclex_correct = None
                st.session_state.nclex_rationale = None
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    if nclex_btn:
        with st.spinner(f"Generating a {difficulty} question on {specialty}..."):
            system_msg = (
                "You are an expert NCLEX question writer with 15+ years of experience creating "
                "challenging, scenario-based nursing examination questions following the NCSBN "
                "clinical judgment measurement model. Write questions that test higher-order "
                "thinking, prioritization, and clinical decision-making."
            )
            prompt = f"""
Create ONE challenging, scenario-based NCLEX-style MCQ for:
- Specialty: {specialty}
- Difficulty: {difficulty}

Requirements:
- Include a realistic clinical scenario (2-4 sentences)
- 4 answer choices (A, B, C, D) that are plausible but only ONE is clearly best
- Test clinical judgment and priority-setting, not just recall
- Include a distractor that tests common misconceptions

Return ONLY valid JSON in this exact format:
{{
    "scenario": "Clinical scenario here...",
    "question": "The stem question here?",
    "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
    }},
    "correct": "B",
    "rationale": "Detailed explanation of why B is correct, why others are wrong, and the scientific/clinical reasoning. Include relevant pathophysiology or pharmacology.",
    "nclex_category": "Safe and Effective Care Environment",
    "cognitive_level": "Application / Analysis"
}}
"""
            raw = ask_ai(prompt, system_msg, max_tokens=1200)
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()
            try:
                qdata = json.loads(raw)
                st.session_state.nclex_question = qdata
                st.session_state.nclex_options = qdata.get("options", {})
                st.session_state.nclex_answer_revealed = False
                st.session_state.nclex_correct = None
                st.session_state.nclex_rationale = None
            except Exception:
                st.session_state.nclex_question = {"error": raw}

    # Display NCLEX question
    if st.session_state.nclex_question:
        qdata = st.session_state.nclex_question

        if "error" in qdata:
            st.error(f"Could not parse question. Raw output: {qdata['error'][:500]}")
        else:
            # Metadata badges
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.markdown(f'<div class="specialty-badge">🏥 {specialty}</div>', unsafe_allow_html=True)
            with col_m2:
                st.markdown(f'<div class="specialty-badge" style="background:linear-gradient(135deg,#6B21A8,#4C1D95);">📊 {qdata.get("cognitive_level","Analysis")}</div>', unsafe_allow_html=True)
            with col_m3:
                st.markdown(f'<div class="specialty-badge" style="background:linear-gradient(135deg,#B45309,#92400E);">📋 {qdata.get("nclex_category","Clinical Judgment")}</div>', unsafe_allow_html=True)

            # Scenario
            st.markdown(f"""
            <div class="card" style="background:#EFF6FF; border:1px solid #BFDBFE;">
                <div class="result-section-title">🏥 Clinical Scenario</div>
                <div style="font-size:15px; line-height:1.75; color:#1E3A5F; font-style:italic;">
                    {qdata.get("scenario", "")}
                </div>
                <div style="font-size:16px; font-weight:600; color:#000080; margin-top:16px;">
                    ❓ {qdata.get("question", "")}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Answer options
            options = qdata.get("options", {})
            if options:
                selected_nclex = st.radio(
                    "Select the BEST answer:",
                    [f"{k}: {v}" for k, v in options.items()],
                    key="nclex_radio",
                    index=None,
                )

                col_submit, col_reveal, _ = st.columns([1.2, 1.2, 3])
                with col_submit:
                    if st.button("✅ Submit Answer", type="primary", key="nclex_submit"):
                        if selected_nclex:
                            correct_key = qdata.get("correct", "")
                            selected_key = selected_nclex.split(":")[0].strip()
                            st.session_state.nclex_correct = (selected_key == correct_key)
                            st.session_state.nclex_rationale = qdata.get("rationale", "")
                            st.session_state.nclex_answer_revealed = True
                        else:
                            st.warning("Please select an answer first.")

                with col_reveal:
                    if st.button("🔑 Reveal Answer", key="nclex_reveal"):
                        st.session_state.nclex_answer_revealed = True
                        st.session_state.nclex_correct = None
                        st.session_state.nclex_rationale = qdata.get("rationale", "")

            # Show result
            if st.session_state.nclex_answer_revealed:
                correct_key = qdata.get("correct", "")
                correct_text = options.get(correct_key, "")

                if st.session_state.nclex_correct is True:
                    st.markdown('<div class="correct-answer">✅ Excellent! You selected the correct answer!</div>', unsafe_allow_html=True)
                elif st.session_state.nclex_correct is False:
                    st.markdown(f'<div class="incorrect-answer">❌ Not the best choice. The correct answer is: <strong>{correct_key}: {correct_text}</strong></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="correct-answer" style="background:#EBF8FF; border-color:#3B82F6; color:#1E40AF;">🔑 Correct Answer: <strong>{correct_key}: {correct_text}</strong></div>', unsafe_allow_html=True)

                if st.session_state.nclex_rationale:
                    st.markdown(f"""
                    <div class="rationale-box">
                        <strong>🔬 Scientific Rationale & Clinical Reasoning:</strong><br><br>
                        {st.session_state.nclex_rationale}
                    </div>
                    """, unsafe_allow_html=True)

# ─── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    ⚕️ <strong>Disclaimer:</strong> This tool is designed for educational purposes and does not replace professional clinical judgment.
</div>
""", unsafe_allow_html=True)
