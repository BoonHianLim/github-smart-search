import time
import requests
import streamlit as st

from loguru import logger

from managers.github import get_repo_readme
from utils.prompt_method import LLM_PROMPTING_METHOD, SUMMARIZE_PROMPTING_METHOD, TEMPLATE_PROMPTING_METHOD
from utils.prompt import RESEARCH_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT, TECHNICAL_ANALYST_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT, get_custom_summarise_prompt_openai, get_key_word_prompt_few_shots_openai, get_key_word_prompt_openai, get_query_refinement_prompt_openai
from managers.openai_manager import chat_completion
TEMPLATE_PROMPTING_PROMPT = [
    RESEARCH_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT, TECHNICAL_ANALYST_ASSISTANT_ZERO_SHOT_SUMMARIZE_PROMPT]


def summarise_tab(compiled_prompt: str, 
                  repository_data: list[dict],
                  load_tabs: bool,
                  summarise_result: str,
                    readme_contents: list[str],
                  endpoint: str,
                  api_key: str,
                  model: str) -> str:
    endpoint = endpoint.strip()
    api_key = api_key.strip()
    model = model.strip()

    selected_summarize_prompting_method = st.segmented_control(
        "Select a prompting method", SUMMARIZE_PROMPTING_METHOD, key="summarize_prompting_method", default=SUMMARIZE_PROMPTING_METHOD[0])
    user_query = st.text_input("Enter your query:",
                                placeholder="What are you thinking?")

    if st.button("Create Summarise Prompt"):
        if not endpoint or not api_key or not model:
            st.error("Please enter your OpenAI API credentials.")
        elif selected_summarize_prompting_method in LLM_PROMPTING_METHOD:
            refine_request = get_query_refinement_prompt_openai(user_query)
            refine_response = chat_completion(
                endpoint=endpoint,
                api_key=api_key,
                model=model,
                prompt=refine_request,
            )
            compiled_prompt = refine_response
        elif selected_summarize_prompting_method in TEMPLATE_PROMPTING_METHOD:
            compiled_prompt = TEMPLATE_PROMPTING_PROMPT[TEMPLATE_PROMPTING_METHOD.index(
                selected_summarize_prompting_method)].format(use_case=user_query)
        else:
            compiled_prompt = user_query
    summarize_prompt = st.text_area(
        "Summarization Prompt:", compiled_prompt, height=200)

    if st.button("Summarize Now!"):
        if not endpoint or not api_key or not model:
            st.error("Please enter your OpenAI API credentials.")
        else:
            with st.spinner("Loading..."):
                readme_contents: list[str] = []
                repo_data_list: list[any] = []
                for item in repository_data:
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
                    endpoint=endpoint,
                    api_key=api_key,
                    model=model,
                    prompt=get_custom_summarise_prompt_openai(summarize_prompt,
                                                                readme_contents),
                )
                load_tabs = True

    if load_tabs:
        st.markdown("### Summarised Content")
        st.write(summarise_result)

        # collapsible sections for each repository
        with st.expander("Readme Contents", expanded=False):
            for i, item in enumerate(repository_data):
                st.markdown(
                    f"### [{item['name']}]({item['html_url']})")
                st.markdown(readme_contents[i])
                st.markdown("---")

    return compiled_prompt, summarise_result, readme_contents, load_tabs
