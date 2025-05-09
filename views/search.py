import streamlit as st

from managers.github import get_repos
from views.components.advanced_filters import advanced_filters
from views.components.repo_box import repo_box
from views.components.summarise import summarise_tab

st.title("🔍 GitHub Repository Search")
st.write("Search for GitHub repositories using the GitHub API.")
with st.expander("Your OpenAI API credentials details: (Set on the left)", expanded=False):
    st.markdown(
        f"Endpoint: `{st.session_state.endpoint}`\nAPI Key: `{st.session_state.api_key}`\nModel: `{st.session_state.model}`")


@st.dialog("Raw Data")
def show_json(data):
    st.json(data, expanded=False)
    st.button("Close", key="close_raw_data_button")


search_bar_col, search_btn_col = st.columns(
    [7, 1], vertical_alignment="bottom")
query = ""
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "best-match"
if "order_by" not in st.session_state:
    st.session_state.order_by = "desc"
if "per_page" not in st.session_state:
    st.session_state.per_page = 10

with search_bar_col:
    query = st.text_input("Enter your search query:",
                          placeholder="Search for repositories...")

with search_btn_col:
    search_selected = st.button("Search")
    if search_selected:
        try:
            if query:
                response = get_repos(query,
                                     per_page=st.session_state.per_page,
                                     sort=st.session_state.sort_by if st.session_state.sort_by != "best-match" else None,
                                     order=st.session_state.order_by)
                data = response.json()
                st.session_state.response_data = response.json()
                st.session_state.show_results = True
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.session_state.show_results = False

if search_selected and not query:
    st.warning("Please enter a search query.")

sort_by, order_by, per_page = advanced_filters()
st.session_state.update({
    "sort_by": sort_by,
    "order_by": order_by,
    "per_page": per_page,
})

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
        if not st.session_state.get("compiled_prompt"):
            st.session_state.compiled_prompt = ""
        if not st.session_state.get("load_tabs"):
            st.session_state.load_tabs = False
        if not st.session_state.get("readme_contents"):
            st.session_state.readme_contents = []
        if not st.session_state.get("summarise_result"):
            st.session_state.summarise_result = ""
        new_compiled_prompt, new_summarise_result, new_readme_content, load_tabs = summarise_tab(st.session_state.compiled_prompt,
                                                                                                 items,
                                                                                                 st.session_state.load_tabs,
                                                                                                 st.session_state.summarise_result,
                                                                                                 st.session_state.readme_contents,
                                                                                                 st.session_state.endpoint.strip(),
                                                                                                 st.session_state.api_key.strip(),
                                                                                                 st.session_state.model.strip())
        st.session_state.update({
            "compiled_prompt": new_compiled_prompt,
            "load_tabs": load_tabs,
            "readme_contents": new_readme_content,
            "summarise_result": new_summarise_result,
        })
