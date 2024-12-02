from relieur.relieur import process_concat
from pathlib import Path
THIS_DIR = Path(__file__).parent

def test_module():
    file_list = (THIS_DIR / "test1.musicxml", THIS_DIR / "test2.musicxml",THIS_DIR / "test3.musicxml",)
    m, files, measures = process_concat([str(file) for file in file_list])
    m.write("/tmp/test.musicxml")
    assert measures == 9
    assert files == 3

