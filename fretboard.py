from fretboardgtr import fretboard
from fretboardgtr.elements import notes, nut, strings

# In getting this to look exactly how I wanted, I had to make a couple changes to the fretboardgtr library:
# TODO: Clean these changes up and fork the library. Consider submitting a PR.
# 1. Add `stroke` and `stroke_width` to the svgwrite.shapes.Rect constructor in fretboardgtr/elements/background.py
#    to get a border around the fretboard.
# 2. Nudge the double inlay dots inward in fretboardgtr/fretboards/fretboard.py to account for string padding.

DEFAULT_CONFIG = fretboard.FretBoardConfig.from_dict(
    {
        "general": {
            "first_fret": 0,
            "last_fret": 12,
            "show_tuning": False,
            "x_start": 10,
            "show_frets": False,
            "fret_width": 80,
            "fret_height": 40,
            "x_end_offset": -30,
            "y_end_offset": -50,
        },
        "neck_dots": {
            "color": "rgb(229,227,222)",
            "width_stroke": 0,
            "radius": 10,
        },
        "nut": {"width": 0},
        "background": {"color": "rgb(254,250,240)", "opacity": 1},
        "frets": {"color": "rgb(152,150,145)", "width": 4},
        "strings": {"width": 0},
    }
)

DEFAULT_NOTE_COLOR = "rgb(183,64,50)"


class FretBoard:
    def __init__(self, config=DEFAULT_CONFIG):
        self.fretboard = fretboard.FretBoard(config=config)

        (self.ulx, uly), (lrx, lry) = self.fretboard.get_inside_bounds()
        n_frets = config.general.last_fret - config.general.first_fret + 1
        n_strings = len(self.fretboard._fretboard.tuning)
        self.fret_width = (lrx - self.ulx) / n_frets
        fret_height = (lry - uly) / (n_strings - 1)

        string_width = 3  # TODO: make this configurable
        string_padding = fret_height // 3  # TODO: make this configurable
        self.top_string_y = uly + string_padding
        bottom_string_y = lry - string_padding
        self.string_sep = (bottom_string_y - self.top_string_y) / (n_strings - 1)
        for string_num in range(n_strings):
            y = self.top_string_y + string_num * self.string_sep
            string = strings.String(
                start_position=(self.ulx + self.fret_width, y),
                end_position=(lrx, y),
                config=strings.StringConfig(color="rgb(209,183,156)", width=string_width),
            )
            self.fretboard.add_element(string)

        nut_width = self.fret_width / 2  # TODO: make this configurable
        self.nut_x = self.ulx + self.fret_width - nut_width / 2
        nut_element = nut.Nut(
            start_position=(self.nut_x, uly - 1),
            end_position=(self.nut_x, lry + 1),
            config=nut.NutConfig(color="rgb(170,170,170)", width=nut_width),
        )
        self.fretboard.add_element(nut_element)

    def add_note(self, string, fret, label="", color=DEFAULT_NOTE_COLOR):
        """Add a note to the fretboard.

        Args:
            string: 1-indexed string number. In standard tuning, 1 is the high E string, and 6 is the low E string.
            fret: 0-indexed fret number.
            label: Label to display on the note. By default, no label is displayed.
            color: Color of the note. By default, the note is red.
        """
        pos_x = self.ulx + (fret + 1 / 2) * self.fret_width if fret > 0 else self.nut_x
        pos_y = self.top_string_y + (string - 1) * self.string_sep
        note = notes.FrettedNote(
            name=label,
            position=(pos_x, pos_y),
            config=notes.FrettedNoteConfig(
                color=color,
                radius=12,  # TODO: make this configurable
                stroke_width=1,
            ),
        )
        self.fretboard.add_element(note)

    def export(self, *args, **kwargs):
        self.fretboard.export(*args, **kwargs)
