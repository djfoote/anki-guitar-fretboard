from fretboardgtr.exporters import PNGExporter, register_exporter
from IPython.display import Image, display


class IPythonExporter(PNGExporter):
    def export(self, to):
        super().export(to)
        display(Image(filename=to))


register_exporter(IPythonExporter, "DRAW")


def draw(fretboard, tmp_filepath="/tmp/fretboard.png"):
    fretboard.export(to=tmp_filepath, format="draw")
