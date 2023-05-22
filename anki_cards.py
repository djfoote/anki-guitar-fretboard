import contextlib
import os
import shutil
import uuid

from anki import notes, storage

import fretboard_utils


class AnkiDeck:
    def __init__(self, deck_name, user_name, collection_path, media_path):
        self.deck_name = deck_name
        self.user_name = user_name
        self.collection_path = collection_path
        self.media_path = media_path

        self.is_open = False

    def __enter__(self):
        self.collection = storage.Collection(self.collection_path)
        self.model = self.collection.models.by_name("Basic")
        self.deck_id = self.collection.decks.id(self.deck_name)
        self.is_open = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.is_open = False
        self.collection.close()

    def add_card(self, question, answer, tags=None):
        if self.is_open:
            self._add_card(question, answer, tags)
        else:
            with self:
                self._add_card(question, answer, tags)

    def _add_card(self, question, answer, tags=None):
        note = notes.Note(self.collection, self.model)
        note.fields = [question, answer]
        if tags:
            note.tags = tags
        self.collection.add_note(note, deck_id=self.deck_id)

    def save_media(self, source_fpath, dest_fname=None):
        if dest_fname is None:
            dest_fname = os.path.basename(source_fpath)
        name, ext = os.path.splitext(dest_fname)
        while os.path.exists(os.path.join(self.media_path, dest_fname)):
            # Add a UUID to the filename if it already exists to avoid overwriting media for other cards.
            dest_fname = f"{name}_{uuid.uuid4()}{ext}"
        dest_fpath = os.path.join(self.media_path, dest_fname)
        shutil.copyfile(source_fpath, dest_fpath)
        return dest_fname


class CardGenerator:
    def __init__(self, question_fn, answer_fn):
        self.question_fn = question_fn
        self.answer_fn = answer_fn

    def generate_card(self, deck=None, print_to_ipynb=False, *args, **kwargs):
        """Generate a card and add it to the deck if provided.

        Other than `deck`, all arguments are passed to the question and answer functions.
        """
        question = self.question_fn(*args, **kwargs)
        answer = self.answer_fn(*args, **kwargs)
        if deck is not None:
            deck.add_card(question, answer)
        if print_to_ipynb:
            self.print_card(question, answer)

    def generate_cards(self, deck=None, print_to_ipynb=False, args_sequence=None, kwargs_sequence=None):
        """Generate multiple cards and add them to the deck if provided. Preferred over calling `generate_card` multiple
        times, as it only opens the deck once.

        Args:
            deck: An AnkiDeck object. If not provided, this will be a dry run that only creates the cards without adding
                them to a deck.
            print_to_ipynb: If True, print the cards to the IPython notebook.
            args_sequence: A sequence of positional arguments (as tuples) to pass to the question and answer functions.
            kwargs_sequence: A sequence of keyword arguments (as dictionaries) to pass to the question and answer
                functions.

        Returns:
            A list of question-answer pairs (as tuples of strings).
        """
        if args_sequence is None and kwargs_sequence is None:
            return []
        if args_sequence is None:
            args_sequence = [()] * len(kwargs_sequence)
        if kwargs_sequence is None:
            kwargs_sequence = [{}] * len(args_sequence)
        with contextlib.ExitStack() as stack:
            if deck is not None:
                stack.enter_context(deck)
            for args, kwargs in zip(args_sequence, kwargs_sequence):
                self.generate_card(deck, print_to_ipynb, *args, **kwargs)

    def print_card(self, *args, **kwargs):
        question = self.question_fn(*args, **kwargs)
        answer = self.answer_fn(*args, **kwargs)
        print("=" * 100)
        print(question)
        print("-" * 50)
        print(answer)


class FretboardCardGenerator(CardGenerator):
    def __init__(self, question_fn, answer_fn, fretboard_fn, tmp_fpath="/tmp/fretboard.png"):
        super().__init__(question_fn, answer_fn)
        self.fretboard_fn = fretboard_fn
        self.tmp_fpath = tmp_fpath

    def generate_card(self, deck=None, print_to_ipynb=False, *args, **kwargs):
        question = self.question_fn(*args, **kwargs)
        fretboard = self.fretboard_fn(*args, **kwargs)
        answer = self.answer_fn(*args, **kwargs)
        if deck is not None:
            # TODO: Add a method to Fretboard or AnkiDeck to do this directly, without the temporary file.
            fretboard.export(to=self.tmp_fpath, format="png")
            dest_fname = deck.save_media(source_fpath=self.tmp_fpath)
            card_question = question + f'<br><br><img src="{dest_fname}">'
            deck.add_card(card_question, answer)
        if print_to_ipynb:
            self.print_card(*args, **kwargs)
        return question, answer

    def print_card(self, *args, **kwargs):
        question_text = self.question_fn(*args, **kwargs)
        fretboard = self.fretboard_fn(*args, **kwargs)
        answer = self.answer_fn(*args, **kwargs)
        print("=" * 100)
        print(question_text)
        fretboard_utils.draw(fretboard)
        print("-" * 50)
        print(answer)
