import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Narrow", layout="wide")
st.title("Narrow — Matthew 7:13–14")
BG = "#0e1117"

pairs = [
    ("Gate", "πλατεῖα", "wide", "στενή", "narrow"),
    ("Way", "εὐρύχωρος", "spacious", "τεθλιμμένη", "hard-pressed"),
    ("Leads to", "ἀπώλεια", "destruction", "ζωή", "life"),
    ("People", "πολλοί", "many", "ὀλίγοι", "few"),
    ("Action", "εἰσερχόμενοι", "enter", "εὑρίσκοντες", "find"),
]
message = [
    "Narrow gate,",
    "hard-pressed way,",
    "leading to life,",
    "and few",
    "are the ones who find it.",
]

N = len(pairs)
step = st.slider("Walk the road", 0, N, 0, help="Move forward through the passage")


def half_width(i):
    # road pinches toward a single point
    return 2.6 * (1 - i / N) + 0.15


fig = go.Figure()

# Road edges
ys = [N - i for i in range(N + 1)]
left = [-half_width(i) for i in range(N + 1)]
right = [half_width(i) for i in range(N + 1)]
fig.add_trace(
    go.Scatter(
        x=left + right[::-1],
        y=ys + ys[::-1],
        fill="toself",
        fillcolor="rgba(240,200,80,0.06)",
        line=dict(color="rgba(240,200,80,0.35)", width=1),
        hoverinfo="skip",
        showlegend=False,
    )
)
fig.add_shape(
    type="line", x0=0, x1=0, y0=0, y1=N + 0.4,
    line=dict(color="#444", dash="dot"),
)

for i, (label, gb, eb, gn, en) in enumerate(pairs):
    y = N - i - 0.5
    w = half_width(i + 0.5)
    lit = step > i
    broad_op = 0.15 if lit else 0.8
    narrow_col = "gold" if lit else "#777"

    fig.add_annotation(
        x=-w - 0.1, y=y, xanchor="right", showarrow=False,
        text=f"{gb} {eb}",
        font=dict(color=f"rgba(220,80,80,{broad_op})", size=15),
    )
    fig.add_annotation(
        x=w + 0.1, y=y, xanchor="left", showarrow=False,
        text=f"{gn} {en}",
        font=dict(color=narrow_col, size=15),
    )
    fig.add_annotation(
        x=0, y=y, showarrow=False, text=label,
        font=dict(color="#888", size=11), bgcolor=BG,
    )

# Traveller dot
if step > 0:
    fig.add_trace(
        go.Scatter(
            x=[0], y=[N - step], mode="markers",
            marker=dict(size=14, color="gold", line=dict(color="white", width=1)),
            hoverinfo="skip", showlegend=False,
        )
    )

fig.update_layout(
    height=650,
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    font_color="white",
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(visible=False, range=[-5.5, 5.5]),
    yaxis=dict(visible=False, range=[-0.3, N + 0.6]),
)
st.plotly_chart(fig, use_container_width=True)

# The message assembles
if step > 0:
    text = " ".join(message[:step])
    st.markdown(
        f"<p style='text-align:center;font-size:1.6em;color:gold'>{text}</p>",
        unsafe_allow_html=True,
    )
if step == N:
    st.markdown(
        "<p style='text-align:center;color:#aaa'>The many simply enter. "
        "The few must find.</p>",
        unsafe_allow_html=True,
    )
