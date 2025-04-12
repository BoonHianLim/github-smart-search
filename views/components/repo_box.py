import streamlit as st

def repo_box(item: dict[str, any], index: int) -> None:
    """
    Displays a box for a GitHub repository with its details and a button to view more information.
    """
    with st.container(height=350):
        st.markdown(
            f"### [{item['name']}]({item['html_url']})")
        st.caption(f"🧑‍💻 {item['owner']['login']}")
        st.write(item['description'] or "No description.")
        st.caption(
            f"⭐ {item['stargazers_count']} stars | 𐂐 {item['forks_count']} forks |❗{item['open_issues_count']} issues")
        st.caption(
            f"⏳ {item['pushed_at']}")

        repo_owner = item["owner"]["login"]
        repo_name = item["name"]
        url = f"/details?repo_owner={repo_owner}&repo_name={repo_name}"

        if st.button("Details", key=f"details_{index}"):
            # Create link to the Details page
            st.markdown(
                f'<meta http-equiv="refresh" content="0; URL={url}">', unsafe_allow_html=True)
