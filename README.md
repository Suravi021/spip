# SPIP & Novatwine: Secure Python Package Ecosystem

> A secure alternative to the Python package management system with built-in security analysis and reputation scoring.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

SPIP (Secure Package Installer for Python) and Novatwine form a comprehensive ecosystem for secure Python package distribution, analysis, and installation. The system includes three main components that work together:

1. **SPIP**: A secure alternative to pip that installs packages from verified commits
2. **Novatwine**: A package upload and security analysis tool
3. **SPyPi Web Server**: Repository server with web interface and metadata storage

![flow](https://raw.githubusercontent.com/Suravi021/spip/refs/heads/main/webserver/static/flow.png)
## Key Features

- **Security-First Approach**: Static code analysis with Bandit for all packages
- **Reputation System**: Package scoring based on GitHub metrics and security analysis
- **Version Pinning**: Exact commit-based installation prevents supply chain attacks
- **Transparency**: Full security reports and metadata accessible through web interface
- **GitHub Integration**: Leverages repository data for reputation scoring

## Components

### 1. SPIP (Secure Package Installer for Python)

SPIP is the client-side tool that securely installs Python packages. Unlike traditional pip, SPIP:

- Clones repositories at the exact commit that was analyzed
- Builds packages directly from source code
- Ensures what you install is precisely what was security-checked

#### Usage

```bash
spip install <package_name>
```

### 2. Novatwine (Package Upload & Analysis Tool)

Novatwine handles the uploading and security analysis of packages:

- Performs static code analysis using Bandit
- Collects GitHub metrics (stars, forks, issues)
- Generates reputation scores
- Uploads package metadata to SPyPi servers

#### Configuration

Novatwine requires a `nt.toml` configuration file:

```toml
[personal]
username = 'username'
email = 'maintaineremail@mail.com'
github = 'https://github.com/username/repo'
description_path = 'README.md'
directory_path = 'package_dir'
```

#### Usage

```bash
python -m novatwine upload -c nt.toml
```

### 3. SPyPi Web Server

The web server component provides:

- Package repository functionality
- Web interface for browsing packages
- Security reports and reputation scores
- API endpoints for SPIP and Novatwine

![Web Interface](https://raw.githubusercontent.com/Suravi021/spip/refs/heads/main/webserver/static/webui.png)

#### Web Interface Features

- Package information and installation command
- Author and repository details
- Static analysis security report
- README content
- Reputation score with visual indicator

## Metadata Storage

The system stores comprehensive metadata for each package in JSON format:

```json
{
  "1": {
    "repo": "tinyrag",
    "username": "divine-architect",
    "githuburl": "https://github.com/divine-architect/tinyrag",
    "github_user": "divine-architect",
    "github_email": "mymail@mail.org",
    "bandit_output": "CompletedProcess(args=['bandit', '-r', 'tinyrag', '-f', 'txt'], returncode=0, stdout='Run started:2025-03-01 18:16:25.106587\\n\\nTest results:\\n\\tNo issues identified.\\n\\nCode scanned:\\n\\tTotal lines of code: 110\\n\\tTotal lines skipped (#nosec): 0\\n\\tTotal potential issues skipped due to specifically being disabled (e.g., #nosec BXXX): 0\\n\\nRun metrics:\\n\\tTotal issues (by severity):\\n\\t\\tUndefined: 0\\n\\t\\tLow: 0\\n\\t\\tMedium: 0\\n\\t\\tHigh: 0\\n\\tTotal issues (by confidence):\\n\\t\\tUndefined: 0\\n\\t\\tLow: 0\\n\\t\\tMedium: 0\\n\\t\\tHigh: 0\\nFiles skipped (0):\\n', stderr='[main]\\tINFO\\tprofile include tests: None\\n[main]\\tINFO\\tprofile exclude tests: None\\n[main]\\tINFO\\tcli include tests: None\\n[main]\\tINFO\\tcli exclude tests: None\\n[main]\\tINFO\\trunning on Python 3.12.8\\n')",
    "commit_sha": "c3db1760bc00fbc3ece2752bce342d9a3febd15b",
    "reputation": "{'stars': 1, 'forks': 0, 'open_issues': 0}",
    "ReadMe": "<h1>H1</h1>\n",
    "timestamp": "2025-03-01T23:46:25.138967"
  }
}
```

### Metadata Fields

| Field | Description |
|-------|-------------|
| `repo` | Package/repository name |
| `username` | GitHub username of the maintainer |
| `githuburl` | Full URL to the GitHub repository |
| `github_user` | Same as username (for redundancy) |
| `github_email` | Maintainer's email address |
| `bandit_output` | Complete output from Bandit security scan |
| `commit_sha` | Specific commit that was analyzed |
| `reputation` | GitHub metrics (stars, forks, open issues) |
| `ReadMe` | HTML-formatted README content |
| `timestamp` | Date and time when the package was uploaded |

## How It Works

1. **Package Upload Flow**:
   - Maintainer configures `nt.toml` with package and repository details
   - Novatwine uploads the package to SPyPi servers
   - Static security analysis is performed using Bandit
   - GitHub metrics are collected
   - Reputation score is calculated
   - Package metadata is stored on the server

2. **Package Installation Flow**:
   - User requests a package via `spip install <package>`
   - SPIP connects to SPyPi server for package information
   - Server returns the GitHub repository URL and specific commit SHA
   - SPIP git clones the repository at the exact commit that was analyzed
   - Package is built and installed from the verified source code

3. **Security Scoring**:
   - Static code analysis identifies potential vulnerabilities
   - GitHub metrics indicate community trust and activity
   - Combined score (0-100) provides at-a-glance security assessment
   - Low scores warn users but don't prevent installation

## Installation

*Installation instructions coming soon*

## Getting Started

### Prerequisites

- Python 3.8+
- Git

### Install SPIP

```bash
# Coming soon
```

### Upload a Package with Novatwine

1. Create a `nt.toml` file:

```toml
[personal]
username = 'your-github-username'
email = 'your-email@example.com'
github = 'https://github.com/your-username/your-repo'
description_path = 'README.md'
directory_path = 'your-package-dir'
```

2. Run the upload command:

```bash
python -m novatwine upload -c nt.toml
```

3. Check your package on the SPyPi web interface.

## Current Limitations

- Only basic installation (`spip install`) and upload commands are supported
- Dynamic analysis is planned but not yet implemented
- Package dependency resolution is limited

## Roadmap

- [ ] Dynamic code analysis
- [ ] Dependency resolution with security verification
- [ ] Additional SPIP commands (update, uninstall, etc.)
- [ ] Enhanced reputation scoring algorithms
- [ ] Improved web interface

## License

This project is licensed under the MIT License - see the LICENSE file for details.

```
MIT License The knights of eastern calculus

Copyright (c) 2025 SPIP and Novatwine Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Contributing

Contributions are welcome! More information on how to contribute will be provided soon.

## Support

For support inquiries and issue reporting, please open an issue in the GitHub repository.
