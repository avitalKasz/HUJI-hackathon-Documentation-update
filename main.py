import argparse
from git_tool import get_changed_files
from gpt_prompt import generate_explanation_from_template
from google_drive import upload_file_text, get_heirarchy, upload_file_image

def parse_arguments():
    parser = argparse.ArgumentParser(description="Get changed files in a Git repository")
    # Add the repository path argument
    parser.add_argument("-r", "--repo", type=str, help="Path to the Git repository", required=True)
    # Add the template path argument
    parser.add_argument("-t", "--template", type=str, help="Path to template file")
    # Add the template path argument
    parser.add_argument("-n", "--notes", type=str, help="Path to notes file")
    # Parse the command-line arguments
    return parser.parse_args()

def main():
    args = parse_arguments()
    print("(1) Identifying changed files")
    changed_files = get_changed_files(args.repo)

    print("\n(2) Getting Hierarchy from Google Drive")
    heirarchy_string = get_heirarchy()

    print("\n(3) Generating Document content via GPT")
    doc_content, name_doc, dir_name = generate_explanation_from_template(changed_files, args.template, args.notes, heirarchy_string)
    
    print(heirarchy_string) # erase!!
    print("\n(4) Uploading new Document to Google Drive")
    print("file_name ", name_doc)
    print("dir_name ", dir_name)
    upload_file_text(text=doc_content, file_name=name_doc, dir_name=dir_name)

if __name__ == "__main__":
    main()
