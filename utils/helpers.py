import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import json
import time


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

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 1000,
                "temperature": 0.7,
                "do_sample": True,
                "top_p": 0.9
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

        # Simplified system message to avoid token issues
        system_content = """You are an expert Upwork proposal writer. Create winning proposals that:
- Lead with their specific technical challenge (no generic enthusiasm)
- Include concrete metrics from relevant experience
- Use technical terminology correctly
- Stay under 5000 characters
- End with clear next steps
Focus on technical competence and proven results."""

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user",
                    "content": prompt[:3000]  # Limit prompt length
                }
            ],
            "model": "llama3-8b-8192",  # More reliable free model
            "temperature": 0.7,
            "max_tokens": 800,
            "top_p": 1,
            "stream": False
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)

        # Debug: Print response details
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code != 200:
            print(f"Response Text: {response.text}")

        if response.status_code == 400:
            # Try with mixtral model instead
            payload["model"] = "mixtral-8x7b-32768"
            payload["max_tokens"] = 500
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

        if 'choices' not in result:
            raise Exception(f"No 'choices' in response. Full response: {result}")

        choices = result.get('choices', [])
        if not choices or len(choices) == 0:
            raise Exception(f"Empty choices array. Full response: {result}")

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise Exception(f"Invalid choice format: {first_choice}")

        if 'message' not in first_choice:
            raise Exception(f"No 'message' in choice. Choice: {first_choice}")

        message = first_choice['message']
        if not isinstance(message, dict):
            raise Exception(f"Invalid message format: {message}")

        if 'content' not in message:
            raise Exception(f"No 'content' in message. Message: {message}")

        content = message['content']
        if content is None:
            raise Exception("Message content is None")

        return content.strip()

    except requests.exceptions.RequestException as e:
        if "400" in str(e):
            raise Exception(f"Groq API error - Invalid request. Check your API key and try again. Details: {str(e)}")
        elif "401" in str(e):
            raise Exception("Invalid Groq API key. Get a new one at https://console.groq.com/")
        elif "429" in str(e):
            raise Exception("Rate limit exceeded. Please wait a moment and try again.")
        else:
            raise Exception(f"Groq API network error: {str(e)}")
    except Exception as e:
        if "object is not subscriptable" in str(e):
            raise Exception(
                f"Groq API returned unexpected format. This might be due to rate limits or API changes. Try again in a moment.")
        raise Exception(f"Groq API error: {str(e)}")


def get_ollama_completion(prompt, model="llama2", ollama_url="http://localhost:11434"):
    """Generate completion using local Ollama (100% FREE!)"""
    try:
        url = f"{ollama_url}/api/generate"

        payload = {
            "model": model,
            "prompt": f"""You are an expert Upwork proposal writer. Create a technical, results-focused proposal that demonstrates deep understanding and proven capability.

Requirements:
- Lead with their specific technical challenge
- Include concrete metrics from past work
- Use industry terminology correctly  
- Stay under 5000 characters
- Focus on solutions, not enthusiasm
- End with clear next steps

{prompt}

Generate a winning proposal:""",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 800
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
    """Create optimized prompt for any LLM provider"""

    # Limit content to avoid token issues
    jd_preview = job_description[:2000] if job_description else "No job description provided"
    content_preview = supporting_content[:2000] if supporting_content else "No supporting content provided"

    prompt = f"""Create a winning Upwork proposal for this job posting.

**MY TECHNICAL BACKGROUND:**
{content_preview}

**JOB POSTING:**
{jd_preview}

**ANALYSIS REQUIREMENTS:**
1. Identify their TOP technical challenge or requirement
2. Extract specific KPIs, metrics, or success criteria mentioned  
3. Note technical tools/platforms they specified
4. Find potential pain points not explicitly mentioned

**PROPOSAL STRUCTURE:**
1. Lead with their core technical challenge (no "excited" language)
2. Specific technical solution approach with exact tools/methods
3. Relevant experience with concrete metrics and results
4. Technical implementation details showing expertise
5. Clear deliverables and timeline
6. Intelligent questions or next steps

**CRITICAL REQUIREMENTS:**
- Under 5000 characters total
- Use technical terminology from the job posting
- Include specific metrics from my background that match their needs
- Show understanding of their business context
- Focus on what I'll deliver, not why I'm great
- Demonstrate technical competence through specific knowledge

Create a proposal that makes them think: "This person understands our exact technical needs and has proven experience solving this specific problem."
"""

    return prompt