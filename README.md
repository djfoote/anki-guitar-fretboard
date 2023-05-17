# anki-guitar-fretboard
Tools for programmatically making Anki decks with guitar fretboard diagrams.

Essentially this is just some glue between the `fretboardgtr` and `anki` python libraries, with some interfaces that I find useful for making the kinds of Anki cards I want to make in bulk.

I'll add the infra code as I clean it up, and I'll add scripts built on top of it as examples of exercises that I've made with it.

The two I have in mind currently are:
1. Q: What is this note? [Image of a fretboard with a note highlighted]
   A: C#
2. Q: What are these notes in ascending order? [Image of a fretboard with one note on each string highlighted]
   A: A# D# G# C# F A#

I made a batch of these by hand using [this tool](https://www.editor.guitarscientist.com/new) but I want to make it very low-friction so I can keep dumping more of this sort of thing into my "Guitar" Anki deck.

---

Current status:
- Messy Jupyter notebook proof-of-concept for making the diagrams.
- I have a script for batch adding "Basic" Anki cards to a specified collection; not committed yet.
