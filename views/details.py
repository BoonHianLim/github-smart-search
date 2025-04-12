import base64
import streamlit as st
import requests

from managers.github import get_repo_readme


repo_owner = st.query_params.get("repo_owner")
repo_name = st.query_params.get("repo_name")

st.title("📄 Repository Details")

if not repo_owner or not repo_name:
    st.warning("No repository selected.")
    st.stop()  # Stop execution if no repo is selected

st.write(f"Showing details for: `{repo_owner}/{repo_name}`")

# Fetch and display repo details
readme_content, repo_data = get_repo_readme(repo_owner, repo_name)

st.markdown("---")


with st.expander("Repository Details", expanded=False):
    st.markdown(readme_content)
    st.json(repo_data, expanded=False)
