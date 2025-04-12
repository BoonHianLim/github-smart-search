import base64
import requests


def get_repo_readme(repo_owner: str, repo_name: str) -> tuple[str, any]:
    """
    Fetches the README content of a GitHub repository.
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/readme"
    response = requests.get(url)
    response.raise_for_status()
    
    repo_data = response.json()
    readme_content_encoded: str = repo_data.get("content", "")
    readme_content = base64.b64decode(readme_content_encoded).decode("utf-8")
    return readme_content, repo_data
    