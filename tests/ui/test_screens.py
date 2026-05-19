"""Integration tests for the main PyQt screens."""

from PyQt5.QtCore import Qt

from core.file_handler import write_abd_file
from ui.editor_screen import EditorScreen
from ui.list_screen import ListScreen
from ui.main_window import MainWindow
from ui.upload_screen import UploadScreen


def test_upload_screen_opens_existing_project(qtbot, app_config, translation_model):
    write_abd_file(
        f"{app_config.data_dir}/book.en.abd",
        {
            "name": "book",
            "author": "Tester",
            "role": "source",
            "language": "",
            "source_language": "en",
        },
        [(1, "First segment"), (2, "Second segment")],
    )
    screen = UploadScreen(translation_model, app_config)
    qtbot.addWidget(screen)
    emitted = []
    screen.file_processed.connect(lambda: emitted.append(True))

    screen.project_list.setCurrentRow(0)
    qtbot.mouseClick(screen.open_btn, Qt.LeftButton)

    assert emitted == [True]
    assert translation_model.base_filename == "book"
    assert translation_model.total_items() == 2
    assert translation_model.get_current_source_text() == "First segment"


def test_list_screen_filters_and_clears_rows(qtbot, app_config, loaded_model):
    screen = ListScreen(loaded_model, app_config)
    qtbot.addWidget(screen)
    screen.refresh()

    assert screen.filter_model.rowCount() == 3

    qtbot.keyClicks(screen.search_input, "World")
    qtbot.wait(250)

    assert screen.filter_model.rowCount() == 1
    assert screen.filter_model.index(0, 1).data() == "World"

    qtbot.mouseClick(screen.clear_search_btn, Qt.LeftButton)

    assert screen.search_input.text() == ""
    assert screen.filter_model.rowCount() == 3


def test_editor_screen_saves_dirty_translation_on_navigation(
    qtbot,
    app_config,
    loaded_model,
):
    screen = EditorScreen(loaded_model, app_config)
    qtbot.addWidget(screen)
    screen.load_current()

    qtbot.keyClicks(screen.translated_text, "Nomoskar")
    qtbot.mouseClick(screen.next_btn, Qt.LeftButton)

    assert loaded_model.current_index == 1
    assert loaded_model.translations[1] == "Nomoskar"
    assert screen.source_text.toPlainText() == "World"


def test_main_window_switches_between_screens(qtbot, app_config):
    window = MainWindow(app_config)
    qtbot.addWidget(window)
    window.model.load_source_text([(1, "Hello")], "book", "en")
    window.model.set_target_lang("bn", data_dir=app_config.data_dir)

    window.show_list_screen()
    assert window.stack.currentWidget() == window.list_screen

    window.show_editor_screen(0)
    assert window.stack.currentWidget() == window.editor_screen
    assert window.editor_screen.source_text.toPlainText() == "Hello"

    window.editor_screen.back_to_list.emit()
    assert window.stack.currentWidget() == window.list_screen
