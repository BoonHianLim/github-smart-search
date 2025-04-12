
import streamlit as st

def advanced_filters():
    """Advanced filters for the GitHub repositories search."""
    with st.expander("Advanced Filters", expanded=False):
        sort_by = st.segmented_control(
            "Sort by", ["best-match", "stars", "forks", "help-wanted-issues", "updated"], key="sort_by_segment", default="best-match")
        order_by = st.segmented_control(
            "Order by", ["asc", "desc"], key="order_by_segment", default="desc")
        per_page = st.number_input(
            "Results per page", min_value=1, max_value=30, value=10, step=1, key="per_page_input")
        return sort_by, order_by, per_page
