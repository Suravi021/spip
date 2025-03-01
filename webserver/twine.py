import toml
import os
import re
import subprocess
import requests
import hashlib
import markdown2
with open('nt.toml', 'r') as f:
    config = toml.load(f)
 
username = config['personal']['username']
email = config['personal']['email']
github = config['personal']['github']
description_path = config['personal']['description_path']
directory_path =config['personal']['directory_path']

pattern = r'[^/]*$'
match = re.search(pattern, github)
repo = match.group(0)


#checks if various params exist
def ExistenceChecker():
    
    validemail = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(email))
    if not validemail:
        print("The provided email isn't valid")
        return False
    try:
        result = subprocess.run(['git', 'ls-remote', str(github)], 
                               capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print("The github link provided isn't valid")
            return False
    except Exception as e:
        print(f"Error validating GitHub link: {str(e)}")
        return False
    
    if not os.path.exists(description_path):
        print("Valid README.md file does not exist")
        return False
    
    if not os.path.exists(directory_path):
        print("Valid directory path doesn't exist")
        return False
    return True


def ReputationCheck(owner, repo, token=None):
    owner = username
    if ExistenceChecker():
    # repo reputation checks
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"
            
            headers = {}
            if token:
                headers["Authorization"] = f"token {token}"
        
            response = requests.get(url, headers=headers)
        
            if response.status_code == 200:
                data = response.json()
                return {
                    "stars": data["stargazers_count"],
                    "forks": data["forks_count"],
                    "open_issues": data["open_issues_count"],
                }
            else:
                return {"error": f"Failed to fetch details. Status code: {response.status_code}"}
        except Exception as e:
            print(str(e))
    

def get_directory_metadata_id(directory_path):
    metadata = []
    
    # Walk directory to collect metadata
    for root, dirs, files in os.walk(directory_path):
        # Sort for consistency
        dirs.sort()
        files.sort()
        
        for filename in files:
            filepath = os.path.join(root, filename)
            if os.path.isfile(filepath):
                # Get file stats
                stats = os.stat(filepath)
                rel_path = os.path.relpath(filepath, directory_path)
                # Add size and modification time
                metadata.append(f"{rel_path}:{stats.st_size}:{stats.st_mtime}")
    
    # Hash the combined metadata
    return hashlib.md5("".join(metadata).encode()).hexdigest()

def get_github_commits(owner, repo, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f'token {token}'
    
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    response = requests.get(url, headers=headers)
    repo2 = f"https://github.com/{owner}/{repo}"
    repogit = repo2 + '.git'
    subprocess.run(['git', 'clone', f"{repogit}"])
    
        
        
    if response.status_code == 200:
        x = response.json()
        subprocess.run(['git','checkout',f"{x[0]['sha']}"],cwd=repo)
        githubrep = ReputationCheck(owner=username,repo=repo)
        githuburl = repo2
        GHuser = username
        GHemail = email
        bandit_report = subprocess.run(['python', '-m','bandit','-r',f'{repo}','-f','txt'],capture_output=True, text=True, check=False)
        github_commit_sha = x[0]['sha']

        fileHandle = open(description_path, 'r')

        with open("README.md", "r", encoding="utf-8") as file:
            markdown_text = file.read()

        readme_html = markdown2.markdown(markdown_text)
                
        print(readme_html)
        msg_json = {
            "repo": str(repo),
            "username": str(username),
            "githuburl": str(githuburl),
            "github_user": str(GHuser),
            "github_email": str(GHemail),
            "bandit_output": str(bandit_report),
            "commit_sha": str(github_commit_sha),
            "reputation": str(githubrep),
            "ReadMe":str(readme_html)
        }

        
        return msg_json
    else:
        print(f"Error: {response.status_code}")
    return None

data = get_github_commits(username, repo)


url = "http://127.0.0.1:5000/receive"
response = requests.post(url, json=data)
print(response)

