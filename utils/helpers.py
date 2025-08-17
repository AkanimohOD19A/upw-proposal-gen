import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import json
import time
import random

def extract_text_from_url(url):
    """Extract text content from a URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        page = requests.get(url, headers=headers, timeout=10)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text()
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text[:8000]
    except Exception as e:
        return f"Error extracting URL content: {str(e)}"


def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file."""
    try:
        reader = PdfReader(uploaded_file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text[:8000]
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def get_huggingface_completion(hf_token, prompt, model_name="microsoft/DialoGPT-medium"):
    """Generate completion using Hugging Face Inference API (FREE!)"""
    try:
        # Free Hugging Face models - no quota limits!
        API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
        headers = {"Authorization": f"Bearer {hf_token}"}

        # Random temperature for variety
        temp = round(random.uniform(0.7, 0.9), 2)

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 1200,
                "temperature": temp,
                "do_sample": True,
                "top_p": round(random.uniform(0.85, 0.95), 2)
            }
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 503:
            # Model is loading, wait and retry
            time.sleep(20)
            response = requests.post(API_URL, headers=headers, json=payload)

        response.raise_for_status()
        result = response.json()

        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '').replace(prompt, '').strip()
        else:
            return result.get('generated_text', '').replace(prompt, '').strip()

    except Exception as e:
        raise Exception(f"Hugging Face API error: {str(e)}")


def get_groq_completion(api_key, prompt):
    """Generate completion using Groq (FREE tier - very fast!)"""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Enhanced system message for personable, conversational proposals
        system_content = """You are a seasoned freelancer and Upwork proposal expert who writes in a natural, conversational tone. Your proposals feel like they're written by a real person who genuinely understands the client's pain points.

Key characteristics of your writing:
• CONVERSATIONAL: Write like you're talking to a friend, not giving a corporate presentation
• PERSONAL: Share relevant experiences naturally, like telling a story
• CONFIDENT but HUMBLE: Show expertise without being boastful
• RELATABLE: Use phrases like "I've been there," "I totally get it," "Here's what I'd do"
• SPECIFIC: Include concrete details and metrics that prove your experience
• HUMAN: Vary sentence length, use contractions, show personality

AVOID at all costs:
❌ "I am excited to work on your project"
❌ "I believe I am the perfect fit"
❌ "I have extensive experience"
❌ Corporate buzzwords and formal language
❌ Generic enthusiasm without substance
❌ Bullet points everywhere

INSTEAD use natural language:
✅ "I've tackled this exact challenge before..."
✅ "Here's how I'd approach your situation..."
✅ "I totally understand the pressure you're under..."
✅ "Let me share what worked for a similar client..."

Structure: Problem acknowledgment → Personal connection → Specific solution → Relevant story/example → Clear next steps

Write proposals that make clients think: "This person really gets it and has been in my shoes."
"""

        # Random temperature for more variety in responses
        temp = round(random.uniform(0.75, 0.95), 2)

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user",
                    "content": prompt[:4000]
                }
            ],
            "model": "llama3-70b-8192",
            "temperature": temp,  # Randomized temperature
            "max_tokens": 1200,
            "top_p": round(random.uniform(0.85, 0.95), 2),  # Randomized top_p
            "stream": False
        }

        response = requests.post(url, headers=headers, json=payload, timeout=45)

        if response.status_code != 200:
            print(f"Response Text: {response.text}")

        if response.status_code == 400:
            # Fallback to smaller model if needed
            payload["model"] = "mixtral-8x7b-32768"
            payload["max_tokens"] = 900
            response = requests.post(url, headers=headers, json=payload, timeout=30)

        response.raise_for_status()

        try:
            result = response.json()
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response from Groq: {response.text[:500]}")

        # Better error handling for response structure
        if not isinstance(result, dict):
            raise Exception(f"Unexpected response type: {type(result)}")

        if 'error' in result:
            error_msg = result.get('error', {})
            if isinstance(error_msg, dict):
                raise Exception(f"Groq API error: {error_msg.get('message', 'Unknown error')}")
            else:
                raise Exception(f"Groq API error: {error_msg}")

        if 'choices' not in result or not result['choices']:
            raise Exception(f"No valid response from Groq API")

        content = result['choices'][0]['message']['content']
        if content is None:
            raise Exception("Empty response from Groq API")

        return content.strip()

    except Exception as e:
        if "object is not subscriptable" in str(e):
            raise Exception(
                f"Groq API returned unexpected format. This might be due to rate limits or API changes. Try again in a moment.")
        raise Exception(f"Groq API error: {str(e)}")


def get_ollama_completion(prompt, model="llama2", ollama_url="http://localhost:11434"):
    """Generate completion using local Ollama (100% FREE!)"""
    try:
        url = f"{ollama_url}/api/generate"

        # Random temperature for variety
        temp = round(random.uniform(0.7, 0.9), 2)

        payload = {
            "model": model,
            "prompt": f"""You are a freelancer writing a personal, conversational Upwork proposal. Write like a real person who understands the client's challenges and has relevant experience to share.

Key requirements:
- Sound natural and conversational (use contractions, vary sentence length)
- Share relevant experiences like you're telling a story
- Show genuine understanding of their specific challenge
- Include concrete metrics and results from past work
- Be confident but relatable, not boastful
- End with a thoughtful question or clear next step

{prompt}

Write a winning, personable proposal:""",
            "stream": False,
            "options": {
                "temperature": temp,
                "top_p": round(random.uniform(0.85, 0.95), 2),
                "num_predict": 1000
            }
        }

        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()

        result = response.json()
        return result.get('response', '').strip()

    except Exception as e:
        raise Exception(f"Ollama error: {str(e)} - Make sure Ollama is running locally")


def get_free_completion(prompt, provider="groq", **kwargs):
    """Unified interface for all free LLM providers"""

    if provider == "huggingface":
        hf_token = kwargs.get('hf_token')
        model_name = kwargs.get('model_name', 'microsoft/DialoGPT-medium')
        return get_huggingface_completion(hf_token, prompt, model_name)

    elif provider == "groq":
        api_key = kwargs.get('api_key')
        return get_groq_completion(api_key, prompt)

    elif provider == "ollama":
        model = kwargs.get('model', 'llama2')
        ollama_url = kwargs.get('ollama_url', 'http://localhost:11434')
        return get_ollama_completion(prompt, model, ollama_url)

    else:
        raise Exception(f"Unknown provider: {provider}")


def create_upwork_prompt(job_description, supporting_content):
    """Create optimized prompt for natural, conversational Upwork proposals with substantial depth"""

    # Limit content to avoid token issues
    jd_preview = job_description[:2500] if job_description else "No job description provided"
    content_preview = supporting_content[:2500] if supporting_content else "No supporting content provided"

    # Random conversation starters for variety
    openings = [
        "I've been in your shoes before - tight deadlines and high stakes are par for the course in data analysis.",
        "Same-day case studies? That's exactly the kind of challenge I live for.",
        "I totally get it - when you need insights fast, there's no room for error or delays.",
        "Urgent data analysis with same-day delivery? I've built my reputation on exactly these situations.",
        "I understand the pressure you're under - critical decisions waiting on data analysis."
    ]

    # Random methodology elements for variety
    methodologies = [
        "rapid data profiling and quality assessment, followed by exploratory analysis to identify key patterns",
        "parallel processing streams - cleaning data while simultaneously running preliminary analysis",
        "iterative validation approach with checkpoints every 2 hours to ensure we're on track",
        "hypothesis-driven analysis combined with open exploration to catch unexpected insights",
        "agile analytics methodology with frequent stakeholder check-ins for course correction"
    ]

    # Random value propositions
    value_props = [
        "My banking background means I understand the regulatory and business context that drives urgent analytics needs",
        "I've briefed C-level executives at major financial institutions, so I know how to translate complex data into boardroom-ready insights",
        "My fintech experience taught me that in fast-moving markets, being 80% right today beats being 100% right tomorrow",
        "I've worked in environments where data delays can cost millions, so I've developed systems for quality under extreme pressure",
        "My compliance background means I naturally build in validation and documentation even when time is tight"
    ]

    chosen_opening = random.choice(openings)
    chosen_methodology = random.choice(methodologies)
    chosen_value_prop = random.choice(value_props)

    prompt = f"""Write a comprehensive, natural, conversational Upwork proposal that demonstrates deep expertise while sounding genuinely human. This needs to be substantial and detailed.

**JOB POSTING:**
{jd_preview}

**MY BACKGROUND:**
{content_preview}

**WRITING STYLE REQUIREMENTS:**
- Start with: "{chosen_opening}"
- Write conversationally - use contractions, vary sentence length, sound human
- Share experiences like you're telling stories to a colleague over coffee
- Show you understand their specific pain points without being generic
- Include concrete numbers/results woven naturally into stories
- Use phrases like "Here's exactly what I'd do," "In my experience," "I've found that," "What I'd recommend"
- Avoid corporate speak and excessive bullet points
- Be confident but relatable, not boastful
- End with a thoughtful, specific question about their situation

**COMPREHENSIVE CONTENT STRUCTURE (Include ALL of these):**

1. **Personal Connection (2-3 sentences)**
   - Start with the chosen opening
   - Show immediate understanding of their specific challenge

2. **Relevant Experience Story (4-5 sentences)**
   - Share a specific, relevant example from your background
   - Include concrete metrics and outcomes
   - Make it feel like you're telling a story, not listing achievements

3. **Detailed Methodology (5-6 sentences)**
   - Explain exactly how you'd tackle their project
   - Include specific tools and techniques
   - Use this approach: "{chosen_methodology}"
   - Break down your process hour-by-hour or phase-by-phase

4. **Additional Proof Point (3-4 sentences)**
   - Share another brief example that reinforces your capability
   - Include different metrics or a different type of challenge
   - Connect it directly to their needs

5. **Unique Value Proposition (3-4 sentences)**
   - What sets you apart from other analysts
   - Use this angle: "{chosen_value_prop}"
   - Show understanding of business context, not just technical skills

6. **Quality Assurance (2-3 sentences)**
   - How you ensure accuracy even under time pressure
   - Specific validation techniques or quality checks you use

7. **Clear Deliverables (3-4 sentences)**
   - Exactly what they'll receive from you
   - Format, timeline, and level of detail
   - How you'll present findings for maximum impact

8. **Collaborative Approach (2-3 sentences)**
   - How you'll keep them involved and informed
   - Communication style and update frequency

9. **Thoughtful Question (1-2 sentences)**
   - Ask something specific about their situation
   - Show you're thinking beyond just the basic requirements

**CRITICAL REQUIREMENTS:**
- **LENGTH**: 4000-5000+ characters (substantial and comprehensive)
- **TONE**: Professional but conversational, like talking to a colleague
- **FOCUS**: Their specific challenge, not generic data analysis capabilities  
- **METRICS**: Include 3-4 specific numbers/results from your background
- **DEPTH**: Go deep on methodology and approach, not just surface-level promises
- **AUTHENTICITY**: Sound like someone who's actually done this work before
- **NO GENERIC PHRASES**: Avoid "excited to work," "perfect fit," "extensive experience"

The client should finish reading and think: "This person has clearly solved problems like mine before, knows exactly what they're doing, and I trust them to handle this urgent situation professionally."

Make every sentence count - this is a high-stakes project that deserves a comprehensive response.

Write the complete, detailed proposal now:"""

    return prompt