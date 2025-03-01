from flask import Flask, render_template, request, jsonify
from tinydb import TinyDB, Query
import datetime
import re

app = Flask(__name__)
db = TinyDB("repos.json")

@app.route("/", methods=["GET"])
def home():
    # Display the main page with all packages
    packages = db.all()
    return render_template("Pypi.html", title="Repository Security Analysis", packages=packages)

@app.route("/receive", methods=["POST"])
def receive_data():
    """Endpoint to receive data from the client script"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    
    # Add timestamp
    data["timestamp"] = datetime.datetime.now().isoformat()
    
    # Get package name
    package_name = data.get("repo", "")
    
    if not package_name:
        return jsonify({"error": "Missing repository name"}), 400
    
    # Store in database
    User = Query()
    existing = db.search(User.repo == package_name)
    
    if existing:
        # Update existing record
        db.update(data, User.repo == package_name)
    else:
        # Insert new record
        db.insert(data)
    
    return jsonify({"status": "success", "message": f"Data for {package_name} received and stored"}), 200

@app.route("/<package_name>", methods=["GET"])
def view_package(package_name):
    """View details of a specific package"""
    User = Query()
    result = db.search(User.repo == package_name)
    
    if result:
        data = result[0]
        
        # Format data for template
        try:
            reputation_score = calculate_reputation_score(data.get("reputation", "{}"))
            bandit_report = data.get("bandit_output", "")
            # things = ["Test results", "Code scanned"]
            bandit_report = str(bandit_report)
            bandit_report = bandit_report[bandit_report.find('Test results:'):]
            bandit_report = bandit_report.replace(r'\n', '<br>')
            bandit_report = bandit_report.replace(r'\t', '&emsp;')

            n = int(reputation_score)

            return render_template("Packages.html", 
                                  package_name=package_name,
                                  score=n,
                                  commitHash=data.get("commit_sha", ""),
                                  banditReport=bandit_report,
                                  gitUrl=data.get("githuburl", ""),
                                  repoHash=data.get("commit_sha", ""),
                                  username=data.get("github_user", ""),
                                  email=data.get("github_email", ""),
                                  readme=data.get("ReadMe", "No README available"))
        except Exception as e:
            return f"Error formatting data: {str(e)}", 500
    else:
        return "Sorry, this package has not been approved or doesn't exist", 404

def calculate_reputation_score(reputation_str):
    """Calculate a reputation score from 0-100 based on GitHub metrics"""
    try:
        if isinstance(reputation_str, str):
            reputation = eval(reputation_str)
        else:
            reputation = reputation_str
            
        stars = reputation.get("stars", 0)
        forks = reputation.get("forks", 0)
        issues = reputation.get("open_issues", 0)
        
        # Simple formula: (stars*5 + forks*3) with max of 100
        # Reduce score slightly for many open issues
        score = min(100, (stars * 5 + forks * 3) - (issues * 0.5))
        return max(0, int(score))
    except Exception as e:
        print(f"Error calculating reputation: {str(e)}")
        return 0




@app.errorhandler(404)
def page_not_found(error):
    package_name = str(request.path)[1:]  # Get the requested URL that caused 404

    User = Query()
    result = db.search(User.repo == package_name)
    if result:
        return view_package(package_name)
    else:
        return "Sorry, this package has not been approved or doesn't exist", 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)
