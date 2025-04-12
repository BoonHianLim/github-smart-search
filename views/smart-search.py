import re

import streamlit as st
from loguru import logger

from views.components.advanced_filters import advanced_filters
from views.components.repo_box import repo_box
from managers.github import get_repo_readme, get_repos
from managers.openai_manager import chat_completion
from utils.prompt import get_key_word_prompt_few_shots_openai, get_key_word_prompt_openai
from views.components.summarise import summarise_tab


@st.dialog("Raw Data")
def show_json(data):
    st.json(data, expanded=False)
    st.button("Close", key="close_raw_data_button")


st.title("GitHub Repository Smart Search 🧠🔍 ")
st.write("Search for GitHub repositories using the GitHub API.")
with st.expander("Your OpenAI API credentials details: (Set on the left)", expanded=False):
    st.markdown(
        f"Endpoint: `{st.session_state.endpoint}`\nAPI Key: `{st.session_state.api_key}`\nModel: `{st.session_state.model}`")
prompting_method = st.segmented_control(
    "Select a prompting method", ["Few-Shot", "Zero-Shot"], key="prompting_method", default="Few-Shot")

if "smart_search_user_input" not in st.session_state:
    st.session_state.smart_search_user_input = ""

search_bar_col, search_btn_col = st.columns(
    [7, 1], vertical_alignment="bottom")
with search_bar_col:
    st.session_state.smart_search_user_input = st.text_area(
        "What would you like to know today?", st.session_state.smart_search_user_input)
with search_btn_col:
    if st.button("Extract"):
        if st.session_state.smart_search_user_input:
            if prompting_method == "Few-Shot":
                keywords = chat_completion(
                    endpoint=st.session_state.endpoint.strip(),
                    api_key=st.session_state.api_key.strip(),
                    model=st.session_state.model.strip(),
                    prompt=get_key_word_prompt_few_shots_openai(
                        st.session_state.smart_search_user_input),
                )
                keywords = re.sub(
                    r'^Keywords:\s*', '', keywords, flags=re.IGNORECASE).strip()
            else:
                keywords = chat_completion(
                    endpoint=st.session_state.endpoint.strip(),
                    api_key=st.session_state.api_key.strip(),
                    model=st.session_state.model.strip(),
                    prompt=get_key_word_prompt_openai(
                        st.session_state.smart_search_user_input),
                )
            st.session_state.smart_search_keywords = keywords.split(",")
        else:
            st.warning("Please enter a query to extract keywords.")

if not st.session_state.get("smart_search_keywords"):
    st.stop()

selected_queries = st.pills(
    "Keywords", st.session_state.get("smart_search_keywords", []), selection_mode="single", key="keywords_pills", default=st.session_state.smart_search_keywords[0])
sort_by, order_by, per_page = advanced_filters()

if st.button("Search"):
    logger.info(
        f"Searching for repositories with keywords: {selected_queries}")
    if not selected_queries:
        st.warning("Please select a keyword to search.")
    else:
        try:
            response = get_repos(selected_queries, per_page=per_page,
                                 sort=sort_by if sort_by != "best-match" else None,
                                 order=order_by)
            data = response.json()
            st.session_state.smart_search_response_data = response.json()
            st.session_state.smart_search_show_results = True
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.session_state.smart_search_show_results = False

if st.session_state.get("smart_search_show_results", False):
    data = st.session_state.smart_search_response_data
    items = data.get("items", [])

    st.markdown("---")
    subheader_title_col, subheader_button_col = st.columns([6, 1])
    with subheader_title_col:
        st.subheader("📬 Search Results")
    with subheader_button_col:
        if st.button("Raw Data", key="raw_data_button"):
            show_json(data)
    st.write("Found **{}** out of {} repositories.".format(
        len(items), data.get("total_count", 0)))

    tabs = st.tabs(["Main", "Summarise"])

    with tabs[0]:
        if not items:
            st.warning("No results found.")
        else:
            cols = st.columns(2)  # 2 columns for the grid
            for index, item in enumerate(items):
                with cols[index % 2]:  # Alternate between col 0 and col 1
                    repo_box(item, index)

    with tabs[1]:
        if not st.session_state.get("smart_search_compiled_prompt"):
            st.session_state.smart_search_compiled_prompt = ""
        if not st.session_state.get("smart_search_load_tabs"):
            st.session_state.smart_search_load_tabs = False
        if not st.session_state.get("smart_search_readme_contents"):
            st.session_state.smart_search_readme_contents = []
        if not st.session_state.get("smart_search_summarise_result"):
            st.session_state.smart_search_summarise_result = ""
        new_compiled_prompt, new_summarise_result, new_readme_content, load_tabs = summarise_tab(st.session_state.smart_search_compiled_prompt,
                                                                                                 items,
                                                                                                 st.session_state.smart_search_load_tabs,
                                                                                                 st.session_state.smart_search_summarise_result,
                                                                                                 st.session_state.smart_search_readme_contents,
                                                                                                 st.session_state.endpoint.strip(),
                                                                                                 st.session_state.api_key.strip(),
                                                                                                 st.session_state.model.strip())
        st.session_state.update({
            "smart_search_compiled_prompt": new_compiled_prompt,
            "smart_search_load_tabs": load_tabs,
            "smart_search_readme_contents": new_readme_content,
            "smart_search_summarise_result": new_summarise_result,
        })
