from tinydb import TinyDB, Query
import click
import requests
import os
import subprocess
import json
import tempfile
import shutil
import sys

# Configuration
SERVER_URL = "http://localhost:5000"  # Change this to your server URL
DB_PATH = 'local_repos.json'  # Local cache of repositories

db = TinyDB(DB_PATH)
Repo = Query()

def get_repo_info(repo_name):
    """Get repository information from the server"""
    try:
        response = requests.get(f"{SERVER_URL}/pipe?repo={repo_name}")
        if response.status_code == 200:
            return response.json()
        else:
            click.echo(f"Error: {response.json().get('error', 'Unknown error')}", err=True)
            return None
    except requests.RequestException as e:
        click.echo(f"Connection error: {str(e)}", err=True)
        return None

def clone_repo(github_url, commit_hash, destination):
    """Clone a specific commit of a repository"""
    try:
        # Clone the repository
        click.echo(f"Cloning {github_url}...")
        subprocess.run(["git", "clone", github_url, destination], check=True, capture_output=True)
        
        # Checkout the specific commit
        click.echo(f"Checking out commit {commit_hash}...")
        subprocess.run(["git", "-C", destination, "checkout", commit_hash], check=True, capture_output=True)
        
        return True
    except subprocess.CalledProcessError as e:
        click.echo(f"Git operation failed: {e.stderr.decode()}", err=True)
        return False
    except Exception as e:
        click.echo(f"Failed to clone repository: {str(e)}", err=True)
        return False

@click.group()
def cli():
    """SPIP - Simple Package Installation Protocol"""
    pass

@cli.command()
@click.argument('repo_name')
@click.option('--destination', '-d', help='Destination directory (default: current directory)')
def install(repo_name, destination):
    """Install a package from the repository"""
    repo_info = get_repo_info(repo_name)
    
    if not repo_info:
        return
    
    # Use current directory if destination not specified
    dest_dir = destination or os.path.join(os.getcwd(), repo_name)
    
    github_url = repo_info.get('githuburl')
    commit_sha = repo_info.get('commit_sha')
    
    if not github_url or not commit_sha:
        click.echo("Missing GitHub URL or commit hash in repository data", err=True)
        return
    
    # Clone the repository directly to the destination
    if clone_repo(github_url, commit_sha, dest_dir):
        # Build the package
        try:
            click.echo(f"Installing package from {dest_dir}...")
            # Change to the cloned directory and install
            subprocess.run(
                ["pip", "install", "-e", "."],
                check=True,
                capture_output=True,
                cwd=dest_dir
            )
            
            click.echo(f"Successfully installed {repo_name}!")
            
            # Cache the repository information locally
            existing = db.search(Repo.repo == repo_name)
            if existing:
                db.update(repo_info, Repo.repo == repo_name)
            else:
                db.insert(repo_info)
                
            click.echo(f"Repository information cached locally.")
        except subprocess.CalledProcessError as e:
            click.echo(f"Installation failed: {e.stderr.decode()}", err=True)
            # Try alternate installation method
            try:
                click.echo("Trying alternate installation method...")
                subprocess.run(
                    ["pip", "install", "."],
                    check=True,
                    capture_output=True,
                    cwd=dest_dir
                )
                click.echo(f"Successfully installed {repo_name}!")
            except subprocess.CalledProcessError as e2:
                click.echo(f"Installation failed: {e2.stderr.decode()}", err=True)
        except Exception as e:
            click.echo(f"Error during installation: {str(e)}", err=True)

if __name__ == '__main__':
    cli()