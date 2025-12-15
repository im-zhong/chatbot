import streamlit as st

# Main page content
st.markdown("# Main page 🎈")
st.sidebar.markdown("# Main page 🎈")

# 2025/12/15
# zhangzhong
# https://docs.streamlit.io/get-started/fundamentals/main-concepts

## Data flow
# any time something must be updated on the screen, Streamlit reruns your entire Python script from top to bottom.
#   - Whenever you modify your app's source code.
#   - Whenever a user interacts with widgets in the app. For example, when dragging a slider, entering text in an input box, or clicking a button.
# callback?
# The @st.cache_data decorator, which allows developers to skip certain costly computations when their apps rerun.

import streamlit as st
import random
import time
import streamlit as st
import pandas as pd
import numpy as np

df = pd.DataFrame({"first column": [1, 2, 3, 4], "second column": [10, 20, 30, 40]})

# Any time that Streamlit sees a variable or a literal value on its own line,
# it automatically writes that to your app using st.write().
df

# You can pass almost anything to st.write(): text, data, Matplotlib figures, Altair charts, and more.
# treamlit will figure it out and render things the right way.
st.write("Here's our first attempt at using data to create a table:")
st.write(
    pd.DataFrame({"first column": [1, 2, 3, 4], "second column": [10, 20, 30, 40]})
)

## Write a data frame
# There are other data specific functions like st.dataframe() and st.table() that you can also use for displaying data.
# Use when you want more control
dataframe = np.random.randn(10, 20)
st.dataframe(dataframe)

dataframe = pd.DataFrame(
    np.random.randn(10, 20), columns=("col %d" % i for i in range(20))
)
st.dataframe(dataframe.style.highlight_max(axis=0))

dataframe = pd.DataFrame(
    np.random.randn(10, 20), columns=("col %d" % i for i in range(20))
)
st.table(dataframe)


## Draw charts and maps
# Streamlit supports several popular data charting libraries like Matplotlib, Altair, deck.gl, and more.

chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
st.line_chart(chart_data)

# With st.map() you can display data points on a map.
# 因为数据是经纬度，所以自动加载了一张世界地图
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4], columns=["lat", "lon"]
)
st.map(map_data)

## Weights
# When you've got the data or model into the state that you want to explore,
# you can add in widgets like st.slider(), st.button() or st.selectbox().
# treat widgets as variables:
# Dataflow:
#   - On first run, the app above should output the text "0 squared is 0".
#   - Then every time a user interacts with a widget,
#   - Streamlit simply reruns your script from top to bottom,
#   - assigning the current state of the widget to your variable in the process.
# 这个有点像react的组件重新渲染的概念
x = st.slider("x")  # 👈 this is a widget
st.write(x, "squared is", x * x)


# Widgets can also be accessed by key, if you choose to specify a string to use as the unique key for the widget:
st.text_input("Your name", key="name")
# You can access the value at any point with:
st.session_state.name

# Use checkboxes to show/hide data
if st.checkbox("Show dataframe"):
    chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
    # implicit st.write
    chart_data

# Use st.selectbox to choose from a series.
# You can write in the options you want, or pass through an array or data frame column.
df = pd.DataFrame({"first column": [1, 2, 3, 4], "second column": [10, 20, 30, 40]})
option = st.selectbox("Which number do you like best?", df["first column"])
"You selected: ", option


## Layout
# Streamlit makes it easy to organize your widgets in a left panel sidebar with st.sidebar
# Each element that's passed to st.sidebar is pinned to the left
# For example, if you want to add a selectbox and a slider to a sidebar, use st.sidebar.slider and st.sidebar.selectbox instead of st.slider and st.selectbox:
# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?", ("Email", "Home phone", "Mobile phone")
)
# Add a slider to the sidebar:
add_slider = st.sidebar.slider("Select a range of values", 0.0, 100.0, (25.0, 75.0))


# st.columns lets you place widgets side-by-side
left_column, right_column = st.columns(2)
# You can use a column just like st.sidebar:
left_column.button("Press me on left side")
# Or even better, call Streamlit functions inside a "with" block:
with right_column:
    chosen = st.radio(
        "Sorting hat", ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin")
    )
    st.write(f"You are in {chosen} house!")
# echo?
# spinner?
# expander?

## Show progress
"Starting a long computation..."

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

# for i in range(100):
#     # Update the progress bar with each iteration.
#     latest_iteration.text(f"Iteration {i + 1}")
#     bar.progress(i + 1)
#     time.sleep(0.1)

"...and now we're done!"

## Caching and Session State
# https://docs.streamlit.io/get-started/fundamentals/advanced-concepts
# Caching allows you to save the [output of a function] so you can [skip over it on rerun]
# Session State lets you save [information for each user] that is [preserved between reruns]

## Caching
# The basic idea behind caching is to store the results of expensive function calls
# and return the cached result when the [same inputs occur again].
# - st.cache_data: It creates a new copy of the data at each function call
# - st.cache_resource: It returns the cached object itself, If you mutate an object that is cached using st.cache_resource, that mutation will exist across all reruns and sessions.

## Session State
# Session State provides a [dictionary-like interface]where you can save information that is [preserved between script reruns].
# st.session_state["my_key"] or st.session_state.my_key
# - A session is a single instance of viewing an app.
# - If you view an app from two different tabs in your browser, each tab will have its own session
# - If the user refreshes their browser page or reloads the URL to the app, their Session State resets and they begin again with a new session.

# used for random seek, so when user interact with page, random data do not change
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(np.random.randn(20, 2), columns=["x", "y"])

st.header("Choose a datapoint color")
color = st.color_picker("Color", "#FF0000")
st.divider()
st.scatter_chart(st.session_state.df, x="x", y="y", color=color)

# first run:
# - The first time the app runs for each user, Session State is empty.
# - Therefore, a key-value pair is created ("counter":0)
if "counter" not in st.session_state:
    st.session_state.counter = 0

# As the script continues, the counter is immediately incremented ("counter":1) and the result is displayed:
# "This page has run 1 times."
st.session_state.counter += 1

# click the button, trigger a rerun, but now the "counter" is in the session state, so it will not be set to zero
# then counter+=1, now counter is 2
# click, rerun, +1 ...
# until we refresh the page, counter will be reset to 0
st.header(f"This page has run {st.session_state.counter} times.")
st.button("Run it again")

## Connections
# st.connection for sql connection


## Static file serving
# on static/

## Apping testing with pytest

## Additional features
# https://docs.streamlit.io/get-started/fundamentals/additional-features
# - Theme
# - Pages
