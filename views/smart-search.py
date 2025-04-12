import re
import time

import streamlit as st
import requests
from loguru import logger

from views.components.advanced_filters import advanced_filters
from views.components.repo_box import repo_box
from managers.github import get_repo_readme, get_repos
from managers.openai_manager import chat_completion
from utils.prompt import RESEARCH_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT, TECHNICAL_ANALYST_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT, get_custom_summarise_prompt_openai, get_key_word_prompt_few_shots_openai, get_key_word_prompt_openai, get_query_refinement_prompt_openai

SUMMARIZE_PROMPTING_METHOD = [
    "Normal"]
LLM_PROMPTING_METHOD = ["LLM: Query Refinement"]
TEMPLATE_PROMPTING_METHOD = [
    "Template: Research Assistant", "Template: Technical Analyst"]
SUMMARIZE_PROMPTING_METHOD.extend(LLM_PROMPTING_METHOD)
SUMMARIZE_PROMPTING_METHOD.extend(TEMPLATE_PROMPTING_METHOD)

TEMPLATE_PROMPTING_PROMPT = [
    RESEARCH_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT, TECHNICAL_ANALYST_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT]


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
                    repo_box(item, index)

    with tabs[1]:
        selected_summarize_prompting_method = st.segmented_control(
            "Select a prompting method", SUMMARIZE_PROMPTING_METHOD, key="summarize_prompting_method", default=SUMMARIZE_PROMPTING_METHOD[0])
        user_query = st.text_input("Enter your query:",
                                   placeholder="What are you thinking?")

        if not st.session_state.get("compiled_prompt"):
            st.session_state.compiled_prompt = ""
        if st.button("Create Summarise Prompt"):
            if selected_summarize_prompting_method in LLM_PROMPTING_METHOD:
                refine_request = get_query_refinement_prompt_openai(user_query)
                refine_response = chat_completion(
                    endpoint=st.session_state.endpoint.strip(),
                    api_key=st.session_state.api_key.strip(),
                    model=st.session_state.model.strip(),
                    prompt=refine_request,
                )
                st.session_state.compiled_prompt = refine_response
            elif selected_summarize_prompting_method in TEMPLATE_PROMPTING_METHOD:
                st.session_state.compiled_prompt = TEMPLATE_PROMPTING_PROMPT[TEMPLATE_PROMPTING_METHOD.index(
                    selected_summarize_prompting_method)].format(use_case=user_query)
            else:
                st.session_state.compiled_prompt = user_query
        summarize_prompt = st.text_area(
            "Summarization Prompt:", st.session_state.compiled_prompt, height=200)

        if st.button("Summarize Now!"):
            if not st.session_state.endpoint or not st.session_state.api_key or not st.session_state.model:
                st.error("Please enter your OpenAI API credentials.")
            else:
                with st.spinner("Loading..."):
                    readme_contents: list[str] = []
                    repo_data_list: list[any] = []
                    for item in items:
                        while True:
                            try:
                                repo_owner = item["owner"]["login"]
                                repo_name = item["name"]
                                readme_content, repo_data = get_repo_readme(
                                    repo_owner, repo_name)

                                readme_contents.append(readme_content)
                                repo_data_list.append(repo_data)
                                break
                            except requests.HTTPError as e:
                                if e.response.status_code == 404:
                                    logger.error(
                                        f"README not found for repository: {item['name']}")
                                    readme_contents.append("")
                                    repo_data_list.append({})
                                    break
                                elif e.response.status_code == 403:
                                    st.warning(
                                        f"Rate limit exceeded for repository: {item['name']}. Waiting for 30 seconds...")
                                    time.sleep(30)
                                    continue
                                else:
                                    logger.error(
                                        f"Error fetching README for repository: {item['name']}: {e}")
                                    readme_contents.append("")
                                    repo_data_list.append({})
                                    break
                            except Exception as e:
                                raise e

                    summarise_result = chat_completion(
                        endpoint=st.session_state.endpoint.strip(),
                        api_key=st.session_state.api_key.strip(),
                        model=st.session_state.model.strip(),
                        prompt=get_custom_summarise_prompt_openai(summarize_prompt,
                                                                  readme_contents),
                    )
                    st.session_state.summarise_result = summarise_result
                    st.session_state.readme_contents = readme_contents
                    st.session_state.load_tabs["Summarise"] = True

        if st.session_state.load_tabs["Summarise"]:
            st.markdown("### Summarised Content")
            st.write(st.session_state.summarise_result)

            # collapsible sections for each repository
            with st.expander("Readme Contents", expanded=False):
                for i, item in enumerate(items):
                    st.markdown(
                        f"### [{item['name']}]({item['html_url']})")
                    st.markdown(st.session_state.readme_contents[i])
                    st.markdown("---")
