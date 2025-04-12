import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

smart_search_page = st.Page(
    page="views/smart-search.py",
    title="Smart Search",
    icon="🔍",
    default=True,
)
search_page = st.Page(
    page="views/search.py",
    title="Search",
    icon="🔍",
)

repo_details_page = st.Page(
    page="views/details.py",
    title="Details",
    icon="📄",
)

endpoint = st.sidebar.text_input(
    "OpenAI-Compatible / Azure Endpoint",
    value="https://api.openai.com/v1",
)
api_key = st.sidebar.text_input(
    "API Key",
    type="password",
    placeholder="sk-...",
)
model = st.sidebar.selectbox(
    "Model",
    options=["gpt-4o", "deepseek-chat", "Other (Please specify)"],
    index=0,
)
if model == "Other (Please specify)":
    model = st.sidebar.text_input(
        "Other Model",
        placeholder="gpt-3.5-turbo",
    )
st.sidebar.button(
    "Set API Credentials",
    on_click=lambda: st.session_state.update({
        "endpoint": endpoint,
        "api_key": api_key,
        "model": model,
    })
)
st.session_state.update({
    "endpoint": endpoint,
    "api_key": api_key,
    "model": model,
})


pg = st.navigation(
    pages=[
        smart_search_page,
        repo_details_page
    ]
)

pg.run()
