from aqt import mw
from aqt.browser import Browser
from aqt.qt import *
from anki.hooks import addHook
from aqt.utils import (
    skip_if_selection_is_empty,
    showInfo,
    qconnect
)
import re

FIELDS_DICT = {}
for note_type in mw.col.models.all():
    all_fields_dict = note_type['flds']
    fields_list = [field_name['name'] for field_name in all_fields_dict]
    FIELDS_DICT.update({note_type['name']: fields_list})
FIELDS = list(set(field for fields_list in FIELDS_DICT.values() for field in fields_list))
FIELDS.insert(0, 'All fields')


def regex(search_field, pattern):
    matches = []
    for note_type, fields in FIELDS_DICT.items():
        if search_field in fields:
            matches.append(note_type)
    search_term = ('note:' + ' or note:'.join(matches))

    nids = mw.col.find_notes(search_term)
    results = []

    for nid in nids:
        note = mw.col.get_note(nid)
        items = dict(note.items())
        if re.search(pattern, items[search_field]):
            results.append(nid)
    return results


def search_in_browser(results):
    browser = Browser(mw)
    browser.show()

    search_query = 'nid:' + ','.join(results)
    browser.searchEdit.setText(search_query)

    browser.onSearch()


def regex_search_window():
    dialog = QDialog(mw)
    dialog.setWindowTitle('Select a field:')
    layout = QVBoxLayout()

    field_dropdown = QComboBox()
    field_dropdown.addItems(FIELDS)
    layout.addWidget(field_dropdown)

    text_label = QLabel('Enter your regular expression:')
    layout.addWidget(text_label)
    regex_input = QLineEdit()
    layout.addWidget(regex_input)

    ok_button = QPushButton('OK')
    ok_button.clicked.connect(lambda: on_ok(dialog, field_dropdown, regex_input))
    layout.addWidget(ok_button)

    dialog.setLayout(layout)

    dialog.exec()


def on_ok(dialog, field_dropdown, regex_input):
    selected_field = field_dropdown.currentText()
    regex_input = regex_input.text()
    results = regex(selected_field, regex_input)
    search_in_browser(results)
    dialog.accept()


def setup_menu():
    action = QAction('Regex Search', mw)
    action.triggered.connect(regex_search_window)
    mw.browser.form.menu_Notes.addAction(action)


setup_menu()
