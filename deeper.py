"""Go deeper: the original Hebrew and Greek words
under each verse, from STEP Bible data (CC BY 4.0,
Tyndale House, www.STEPBible.org)."""

import io
import re
import urllib.request

import pandas as pd
import streamlit as st

HF = "https://huggingface.co/datasets/hmcgovern/"
TAIL = "/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet"
HEB_URL = HF + "original-language-bibles-hebrew" + TAIL
GRK_URL = HF + "original-language-bibles-greek" + TAIL


def _download(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "narrow-app"}
    )
    with urllib.request.urlopen(req) as r:
        return pd.read_parquet(io.BytesIO(r.read()))


def _lemma(code, hebrew):
    """Main Strong's number of a word, like H7225 or G2212."""
    if hebrew:
        m = re.search(r"\{([^}]*)\}", code)
        code = m.group(1) if m else code
    else:
        code = code.split("=")[0]
    m = re.search(r"([GH])0*(\d+)", code)
    if not m:
        return None
    lem = m.group(1) + m.group(2)
    if hebrew and int(m.group(2)) >= 9000:
        return None  # prefixes and markers, not words
    return lem


def _build(df, ref_col, hebrew, names):
    """Map each word to a KJV-style verse reference."""
    words, threads, abbrs = {}, {}, []
    for ref, text, tr, gloss, code in zip(
        df[ref_col], df["text"], df["transliteration"],
        df["translation"], df["dStrongs"],
    ):
        parts = str(ref).split(".")
        if len(parts) < 3:
            continue
        ab = parts[0]
        if ab not in abbrs:
            abbrs.append(ab)
        i = abbrs.index(ab)
        if i >= len(names):
            continue
        chap = re.sub(r"\D", "", parts[1])
        verse = re.sub(r"\D", "", parts[2])
        if not chap or not verse:
            continue
        key = f"{names[i]} {int(chap)}:{int(verse)}"
        lem = _lemma(str(code), hebrew)
        words.setdefault(key, []).append(
            (text, tr, gloss, lem or "")
        )
        if lem:
            t = threads.setdefault(lem, [])
            if not t or t[-1] != key:
                t.append(key)
    if len(abbrs) != len(names):
        raise ValueError("book list did not line up")
    return words, threads


@st.cache_resource(show_spinner="Opening the Hebrew and Greek...")
def load_original(books):
    heb = _download(HEB_URL)
    grk = _download(GRK_URL)
    w1, t1 = _build(heb, "english_reference", True, books[:39])
    ref = "reference" if "reference" in grk else grk.columns[0]
    w2, t2 = _build(grk, ref, False, books[39:])
    w1.update(w2)
    t1.update(t2)
    return w1, t1


def show(found, books, kjv):
    """Draw the Go deeper section. kjv maps ref -> text."""
    try:
        words, threads = load_original(tuple(books))
    except Exception as e:
        st.error(f"Couldn't open the original texts: {e}")
        return

    refs = [r for r, _ in found]
    ref = st.selectbox("Choose a verse", refs)
    st.markdown(f"> {kjv.get(ref, '')}")
    rows = words.get(ref)
    if not rows:
        st.info("No original-language data for this verse.")
        return

    table = pd.DataFrame(
        [
            {
                "Original": t,
                "Sounds like": tr,
                "English": g,
                "Strong's": lem,
                "Verses with it": len(threads.get(lem, [])),
            }
            for t, tr, g, lem in rows
        ]
    )
    st.dataframe(table, hide_index=True, use_container_width=True)

    choices = [
        f"{g} · {t} ({lem})" for t, tr, g, lem in rows if lem
    ]
    if not choices:
        return
    pick = st.selectbox("Follow a word through the Bible", choices)
    lem = pick.rsplit("(", 1)[1].rstrip(")")
    hits = threads.get(lem, [])
    lang = "Hebrew" if lem.startswith("H") else "Greek"
    st.write(
        f"This {lang} word ({lem}) appears in "
        f"**{len(hits)}** verses. The first 12:"
    )
    for r in hits[:12]:
        st.markdown(f"**{r}**: {kjv.get(r, '')}")
    st.caption(
        "Original-language data: STEP Bible (Tyndale House), "
        "CC BY 4.0, www.STEPBible.org. Strong's numbers mark "
        "the same dictionary word, not a proven shared root."
    )
