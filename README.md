# Demo Python With Azure
Sample project to play around Azure with Python containing Python standard project structure.

repository
  ├── LICENSE
  ├── README.md
  ├── src/
  │   └── package_name/
  ├── tests/
  ├── docs/
  ├── requirements.txt
  ├── azure-pipeline.yml
  ├── sonar-project.properties
  └── setup.py

# Features
## Python Docker Base Image
- Mandatory Labels
- Proxies if any to be configured
- Common requirements installation

## Python CI STPL
- Linting
- Versioning
- Unit Testing
- Code Coverage
- Static code quality scan e.g. SonarQube Scan
- Third party library vulnerability scanning e.g. NexusIQ
- Static code scanning for security issues e.g. Fortify Scan
- Publishing Artifact

## Docker CI/CD STPL
- Hadonlint Scan
- Container Build
- COntainer Structure Tests
- Static Security Scan e.g. PCC
- Smoke Test
- Versioning
- Optionally add extra docker tags
- Publishing to Registry
