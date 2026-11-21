import json
import urllib.request

import anthropic
import streamlit as st
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Narrow Road Oracle")

KJV_URL = (
    "https://raw.githubusercontent.com/"
    "thiagobodruk/bible/master/json/en_kjv.json"
)

BOOKS = """Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth
1 Samuel|2 Samuel|1 Kings|2 Kings|1 Chronicles|2 Chronicles|Ezra|Nehemiah
Esther|Job|Psalm|Proverbs|Ecclesiastes|Song of Solomon|Isaiah|Jeremiah
Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum
Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts
Romans|1 Corinthians|2 Corinthians|Galatians|Ephesians|Philippians
Colossians|1 Thessalonians|2 Thessalonians|1 Timothy|2 Timothy|Titus
Philemon|Hebrews|James|1 Peter|2 Peter|1 John|2 John|3 John|Jude
Revelation""".replace("\n", "|").split("|")

MT77 = (
    "Ask, and it shall be given you; "
    "seek, and ye shall find; "
    "knock, and it shall be opened unto you:"
)
MT78 = (
    "For every one that asketh receiveth; "
    "and he that seeketh findeth; "
    "and to him that knocketh it shall be opened."
)

FILLER = set("""unto thee thou thy thine ye hath hast doth
dost saith said shall shalt wilt art lo behold yea came come
cometh went let things man men""".split())
KEEP = {"find", "found", "give"}
STOP = sorted((ENGLISH_STOP_WORDS - KEEP) | FILLER)


@st.cache_data(show_spinner="Opening the whole Bible...")
def load_bible():
    with urllib.request.urlopen(KJV_URL) as r:
        data = json.loads(r.read().decode("utf-8-sig"))
    verses = []
    for b, book in enumerate(data):
        name = BOOKS[b]
        for c, chap in enumerate(book["chapters"], 1):
            for v, text in enumerate(chap, 1):
                text = text.replace("{", "").replace("}", "")
                verses.append((f"{name} {c}:{v}", text))
    return verses


@st.cache_resource(show_spinner="Preparing the road...")
def build_index():
    verses = load_bible()
    vec = TfidfVectorizer(stop_words=STOP, sublinear_tf=True)
    mat = vec.fit_transform([t for _, t in verses])
    return verses, vec, mat


def seek(query, k=5):
    verses, vec, mat = build_index()
    q = vec.transform([query])
    scores = cosine_similarity(q, mat)[0]
    top = scores.argsort()[::-1][:k]
    return [verses[i] for i in top if scores[i] > 0]


def get_key():
    try:
        return st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        return None


def reading(question, seeking, found):
    key = get_key()
    if not key:
        return None, "⚪ No API key found in Secrets."
    lines = [f"{r} (KJV): {t}" for r, t in found]
    prompt = (
        "You are giving a reflective reading for "
        "someone walking the Narrow Road Oracle, "
        "built on Matthew 7:7-8 (ask, seek, knock)."
        f"\n\nTheir question: {question}"
        f"\nWhat they truly seek: {seeking}"
        "\n\nThe verses they found:\n"
        + "\n".join(lines)
        + "\n\nWrite two or three short paragraphs "
        "that answer their question directly, "
        "drawing the answer out of what these "
        "verses say together. Be specific to "
        "their question. Use only these verses, "
        "quote them word for word with their "
        "references, never invent or reword "
        "scripture, never predict the future or "
        "claim to speak for God. Speak warmly "
        "and plainly."
    )
    try:
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = [b.text for b in msg.content if b.type == "text"]
        return "\n\n".join(parts).strip(), "🟢 API connected."
    except Exception as e:
        return None, f"🔴 API error: {e}"


ss = st.session_state
if "gate" not in ss:
    ss.gate = 0

GOLD = "color:goldenrod;text-align:center"
st.markdown(
    f"<h1 style='{GOLD}'>The Narrow Road</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align:center;color:#aaa'>"
    f"<i>{MT77}</i> (Matthew 7:7)</p>",
    unsafe_allow_html=True,
)
labels = ["Ask", "Seek", "Knock", "Opened"]
st.progress(ss.gate / 3, text=labels[ss.gate])

if ss.gate == 0:
    st.subheader("Ask")
    q = st.text_area("What is your question?")
    if st.button("Ask") and q.strip():
        ss.question = q
        ss.gate = 1
        st.rerun()

elif ss.gate == 1:
    st.subheader("Seek")
    st.write(f"Your question: *{ss.question}*")
    s = st.text_area(
        "What are you truly looking for "
        "underneath this question?"
    )
    if st.button("Seek") and s.strip():
        ss.seeking = s
        found = seek(ss.question + " " + s)
        ss.found = found or [(
            "Jeremiah 29:13",
            "And ye shall seek me, and find me, "
            "when ye shall search for me "
            "with all your heart.",
        )]
        ss.gate = 2
        st.rerun()

elif ss.gate == 2:
    st.subheader("You found")
    for ref, text in ss.found:
        st.markdown(f"> {text}\n>\n> **{ref}**")
    if st.button("Knock"):
        with st.spinner("Knocking..."):
            ss.reading, ss.status = reading(
                ss.question, ss.seeking, ss.found
            )
        ss.gate = 3
        st.rerun()

else:
    st.markdown(
        f"<h2 style='{GOLD}'>It is opened.</h2>",
        unsafe_allow_html=True,
    )
    st.write(f"**You asked:** {ss.question}")
    st.write(f"**You sought:** {ss.seeking}")
    with st.expander("The verses you found"):
        for ref, text in ss.found:
            st.markdown(f"**{ref}**: {text}")
    st.subheader("Your reading")
    if ss.reading:
        st.markdown(ss.reading)
    st.caption(ss.status)
    st.divider()
    st.markdown(
        f"<p style='{GOLD}'><i>{MT78}</i>"
        f"<br>Matthew 7:8</p>",
        unsafe_allow_html=True,
    )
    if st.button("Walk again"):
        for k in ("question", "seeking", "found",
                  "reading", "status"):
            ss.pop(k, None)
        ss.gate = 0
        st.rerun()
