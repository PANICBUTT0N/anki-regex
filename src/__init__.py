from aqt import mw
from aqt.browser import Browser
from anki.hooks import addHook
from aqt.utils import (
    ensure_editor_saved,
    skip_if_selection_is_empty,
    showInfo,
    qconnect
)
import re


@skip_if_selection_is_empty
def regex(browser: Browser) -> None:
    nids = browser.table.get_selected_note_ids()

    for nid in nids:
        note = mw.col.get_note(nid)
        field = note.items()
    mw.reset()
