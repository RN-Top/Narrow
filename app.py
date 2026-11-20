import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Narrow Road Oracle", layout="centered")

# (reference, KJV text, modern theme words used for matching)
VERSES = [
    ("Matthew 6:34", "Take therefore no thought for the morrow: for the morrow shall take thought for the things of itself. Sufficient unto the day is the evil thereof.", "worry anxiety future tomorrow stress fear"),
    ("Philippians 4:6", "Be careful for nothing; but in every thing by prayer and supplication with thanksgiving let your requests be made known unto God.", "worry anxiety prayer stress ask help"),
    ("Philippians 4:7", "And the peace of God, which passeth all understanding, shall keep your hearts and minds through Christ Jesus.", "peace calm mind heart rest anxiety"),
    ("John 14:27", "Peace I leave with you, my peace I give unto you: not as the world giveth, give I unto you. Let not your heart be troubled, neither let it be afraid.", "peace fear afraid troubled calm"),
    ("Matthew 11:28", "Come unto me, all ye that labour and are heavy laden, and I will give you rest.", "tired exhausted rest burden overwhelmed work weary"),
    ("Isaiah 40:31", "But they that wait upon the LORD shall renew their strength; they shall mount up with wings as eagles; they shall run, and not be weary; and they shall walk, and not faint.", "strength tired waiting patience energy hope weary"),
    ("Proverbs 3:5", "Trust in the LORD with all thine heart; and lean not unto thine own understanding.", "trust guidance decision direction confused"),
    ("Proverbs 3:6", "In all thy ways acknowledge him, and he shall direct thy paths.", "direction path guidance decision future way"),
    ("Psalm 119:105", "Thy word is a lamp unto my feet, and a light unto my path.", "guidance path light direction way lost"),
    ("James 1:5", "If any of you lack wisdom, let him ask of God, that giveth to all men liberally, and upbraideth not; and it shall be given him.", "wisdom understanding knowledge decision answer truth"),
    ("Proverbs 25:2", "It is the glory of God to conceal a thing: but the honour of kings is to search out a matter.", "search hidden knowledge research mystery discover secret"),
    ("Jeremiah 29:13", "And ye shall seek me, and find me, when ye shall search for me with all your heart.", "seek search find god heart purpose"),
    ("Jeremiah 33:3", "Call unto me, and I will answer thee, and shew thee great and mighty things, which thou knowest not.", "answer hidden knowledge mystery revelation understand"),
    ("Matthew 6:33", "But seek ye first the kingdom of God, and his righteousness; and all these things shall be added unto you.", "priorities money provision needs seek purpose"),
    ("Matthew 6:26", "Behold the fowls of the air: for they sow not, neither do they reap, nor gather into barns; yet your heavenly Father feedeth them. Are ye not much better than they?", "money provision needs job worth value worry"),
    ("Jeremiah 29:11", "For I know the thoughts that I think toward you, saith the LORD, thoughts of peace, and not of evil, to give you an expected end.", "future plans purpose hope career"),
    ("Romans 8:28", "And we know that all things work together for good to them that love God, to them who are the called according to his purpose.", "purpose meaning hard times calling good"),
    ("Ecclesiastes 3:1", "To every thing there is a season, and a time to every purpose under the heaven:", "timing season change waiting patience purpose"),
    ("Psalm 46:10", "Be still, and know that I am God: I will be exalted among the heathen, I will be exalted in the earth.", "still calm quiet rest peace overwhelmed"),
    ("Joshua 1:9", "Have not I commanded thee? Be strong and of a good courage; be not afraid, neither be thou dismayed: for the LORD thy God is with thee whithersoever thou goest.", "courage fear brave move change new start afraid"),
    ("Isaiah 41:10", "Fear thou not; for I am with thee: be not dismayed; for I am thy God: I will strengthen thee; yea, I will help thee; yea, I will uphold thee with the right hand of my righteousness.", "fear help strength alone afraid support"),
    ("Psalm 34:18", "The LORD is nigh unto them that are of a broken heart; and saveth such as be of a contrite spirit.", "grief sad broken heart loss pain"),
    ("Matthew 5:4", "Blessed are they that mourn: for they shall be comforted.", "grief mourning loss comfort sad"),
    ("Revelation 21:4", "And God shall wipe away all tears from their eyes; and there shall be no more death, neither sorrow, nor crying, neither shall there be any more pain: for the former things are passed away.", "grief death loss pain sorrow"),
    ("1 John 1:9", "If we confess our sins, he is faithful and just to forgive us our sins, and to cleanse us from all unrighteousness.", "forgiveness guilt sin mistake shame"),
    ("Matthew 6:14", "For if ye forgive men their trespasses, your heavenly Father will also forgive you:", "forgive others anger hurt relationship"),
    ("1 Corinthians 13:4", "Charity suffereth long, and is kind; charity envieth not; charity vaunteth not itself, is not puffed up,", "love relationship patience kindness family"),
    ("John 15:13", "Greater love hath no man than this, that a man lay down his life for his friends.", "love friends friendship sacrifice"),
    ("Galatians 6:9", "And let us not be weary in well doing: for in due season we shall reap, if we faint not.", "persevere keep going give up tired effort reward"),
    ("2 Corinthians 12:9", "And he said unto me, My grace is sufficient for thee: for my strength is made perfect in weakness.", "weakness struggle limits strength grace"),
    ("John 8:32", "And ye shall know the truth, and the truth shall make you free.", "truth freedom knowledge understanding"),
    ("Matthew 7:14", "Because strait is the gate, and narrow is the way, which leadeth unto life, and few there be that find it.", "narrow path hard road life few find"),
]

ASK_SEEK_KNOCK = ("Matthew 7:7", "Ask, and it shall be given you; seek, and ye shall find; knock, and it shall be opened unto you:")
PROMISE = ("Matthew 7:8", "For every one that asketh receiveth; and he that seeketh findeth; and to him that knocketh it shall be opened.")

@st.cache_resource
def build_index():
    docs = [f"{theme} {theme} {text}" for _, text, theme in VERSES]
    vec = TfidfVectorizer(stop_words="english")
    return vec, vec.fit_transform(docs)

def seek(query, k=3):
    vec, mat = build_index()
    scores = cosine_similarity(vec.transform([query]), mat)[0]
    ranked = scores.argsort()[::-1]
    return [VERSES[i] for i in ranked[:k] if scores[i] > 0]

if "gate" not in st.session_state:
    st.session_state.gate = 0

gold = "color:goldenrod"
st.markdown(f"<h1 style='text-align:center;{gold}'>The Narrow Road</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;color:#aaa'><i>{ASK_SEEK_KNOCK[1]}</i> ({ASK_SEEK_KNOCK[0]})</p>", unsafe_allow_html=True)
st.progress(st.session_state.gate / 3, text=["Gate 1: Ask", "Gate 2: Seek", "Gate 3: Knock", "Opened"][st.session_state.gate])

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
    s = st.text_area("In your own words, what are you truly looking for underneath this question?")
    if st.button("Seek") and s.strip():
        found = seek(st.session_state.question + " " + s)
        st.session_state.found = found or [VERSES[11]]
        st.session_state.gate = 2
        st.rerun()

# Gate 3: Knock
elif st.session_state.gate == 2:
    st.subheader("You found")
    for ref, text, _ in st.session_state.found:
        st.markdown(f"> {text}\n>\n> **{ref}** (KJV)")
    if st.button("Knock"):
        st.session_state.gate = 3
        st.rerun()

# Opened
else:
    st.markdown(f"<h2 style='text-align:center;{gold}'>It is opened.</h2>", unsafe_allow_html=True)
    st.write(f"**You asked:** {st.session_state.question}")
    for ref, text, _ in st.session_state.found:
        st.markdown(f"**{ref}**: {text}")
    st.markdown(f"<p style='text-align:center;{gold}'><i>{PROMISE[1]}</i><br>{PROMISE[0]}</p>", unsafe_allow_html=True)
    if st.button("Walk again"):
        for key in ("question", "found"):
            st.session_state.pop(key, None)
        st.session_state.gate = 0
        st.rerun()