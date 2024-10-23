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
    results = []
    if search_field == 'All Fields':
        matches = [f'"note:{note_type}"' for note_type in FIELDS_DICT]
        search_term = (' or '.join(matches))
        nids = mw.col.find_notes(search_term)

        for nid in nids:
            note = mw.col.get_note(nid)
            items = (note.items())
            for field in items:
                if re.search(pattern, field[1]):
                    results.append(nid)
    else:
        matches = []
        for note_type, fields in FIELDS_DICT.items():
            if search_field in fields:
                matches.append(f'"note:{note_type}"')  # Add handling for no results
        search_term = (' or '.join(matches))
        nids = mw.col.find_notes(search_term)

        for nid in nids:
            note = mw.col.get_note(nid)
            items = dict(note.items())
            if re.search(pattern, items[search_field]):
                results.append(nid)

    return results


def search_in_browser(results):
    search_query = 'nid:' + ','.join(map(str, results))
    browser = Browser(mw)
    browser.form.searchEdit.lineEdit().setText(search_query)
    browser.onSearchActivated()


def regex_search_window():
    dialog = QDialog(mw)
    dialog.setWindowTitle('Regex Find and Replace')
    layout = QVBoxLayout()
    dialog.resize(200, 150)

    all_fields = list(set(field for fields_list in FIELDS_DICT.values() for field in fields_list))
    all_fields.sort()
    all_fields = ['All Fields'] + all_fields

    fields_dropdown_text_label = QLabel('Choose field:')
    layout.addWidget(fields_dropdown_text_label)
    field_dropdown = QComboBox()
    field_dropdown.addItems(all_fields)
    layout.addWidget(field_dropdown)

    regex_text_label = QLabel('Enter your regular expression:')
    layout.addWidget(regex_text_label)
    regex_input = QLineEdit()
    layout.addWidget(regex_input)

    ok_button = QPushButton('OK')
    ok_button.clicked.connect(lambda: on_ok(dialog, field_dropdown, regex_input))
    layout.addWidget(ok_button)

    dialog.setLayout(layout)
    dialog.exec()


def on_ok(dialog, field_dropdown, regex_input):
    if regex_input.text():
        regex_input_text = regex_input.text()
        selected_field = field_dropdown.currentText()

        results = regex(selected_field, regex_input_text)
        if not results:
            showInfo('no results man')
        else:
            search_in_browser(results)
        dialog.accept()
    else:
        showInfo("hey bro you didn't input a regex pattern")
        dialog.accept()


def setup_menu(browser: Browser) -> None:
    menu = browser.form.menuEdit
    menu.addSeparator()
    action = menu.addAction('Regex Search')
    action.triggered.connect(regex_search_window)

    mw.form.menuEdit.addAction(action)


addHook("browser.setupMenus", setup_menu)
