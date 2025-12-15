# uv run streamlit run try_streamlit/entrypoint.py
# PHTONPATH=try_streamlit 也就是从脚本所在的目录开始查找python模块
# 1. Create an entry point script that defines and connects your pages
# 2. Create separate Python files for each page's content
# 3. Use st.Page to define your pages and st.navigation to connect them

import streamlit as st

# Define the pages
main_page = st.Page("main_page.py", title="Main Page", icon="🎈")
page_2 = st.Page("page_2.py", title="Page 2", icon="❄️")
page_3 = st.Page("page_3.py", title="Page 3", icon="🎉")

# Set up navigation
pg = st.navigation([main_page, page_2, page_3])

# Run the selected page
pg.run()
