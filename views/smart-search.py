import re
import time
import streamlit as st
import requests

from loguru import logger

from managers.github import get_repo_readme
from managers.openai_manager import chat_completion
from utils.prompt import RESEARCH_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT, TECHNICAL_ANALYST_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT, get_custom_summarise_prompt_openai, get_key_word_prompt_few_shots_openai, get_key_word_prompt_openai


@st.dialog("Raw Data")
def show_json(data):
    st.json(data, expanded=False)
    st.button("Close", key="close_raw_data_button")


st.title("🔍 GitHub Repository Search")
st.write("Search for GitHub repositories using the GitHub API.")
with st.expander("Your OpenAI API credentials details: (Set on the left)", expanded=False):
    st.markdown(
        f"Endpoint: `{st.session_state.endpoint}`\nAPI Key: `{st.session_state.api_key}`\nModel: `{st.session_state.model}`")
prompting_method = st.segmented_control(
    "Select a prompting method", ["Few-Shot", "Zero-Shot"], key="prompting_method", default="Few-Shot")

if "smart_search_user_input" not in st.session_state:
    st.session_state.smart_search_user_input = ""
st.session_state.smart_search_user_input = st.text_area(
    "What would you like to know today?", st.session_state.smart_search_user_input)
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
if st.button("Search"):
    logger.info(
        f"Searching for repositories with keywords: {selected_queries}")
    response = requests.get(
        "https://api.github.com/search/repositories", params={"q": selected_queries})

    try:
        response.raise_for_status()
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
        SUMMARIZE_PROMPTING_METHOD = [
            "Research Assistant Zero-Shot", "Technical Analyst Zero-Shot"]
        DEFAULT_SUMMARIZE_PROMPT = [
            RESEARCH_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT, TECHNICAL_ANALYST_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT]
        selected_summarize_prompting_method = st.segmented_control(
            "Select a prompting method", SUMMARIZE_PROMPTING_METHOD, key="summarize_prompting_method", default=SUMMARIZE_PROMPTING_METHOD[0])
        use_case = st.text_input("Enter your use case:",
                                 placeholder="What are you thinking?")

        if not st.session_state.get("compiled_prompt"):
            st.session_state.compiled_prompt = DEFAULT_SUMMARIZE_PROMPT[SUMMARIZE_PROMPTING_METHOD.index(
                selected_summarize_prompting_method)].format(use_case=use_case)
        if st.button("Create Summarise Prompt"):
            st.session_state.compiled_prompt = DEFAULT_SUMMARIZE_PROMPT[SUMMARIZE_PROMPTING_METHOD.index(
                selected_summarize_prompting_method)].format(use_case=use_case)
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
