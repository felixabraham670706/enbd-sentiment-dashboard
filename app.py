import streamlit as st
from pipeline import run_pipeline
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import pytz

st.title("Emirates NBD Reddit Sentiment Dashboard")
# Dubai timezone
dubai = pytz.timezone("Asia/Dubai")
dubai_time = datetime.now(dubai)

st.write("Last refreshed at:", dubai_time.strftime("%Y-%m-%d %H:%M:%S"), "Dubai Time")

# refresh every 5 minutes
st_autorefresh(interval=300000)

df = run_pipeline()

positive = df[df["sentiment"]=="Positive"]
neutral = df[df["sentiment"]=="Neutral"]
negative = df[df["sentiment"]=="Negative"]

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Positive Comments")
    for c in positive["comment"]:
        st.success(c)

with col2:
    st.subheader("Neutral Comments")
    for c in neutral["comment"]:
        st.warning(c)

with col3:
    st.subheader("Negative Comments")
    for c in negative["comment"]:
        st.error(c)