import streamlit as st
from utils.helpers import *

# Page configuration
st.set_page_config(
    page_title="Upwork Proposal Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #00875A;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .section-header {
        color: #14A800;
        border-bottom: 2px solid #108E00;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .metrics-container {
        background: linear-gradient(135deg, #f8fffe 0%, #f0fff4 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #14A800;
        margin: 1rem 0;
    }
    .tech-focus {
        background: #001e00;
        color: #14A800;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    .char-counter {
        font-size: 0.8rem;
        color: #666;
        text-align: right;
        margin-top: 0.25rem;
    }
    .char-counter.warning {
        color: #ff6b35;
        font-weight: bold;
    }
    .char-counter.good {
        color: #14A800;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">Proposal Generator</h1>', unsafe_allow_html=True)
st.markdown("**Generate technical, results-focused proposals that win high-value projects**")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Key input
    # api_key = st.text_input(
    #     "🔑 Cohere API Key",
    #     type="password",
    #     value=st.secrets.get('COHERE_API_KEY', ''),
    #     help="Get your API key from https://dashboard.cohere.ai/"
    # )

    api_key = st.secrets['api_key']

    st.markdown("---")
    st.markdown("### 🎯 Proposal Strategy")
    st.markdown("""
    **This generator creates proposals that:**
    - Lead with technical understanding
    - Include specific metrics and results
    - Demonstrate deep domain expertise
    - Stay under 5000 characters
    - Focus on solutions, not enthusiasm
    """)

    st.markdown("---")
    st.markdown("### 💡 Pro Tips")
    st.info("""
    **What makes proposals win:**
    • Address their specific technical challenges
    • Show concrete results from similar work
    • Use industry terminology correctly
    • Outline clear deliverables and approach
    • Ask intelligent follow-up questions
    """)

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<h3 class="section-header">📋 Job Posting Analysis</h3>', unsafe_allow_html=True)

    jd_input = st.text_area(
        "📌 Paste Complete Job Description *",
        height=300,
        placeholder="Paste the entire Upwork job posting here including:\n- Project description\n- Required skills\n- KPIs or success metrics\n- Technical requirements\n- Budget and timeline",
        help="Include ALL details - KPIs, technical requirements, success criteria"
    )

    if jd_input:
        char_count = len(jd_input)
        if char_count < 200:
            st.markdown(
                f'<div class="char-counter warning">⚠️ Characters: {char_count} (Add more detail for better analysis)</div>',
                unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="char-counter good">✅ Characters: {char_count} (Good detail level)</div>',
                        unsafe_allow_html=True)

with col2:
    st.markdown('<h3 class="section-header">📂 Your Technical Profile</h3>', unsafe_allow_html=True)

    sources = ""

    # URL input
    link = st.text_input(
        "🌐 Portfolio/LinkedIn URL",
        placeholder="https://your-portfolio.com or LinkedIn profile",
        help="Link to technical portfolio, GitHub, or LinkedIn"
    )

    if link and link.startswith(('http://', 'https://')):
        with st.spinner("Extracting technical profile..."):
            url_content = extract_text_from_url(link)
            if not url_content.startswith("Error"):
                sources += url_content
                st.success(f"✅ Profile extracted ({len(url_content)} characters)")
            else:
                st.error(url_content)
    elif link and not link.startswith(('http://', 'https://')):
        st.warning("⚠️ Please enter a valid URL")

    # PDF upload
    pdf = st.file_uploader(
        "📄 Upload Resume/Portfolio",
        type="pdf",
        help="Upload your technical resume or portfolio"
    )

    if pdf:
        with st.spinner("Processing technical background..."):
            pdf_content = extract_text_from_pdf(pdf)
            if not pdf_content.startswith("Error"):
                sources += "\n\n" + pdf_content
                st.success(f"✅ Resume processed ({len(pdf_content)} characters)")
            else:
                st.error(pdf_content)

    # Manual technical input
    manual = st.text_area(
        "⚙️ Key Technical Experience",
        height=150,
        placeholder="Add specific technical achievements:\n- Technologies used (Python, SQL, etc.)\n- Quantified results (improved efficiency by X%)\n- Similar project experience\n- Relevant certifications",
        help="Focus on technical skills and quantified results"
    )

    if manual:
        sources += "\n\n" + manual

# Technical preview
if sources:
    with st.expander("🔍 Technical Profile Preview", expanded=False):
        preview_text = sources[:1500] + "..." if len(sources) > 1500 else sources
        st.text_area("Your technical background:", preview_text, height=200, disabled=True)
        st.markdown(f'<div class="char-counter">Total characters: {len(sources)}</div>', unsafe_allow_html=True)

# Key insights extraction
if jd_input:
    st.markdown('<h3 class="section-header">🧠 Job Analysis Insights</h3>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # Simple keyword extraction for demo
    keywords = []
    tech_terms = ['Python', 'SQL', 'Excel', 'Tableau', 'Power BI', 'Analytics', 'Machine Learning', 'Dashboard', 'API',
                  'Database']
    for term in tech_terms:
        if term.lower() in jd_input.lower():
            keywords.append(term)

    with col1:
        if keywords:
            st.markdown("**🔧 Technologies Mentioned:**")
            for keyword in keywords[:5]:
                st.markdown(f'<div class="tech-focus">{keyword}</div>', unsafe_allow_html=True)

    with col2:
        # Look for metrics or KPIs
        metric_indicators = ['KPI', 'target', 'improve', 'increase', 'reduce', 'month', '%', 'metrics']
        has_metrics = any(indicator.lower() in jd_input.lower() for indicator in metric_indicators)
        st.markdown("**📊 Success Metrics:**")
        if has_metrics:
            st.success("✅ Specific KPIs found")
        else:
            st.warning("⚠️ No clear metrics identified")

    with col3:
        # Check project complexity
        complexity_indicators = ['complex', 'advanced', 'senior', 'lead', 'architect', 'scale']
        is_complex = any(indicator.lower() in jd_input.lower() for indicator in complexity_indicators)
        st.markdown("**⚡ Project Level:**")
        if is_complex:
            st.info("🎯 High-complexity project")
        else:
            st.info("📈 Standard complexity")

# Generation section
st.markdown('<h3 class="section-header">🚀 Generate Winning Proposal</h3>', unsafe_allow_html=True)

# Validation before generation
can_generate = True
warnings = []

if not api_key:
    warnings.append("🔑 API key required")
    can_generate = False
if not jd_input:
    warnings.append("📌 Job description required")
    can_generate = False
if not sources:
    warnings.append("📂 Technical background recommended for better results")

if warnings:
    for warning in warnings:
        st.warning(warning)

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    generate_button = st.button(
        "🎯 Generate Technical Proposal",
        use_container_width=True,
        type="primary",
        disabled=not can_generate
    )

# Generation logic
if generate_button and can_generate:
    with st.spinner("Analyzing job requirements and crafting technical proposal..."):
        try:
            # Create specialized prompt
            prompt = create_upwork_prompt(jd_input, sources)

            # Generate proposal
            result = get_upwork_proposal(api_key, prompt)

            # Calculate metrics
            word_count = len(result.split())
            char_count = len(result)

            # Display results
            st.markdown("---")
            st.markdown("### 🎯 Your Winning Proposal")

            # Metrics display
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("📝 Word Count", word_count)
            with col2:
                char_color = "green" if char_count <= 5000 else "red"
                st.metric("📊 Characters", f"{char_count}/5000",
                          delta=f"{char_count - 5000}" if char_count > 5000 else None)
            with col3:
                connects_est = max(1, min(6, word_count // 150))  # Rough estimate
                st.metric("💎 Est. Connects", connects_est)
            with col4:
                if char_count <= 5000 and word_count >= 100:
                    st.metric("✅ Quality Score", "Excellent")
                elif char_count <= 5000:
                    st.metric("⚠️ Quality Score", "Good")
                else:
                    st.metric("❌ Quality Score", "Too Long")

            # Proposal display
            st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
            proposal_text = st.text_area(
                "Your technical proposal:",
                result,
                height=400,
                help="Copy this directly into Upwork"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            # Character count warning
            if char_count > 5000:
                st.error(f"⚠️ Proposal is {char_count - 5000} characters over Upwork's limit. Consider shortening.")
            elif char_count > 4500:
                st.warning(f"⚠️ Getting close to limit. {5000 - char_count} characters remaining.")
            else:
                st.success(f"✅ Perfect length! {5000 - char_count} characters remaining.")

            # Action buttons
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.download_button(
                    "💾 Download Proposal",
                    result,
                    file_name=f"upwork_proposal_{hash(jd_input[:50]) % 10000}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with col2:
                if st.button("📋 Copy Instructions", use_container_width=True):
                    st.info("Select all text above, then Ctrl+C (or Cmd+C on Mac)")

            with col3:
                if st.button("🔄 Generate Variation", use_container_width=True):
                    st.rerun()

            with col4:
                if st.button("✏️ Refine Further", use_container_width=True):
                    st.info("Adjust your technical background above and regenerate")

            # Technical analysis of generated proposal
            st.markdown("---")
            st.markdown("### 📊 Proposal Analysis")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**🔧 Technical Terms Found:**")
                tech_in_proposal = [term for term in keywords if term.lower() in result.lower()]
                if tech_in_proposal:
                    for term in tech_in_proposal:
                        st.markdown(f"✅ {term}")
                else:
                    st.warning("Consider adding more technical terminology")

            with col2:
                st.markdown("**📈 Strength Indicators:**")
                strength_words = ['experience', 'improved', 'increased', 'reduced', 'built', 'implemented', 'achieved']
                strengths_found = sum(1 for word in strength_words if word.lower() in result.lower())

                if strengths_found >= 4:
                    st.success(f"✅ Strong evidence ({strengths_found}/7 indicators)")
                elif strengths_found >= 2:
                    st.info(f"✅ Good evidence ({strengths_found}/7 indicators)")
                else:
                    st.warning(f"⚠️ Could use more concrete examples ({strengths_found}/7)")

        except Exception as e:
            st.error(f"❌ Generation failed: {str(e)}")

            if "api key" in str(e).lower():
                st.info("💡 **Get a Cohere API key**: https://dashboard.cohere.ai/")
            elif "quota" in str(e).lower():
                st.info("💡 **Tip**: You may have hit your free tier limit. Check your Cohere dashboard.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <strong>🎯 Elite Upwork Proposal Generator</strong><br>
        <small>Focus on technical competence • Prove with metrics • Win with substance</small>
    </div>
    """,
    unsafe_allow_html=True
)