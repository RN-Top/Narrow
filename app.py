import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Narrow", layout="wide")
st.title("Narrow — Matthew 7:13–14")
BG = "#0e1117"

pairs = [
    ("Gate",     "πλατεῖα",      "wide",        "στενή",       "narrow"),
    ("Way",      "εὐρύχωρος",    "spacious",    "τεθλιμμένη",  "hard-pressed"),
    ("Leads to", "ἀπώλεια",      "destruction", "ζωή",         "life"),
    ("People",   "πολλοί",       "many",        "ὀλίγοι",      "few"),
    ("Action",   "εἰσερχόμενοι", "enter",       "εὑρίσκοντες", "find"),
]
message = ["Narrow gate,", "hard-pressed way,", "leading to life,", "and few", "are the ones who find it."]

N = len(pairs)
step = st.slider("Walk the road", 0, N, 0, help="Move forward through the passage")

def half_width(i):           # road pinches toward a single point
    return 2.6 * (1 - i / N) + 0.15

fig = go.Figure()

# Road edges
ys = [N - i for i in range(N + 1)]
left = [-half_width(i) for i in range(N + 1)]
right = [half_width(i) for i
