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
    "faith": ({"fa
