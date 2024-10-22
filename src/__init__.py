from aqt import mw
from aqt.browser import Browser
from aqt.qt import *
from anki.hooks import addHook
from aqt.utils import showInfo, qconnect
import re

FIELDS_DICT = {}
models = []


def retrieve_note_types():
    global models, FIELDS_DICT
    if mw and mw.col:
        models = mw.col.models.all()
        for note_type in models:
            all_fields_dict = note_type['flds']
            fields_list = [field_name['name'] for field_name in all_fields_dict]
            FIELDS_DICT[note_type['name']] = fields_list

addHook("profileLoaded", retrieve_note_types)


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
    search_query = 'nid:' + ','.join(map(str, results))
    showInfo(search_query)
    browser = Browser(mw)
    browser.form.searchEdit.lineEdit().setText(search_query)
    browser.onSearchActivated()


def regex_search_window():
    if not models:
        showInfo("Note types have not been loaded yet!")
        return

    dialog = QDialog(mw)
    dialog.setWindowTitle('Select a field:')
    layout = QVBoxLayout()

    all_fields = list(set(field for fields_list in FIELDS_DICT.values() for field in fields_list))
    all_fields.sort()
    all_fields = ['All fields'] + all_fields

    field_dropdown = QComboBox()
    field_dropdown.addItems(all_fields)
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
    regex_input_text = regex_input.text()
    results = regex(selected_field, regex_input_text)
    search_in_browser(results)
    dialog.accept()


def setup_menu(browser: Browser) -> None:
    menu_notes = browser.form.menu_Notes
    menu_notes.addSeparator()
    regex_search = QAction('Regex Search', menu_notes)
    regex_search.setObjectName('regex_search')
    qconnect(regex_search.triggered, lambda: regex_search_window())
    menu_notes.addAction(regex_search)


def main():
    addHook('browser.setupMenus', setup_menu)


main()
