# Narrow

The Narrow Road Oracle, built on Matthew 7:7–8 and 7:13–14.

> Ask, and it shall be given you; seek, and ye shall find;
> knock, and it shall be opened unto you. (Matthew 7:7)

## How it works

1. **Ask**: bring your question to the first gate.
2. **Seek**: say what you are truly looking for underneath it.
   The oracle searches the whole King James Bible, about
   31,000 verses, and finds the five closest in meaning.
3. **Knock**: the last gate opens with a written reading that
   answers your question from the verses you found, closing
   with the promise of Matthew 7:8.

## After the reading

- **Save reading**: download your question, the verses and
  the reading together as a text file.
- **Go deeper**: see the original Hebrew or Greek word under
  each English word, with how it sounds, its meaning and its
  Strong's number. Pick a word to follow it through every
  verse where that same original word appears.

## Accuracy

Every verse is quoted word for word from the King James
Version, with its real reference. The reading uses only the
verses you found. It never invents or rewords scripture,
never predicts the future, and never claims to speak for God.
Go deeper links words only by Strong's number, so it shows
the same original word, never words that just look alike in
English.

## Setup

The reading uses the Anthropic API. In Streamlit Cloud, open
the app's **Settings → Secrets** and add:

    ANTHROPIC_API_KEY = "your-key"

Never put the key in the code or anywhere in this repo.

## Run locally

    pip install -r requirements.txt
    streamlit run app.py

## Built with

Streamlit, scikit-learn (TF-IDF verse matching), pandas and
the Anthropic API.

## Credits

- King James Bible text (public domain).
- Hebrew and Greek word data: STEP Bible, Tyndale House,
  www.STEPBible.org, used under CC BY 4.0.

## Author

Erin Rae Toppe
