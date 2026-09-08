from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import re
import os

app = Flask(__name__)
IS_VERCEL = os.environ.get("VERCEL") == "1"

LM_STUDIO_BASE_URL = os.environ.get("LM_STUDIO_BASE_URL", "https://api.groq.com/openai/v1")
LM_STUDIO_API_KEY = os.environ.get("LM_STUDIO_API_KEY", "")
MODEL_NAME = os.environ.get("MODEL_NAME", "llama-3.1-8b-instant")
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "8000"))

client = OpenAI(base_url=LM_STUDIO_BASE_URL, api_key=LM_STUDIO_API_KEY)

def setup_loggers():
    # Vercel Functions have an ephemeral, read-only deployment filesystem.
    # Keep the existing local/Fly file logs, but send deployment logs to stdout.
    if IS_VERCEL:
        logging.basicConfig(level=logging.INFO)
        return

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    
    # Count logger
    count_logger = logging.getLogger('count')
    count_logger.setLevel(logging.INFO)
    count_handler = logging.FileHandler('logs/message_count.log')
    count_formatter = logging.Formatter('%(asctime)s - %(message)s')
    count_handler.setFormatter(count_formatter)
    if not count_logger.handlers:
        count_logger.addHandler(count_handler)

    # Project logger
    project_logger = logging.getLogger('project')
    project_logger.setLevel(logging.INFO)
    project_handler = logging.FileHandler('logs/project_log.log')
    project_formatter = logging.Formatter('%(asctime)s - %(message)s')
    project_handler.setFormatter(project_formatter)
    if not project_logger.handlers:
        project_logger.addHandler(project_handler)

setup_loggers()

def log_generated_message(message, user_email, message_type):
    """Keep existing file logs locally; use Vercel runtime logs when deployed."""
    project_name_match = re.search(r"Project Name - \*(.*?)\*", message)
    project_name = project_name_match.group(1).strip() if project_name_match else "Unknown Project"

    if IS_VERCEL:
        app.logger.info("Message generated: project=%s email=%s type=%s", project_name, user_email, message_type.upper())
        return

    # Log total message count
    total_count_logger = logging.getLogger('count')
    total_count = 1
    total_count_log_path = 'logs/message_count.log'
    if os.path.exists(total_count_log_path):
        try:
            with open(total_count_log_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    last_count = int(last_line.split(' - ')[1])
                    total_count = last_count + 1
        except (IOError, IndexError, ValueError):
            total_count = 1
    total_count_logger.info(total_count)

    # Log daily message count
    daily_count_log_filename = f"logs/{datetime.now().strftime('%Y-%m-%d')}_daily_count.log"
    daily_count_logger = logging.getLogger('daily_count')
    daily_count_logger.setLevel(logging.INFO)
    for handler in daily_count_logger.handlers[:]:
        daily_count_logger.removeHandler(handler)
    daily_handler = logging.FileHandler(daily_count_log_filename)
    daily_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    daily_count_logger.addHandler(daily_handler)

    daily_count = 1
    if os.path.exists(daily_count_log_filename):
        try:
            with open(daily_count_log_filename, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    last_count = int(last_line.split(' - ')[1])
                    daily_count = last_count + 1
        except (IOError, IndexError, ValueError):
            daily_count = 1
    daily_count_logger.info(daily_count)

    logging.getLogger('project').info(f"Project: {project_name} - Email: {user_email} - Type: {message_type.upper()}")

def create_whatsapp_message(link, data, message_type='bx1'):
    """
    This function takes a link and data,
    then uses a local large language model to generate a WhatsApp message.
    message_type: 'bx1' or 'bx2'
    """
    system_prompt = "You are a helpful assistant that creates WhatsApp messages."

    if message_type == 'bx2':
        user_prompt = f"""You are a professional Biltrax business writer for the Bx2 (Industrial & Infrastructure) division.

You will be given plain text project data that may be messy, unstructured, or incomplete.

Your job is to:

Extract relevant project details.

Generate a project update message in the exact format shown below.

Do NOT invent or assume missing information.

Skip any section where data is not available.

Keep company names, contacts, and numbers exactly as written.

✅ STRICT FORMAT TO FOLLOW

Start with Dear Team

Use bullet symbol ■ exactly.

Maintain spacing and line breaks exactly like below.

✅ OUTPUT FORMAT

Dear Team,

■ {{Company Name}} has proposed for a {{greenfield/brownfield}} project for a {{Project Type}} at {{Location}}. {{One line about land area or investment cost if available}}.

■ Project name - {{Project Name}}

■ Biltrax Project Unique ID - {{Project ID}}

■ Project Cost - {{Project Cost}} Crores
{{If cost is tentative, add: The construction cost and area of the proposed project are tentative.}}

■ Associated Companies:
{{Company Name}} - {{Role}} - {{Sector/Industry}}

■ Project Status:

{{Write a natural paragraph summarizing the latest status update. Include: who was spoken to, what was shared, any timelines or next steps mentioned. Do not use bullet points here. Write it as a professional narrative paragraph.}}

■ Please refer to the contacts verified by Biltrax representative given below:

{{Name}} - {{Company Name}}
{{Designation}}
{{City/State}}
{{Email if available}}
{{Mobile if available}}

■ For more information please refer to the Project link provided below:

{link}

✅ EXTRA RULES

All mentioned contacts should be included with their details if available.

Only the latest status update should be included. If multiple updates exist, use only the most recent one.

In the project status section, write a paragraph (not bullet points) describing what was communicated by the contact person.

Do NOT add extra explanation.

Do NOT change wording unnecessarily.

Do NOT guess missing values.

If project cost or ID not found → remove that line.

If no contacts → remove contact section.

If no company roles → list company names only.

Keep professional tone.

✅ INPUT DATA

You will receive project details in plain text below:

{data}
✅ FINAL RULE

Return ONLY the formatted message.
No notes, no markdown, no explanation.

"""
    else:
        user_prompt = f"""You are a professional Biltrax business writer.

You will be given plain text project data that may be messy, unstructured, or incomplete.

Your job is to:

Extract relevant project details.

Generate a project update message in the exact format shown below.

Do NOT invent or assume missing information.

Skip any section where data is not available.

Keep company names, contacts, and numbers exactly as written.

✅ STRICT FORMAT TO FOLLOW

Start with Dear Team

Use bullet symbol ■ exactly.

Maintain spacing and line breaks exactly like below.

✅ OUTPUT FORMAT

Dear Team

■ *{{Authority/Developer Name}}* is coming up with a *{{Building Use}} * project for construction of {{Project Name}} at {{Location}}.

■ {{Project Description}}

You can write the project description in your own words, but make sure to include the key details such as project type, location, and any unique features mentioned in the data. You can include building type, number of floors, amenities, or any other relevant information that helps describe the project clearly.

■ Project Name - *{{Project Name}}*
■ Biltrax Project Unique ID - {{Project ID}}
■ Project Cost - {{Project Cost}} INR Crore
■ Project Construction Area - {{Construction Area}} sq.ft

■ Biltrax latest Update - *{{Project Status}} - {{Project Substatus}}*
- {{status update}}
{{Write updates as bullet points starting with *}}

■ *Associated Companies:*
{{Company Name}} - {{Role}} {{Specialization}}

■ *Please refer to the contacts verified by the Biltrax representative given below:*

{{Name}} - {{Designation}}
Organization - {{Company}}
Mobile - {{Mobile Number}}
Email - {{Email}}

■ For more information, please refer to the Biltrax Project link provided below:
{link}

✅ EXTRA RULES

All mentioned professionals should be included in contact section with their details if available. no need of professional state to be included.

Only latest status update should be included in the message. If multiple updates are available, include only the most recent one.

Do NOT add extra explanation.

Do NOT change wording unnecessarily.

Do NOT guess missing values.

If project cost or ID not found → remove that line.

If no contacts → remove contact section.

If no company roles → list company names only.

Keep professional tone.

✅ INPUT DATA

You will receive project details in plain text below:

{data}
✅ FINAL RULE

Return ONLY the formatted message.
No notes, no markdown, no explanation.

"""

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        timeout=120,
    )

    return completion.choices[0].message.content

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create():
    try:
        user_email = request.form.get('user_email', 'anonymous')
        message_type = request.form.get('message_type', 'bx1')
        link = request.form.get('link', '')
        project_details = request.form.get('project_details', '')
        companies_contacts = request.form.get('companies_contacts', '')
        status = request.form.get('status', '')
        other_data = request.form.get('other_data', '')

        # Merge the data from the four fields into a single string with headers
        merged_data = []
        if project_details:
            merged_data.append("--- PROJECT DETAILS ---\n" + project_details)
        if companies_contacts:
            merged_data.append("\n\n--- COMPANIES & CONTACTS ---\n" + companies_contacts)
        if status:
            merged_data.append("\n\n--- STATUS ---\n" + status)
        if other_data:
            merged_data.append("\n\n--- ADDITIONAL DATA ---\n" + other_data)
        
        data = "".join(merged_data)

        if not data:
            return jsonify({'error': 'No data provided to generate a message.'}), 400

        message = create_whatsapp_message(link, data, message_type)

        log_generated_message(message, user_email, message_type)

        return jsonify({'message': message})
    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5556))
    app.run(debug=False, host='0.0.0.0', port=port)
