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


def test_a_deleted_file_waits_in_the_trash_and_is_restored_from_it(q):
    """Deleting moves a file to the share's Trash, where its record says when
    and where from; moving it back out restores it."""
    drive = next(s for s in q.list("share") if s["kind"] == "drive")
    q.seed("file", share=drive.id, name="Letters", kind="folder", folder="")
    note = q.seed("file", share=drive.id, name="old.md", folder="Letters", text="Dear all")
    assert note["deleted"] is None
    q.delete("file", note.id)
    assert [f["name"] for f in q.list("file", share=drive.id, folder="Letters")] == []
    trashed = q.list("file", share=drive.id, folder="Trash")
    assert [f["name"] for f in trashed] == ["old.md"]
    assert trashed[0]["deleted"] and trashed[0]["deleted_from"] == "Letters/old.md"
    back = q.change("file", trashed[0].id, folder="Letters", name="old.md")
    assert back["path"] == "Letters/old.md" and back["deleted"] is None
    assert q.list("file", share=drive.id, folder="Trash") == []
    # In the Trash, delete is for good.
    q.delete("file", back.id)
    gone = q.list("file", share=drive.id, folder="Trash")[0]
    q.delete("file", gone.id)
    assert q.list("file", share=drive.id, folder="Trash") == []
