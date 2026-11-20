import json
import urllib.request

import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Narrow Road Oracle", layout="centered")

# Full King James Bible (public domain), all 66 books
KJV_URL = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/en_kjv.json"

BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth",
    "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalm", "Proverbs", "Ecclesiastes", "Song of Solomon",
    "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah",
    "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians",
    "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians",
    "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon",
    "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude",
    "Revelation",
]

ASK_SEEK_KNOCK = (
    "Matthew 7:7",
    "Ask, and it shall be given you; seek, and ye shall find; "
    "knock, and it shall be opened unto you:",
)
PROMISE = (
    "Matthew 7:8",
    "For every one that asketh receiveth; and he that seeketh findeth; "
    "and to him that knocketh it shall be opened.",
)


@st.cache_data(show_spinner="Opening the whole Bible...")
def load_bible():
    with urllib.request.urlopen(KJV_URL) as r:
        data = json.loads(r.read().decode("utf-8-sig"))
    verses = []
    for b, book in enumerate(data):
        name = BOOKS[b] if b < len(BOOKS) else book.get("abbrev", "")
        for c, chapter in enumerate(book["chapters"], start=1):
            for v, text in enumerate(chapter, start=1):
                text = text.replace("{", "").replace("}", "")
                verses.append((f"{name} {c}:{v}", text))
    return verses


@st.cache_resource(show_spinner="Preparing the road...")
def build_index():
    verses = load_bible()
    vec = TfidfVectorizer(stop_words="english", sublinear_tf=True)
    mat = vec.fit_transform([t for _, t in verses])
    return verses, vec, mat


def seek(query, k=3):
    verses, vec, mat = build_index()
    scores = cosine_similarity(vec.transform([query]), mat)[0]
    ranked = scores.argsort()[::-1]
    return [verses[i] for i in ranked[:k] if scores[i] > 0]


def get_api_key():
    try:
        return st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        return None


def shared_words(question, found):
    """Words from the seeker's question that also appear in the verses found."""
    _, vec, _ = build_index()
    analyzer = vec.build_analyzer()
    asked = set(analyzer(question))
    in_verses = set()
    for _, text in found:
        in_verses |= set(analyzer(text))
    return sorted(asked & in_verses)


def simple_reading(question, seeking, found):
    """A reading built only from the seeker's words and the verses themselves."""
    words = shared_words(question + " " + seeking, found)
    lines = []
    if words:
        lines.append(
            "The road met your question at these words: **"
            + ", ".join(words) + "**."
        )
    first_ref, first_text = found[0]
    lines.append(f"The first gate you passed was **{first_ref}**: *\"{first_text}\"*")
    if len(found) > 1:
        rest = "; ".join(f"**{r}**" for r, _ in found[1:])
        lines.append(f"It is joined on the road by {rest}, which speak to the same need.")
    lines.append(
        "Read them together, slowly, as one answer. What do they ask of you, "
        "and what do they promise?"
    )
    return "\n\n".join(lines)


def ai_reading(question, seeking, found, key):
    """A reading written by Claude, grounded only in the verses found."""
    import anthropic

    verses = "\n".join(f"{ref} (KJV): {text}" for ref, text in found)
    prompt = (
        "You are giving a reflective reading for someone walking the Narrow Road "
        "Oracle, built on Matthew 7:7-8 (ask, seek, knock).\n\n"
        f"Their question: {question}\n"
        f"What they are truly seeking: {seeking}\n\n"
        f"The verses they found:\n{verses}\n\n"
        "Write a reading of two or three short paragraphs that brings these verses "
        "together into one message for them. Rules: use only the verses above; "
        "quote them word for word with their references; do not invent or reword "
        "scripture; do not predict the future or claim to speak for God. Speak "
        "warmly and plainly, as a reflection on what the verses say to their question."
    )
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def make_reading(question, seeking, found):
    key = get_api_key()
    if key:
        try:
            return ai_reading(question, seeking, found, key)
        except Exception as e:
            st.warning(f"The written reading couldn't be reached ({e}). Showing the simple reading.")
    return simple_reading(question, seeking, found)


if "gate" not in st.session_state:
    st.session_state.gate = 0

gold = "color:goldenrod"
st.markdown(
    f"<h1 style='text-align:center;{gold}'>The Narrow Road</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align:center;color:#aaa'><i>{ASK_SEEK_KNOCK[1]}</i> "
    f"({ASK_SEEK_KNOCK[0]})</p>",
    unsafe_allow_html=True,
)
labels = ["Gate 1: Ask", "Gate 2: Seek", "Gate 3: Knock", "Opened"]
st.progress(st.session_state.gate / 3, text=labels[st.session_state.gate])

# Gate 1: Ask
if st.session_state.gate == 0:
    st.subheader("Ask")
    q = st.text_area("What is your question?")
    if st.button("Ask") and q.strip():
        st.session_state.question = q
        st.session_state.gate = 1
        st.rerun()

# Gate 2: Seek
elif st.session_state.gate == 1:
    st.subheader("Seek")
    st.write(f"Your question: *{st.session_state.question}*")
    s = st.text_area(
        "In your own words, what are you truly looking for underneath this question?"
    )
    if st.button("Seek") and s.strip():
        st.session_state.seeking = s
        found = seek(st.session_state.question + " " + s)
        st.session_state.found = found or [
            (
                "Jeremiah 29:13",
                "And ye shall seek me, and find me, "
                "when ye shall search for me with all your heart.",
            )
        ]
        st.session_state.gate = 2
        st.rerun()

# Gate 3: Knock
elif st.session_state.gate == 2:
    st.subheader("You found")
    for ref, text in st.session_state.found:
        st.markdown(f"> {text}\n>\n> **{ref}** (KJV)")
    if st.button("Knock"):
        with st.spinner("Knocking..."):
            st.session_state.reading = make_reading(
                st.session_state.question,
                st.session_state.seeking,
                st.session_state.found,
            )
        st.session_state.gate = 3
        st.rerun()

# Opened
else:
    st.markdown(
        f"<h2 style='text-align:center;{gold}'>It is opened.</h2>",
        unsafe_allow_html=True,
    )
    st.write(f"**You asked:** {st.session_state.question}")
    st.write(f"**You sought:** {st.session_state.seeking}")
    with st.expander("The verses you found", expanded=False):
        for ref, text in st.session_state.found:
            st.markdown(f"**{ref}**: {text}")
    st.subheader("Your reading")
    st.markdown(st.session_state.reading)
    st.divider()
    st.markdown(
        f"<p style='text-align:center;{gold}'><i>{PROMISE[1]}</i><br>{PROMISE[0]}</p>",
        unsafe_allow_html=True,
    )
    if st.button("Walk again"):
        for key in ("question", "seeking", "found", "reading"):
            st.session_state.pop(key, None)
        st.session_state.gate = 0
        st.rerun()
