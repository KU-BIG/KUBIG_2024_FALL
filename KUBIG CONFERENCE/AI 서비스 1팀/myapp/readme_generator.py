import os
from PyPDF2 import PdfReader
from openai import OpenAI
from django.conf import settings
from django.core.files.base import ContentFile

def extract_text_from_pdf(pdf_path):
    pdf_reader = PdfReader(pdf_path)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def create_prompt(code_contents, pdf_contents, title, description):
    # Combine all code contents with markerss
    combined_code = ""
    for i, code in enumerate(code_contents, 1):
        code_summary = code[:500] + "..." if len(code) > 500 else code
        combined_code += f"\nSource Code File {i}:\n```\n{code_summary}\n```\n"

    # Combine all PDF contents with markers
    combined_pdf = ""
    for i, pdf in enumerate(pdf_contents, 1):
        pdf_summary = pdf[:500] + "..." if len(pdf) > 500 else pdf
        combined_pdf += f"\nPresentation File {i}:\n{pdf_summary}\n"

    prompt = f"""As an AI assistant, please create a GitHub README in English based on the provided source code and presentation materials.
    
    Project Title: {title}
    Project Description: {description}
    
    Please include the following sections: Project Description, Key Features, Installation Guide, Usage Examples, Testing, Deployment, How to Contribute, License, and Acknowledgments.

    Source Code Summary:
    {combined_code}

    Presentation Summary:
    {combined_pdf}

    Please consider the following when writing the README:
    0. Follow the EXACT structure provided below
    1. Use the provided project title for the README title.
    2. Base the project description section on the provided description, supplemented with information from other sources.
    3. Use **bold text** to emphasize important words or phrases.
    4. Include appropriate emojis for each section.
    5. Utilize various Markdown elements to enhance readability.
    6. Write in a professional yet friendly tone.
    7. Don't include Deployment, License, Usage Example and Testing 
    8. When writing a README, make sure to reflect the details of the source code and presentation materials
    9. Follow the EXACT Installation guide
    """
    return prompt

def generate_readme(source_codes, presentation_texts, project_title, project_description):    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    prompt = create_prompt(source_codes, presentation_texts, project_title, project_description)
    few_shot_examples = [
        {
            "role": "user",
            "content": "Please create a GitHub README for a Python-based data analysis project."
        },
        {
            "role": "assistant",
            "content": """# 📊 Data Analysis Tool

            ## 🔍 Project Title
            Python data analysis project
                        
            ## 🔍 Project Description
            This project is a Python-based data analysis tool designed to analyze **large datasets** and derive **statistical insights**.

            ## ✨ Key Features
            - 🧹 **Data Processing**: Clean, transform, and filter data
            - 📈 **Visualization**: Generate graphs in various formats
            - 🧮 **Statistical Analysis**: Calculate basic statistics including mean, variance, etc.

            ## 🛠 Installation Guide
            1. Clone the repository:
            ```bash
            git clone {github repository url}
            ```
            2. Install required packages:
            ```bash
            pip install -r requirements.txt
            ```

            ## 💻 Usage Example
            ```python
            from data_analysis_tool import DataAnalyzer
            analyzer = DataAnalyzer('data.csv')
            results = analyzer.analyze()
            analyzer.visualize(results, 'output.png')
            ```

            ## 🎉 Acknowledgments
            A big thank you to Korea University and all the developers who worked on this project. Special thanks to Upstage LLM Innovators Challenge for providing a platform for this innovative project.
            """
        },
        {
            "role": "user",
            "content": "Please create a GitHub README for a web scraping automation tool in Python"
        },
        {
            "role": "assistant",
            "content": """# 📊 Web Scraping Automation Tool

            ## 🔍 Project Title
            Python Web Scraping Automation Tool
                        
            ## 🔍 Project Description
            This project is a Python-based tool designed to automate web scraping tasks, making it easy to extract data from multiple websites.

            ## ✨ Key Features
            🤖 Automated Scraping: Fetch data from multiple web sources
            💾 Data Export: Export data in CSV, JSON, and other formats
            ⏰ Scheduling: Automate scraping on a regular schedule for consistent data updates

            ## 🛠 Installation Guide
            1. Clone the repository:
            ```bash
            git clone {github repository url}
            ```
            2. Install required packages:
            ```bash
            pip install -r requirements.txt
            ```

            ## 💻 Usage Example
            ```python
            from web_scraper import Scraper
            scraper = Scraper('https://example.com')
            data = scraper.fetch_data()
            scraper.export(data, 'output.csv')
            ```

            ## 🎉 Acknowledgments
            Thanks to the open-source community for resources and support. This project is inspired by data collection research from Korea University.
            """
        },
    
    ]
    messages = few_shot_examples + [{"role": "user", "content": prompt}]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.5,
        max_tokens=3000
    )
    
    return response.choices[0].message.content

def process_uploaded_files(document):
    source_codes = []
    presentation_texts = []
    
    # Process source code files
    for source_code_file in document.source_codes.all():
        source_code_path = os.path.join(settings.MEDIA_ROOT, source_code_file.file.name)
        encodings = ['utf-8', 'cp949', 'euc-kr']
        for encoding in encodings:
            try:
                with open(source_code_path, 'r', encoding=encoding) as file:
                    source_code = file.read()
                source_codes.append(source_code)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError(f"Unable to decode the source code file {source_code_file.file.name} with any known encoding")
    
    # Process presentation files
    for presentation_file in document.presentations.all():
        pdf_path = os.path.join(settings.MEDIA_ROOT, presentation_file.file.name)
        presentation_text = extract_text_from_pdf(pdf_path)
        presentation_texts.append(presentation_text)
    
    # Generate README
    readme_content = generate_readme(source_codes, presentation_texts, document.project_title, document.project_description)    
    return readme_content

    # run