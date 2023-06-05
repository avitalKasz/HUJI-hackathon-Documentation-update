import sys
import re
import os
import openai
from typing import List, Optional

openai.api_key = "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"
openai.organization = 'hujihackathon'

EXAMPLE_HIERARCHY="""
hackathon
__company_files
__project_classification
____animal_clasification
____features
____configuration
____bugs
____cities_classification
____cars_classification
__project_electricity
__project_timer
"""

EXAMPLE_DIR="features"


# prompt = """
# 1. Give a Title to the project
# 2. Please provide an overview of the code.
# 3. Please provide a background of the code.
# 4. Please provide The impact of the code.
# 5. Please analyze generally the provided code and generate an explanation focusing on the top 5 features,
# that dont include the first 4 questions above.
# Consider the most important aspects and provide detailed insights on those, and give each feature a title.
# """
# 6. Discuss the goals of the project.
# 7. Discuss any potential future improvements or enhancements.
# 8. Outline the steps to run or deploy the code
# 9. Describe any error handling or exception handling mechanisms.
# 10. Discuss any security considerations or precautions taken.
# 11. Discuss any known limitations or known issues.


def _prepare_file_to_prompt(index, file_content):
    return f'File {index}: \n{file_content}\n'


def _prepare_git_files_to_prompt(git_files_content):
    git_files_string = ''
    for i, file in enumerate(git_files_content):
        git_files_string += _prepare_file_to_prompt(i, file)
    return git_files_string


def create_prompt(git_files_string, template_file_content, notes_file_content=None):
    # git_files_string = _prepare_git_files_to_prompt(git_files_content)

    prompt = f"""
We developed a new feature. {notes_file_content or ''}
Our code files are:
    {git_files_string}
Write documentation that explains the new feature, in the following structure:
    {template_file_content}
"""
    return prompt


def read_file_content(file_path: str):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except IOError:
        print(f"Error reading file: {file_path}")
        return None


def get_title(file_text: str):
    return file_text.split('<h1 class="c4"><span class="c9">')[1].split('<')[0]


def build_prompt(git_file_paths: List[str], template_file_path: str, notes_file_path: Optional[str] = None):
    git_files_contents: List[str] = [read_file_content(file_path) for file_path in git_file_paths]
    git_files_string = _prepare_git_files_to_prompt(git_files_contents)
    template_file_content: str = read_file_content(template_file_path)
    notes_file_content = read_file_content(notes_file_path) if notes_file_path else None
    prompt = create_prompt(git_files_string, template_file_content, notes_file_content)

    return prompt, git_files_string


def get_dalle_prompt(code):
    dalle_template = f"""
        This is the code:
        {code}   
        provide only the number of steps for AI images generator diagram describing the code's flow         
    """
    return dalle_template


def generate_explanation_from_template(code_files_paths: List[str],
                                       template_file_path: str,
                                       notes_file_path: Optional[str],
                                       hierarchy_string):
    template, files_code = build_prompt(code_files_paths, template_file_path, notes_file_path)
    # print("Template:")
    # print(template)

    chat_history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": template},
    ]

    print("Running... ")
    response_files = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
        temperature=0.7,
        max_tokens=2000  # Adjust as per your requirements
    )
    explanation = response_files.choices[0].message['content']
    filename = get_title(explanation).replace(" ", "_")
    parent_folder = generate_file_system_addr(hierarchy_string, filename)
    return explanation, filename, parent_folder


def generate_picture_from_dalle(code_files_paths, template_file_path):
    _, files_code = build_prompt(code_files_paths, template_file_path)
    dalle_prompt = get_dalle_prompt(files_code)
    chat_history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": dalle_prompt},
        # {"role": "assistant", "content": code},
    ]

    response_code = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
        temperature=0.7,
        max_tokens=2000  # Adjust as per your requirements
    )
    explanation_prompt_dalle = response_code.choices[0].message['content']
    print(explanation_prompt_dalle)
    response = openai.Image.create(
        prompt="a white siamese cat",
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    print(image_url)
    return image_url


def prompt_file_system_tree(filesytsm_hierarchy: str, filename: str):
    prompt_filesystem_tree = f"""
            This is the hierarchy of the file system:
            {filesytsm_hierarchy}   
            This is the filename:
            {filename}""".join("Assistant, please provide me with the name of the desired file from the following hierarchy:\n\n{}".format(filesytsm_hierarchy)
)       
        
    return prompt_filesystem_tree


def generate_file_system_addr(file_system_hierarchy: str, filename: str):
    # file_system_prompt = prompt_file_system_tree(file_system_hierarchy, filename)
    chat_history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": EXAMPLE_HIERARCHY},
        {"role": "assistant", "content": EXAMPLE_DIR},
        {"role": "user", "content": file_system_hierarchy}

    ]

    # response_file_system_tree = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=chat_history,
    #     temperature=0.7,
    #     max_tokens=2000  # Adjust as per your requirements
    # )
    # explanation_file_system = response_file_system_tree.choices[0].message['content']
    explanation_file_system=EXAMPLE_DIR
    return explanation_file_system
