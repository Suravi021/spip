import click
import toml
import os
import re
import subprocess
import requests
import hashlib
import markdown2
from pathlib import Path

class RepoAnalyzer:
    url = "http://127.0.0.1:5000/receive"
    def __init__(self, config_file='nt.toml'):
        with open(config_file, 'r') as f:
            config = toml.load(f)
        
        self.username = config['personal']['username']
        self.email = config['personal']['email']
        self.github = config['personal']['github']
        self.description_path = config['personal']['description_path']
        self.directory_path = config['personal']['directory_path']

        pattern = r'[^/]*$'
        match = re.search(pattern, self.github)
        self.repo = match.group(0)

    def existence_checker(self):
        validemail = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(self.email))
        if not validemail:
            click.echo("The provided email isn't valid")
            return False
        try:
            result = subprocess.run(['git', 'ls-remote', str(self.github)], 
                                capture_output=True, text=True, check=False)
            if result.returncode != 0:
                click.echo("The github link provided isn't valid")
                return False
        except Exception as e:
            click.echo(f"Error validating GitHub link: {str(e)}")
            return False
        
        if not os.path.exists(self.description_path):
            click.echo("Valid README.md file does not exist")
            return False
        
        if not os.path.exists(self.directory_path):
            click.echo("Valid directory path doesn't exist")
            return False
        return True

    def reputation_check(self, owner, repo, token=None):
        if not self.existence_checker():
            return None
            
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
            click.echo(str(e))
            return None

    @staticmethod
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

    def get_github_commits(self, owner, repo, token=None):
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
            subprocess.run(['git', 'checkout', f"{x[0]['sha']}"], cwd=repo)
            githubrep = self.reputation_check(owner=self.username, repo=repo)
            if not githubrep:
                return None
            githuburl = repo2
            GHuser = self.username
            GHemail = self.email
            bandit_report = subprocess.run(['python', '-m', 'bandit', '-r', f'{repo}', '-f', 'txt'], 
                                        capture_output=True, text=True, check=False)
            github_commit_sha = x[0]['sha']

            with open(self.description_path, "r", encoding="utf-8") as file:
                markdown_text = file.read()

            readme_html = markdown2.markdown(markdown_text)
                    
            click.echo(readme_html)
            msg_json = {
                "repo": str(repo),
                "username": str(self.username),
                "githuburl": str(githuburl),
                "github_user": str(GHuser),
                "github_email": str(GHemail),
                "bandit_output": str(bandit_report),
                "commit_sha": str(github_commit_sha),
                "reputation": str(githubrep),
                "ReadMe": str(readme_html)
            }
            
            return msg_json
        else:
            click.echo(f"Error: {response.status_code}")
        return None

@click.group()
def cli():
    """GitHub Repository Analysis CLI Tool"""
    pass

@cli.command()
@click.option('--config', '-c', help='Path to config file')
def upload(config):
    """Initialize the repository analyzer with configuration"""
    if not os.path.exists(config):
        click.echo(f"Error: Config file {config} not found")
        return
    
    click.echo(f"Initialized with config from {config}")
    report = RepoAnalyzer(config_file=config)

# @cli.command()
# @click.option('--config', '-c', help='Path to config file')
# @click.option('--url', '-u', default="http://127.0.0.1:5000/receive", help='URL to upload data to')
# def upload(config, url):
    click.echo("Analyzing GitHub repo...")
    analyzer = RepoAnalyzer(config_file=config)
    data = analyzer.get_github_commits(analyzer.username, analyzer.repo)
    
    if data:
        response = requests.post(report.url, json=data)
        click.echo(f"Upload response: {response.status_code}")
        click.echo(response.text)
        click.echo("Results uploaded.")
    else:
        click.echo("Failed to collect repository data")


if __name__ == '__main__':
    cli()
