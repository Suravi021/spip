from flask import Flask, render_template, request, jsonify
from tinydb import TinyDB, Query
import requests
import subprocess

github_token = None 

app = Flask(__name__)
db = TinyDB("repos.json")

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        USERNAME = request.form.get("USERNAME")  # Get input from form
        REPO = request.form.get("REPO")
        GITHUB_TOKEN = request.form.get("PRIVATE")
        return f"You entered: {USERNAME}" # return a html page
    return render_template("Pypi.html", title="About Us")


@app.route("/receive", methods=["POST"])
def receive_string():
    data = request.json
    
    # Format the data for the template - passing each field directly
    package_name = data.get("repo", "")
    githubReputationScore = calculate_reputation_score(data.get("reputation", "{}"))
    commitHash = data.get("commit_sha", "")
    banditReport = parse_bandit_report(data.get("bandit_output", ""))
    gitUrl = data.get("githuburl", "")
    repoHash = data.get("commit_sha", "")  # Using commit_sha as repo_hash if not available
    username = data.get("github_user", "")
    email = data.get("github_email", "")
    readme = data.get("ReadMe", "No README available")
    
    # Pass each variable to the template individually
    return render_template("Packages.html", 
                          package_name=package_name,
                          githubReputationScore=int(githubReputationScore),
                          commitHash=commitHash,
                          banditReport=banditReport,
                          gitUrl=gitUrl,
                          repoHash=repoHash,
                          username=username,
                          email=email,
                          readme=readme)

def calculate_reputation_score(reputation_str):
    """Calculate a reputation score from 0-100 based on GitHub metrics"""
    try:
        reputation = eval(reputation_str)
        stars = reputation.get("stars", 0)
        forks = reputation.get("forks", 0)
        issues = reputation.get("open_issues", 0)
        
        # Simple formula: (stars*5 + forks*3) with max of 100
        # Reduce score slightly for many open issues
        score = min(100, (stars * 5 + forks * 3) - (issues * 0.5))
        return max(0, int(score))
    except:
        return 0

def parse_bandit_report(bandit_output):
    """Parse the bandit output to extract high, medium, low counts"""
    high, medium, low = 0, 0, 0
    
    if "stdout" in bandit_output:
        try:
            # Try to extract using regex or string parsing
            import re
            
            # Look for patterns like "Low: 0" in the output
            high_match = re.search(r"High: (\d+)", bandit_output)
            if high_match:
                high = int(high_match.group(1))
                
            medium_match = re.search(r"Medium: (\d+)", bandit_output)
            if medium_match:
                medium = int(medium_match.group(1))
                
            low_match = re.search(r"Low: (\d+)", bandit_output)
            if low_match:
                low = int(low_match.group(1))
        except:
            pass
    
    return {
        "high": high,
        "medium": medium,
        "low": low
    }

@app.errorhandler(404)
def page_not_found(error):
    package_name = str(request.path)[1:]  # Get the requested URL that caused 404

    User = Query()
    result = db.search(User.package_name == package_name)
    if result:
        return render_template("Package.html", repos=result)
    else:
        return "sorry its not a package that has been approved of"


if __name__ == "__main__":
    app.run(debug=True)
