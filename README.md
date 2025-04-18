# GitHub Repository Smart Search 🧠🔍

This project is a **Streamlit-based web application** that allows users to search for GitHub repositories using the GitHub API. It leverages OpenAI's language models to enhance search capabilities with features like keyword extraction, advanced filtering, and summarization of repository content.

## Features

- **Smart Search**: Extracts keywords from user queries using OpenAI's API and performs GitHub repository searches.
- **Advanced Filters**: Sort and filter repositories by stars, forks, issues, and more.
- **Summarization**: Summarizes README files of repositories using OpenAI's language models.
- **Repository Details**: View detailed information about a selected repository, including its README content.
- **Customizable API Credentials**: Supports OpenAI-compatible and Azure OpenAI endpoints.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/BoonHianLim/github-smart-search.git
   cd github-smart-search
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   streamlit run main.py
   ```

## Usage

1. Open the application in your browser (default: `http://localhost:8501`).
2. Set your OpenAI API credentials in the sidebar.
3. Navigate between the following pages:
   - **Smart Search**: Extract keywords and search for repositories.
   - **Search**: Perform a direct search for repositories.
   - **Details**: View detailed information about a specific repository.

## File Structure

- **`main.py`**: Entry point for the Streamlit application.
- **`views`**: Contains the UI components and pages.
  - [smart-search.py](views/smart-search.py): Implements the smart search functionality.
  - [search.py](views/search.py): Implements the basic search functionality.
  - [details.py](views/details.py): Displays repository details.
  - `components/`: Reusable UI components (e.g., filters, repo boxes).
- **`managers`**: Handles API interactions (e.g., GitHub, OpenAI).
- **`utils`**: Utility functions and prompt templates.
- **`requirements.txt`**: Python dependencies.
- **`start.bat` / `start.sh`**: Scripts to start the application on Windows/Linux.

## Configuration

- **API Credentials**: Add your OpenAI or Azure OpenAI credentials in the sidebar or in credentials.txt.
- **Models**: Supports multiple OpenAI models, including custom ones.

## Example Prompts

- "I am a researcher interested in frontend UI generation from designs or sketches. I need to know the frontier knowledge about this area."
- "I am a student studying SC4052 cloud computing in NTU, and I want to know what the seniors do for their assignment 1."
- "I am a developer interested in frameworks or tools to build a web prototype for my hackathon."

## Requirements

- Python 3.8+
- Dependencies listed in [requirements.txt](requirements.txt)

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/)
- [OpenAI](https://openai.com/)
- [GitHub API](https://docs.github.com/en/rest)

Enjoy exploring GitHub repositories with enhanced search capabilities! 🎉