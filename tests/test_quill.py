"""Files' tests: the real shares backend and gate, on this machine.

Files has no code: its grid and the shares behind it are the core's. These
hold what the manifest promises.
"""

import pytest

from cloudmorrow.quill.testing import Harness


@pytest.fixture()
def q():
    with Harness(".") as harness:
        yield harness


def test_everybody_has_my_files(q):
    shares = q.list("share")
    assert any(s["kind"] == "drive" for s in shares)


def test_a_folder_made_in_my_files_is_there(q):
    drive = next(s for s in q.list("share") if s["kind"] == "drive")
    q.seed("file", share=drive.id, name="Photos", kind="folder", folder="")
    names = [f["name"] for f in q.list("file", share=drive.id, folder="")]
    assert "Photos" in names
