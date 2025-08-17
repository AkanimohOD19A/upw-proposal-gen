import streamlit as st
import pyperclip
from utils.helpers import *


# Page configuration
st.set_page_config(
    page_title="Free Upwork Proposal Generator",
    page_icon="🆓",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #00875A;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .provider-card {
        background: linear-gradient(135deg, #f8fffe 0%, #f0fff4 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #14A800;
        margin: 1rem 0;
    }
    .free-badge {
        background: #14A800;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .char-counter {
        font-size: 0.8rem;
        color: #666;
        text-align: right;
    }
    .char-counter.warning { color: #ff6b35; font-weight: bold; }
    .char-counter.good { color: #14A800; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">🆓 Free Upwork Proposal Generator</h1>', unsafe_allow_html=True)
st.markdown("**Generate winning proposals using completely free LLM APIs - no quotas, no limits!**")

# Sidebar - LLM Provider Selection
with (st.sidebar):
    st.header("🤖 Choose Your FREE LLM")

    provider = st.selectbox(
        "Select LLM Provider",
        ["groq", "huggingface", "ollama"],
        help="All options are completely free!"
    )

    # Provider-specific configuration
    if provider == "groq":
        st.markdown('<div class="provider-card">', unsafe_allow_html=True)
        st.markdown('**🚀 Groq** <span class="free-badge">FREE</span>', unsafe_allow_html=True)
        st.markdown("• **Fastest** free option")
        st.markdown("• High-quality Mixtral model")
        st.markdown("• 6,000 requests/hour free")
        api_key = st.secrets["groq_api_key"]
        # st.text_input(
        #     "Groq API Key",
        #     type="password",
        #     help="Get free key at https://console.groq.com/"
        # )
        st.markdown("**Get your free key:** https://console.groq.com/", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    elif provider == "huggingface":
        st.markdown('<div class="provider-card">', unsafe_allow_html=True)
        st.markdown('**🤗 Hugging Face** <span class="free-badge">FREE</span>', unsafe_allow_html=True)
        st.markdown("• Completely free inference API")
        st.markdown("• Multiple model options")
        st.markdown("• No usage limits")
        hf_token = st.text_input(
            "HF Token",
            type="password",
            help="Get free token at https://huggingface.co/settings/tokens"
        )

        model_options = {
            "microsoft/DialoGPT-medium": "DialoGPT (Conversational)",
            "google/flan-t5-large": "FLAN-T5 (Instruction)",
            "EleutherAI/gpt-neo-2.7B": "GPT-Neo (General)",
            "facebook/blenderbot-400M-distill": "BlenderBot (Chat)"
        }

        selected_model = st.selectbox(
            "Model",
            list(model_options.keys()),
            format_func=lambda x: model_options[x]
        )
        st.markdown("**Get free token:** https://huggingface.co/settings/tokens")
        st.markdown('</div>', unsafe_allow_html=True)

    else:  # ollama
        st.markdown('<div class="provider-card">', unsafe_allow_html=True)
        st.markdown('**🦙 Ollama** <span class="free-badge">100% FREE</span>', unsafe_allow_html=True)
        st.markdown("• **Completely local** - total privacy")
        st.markdown("• No API keys needed")
        st.markdown("• Unlimited usage")
        st.markdown("• Requires local installation")

        ollama_url = st.text_input("Ollama URL", value="http://localhost:11434")

        model_options = ["llama2", "codellama", "mistral", "neural-chat", "starling-lm"]
        selected_model = st.selectbox("Model", model_options, index=0)

        st.markdown("**Setup Instructions:**")
        st.code("""
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download model
ollama pull llama2

# Start Ollama
ollama serve
        """, language="bash")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 Pro Tips")
    st.info("""
    **Best Options:**
    • **Groq**: Fastest, highest quality
    • **Ollama**: Most private, unlimited
    • **HuggingFace**: Most models, experimental
    """)

# Main content
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### 📋 Job Posting")

    jd_input = st.text_area(
        "Paste Upwork Job Description",
        height=300,
        placeholder="Paste the complete job posting here..."
    )

    if jd_input:
        char_count = len(jd_input)
        st.markdown(
            f'<div class="char-counter {"good" if char_count > 200 else "warning"}">Characters: {char_count}</div>',
            unsafe_allow_html=True)

with col2:
    st.markdown("### 📂 Your Background")

    sources = ""

    # URL input
    link = st.text_input("Portfolio/LinkedIn URL", placeholder="https://...")
    if link and link.startswith(('http://', 'https://')):
        with st.spinner("Extracting profile..."):
            url_content = extract_text_from_url(link)
            if not url_content.startswith("Error"):
                sources += url_content
                st.success(f"✅ Extracted ({len(url_content)} chars)")
            else:
                st.error(url_content)

    # PDF upload
    pdf = st.file_uploader("Upload Resume", type="pdf")
    if pdf:
        pdf_content = extract_text_from_pdf(pdf)
        if not pdf_content.startswith("Error"):
            sources += "\n\n" + pdf_content
            st.success(f"✅ Processed ({len(pdf_content)} chars)")
        else:
            st.error(pdf_content)

    # Manual input
    manual = st.text_area(
        "Technical Experience",
        height=150,
        placeholder="Add key achievements, technologies, metrics..."
    )
    if manual:
        sources += "\n\n" + manual

# Preview
if sources:
    with st.expander("📝 Background Preview"):
        preview = sources[:1000] + "..." if len(sources) > 1000 else sources
        st.text_area(
            "Generated Proposal",
            preview,
            height=400,
            help="Copy this directly into Upwork",
            label_visibility="hidden"
        )

# Generation
st.markdown("### 🚀 Generate Proposal")

# Validation
can_generate = True
errors = []

if not jd_input:
    errors.append("📌 Job description required")
    can_generate = False

if provider == "groq" and not api_key:
    errors.append("🔑 Groq API key required")
    can_generate = False
elif provider == "huggingface" and not hf_token:
    errors.append("🤗 Hugging Face token required")
    can_generate = False

for error in errors:
    st.error(error)

# Generate button
if st.button("🆓 Generate FREE Proposal", type="primary", disabled=not can_generate):
    if can_generate:
        with st.spinner(f"Generating proposal using {provider.title()}..."):
            try:
                # Create prompt
                prompt = create_upwork_prompt(jd_input, sources)

                # Generate based on provider
                if provider == "groq":
                    result = get_free_completion(prompt, "groq", api_key=api_key)
                elif provider == "huggingface":
                    result = get_free_completion(
                        prompt, "huggingface",
                        hf_token=hf_token,
                        model_name=selected_model
                    )
                else:  # ollama
                    result = get_free_completion(
                        prompt, "ollama",
                        model=selected_model,
                        ollama_url=ollama_url
                    )

                # Display results
                st.markdown("---")
                st.markdown("### 🎯 Generated Proposal")

                # Metrics
                word_count = len(result.split())
                char_count = len(result)

                col1, col2, col3 = st.columns(3)
                col1.metric("📝 Words", word_count)
                col2.metric("📊 Characters", f"{char_count}/5000")

                if char_count <= 5000:
                    col3.metric("✅ Status", "Perfect Length")
                else:
                    col3.metric("⚠️ Status", f"{char_count - 5000} over limit")

                # Proposal text
                st.text_area(
                    "Your proposal:",
                    result,
                    height=400,
                    help="Copy this directly into Upwork"
                )

                # Action buttons
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.download_button(
                        "💾 Download",
                        result,
                        file_name="upwork_proposal.txt",
                        use_container_width=True
                    )

                # with col2:
                #     if st.button("🔄 Generate Another", use_container_width=True):
                #         st.rerun()
                #
                # with col3:
                #     # Use a simple approach with instructions
                #     if st.button("📋 Select Text", use_container_width=True):
                #         pyperclip.copy(result)
                #         st.success('Text copied successfully!')
                    # st.button("📋 Copy Text", use_container_width=True,
                    #           help="Select all text above and Ctrl+C")

                # Analysis
                if char_count <= 5000:
                    st.success("✅ Ready to submit on Upwork!")
                else:
                    st.warning("⚠️ Please shorten before submitting")

            except Exception as e:
                st.error(f"❌ Generation failed: {str(e)}")

                # Provider-specific help
                if provider == "groq" and "unauthorized" in str(e).lower():
                    st.info("💡 Check your Groq API key at https://console.groq.com/")
                elif provider == "huggingface" and "401" in str(e):
                    st.info("💡 Check your HF token at https://huggingface.co/settings/tokens")
                elif provider == "ollama":
                    st.info("💡 Make sure Ollama is running: `ollama serve`")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <strong>🆓 Completely Free LLM Options</strong><br>
    <small>No quotas • No limits • No credit cards required</small>
</div>
""", unsafe_allow_html=True)