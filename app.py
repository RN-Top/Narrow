import json
import urllib.request

import streamlit as st
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
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


# Common filler words to skip, plus old King James forms like "unto" and "thee".
# "find", "found" and "give" are kept in, because seeking and finding matter here.
KJV_FILLER = {
    "unto", "thee", "thou", "thy", "thine", "ye", "hath", "hast", "doth", "dost",
    "saith", "said", "shall", "shalt", "wilt", "art", "lo", "behold", "yea",
    "came", "come", "cometh", "went", "let", "things", "man", "men",
}
STOP_WORDS = sorted((ENGLISH_STOP_WORDS - {"find", "found", "give"}) | KJV_FILLER)


@st.cache_resource(show_spinner="Preparing the road...")
def build_index():
    verses = load_bible()
    vec = TfidfVectorizer(stop_words=STOP_WORDS, sublinear_tf=True)
    mat = vec.fit_transform([t for _, t in verses])
    return verses, vec, mat


def seek(query, k=5):
    verses, vec, mat = build_index()
    scores = cosine_similarity(vec.transform([query]), mat)[0]
    ranked = scores.argsort()[::-1]
    return [verses[i] for i in ranked[:k] if scores[i] > 0]


def get_api_key():
    try:
        return st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        return None


# ---------- The simple reading (no API key needed) ----------

# Where each book sits in the Bible, by its position in BOOKS
SECTIONS = [
    (0, 4, "the Law", "Old Testament"),
    (5, 16, "the History books", "Old Testament"),
    (17, 21, "the Wisdom books", "Old Testament"),
    (22, 26, "the Major Prophets", "Old Testament"),
    (27, 38, "the Minor Prophets", "Old Testament"),
    (39, 42, "the Gospels", "New Testament"),
    (43, 43, "the Acts of the Apostles", "New Testament"),
    (44, 64, "the Letters", "New Testament"),
    (65, 65, "Revelation", "New Testament"),
]

# Key words: the KJV forms, then the Greek word it most often translates in the
# New Testament and the Hebrew word it most often translates in the Old Testament.
WORDS_BENEATH = {
    "seek": ({"seek", "seeketh", "seeking", "sought"},
             ("ζητέω", "zēteō", "to seek, search for, strive after"),
             ("בָּקַשׁ", "baqash", "to seek, search out, desire")),
    "find": ({"find", "findeth", "found", "finding"},
             ("εὑρίσκω", "heuriskō", "to find, discover (the root of 'eureka')"),
             ("מָצָא", "matsa", "to find, come upon, attain")),
    "ask": ({"ask", "asketh", "asked", "asking"},
            ("αἰτέω", "aiteō", "to ask, request"),
            ("שָׁאַל", "shaal", "to ask, inquire")),
    "knock": ({"knock", "knocketh", "knocked"},
              ("κρούω", "krouō", "to knock at a door"),
              None),
    "way": ({"way", "ways", "path", "paths"},
            ("ὁδός", "hodos", "road, path, way of life"),
            ("דֶּרֶךְ", "derekh", "road, journey, way of living")),
    "gate": ({"gate", "gates"},
             ("πύλη", "pylē", "gate, entrance"),
             ("שַׁעַר", "shaar", "gate")),
    "narrow": ({"strait", "narrow"},
               ("στενός", "stenos", "narrow, tight"),
               None),
    "life": ({"life", "live", "liveth", "living"},
             ("ζωή", "zōē", "life, the fullness of life"),
             ("חַיִּים", "chayyim", "life")),
    "light": ({"light", "lights"},
              ("φῶς", "phōs", "light"),
              ("אוֹר", "or", "light")),
    "heart": ({"heart", "hearts"},
              ("καρδία", "kardia", "heart, the inner self"),
              ("לֵב", "lev", "heart, mind, will")),
    "peace": ({"peace"},
              ("εἰρήνη", "eirēnē", "peace, wholeness, rest"),
              ("שָׁלוֹם", "shalom", "peace, completeness, wellbeing")),
    "truth": ({"truth", "true"},
              ("ἀλήθεια", "alētheia", "truth, what is real and unhidden"),
              ("אֱמֶת", "emet", "truth, faithfulness, firmness")),
    "faith": ({"faith", "believe", "believeth", "believed"},
              ("πίστις", "pistis", "faith, trust, faithfulness"),
              None),
    "hope": ({"hope", "hoped"},
             ("ἐλπίς", "elpis", "hope, confident expectation"),
             None),
    "love": ({"love", "loveth", "loved", "charity"},
             ("ἀγάπη", "agapē", "love that gives itself"),
             ("אַהֲבָה", "ahavah", "love")),
    "grace": ({"grace"},
              ("χάρις", "charis", "grace, favour, gift"),
              None),
    "fear": ({"fear", "afraid", "feared"},
             ("φόβος", "phobos", "fear, awe, reverence"),
             ("יִרְאָה", "yirah", "fear, awe, reverence")),
    "door": ({"door", "doors", "opened", "open"},
             ("θύρα", "thyra", "door, entrance"),
             None),
}

CLOSING_QUESTIONS = [
    "What are these verses asking you to do next?",
    "Which line stopped you, and why that one?",
    "What would it look like to walk this answer for one week?",
    "Where in your life is the gate narrow right now?",
]


def book_of(ref):
    return ref.rsplit(" ", 1)[0]


def place_of(ref):
    """Section and testament for a reference like 'Psalm 27:8'."""
    name = book_of(ref)
    i = BOOKS.index(name) if name in BOOKS else -1
    for lo, hi, section, testament in SECTIONS:
        if lo <= i <= hi:
            return i, section, testament
    return i, "", ""


def simple_reading(question, seeking, found):
    """A reading built only from the seeker's words and the real verses found."""
    _, vec, _ = build_index()
    words = vec.build_analyzer()
    asked = set(words(question + " " + seeking))
    verse_words = [set(words(t)) for _, t in found]
    all_verse_words = set().union(*verse_words)

    # Put the verses in the order they appear in the Bible
    ordered = sorted(found, key=lambda rv: place_of(rv[0])[0])
    places = [place_of(r) for r, _ in ordered]
    sections = list(dict.fromkeys(p[1] for p in places if p[1]))
    testaments = {p[2] for p in places if p[2]}

    out = []

    # 1. Where the road led
    out.append("#### Where the road led")
    if len(testaments) == 2:
        span = "Your answer runs through both the Old and the New Testament"
    elif testaments:
        span = f"Your answer comes from the {testaments.pop()}"
    else:
        span = "Your answer"
    if len(sections) > 1:
        through = ", ".join(sections[:-1]) + " and " + sections[-1]
    else:
        through = sections[0] if sections else "the scriptures"
    out.append(f"{span}, through {through}.")

    # 2. What they share
    met = sorted(asked & all_verse_words)
    common = sorted(
        w for w in all_verse_words
        if sum(w in vw for vw in verse_words) >= 2 and len(w) > 3
    )
    out.append("#### What the verses share")
    if met:
        out.append("Your own words met the scripture at: **" + ", ".join(met) + "**.")
    if common:
        out.append("The verses speak to each other through: **" + ", ".join(common) + "**.")
    if not met and not common:
        out.append("Each verse answers from a different side. Read them as one voice.")

    # 3. The verses, in the order they appear
    out.append("#### The road, in order")
    for (ref, text), (_, section, _) in zip(ordered, places):
        out.append(f"**{ref}** · {section}\n\n> {text}")

    # 4. Words beneath the words
    notes = []
    for key, (forms, greek, hebrew) in WORDS_BENEATH.items():
        hits = [(r, place_of(r)[2]) for (r, _), vw in zip(found, verse_words) if vw & forms]
        if not hits:
            continue
        refs = ", ".join(r for r, _ in hits)
        lines = []
        if greek and any(t == "New Testament" for _, t in hits):
            lines.append(f"Greek **{greek[0]}** ({greek[1]}): {greek[2]}")
        if hebrew and any(t == "Old Testament" for _, t in hits):
            lines.append(f"Hebrew **{hebrew[0]}** ({hebrew[1]}): {hebrew[2]}")
        if lines:
            notes.append(f"- **{key}** ({refs}): " + "; ".join(lines))
    if notes:
        out.append("#### Words beneath the words")
        out.append("\n".join(notes))
        out.append("*The original word most often behind the English. Check an interlinear for the exact word in each verse.*")

    # 5. Closing
    out.append("#### Knock")
    out.append(
        "You asked, you sought, and you have knocked. "
        + CLOSING_QUESTIONS[len(question + seeking) % len(CLOSING_QUESTIONS)]
    )
    return "\n\n".join(out)


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
        "Write a reading of two or three short paragraphs that answers their question "
        "directly, drawing the answer out of what these particular verses say "
        "together. Make it specific to their question, not general encouragement. "
        "Rules: use only the verses above; "
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
    # The reply can start with a "thinking" block, so keep only the text blocks
    return "\n\n".join(b.text for b in msg.content if b.type == "text").strip()


def make_reading(question, seeking, found):
    """Returns the reading and a status line saying whether the API was used."""
    key = get_api_key()
    if not key:
        return (simple_reading(question, seeking, found),
                "⚪ Simple reading: no API key found in Streamlit Secrets.")
    try:
        return (ai_reading(question, seeking, found, key),
                "🟢 Written reading: API connected.")
    except Exception as e:
        return (simple_reading(question, seeking, found),
                f"🔴 API key found but it didn't work: {e}")


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
            st.session_state.reading, st.session_state.status = make_reading(
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
    st.caption(st.session_state.get("status", ""))
    st.divider()
    st.markdown(
        f"<p style='text-align:center;{gold}'><i>{PROMISE[1]}</i><br>{PROMISE[0]}</p>",
        unsafe_allow_html=True,
    )
    if st.button("Walk again"):
        for key in ("question", "seeking", "found", "reading", "status"):
            st.session_state.pop(key, None)
        st.session_state.gate = 0
        st.rerun()
