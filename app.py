import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Narrow", layout="wide")
st.title("Narrow — Matthew 7:13–14")
BG = "#0e1117"
tab1, tab2 = st.tabs(["The Roads", "The Mirror"])

# ---------- Tab 1: the two roads ----------
with tab1:
    c1, c2, c3 = st.columns(3)
    n = c1.slider("Travellers", 50, 2000, 600)
    few = c2.slider("Share who find the narrow way (%)", 1, 50, 8) / 100
    tight = c3.slider("Narrowness", 0.1, 1.0, 0.6)

    x = np.linspace(0, 10, 200)
    wide_half = lambda p: 0.3 + 0.35 * p
    narrow_half = lambda p: 0.3 * (1 - tight * p / 10.5)

    fig = go.Figure()
    for c, h, col, name in [(-0.6, wide_half, "rgba(200,60,60,0.25)", "Broad way → ἀπώλεια (destruction)"),
                            (0.6, narrow_half, "rgba(240,200,80,0.45)", "Narrow way → ζωή (life)")]:
        fig.add_trace(go.Scatter(x=np.r_[x, x[::-1]],
            y=np.r_[c * x + h(x), (c * x - h(x))[::-1]],
            fill="toself", fillcolor=col, line=dict(width=0), name=name, hoverinfo="name"))

    rng = np.random.default_rng(7)
    k = int(n * few)
    for count, c, h, col in [(n - k, -0.6, wide_half, "crimson"), (k, 0.6, narrow_half, "goldenrod")]:
        px = rng.uniform(0.2, 10, count)
        py = c * px + rng.uniform(-0.9, 0.9, count) * h(px)
        fig.add_trace(go.Scatter(x=px, y=py, mode="markers", marker=dict(size=4, color=col),
                                 showlegend=False, hoverinfo="skip"))

    fig.add_annotation(x=0, y=0, text="πύλη (gate)", showarrow=False, yshift=18)
    fig.update_layout(height=620, plot_bgcolor=BG, paper_bgcolor=BG, font_color="white",
        xaxis=dict(title="Journey", gridcolor="#333"), yaxis=dict(gridcolor="#333", zeroline=False),
        legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"πολλοί (many): {n-k} · ὀλίγοι (few): {k}")

# ---------- Tab 2: the mirror structure ----------
with tab2:
    pairs = [
        ("Gate",      "πλατεῖα",       "wide",          "στενή",        "narrow"),
        ("Way",       "εὐρύχωρος",     "spacious",      "τεθλιμμένη",   "pressed, constricted"),
        ("Leads to",  "ἀπώλεια",       "destruction",   "ζωή",          "life"),
        ("People",    "πολλοί",        "many",          "ὀλίγοι",       "few"),
        ("Action",    "εἰσερχόμενοι",  "entering",      "εὑρίσκοντες",  "finding"),
    ]
    f2 = go.Figure()
    for i, (label, gl, el, gr, er) in enumerate(pairs):
        y = len(pairs) - i
        f2.add_trace(go.Scatter(x=[-1, 1], y=[y, y], mode="lines",
            line=dict(color="#555", dash="dot"), hoverinfo="skip", showlegend=False))
        f2.add_trace(go.Scatter(x=[-1], y=[y], mode="markers+text", text=[f"{gl}<br><i>{el}</i>"],
            textposition="middle left", marker=dict(size=18, color="crimson"),
            hoverinfo="skip", showlegend=False))
        f2.add_trace(go.Scatter(x=[1], y=[y], mode="markers+text", text=[f"{gr}<br><i>{er}</i>"],
            textposition="middle right", marker=dict(size=18, color="goldenrod"),
            hoverinfo="skip", showlegend=False))
        f2.add_annotation(x=0, y=y, text=label, showarrow=False, font=dict(color="#aaa"),
                          bgcolor=BG)
    f2.add_shape(type="line", x0=0, x1=0, y0=0.4, y1=len(pairs) + 0.6, line=dict(color="white", width=1))
    f2.update_layout(height=620, plot_bgcolor=BG, paper_bgcolor=BG, font_color="white",
        xaxis=dict(visible=False, range=[-3, 3]), yaxis=dict(visible=False, range=[0, len(pairs) + 1]))
    st.plotly_chart(f2, use_container_width=True)
    st.markdown("**The pattern:** each line on the broad side is answered by its opposite on the narrow side. "
                "The final pair breaks the symmetry — the many simply *enter*; the few must *find*.")
