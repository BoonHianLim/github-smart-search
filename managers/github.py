import base64
from typing import Literal
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


def get_repos(query: str, 
              sort: Literal["stars", "forks", "help-wanted-issues", "updated"] = None, 
              order: Literal["asc", "desc"] = "desc",
              per_page: int = 30,
              page: int = 1) -> requests.Response:
    """
    Fetches GitHub repositories based on a search query.
    """
    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "order": order,
        "per_page": per_page,
        "page": page,
    }
    if sort:
        params["sort"] = sort
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response
