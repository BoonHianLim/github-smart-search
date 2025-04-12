import time
import streamlit as st
import requests

from managers.openai_manager import chat_completion
from utils.prompt import get_summarise_prompt_openai
st.title("🔍 GitHub Repository Search")
st.write("Search for GitHub repositories using the GitHub API.")

query = st.text_input("Enter your search query:",
                      placeholder="Search for repositories...")


@st.dialog("Raw Data")
def show_json(data):
    st.json(data, expanded=False)
    st.button("Close", key="close_raw_data_button")


if st.button("Search"):
    response = requests.get(
        "https://api.github.com/search/repositories", params={"q": query})

    try:
        response.raise_for_status()
        data = response.json()
        st.session_state.response_data = response.json()
        st.session_state.show_results = True
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.session_state.show_results = False

if st.session_state.get("show_results", False):
    data = st.session_state.response_data
    items = data.get("items", [])

    st.markdown("---")
    subheader_title_col, subheader_button_col = st.columns([6, 1])
    with subheader_title_col:
        st.subheader("📬 Search Results")
    with subheader_button_col:
        if st.button("Raw Data", key="raw_data_button"):
            show_json(data)
    st.write("Found **{}** repositories.".format(
        data.get("total_count", 0)))

    tabs = st.tabs(["Main", "Summarise"])
    # Store if sub-tabs are "loaded"
    if "load_tabs" not in st.session_state:
        st.session_state.load_tabs = {"Summarise": False}

    with tabs[0]:
        if not items:
            st.warning("No results found.")
        else:
            cols = st.columns(2)  # 2 columns for the grid
            for index, item in enumerate(items):
                with cols[index % 2]:  # Alternate between col 0 and col 1
                    with st.container(height=300):
                        st.markdown(
                            f"### [{item['name']}]({item['html_url']})")
                        st.write(item['description'] or "No description.")
                        st.caption(
                            f"⭐ {item['stargazers_count']} stars | 🧑‍💻 {item['owner']['login']}")

                        repo_owner = item["owner"]["login"]
                        repo_name = item["name"]
                        url = f"/details?repo_owner={repo_owner}&repo_name={repo_name}"

                        if st.button("Details", key=f"details_{index}"):
                            # Create link to the Details page
                            st.markdown(
                                f'<meta http-equiv="refresh" content="0; URL={url}">', unsafe_allow_html=True)

    with tabs[1]:
        with st.expander("Your OpenAI API credentials details: (Set on the left)", expanded=False):
            st.markdown(
                f"Endpoint: `{st.session_state.endpoint}`\nAPI Key: `{st.session_state.api_key}`\nModel: `{st.session_state.model}`")
        if st.button("Load Summarise Content"):

            if not st.session_state.endpoint or not st.session_state.api_key or not st.session_state.model:
                st.error("Please enter your OpenAI API credentials.")
            else:
                with st.spinner("Loading..."):

                    summarise_result = chat_completion(
                        endpoint=st.session_state.endpoint.strip(),
                        api_key=st.session_state.api_key.strip(),
                        model=st.session_state.model.strip(),
                        prompt=get_summarise_prompt_openai(
                            [item["description"] for item in items if item["description"]]),
                    )
                    st.session_state.summarise_result = summarise_result
                    st.session_state.load_tabs["Summarise"] = True

        if st.session_state.load_tabs["Summarise"]:
            st.markdown("### Summarised Content")
            st.write(st.session_state.summarise_result)
