import cohere
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader


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

        return text[:8000]  # Increased limit for more context
    except Exception as e:
        return f"Error extracting URL content: {str(e)}"


def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file."""
    try:
        reader = PdfReader(uploaded_file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text[:8000]  # Increased limit for more context
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def get_upwork_proposal(api_key, prompt):
    """Generate Upwork proposal using Cohere's chat API with specialized prompting."""
    try:
        co = cohere.Client(api_key)

        system_message = """You are an elite Upwork proposal writer with a 90%+ win rate on technical projects. Your proposals are known for:

1. IMMEDIATE TECHNICAL CREDIBILITY - You demonstrate deep understanding of the specific technical challenges mentioned in the job posting
2. CONCRETE PROOF - You provide specific examples, metrics, and technical details from past work that directly relate to their needs
3. NO FLUFF - Every sentence adds value. No generic enthusiasm or "I'm excited" openings
4. SOLUTION-FOCUSED - You outline specific technical approaches and methodologies you'll use
5. UPFRONT VALUE - You provide insights or identify potential challenges that show your expertise

STRUCTURE YOUR PROPOSALS:
1. Direct Problem Statement - Show you understand their core challenge
2. Technical Solution Overview - Specific tools, methods, and approach
3. Relevant Experience with Metrics - Concrete examples with measurable results
4. Technical Deep-dive - Show expertise through specific technical knowledge
5. Practical Next Steps - Immediate actions you'll take

CRITICAL REQUIREMENTS:
- Stay under 5000 characters (roughly 800-900 words)
- Use technical terminology appropriate to the field
- Include specific metrics and results from past work
- Mention exact tools, technologies, and methodologies
- Avoid generic phrases like "I'm excited" or "perfect fit"
- Focus on what you'll deliver, not why you're great
- End with specific questions or next steps

Remember: Clients hire based on confidence in your ability to solve their specific problem. Demonstrate that confidence through technical knowledge and proven results."""

        response = co.chat(
            model="command-r-plus",
            message=prompt,
            preamble=system_message,
            max_tokens=1200,
            temperature=0.6  # Slightly lower for more focused responses
        )

        return response.text.strip()

    except Exception as e:
        if "unauthorized" in str(e).lower():
            raise Exception("Invalid API key. Please check your Cohere API key.")
        elif "quota" in str(e).lower() or "limit" in str(e).lower():
            raise Exception("API quota exceeded. Please check your Cohere account limits.")
        else:
            raise Exception(f"Cohere API error: {str(e)}")


def create_upwork_prompt(job_description, supporting_content):
    """Create a specialized prompt for Upwork proposals with technical focus."""

    # Extract key technical requirements and KPIs from job description
    jd_preview = job_description[:4000] if job_description else "No job description provided"
    content_preview = supporting_content[:4000] if supporting_content else "No supporting content provided"

    prompt = f"""
    Analyze this Upwork job posting and create a winning proposal that demonstrates deep technical understanding and proven capability.

    **CRITICAL ANALYSIS REQUIREMENTS:**
    1. Identify the TOP 3 technical challenges or requirements from the job posting
    2. Extract specific KPIs, metrics, or success criteria mentioned
    3. Note any technical tools, platforms, or methodologies specified
    4. Identify potential pain points or challenges not explicitly mentioned
    
    **MY TECHNICAL BACKGROUND:**
    {content_preview}
    
    **JOB POSTING TO ANALYZE:**
    {jd_preview}
    
    **PROPOSAL REQUIREMENTS:**
    - Lead with the most critical technical challenge they face
    - Provide specific examples from my background that directly address their needs
    - Include concrete metrics and results from previous similar work
    - Demonstrate technical depth by mentioning specific tools, methodologies, or approaches
    - Show understanding of their business context and industry
    - Outline specific deliverables and technical approach
    - Stay under 5000 characters total
    - NO generic enthusiasm - focus on technical competence and results
    
    **STRUCTURE:**
    1. Problem identification (their core challenge)
    2. Technical solution approach (specific methods/tools)
    3. Relevant experience with metrics (proof of capability)
    4. Technical implementation details (show expertise)
    5. Specific deliverables and timeline
    6. Clear next steps or questions
    
    Create a proposal that makes the client think: "This person clearly understands our technical needs and has the exact experience to solve this problem."
    """