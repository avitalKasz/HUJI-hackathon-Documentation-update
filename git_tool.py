import git
import os

def print_file_names(files):
    print("files changed:")
    for file in files:
        print(file)

def is_git_repo(repo_path):
    try:
        _ = git.Repo(repo_path)
        return True
    except git.exc.InvalidGitRepositoryError:
        return False

def get_changed_files(repo_path):
    if not is_git_repo(repo_path):
        print(f"{repo_path} is not a valid Git repository.")
        return
    repo = git.Repo(repo_path)
    last_commit = repo.head.commit
    previous_commit = last_commit.parents[0] if last_commit.parents else None

    changed_files = []
    if previous_commit:
        for diff in previous_commit.diff(last_commit):
            file_path = os.path.join(repo_path, diff.a_path)
            if os.path.exists(file_path):
                changed_files.append(file_path)

    print_file_names(changed_files)
    return changed_files

