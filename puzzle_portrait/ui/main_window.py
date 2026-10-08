"""Main window with a controls panel and a preview panel."""

from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QColor, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QToolBar,
    QToolButton,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from puzzle_portrait.config import (
    COLOR_COUNTS,
    CONFIG_FILENAME,
    DEFAULT_CELL_SIZE,
    DEFAULT_COLOR_COUNT,
    DEFAULT_ALLOW_BACKWARDS,
    DEFAULT_ALLOW_PHRASES,
    DEFAULT_BALANCE_DIRECTIONS,
    DEFAULT_DIAGONAL_WEIGHT,
    DEFAULT_FILL_PERCENT,
    DEFAULT_FONT_SIZE,
    DEFAULT_FONT_WEIGHT,
    DEFAULT_GRID_COLUMNS,
    DEFAULT_GRID_ROWS,
    DEFAULT_HORIZONTAL_WEIGHT,
    DEFAULT_SEED,
    DEFAULT_SPREAD_RATE,
    DEFAULT_SPREAD_WORDS,
    DEFAULT_TEXT_COLOR_MODE,
    DEFAULT_VERTICAL_WEIGHT,
    FONT_WEIGHT_LABELS,
    FONT_WEIGHTS,
    MAX_FILL_PERCENT,
    MAX_FONT_SIZE,
    MAX_GRID_SIZE,
    MAX_SPREAD_RATE,
    MAX_TILE_SIZE,
    MIN_FILL_PERCENT,
    MIN_FONT_SIZE,
    MIN_SPREAD_RATE,
    MIN_TILE_SIZE,
    MOSAIC_FILENAME,
    MOSAIC_LETTERS_FILENAME,
    PREVIEW_DEBOUNCE_MS,
    TEXT_COLOR_MODE_LABELS,
    TEXT_COLOR_MODES,
    WORDS_FILENAME,
)
from puzzle_portrait.image import (
    crop_region,
    grid_from_image,
    load_image,
    quantize_colors,
    resize_to_grid,
)
from puzzle_portrait.grid import RGB, combine_grids
from puzzle_portrait.project import (
    ProjectSettings,
    load_project,
    resolve_project_file,
    save_project,
)
from puzzle_portrait.render import (
    available_font_weights,
    render_color_grid,
    render_color_grid_svg,
)
from puzzle_portrait.ui.fonts import font_file_for_family, list_system_fonts
from puzzle_portrait.ui.preview import FitPreview
from puzzle_portrait.ui.preview_job import PreviewSettings, PreviewWorker
from puzzle_portrait.ui.sections import (
    CollapsibleSection,
    checkbox_with_help,
    labeled_field,
    stretch_control,
)
from puzzle_portrait.wordsearch import (
    LetterGrid,
    WordSearch,
    direction_weights_from_axes,
    fill_empty_random,
    generate_word_search,
    placement_directions,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Puzzle Portrait")
        self.resize(960, 600)
        self.source_image = None
        self._updating_crop = False
        self.output_dir: Path | None = None
        self._preview_token = 0
        self._preview_timer = QTimer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._start_preview_job)
        self._preview_workers: list[PreviewWorker] = []
        self._build_file_menu()

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.controls_panel = self._build_controls_panel()
        self.preview_panel = self._build_preview_panel()
        self.main_splitter.addWidget(self.controls_panel)
        self.main_splitter.addWidget(self.preview_panel)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 2)
        self.main_splitter.setCollapsible(0, False)
        self.main_splitter.setCollapsible(1, False)
        self.main_splitter.setSizes([280, 680])

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.main_splitter)
        self.setCentralWidget(container)

    def _build_controls_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("controlsPanel")
        panel.setMinimumWidth(180)

        title = QLabel("Controls")
        title.setObjectName("panelTitle")

        self.image_path = QLineEdit()
        self.image_path.setPlaceholderText("Path to photograph")
        self.image_path.setReadOnly(True)
        self.browse_button = QPushButton("Browse…")
        self.browse_button.clicked.connect(self.select_image)

        self.words_path = QLineEdit()
        self.words_path.setPlaceholderText("Path to word list")
        self.words_path.setReadOnly(True)
        self.browse_words_button = QPushButton("Browse…")
        self.browse_words_button.clicked.connect(self.select_word_list)

        self.words_input = QPlainTextEdit()
        self.words_input.setPlaceholderText(
            "One word or phrase per line. Optional: {{row, col}, HOR}"
        )
        self.words_input.setFixedHeight(120)

        self.unplaced_list = QLabel("All words fit.")
        self.unplaced_list.setObjectName("unplacedWords")
        self.unplaced_list.setWordWrap(True)
        self.unplaced_list.setTextFormat(Qt.TextFormat.PlainText)
        self.unplaced_report = CollapsibleSection("Could not place")
        self.unplaced_report.add_widget(self.unplaced_list)

        self.colors_input = QComboBox()
        self.colors_input.addItems([str(count) for count in COLOR_COUNTS])
        self.colors_input.setCurrentText(str(DEFAULT_COLOR_COUNT))
        self.colors_input.setEnabled(False)

        self.crop_width = self._crop_spinbox()
        self.crop_height = self._crop_spinbox()
        self.crop_x = self._crop_spinbox(minimum=0)
        self.crop_y = self._crop_spinbox(minimum=0)

        self.grid_columns = self._grid_spinbox(DEFAULT_GRID_COLUMNS)
        self.grid_rows = self._grid_spinbox(DEFAULT_GRID_ROWS)
        self.tile_size = QSpinBox()
        self.tile_size.setRange(MIN_TILE_SIZE, MAX_TILE_SIZE)
        self.tile_size.setValue(DEFAULT_CELL_SIZE)
        self.tile_size.valueChanged.connect(self._on_mosaic_settings_changed)

        self.font_input = QComboBox()
        self.font_input.setMaxVisibleItems(16)
        self.font_input.setMinimumContentsLength(12)
        self.font_input.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self._populate_font_input()
        self.font_input.currentIndexChanged.connect(self._on_mosaic_settings_changed)

        self.font_size = QSpinBox()
        self.font_size.setRange(MIN_FONT_SIZE, MAX_FONT_SIZE)
        self.font_size.setValue(DEFAULT_FONT_SIZE)
        self.font_size.valueChanged.connect(self._on_mosaic_settings_changed)

        self.font_weight = QComboBox()
        for key in FONT_WEIGHTS:
            self.font_weight.addItem(FONT_WEIGHT_LABELS[key], key)
        self.font_weight.setCurrentIndex(FONT_WEIGHTS.index(DEFAULT_FONT_WEIGHT))
        self.font_weight.currentIndexChanged.connect(self._on_mosaic_settings_changed)

        self._custom_text_color = RGB(0, 0, 0)
        self.font_color = QComboBox()
        for key in TEXT_COLOR_MODES:
            self.font_color.addItem(TEXT_COLOR_MODE_LABELS[key], key)
        self.font_color.setCurrentIndex(TEXT_COLOR_MODES.index(DEFAULT_TEXT_COLOR_MODE))
        self.font_color.currentIndexChanged.connect(self._on_text_color_mode_changed)
        self.custom_color_button = QPushButton("Pick…")
        self.custom_color_button.clicked.connect(self.select_custom_text_color)
        self._sync_custom_color_button()

        self.seed = QSpinBox()
        self.seed.setRange(0, 2_147_483_647)
        self.seed.setValue(DEFAULT_SEED)
        self.seed.valueChanged.connect(self._on_mosaic_settings_changed)

        self.spread_words = QCheckBox("Place words from the center outward")
        self.spread_words.setChecked(DEFAULT_SPREAD_WORDS)
        self.spread_words.toggled.connect(self._on_spread_words_toggled)
        self.spread_rate = QDoubleSpinBox()
        self.spread_rate.setRange(MIN_SPREAD_RATE, MAX_SPREAD_RATE)
        self.spread_rate.setSingleStep(0.1)
        self.spread_rate.setDecimals(2)
        self.spread_rate.setValue(DEFAULT_SPREAD_RATE)
        self.spread_rate.valueChanged.connect(self._on_mosaic_settings_changed)
        self._sync_spread_rate()
        self.allow_phrases = QCheckBox("Allow short phrases")
        self.allow_phrases.setChecked(DEFAULT_ALLOW_PHRASES)
        self.allow_phrases.toggled.connect(self._on_mosaic_settings_changed)
        self.fill_percent = QSpinBox()
        self.fill_percent.setRange(MIN_FILL_PERCENT, MAX_FILL_PERCENT)
        self.fill_percent.setValue(DEFAULT_FILL_PERCENT)
        self.fill_percent.setSuffix(" %")
        self.fill_percent.valueChanged.connect(self._on_mosaic_settings_changed)
        self.allow_backwards = QCheckBox("Allow backwards words")
        self.allow_backwards.setChecked(DEFAULT_ALLOW_BACKWARDS)
        self.allow_backwards.toggled.connect(self._on_mosaic_settings_changed)
        self.balance_directions = QCheckBox("Balance word directions")
        self.balance_directions.setChecked(DEFAULT_BALANCE_DIRECTIONS)
        self.balance_directions.toggled.connect(self._on_mosaic_settings_changed)
        self.horizontal_weight = self._weight_spinbox(DEFAULT_HORIZONTAL_WEIGHT)
        self.vertical_weight = self._weight_spinbox(DEFAULT_VERTICAL_WEIGHT)
        self.diagonal_weight = self._weight_spinbox(DEFAULT_DIAGONAL_WEIGHT)

        self.words_input.textChanged.connect(self._on_mosaic_settings_changed)
        self._set_image_controls_enabled(False)

        self.colors_input.currentTextChanged.connect(self._on_mosaic_settings_changed)
        self.words_input.setMinimumHeight(80)
        stretch_control(self.image_path)
        stretch_control(self.words_path)
        stretch_control(self.words_input)
        stretch_control(self.colors_input)
        stretch_control(self.font_input)
        stretch_control(self.font_color)
        for box in (
            self.crop_width,
            self.crop_height,
            self.crop_x,
            self.crop_y,
            self.grid_columns,
            self.grid_rows,
            self.tile_size,
            self.font_size,
            self.seed,
            self.fill_percent,
            self.spread_rate,
            self.horizontal_weight,
            self.vertical_weight,
            self.diagonal_weight,
        ):
            stretch_control(box)

        image_block = QWidget()
        image_block_layout = QHBoxLayout(image_block)
        image_block_layout.setContentsMargins(0, 0, 0, 0)
        image_block_layout.addWidget(self.image_path, 1)
        image_block_layout.addWidget(self.browse_button)

        words_file_block = QWidget()
        words_file_layout = QHBoxLayout(words_file_block)
        words_file_layout.setContentsMargins(0, 0, 0, 0)
        words_file_layout.addWidget(self.words_path, 1)
        words_file_layout.addWidget(self.browse_words_button)

        font_color_block = QWidget()
        font_color_layout = QHBoxLayout(font_color_block)
        font_color_layout.setContentsMargins(0, 0, 0, 0)
        font_color_layout.addWidget(self.font_color, 1)
        font_color_layout.addWidget(self.custom_color_button)

        image_section = CollapsibleSection("Image")
        image_section.add_widget(
            labeled_field(
                "Photograph",
                image_block,
                "The source picture. Crop and grid are taken from this file. "
                "The original image resolution is not changed.",
            )
        )
        image_section.add_widget(
            labeled_field(
                "Color count",
                self.colors_input,
                "How many colors the mosaic uses. Fewer colors look more "
                "poster-like. More colors keep more photo detail.",
            )
        )

        words_section = CollapsibleSection("Words")
        words_section.add_widget(
            labeled_field(
                "Word list file",
                words_file_block,
                "Load a text file with one word or phrase per line.",
            )
        )
        words_section.add_widget(
            labeled_field(
                "Words",
                self.words_input,
                "Entries to hide in the mosaic. One word or phrase per line. "
                "To pin the first letter, add {{row, col}, DIRECTION} after "
                "the text. Directions: HOR, VER, DIAG_LB_RU, DIAG_LU_RB. "
                "Row and column are 0-based from the top-left cell. Lines "
                "without a pin are placed by the tool.",
            )
        )
        words_section.add_widget(self.unplaced_report)
        words_section.add_widget(
            checkbox_with_help(
                self.allow_phrases,
                'When on, a line like "someone cool" is placed as one entry. '
                "The space occupies a tile.",
            )
        )
        words_section.add_widget(
            labeled_field(
                "Percent of empty tiles to fill",
                self.fill_percent,
                "Share of leftover tiles filled with random letters. "
                "0 leaves them empty. 100 fills all of them.",
            )
        )

        crop_section = CollapsibleSection("Crop")
        crop_section.add_widget(
            labeled_field(
                "Width",
                self.crop_width,
                "How wide a slice of the original photo to use. This crops; "
                "it does not shrink the source image.",
            )
        )
        crop_section.add_widget(
            labeled_field(
                "Height",
                self.crop_height,
                "How tall a slice of the original photo to use. This crops; "
                "it does not shrink the source image.",
            )
        )
        crop_section.add_widget(
            labeled_field(
                "X",
                self.crop_x,
                "Left edge of the crop, in pixels from the left of the original photo.",
            )
        )
        crop_section.add_widget(
            labeled_field(
                "Y",
                self.crop_y,
                "Top edge of the crop, in pixels from the top of the original photo.",
            )
        )

        grid_section = CollapsibleSection("Grid")
        grid_section.add_widget(
            labeled_field(
                "Columns",
                self.grid_columns,
                "How many tiles across. More columns keep more image detail.",
            )
        )
        grid_section.add_widget(
            labeled_field(
                "Rows",
                self.grid_rows,
                "How many tiles down. More rows keep more image detail.",
            )
        )
        grid_section.add_widget(
            labeled_field(
                "Tile size",
                self.tile_size,
                "How many pixels wide and tall each tile is drawn. This only "
                "changes the preview and saved image size. It does not change "
                "the puzzle grid or the source photo.",
            )
        )

        font_section = CollapsibleSection("Font")
        font_section.add_widget(
            labeled_field(
                "Font",
                self.font_input,
                "Typeface used for letters in the preview and saved mosaics.",
            )
        )
        font_section.add_widget(
            labeled_field(
                "Font size",
                self.font_size,
                "Letter size in pixels on the rendered mosaic.",
            )
        )
        font_section.add_widget(
            labeled_field(
                "Font weight",
                self.font_weight,
                "Regular, Medium, SemiBold, or Bold, when that weight file exists.",
            )
        )
        font_section.add_widget(
            labeled_field(
                "Font color",
                font_color_block,
                "How letter color is chosen: automatic contrast, black, white, "
                "a custom color, or a lighter/darker shade of the tile.",
            )
        )

        placement_section = CollapsibleSection("Placement")
        placement_section.add_widget(
            labeled_field(
                "Seed",
                self.seed,
                "The same seed and settings produce the same word placement.",
            )
        )
        placement_section.add_widget(
            checkbox_with_help(
                self.spread_words,
                "When on, the first words put their middle letter on the center "
                "tile. Later words move outward.",
            )
        )
        placement_section.add_widget(
            labeled_field(
                "Spread rate",
                self.spread_rate,
                "How quickly later words move away from the center. 0 keeps "
                "them near the middle. Higher reaches the edges sooner.",
            )
        )
        placement_section.add_widget(
            checkbox_with_help(
                self.allow_backwards,
                "When off, words only run left to right, top to bottom, and "
                "left-to-right diagonals. When on, reverse directions are also used.",
            )
        )
        placement_section.add_widget(
            checkbox_with_help(
                self.balance_directions,
                "Prefer a mix of horizontal, vertical, and diagonal so one "
                "axis does not take most of the words.",
            )
        )
        placement_section.add_widget(
            labeled_field(
                "Horizontal weight",
                self.horizontal_weight,
                "Share of words that run left–right. 1, 1, 2 means about "
                "25% horizontal, 25% vertical, 50% diagonal. 0 forbids this axis.",
            )
        )
        placement_section.add_widget(
            labeled_field(
                "Vertical weight",
                self.vertical_weight,
                "Share of words that run top–bottom. 1, 1, 2 means about "
                "25% horizontal, 25% vertical, 50% diagonal. 0 forbids this axis.",
            )
        )
        placement_section.add_widget(
            labeled_field(
                "Diagonal weight",
                self.diagonal_weight,
                "Share of words that run diagonally. 1, 1, 2 means about "
                "25% horizontal, 25% vertical, 50% diagonal. 0 forbids this axis.",
            )
        )

        self.control_sections = (
            image_section,
            words_section,
            crop_section,
            grid_section,
            font_section,
            placement_section,
        )

        form_host = QWidget()
        form_layout = QVBoxLayout(form_host)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(2)
        for section in self.control_sections:
            form_layout.addWidget(section)
        form_layout.addStretch(1)

        self.controls_scroll = QScrollArea()
        self.controls_scroll.setObjectName("controlsScroll")
        self.controls_scroll.setWidgetResizable(True)
        self.controls_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.controls_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.controls_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.controls_scroll.setWidget(form_host)

        layout = QVBoxLayout(panel)
        layout.addWidget(title)
        layout.addWidget(self.controls_scroll, 1)
        return panel

    def _build_file_menu(self) -> None:
        file_menu = QMenu(self)

        self.new_action = QAction("Create &New", self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.triggered.connect(self.create_new_project)
        file_menu.addAction(self.new_action)
        self.addAction(self.new_action)

        self.open_action = QAction("&Open…", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self.select_project)
        file_menu.addAction(self.open_action)
        self.addAction(self.open_action)

        file_menu.addSeparator()

        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_current_project)
        file_menu.addAction(self.save_action)
        self.addAction(self.save_action)

        self.save_as_action = QAction("Save &As…", self)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_action.triggered.connect(self.select_output_directory)
        file_menu.addAction(self.save_as_action)
        self.addAction(self.save_as_action)

        file_menu.addSeparator()

        quit_action = QAction("E&xit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        self.addAction(quit_action)

        self.menuBar().hide()
        self.file_button = QToolButton()
        self.file_button.setObjectName("fileMenuButton")
        self.file_button.setText("File")
        self.file_button.setMenu(file_menu)
        self.file_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.file_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.file_button.setAutoRaise(False)
        self.file_button.setStyleSheet(
            "QToolButton#fileMenuButton {"
            " padding: 4px 16px;"
            " min-width: 56px;"
            "}"
        )

        toolbar = QToolBar()
        toolbar.setObjectName("fileToolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.addWidget(self.file_button)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

    def closeEvent(self, event) -> None:
        self._wait_for_preview_workers(timeout_ms=3000)
        super().closeEvent(event)

    def _build_preview_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("previewPanel")
        panel.setMinimumWidth(240)

        title = QLabel("Preview")
        title.setObjectName("panelTitle")
        self.show_cell_coords = QCheckBox("Show row, col")
        self.show_cell_coords.setObjectName("showCellCoords")
        self.show_cell_coords.setToolTip(
            "When on, hovering a mosaic cell shows its row and column. "
            "Top-left is 0, 0, matching {{row, col}, DIRECTION} pins."
        )
        self.show_cell_coords.toggled.connect(self._on_show_cell_coords)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.show_cell_coords)

        self.preview_placeholder = FitPreview()

        layout = QVBoxLayout(panel)
        layout.addWidget(header)
        layout.addWidget(self.preview_placeholder, 1)
        return panel

    def _on_show_cell_coords(self, enabled: bool) -> None:
        self.preview_placeholder.set_show_cell_hover(enabled)

    def select_image(self) -> None:
        QToolTip.hideText()
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a photograph",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff);;All files (*.*)",
        )
        if path:
            self.load_selected_image(path)

    def load_selected_image(self, path: str | Path) -> None:
        try:
            image = load_image(path)
        except (FileNotFoundError, OSError) as exc:
            QMessageBox.warning(self, "Could not load image", str(exc))
            return

        self.source_image = image
        self.image_path.setText(str(Path(path)))
        self._reset_crop_to_full_image()
        self._refresh_preview()

    def select_word_list(self) -> None:
        QToolTip.hideText()
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a word list",
            "",
            "Text files (*.txt);;All files (*.*)",
        )
        if path:
            self.load_word_list(path)

    def load_word_list(self, path: str | Path) -> None:
        try:
            text = Path(path).read_text(encoding="utf-8")
        except OSError as exc:
            QMessageBox.warning(self, "Could not load word list", str(exc))
            return

        words = [line.strip() for line in text.splitlines() if line.strip()]
        self.words_path.setText(str(Path(path)))
        self.words_input.setPlainText("\n".join(words))

    def _crop_spinbox(self, minimum: int = 1) -> QSpinBox:
        box = QSpinBox()
        box.setMinimum(minimum)
        box.setMaximum(1)
        box.valueChanged.connect(self._on_crop_changed)
        return box

    def _set_image_controls_enabled(self, enabled: bool) -> None:
        for box in (
            self.crop_width,
            self.crop_height,
            self.crop_x,
            self.crop_y,
            self.colors_input,
            self.grid_columns,
            self.grid_rows,
            self.tile_size,
            self.font_input,
            self.font_size,
            self.font_weight,
            self.font_color,
            self.custom_color_button,
            self.seed,
            self.spread_words,
            self.spread_rate,
            self.balance_directions,
            self.horizontal_weight,
            self.vertical_weight,
            self.diagonal_weight,
        ):
            box.setEnabled(enabled)
        self._sync_custom_color_button()
        self._sync_spread_rate()

    def _reset_crop_to_full_image(self) -> None:
        if self.source_image is None:
            return
        width, height = self.source_image.size
        self._updating_crop = True
        self.crop_width.setRange(1, width)
        self.crop_height.setRange(1, height)
        self.crop_width.setValue(width)
        self.crop_height.setValue(height)
        self.crop_x.setRange(0, 0)
        self.crop_y.setRange(0, 0)
        self.crop_x.setValue(0)
        self.crop_y.setValue(0)
        self._set_image_controls_enabled(True)
        self._updating_crop = False

    def _grid_spinbox(self, value: int) -> QSpinBox:
        box = QSpinBox()
        box.setRange(2, MAX_GRID_SIZE)
        box.setValue(value)
        box.valueChanged.connect(self._on_mosaic_settings_changed)
        return box

    def _weight_spinbox(self, value: float) -> QDoubleSpinBox:
        box = QDoubleSpinBox()
        box.setRange(0.0, 20.0)
        box.setSingleStep(0.1)
        box.setDecimals(2)
        box.setValue(value)
        box.valueChanged.connect(self._on_mosaic_settings_changed)
        return box

    def _on_spread_words_toggled(self, *_args) -> None:
        self._sync_spread_rate()
        self._on_mosaic_settings_changed()

    def _sync_spread_rate(self) -> None:
        self.spread_rate.setEnabled(
            self.spread_words.isEnabled() and self.spread_words.isChecked()
        )

    def _on_mosaic_settings_changed(self, *_args) -> None:
        if self._updating_crop or self.source_image is None:
            return
        self._schedule_preview()

    def _on_text_color_mode_changed(self, *_args) -> None:
        self._sync_custom_color_button()
        self._on_mosaic_settings_changed()

    def select_custom_text_color(self) -> None:
        current = QColor(
            self._custom_text_color.red,
            self._custom_text_color.green,
            self._custom_text_color.blue,
        )
        chosen = QColorDialog.getColor(current, self, "Letter color")
        if not chosen.isValid():
            return
        self._custom_text_color = RGB(chosen.red(), chosen.green(), chosen.blue())
        self._sync_custom_color_button()
        self._on_mosaic_settings_changed()

    def _sync_custom_color_button(self) -> None:
        custom = self.font_color.currentData() == "custom"
        self.custom_color_button.setEnabled(custom and self.font_color.isEnabled())
        color = self._custom_text_color
        self.custom_color_button.setStyleSheet(
            f"background-color: rgb({color.red}, {color.green}, {color.blue});"
        )

    def _selected_font_weight(self) -> str:
        return str(self.font_weight.currentData() or "regular")

    def _selected_text_color_mode(self) -> str:
        return str(self.font_color.currentData() or "automatic")

    def _letter_style(self, font_weight: str | None = None) -> dict:
        return {
            "font_weight": font_weight or self._selected_font_weight(),
            "text_color_mode": self._selected_text_color_mode(),
            "text_color": self._custom_text_color,
        }

    def _lettered_svgs_by_weight(self, grid) -> dict[str, str]:
        return {
            weight: self._render_mosaic_svg(
                grid,
                draw_letters=True,
                font_weight=weight,
            )
            for weight in available_font_weights(self._selected_font_path())
        }

    def _on_crop_changed(self) -> None:
        if self._updating_crop or self.source_image is None:
            return
        self._updating_crop = True
        self._sync_crop_limits()
        self._updating_crop = False
        self._schedule_preview()

    def _sync_crop_limits(self) -> None:
        if self.source_image is None:
            return
        image_width, image_height = self.source_image.size
        width = min(self.crop_width.value(), image_width)
        height = min(self.crop_height.value(), image_height)
        max_x = image_width - width
        max_y = image_height - height
        self.crop_width.setRange(1, image_width)
        self.crop_height.setRange(1, image_height)
        self.crop_x.setRange(0, max_x)
        self.crop_y.setRange(0, max_y)
        self.crop_x.setValue(min(self.crop_x.value(), max_x))
        self.crop_y.setValue(min(self.crop_y.value(), max_y))

    def create_new_project(self) -> bool:
        if not self._confirm_save_before_replace():
            return False
        self._reset_session()
        return True

    def _has_project_work(self) -> bool:
        return bool(
            self.source_image is not None
            or self.output_dir is not None
            or self.image_path.text().strip()
            or self.words_path.text().strip()
            or self._current_words()
        )

    def _confirm_save_before_replace(self) -> bool:
        if not self._has_project_work():
            return True
        QToolTip.hideText()
        answer = QMessageBox.question(
            self,
            "Save current project?",
            "Save the current project before starting a new one?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Cancel:
            return False
        if answer == QMessageBox.StandardButton.Save:
            return self.save_current_project() is not None
        return True

    def _reset_session(self) -> None:
        self._wait_for_preview_workers()
        self.source_image = None
        self.output_dir = None
        self._updating_crop = True
        self.image_path.clear()
        self.words_path.clear()
        self.words_input.clear()
        self.colors_input.setCurrentText(str(DEFAULT_COLOR_COUNT))
        self.crop_width.setRange(1, 1)
        self.crop_height.setRange(1, 1)
        self.crop_width.setValue(1)
        self.crop_height.setValue(1)
        self.crop_x.setRange(0, 0)
        self.crop_y.setRange(0, 0)
        self.crop_x.setValue(0)
        self.crop_y.setValue(0)
        self.grid_columns.setValue(DEFAULT_GRID_COLUMNS)
        self.grid_rows.setValue(DEFAULT_GRID_ROWS)
        self.tile_size.setValue(DEFAULT_CELL_SIZE)
        self.font_input.blockSignals(True)
        self._select_preferred_font()
        self.font_input.blockSignals(False)
        self.font_size.setValue(DEFAULT_FONT_SIZE)
        self.font_weight.setCurrentIndex(FONT_WEIGHTS.index(DEFAULT_FONT_WEIGHT))
        self.font_color.setCurrentIndex(TEXT_COLOR_MODES.index(DEFAULT_TEXT_COLOR_MODE))
        self._custom_text_color = RGB(0, 0, 0)
        self._sync_custom_color_button()
        self.seed.setValue(DEFAULT_SEED)
        self.spread_words.setChecked(DEFAULT_SPREAD_WORDS)
        self.spread_rate.setValue(DEFAULT_SPREAD_RATE)
        self.allow_phrases.setChecked(DEFAULT_ALLOW_PHRASES)
        self.fill_percent.setValue(DEFAULT_FILL_PERCENT)
        self.allow_backwards.setChecked(DEFAULT_ALLOW_BACKWARDS)
        self.balance_directions.setChecked(DEFAULT_BALANCE_DIRECTIONS)
        self.horizontal_weight.setValue(DEFAULT_HORIZONTAL_WEIGHT)
        self.vertical_weight.setValue(DEFAULT_VERTICAL_WEIGHT)
        self.diagonal_weight.setValue(DEFAULT_DIAGONAL_WEIGHT)
        for section in self.control_sections:
            section.set_expanded(False)
        self.unplaced_report.set_expanded(False)
        self._set_unplaced_words(())
        self._updating_crop = False
        self._set_image_controls_enabled(False)
        self.preview_placeholder.clear_preview()

    def save_current_project(self) -> Path | None:
        if self.output_dir is not None:
            return self.save_project_to(self.output_dir)
        return self.select_output_directory()

    def select_output_directory(self) -> Path | None:
        if self.source_image is None or not self.image_path.text():
            QMessageBox.warning(self, "Nothing to save", "Load a photograph first.")
            return None
        QToolTip.hideText()
        directory = QFileDialog.getExistingDirectory(self, "Choose output folder")
        if directory:
            return self.save_project_to(directory)
        return None

    def save_project_to(self, directory: str | Path) -> Path | None:
        if self.source_image is None or not self.image_path.text():
            QMessageBox.warning(self, "Nothing to save", "Load a photograph first.")
            return None
        QToolTip.hideText()
        self._wait_for_preview_workers()
        self.preview_placeholder.set_working(True)
        QApplication.processEvents()
        try:
            combined, failed_words = self._combined_grid()
            config_path = save_project(
                directory,
                self._current_settings(failed_words=failed_words),
                source_image=self.image_path.text(),
                mosaic=self._render_mosaic(combined, draw_letters=False),
                mosaic_letters=self._render_mosaic(combined, draw_letters=True),
                mosaic_svg=self._render_mosaic_svg(combined, draw_letters=False),
                mosaic_letters_svg=self._render_mosaic_svg(combined, draw_letters=True),
                mosaic_letters_svgs=self._lettered_svgs_by_weight(combined),
            )
        except Exception as exc:
            QMessageBox.warning(self, "Could not save project", str(exc))
            return None
        finally:
            self.preview_placeholder.set_working(False)

        self.output_dir = Path(directory)
        self.words_path.setText(str(self.output_dir / WORDS_FILENAME))
        return config_path

    def select_project(self) -> None:
        QToolTip.hideText()
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open a project",
            "",
            f"Project ({CONFIG_FILENAME});;JSON (*.json);;All files (*.*)",
        )
        if path:
            self.load_project_from(path)

    def load_project_from(self, path: str | Path) -> None:
        self.preview_placeholder.set_working(True)
        try:
            settings, folder = load_project(path)
            image_path = resolve_project_file(folder, settings.image)
            image = load_image(image_path)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            self.preview_placeholder.set_working(False)
            QMessageBox.warning(self, "Could not open project", str(exc))
            return

        self._apply_project(settings, folder, image, image_path)

    def _set_unplaced_words(self, failed_words: tuple[str, ...] = ()) -> None:
        if failed_words:
            self.unplaced_report.set_title(f"Could not place ({len(failed_words)})")
            self.unplaced_list.setText("\n".join(failed_words))
        else:
            self.unplaced_report.set_title("Could not place")
            self.unplaced_list.setText("All words fit.")

    def _current_words(self) -> list[str]:
        return [
            line.strip()
            for line in self.words_input.toPlainText().splitlines()
            if line.strip()
        ]

    def _current_settings(self, failed_words: tuple[str, ...] = ()) -> ProjectSettings:
        return ProjectSettings(
            image=Path(self.image_path.text()).name,
            words=tuple(self._current_words()),
            words_file=WORDS_FILENAME,
            seed=self.seed.value(),
            color_count=int(self.colors_input.currentText()),
            crop_x=self.crop_x.value(),
            crop_y=self.crop_y.value(),
            crop_width=self.crop_width.value(),
            crop_height=self.crop_height.value(),
            columns=self.grid_columns.value(),
            rows=self.grid_rows.value(),
            tile_size=self.tile_size.value(),
            font=self.font_input.currentText(),
            font_file=self._selected_font_path(),
            font_size=self.font_size.value(),
            font_weight=self._selected_font_weight(),
            text_color_mode=self._selected_text_color_mode(),
            custom_text_color=(
                self._custom_text_color.red,
                self._custom_text_color.green,
                self._custom_text_color.blue,
            ),
            grid_lines=True,
            mosaic=MOSAIC_FILENAME,
            mosaic_letters=MOSAIC_LETTERS_FILENAME,
            failed_words=failed_words,
            spread_words=self.spread_words.isChecked(),
            spread_rate=self.spread_rate.value(),
            balance_directions=self.balance_directions.isChecked(),
            horizontal_weight=self.horizontal_weight.value(),
            vertical_weight=self.vertical_weight.value(),
            diagonal_weight=self.diagonal_weight.value(),
            allow_phrases=self.allow_phrases.isChecked(),
            fill_percent=self.fill_percent.value(),
            allow_backwards=self.allow_backwards.isChecked(),
        )

    def _apply_project(
        self,
        settings: ProjectSettings,
        folder: Path,
        image,
        image_path: Path,
    ) -> None:
        self._updating_crop = True
        self.source_image = image
        self.output_dir = folder
        self.image_path.setText(str(image_path))
        words_path = resolve_project_file(folder, settings.words_file)
        self.words_path.setText(str(words_path) if words_path.exists() else "")
        self.words_input.setPlainText("\n".join(settings.words))
        self.colors_input.setCurrentText(str(settings.color_count))
        width, height = image.size
        self.crop_width.setRange(1, width)
        self.crop_height.setRange(1, height)
        self.crop_width.setValue(min(settings.crop_width, width))
        self.crop_height.setValue(min(settings.crop_height, height))
        self._sync_crop_limits()
        self.crop_x.setValue(min(settings.crop_x, self.crop_x.maximum()))
        self.crop_y.setValue(min(settings.crop_y, self.crop_y.maximum()))
        self.grid_columns.setValue(settings.columns)
        self.grid_rows.setValue(settings.rows)
        self.tile_size.setValue(settings.tile_size)
        self._select_font(settings.font, settings.font_file)
        self.font_size.setValue(settings.font_size)
        weight_index = self.font_weight.findData(settings.font_weight)
        if weight_index >= 0:
            self.font_weight.setCurrentIndex(weight_index)
        mode_index = self.font_color.findData(settings.text_color_mode)
        if mode_index >= 0:
            self.font_color.setCurrentIndex(mode_index)
        red, green, blue = settings.custom_text_color
        self._custom_text_color = RGB(red, green, blue)
        self._sync_custom_color_button()
        self.seed.setValue(settings.seed)
        self.spread_words.setChecked(settings.spread_words)
        self.spread_rate.setValue(settings.spread_rate)
        self.allow_phrases.setChecked(settings.allow_phrases)
        self.fill_percent.setValue(settings.fill_percent)
        self.allow_backwards.setChecked(settings.allow_backwards)
        self.balance_directions.setChecked(settings.balance_directions)
        self.horizontal_weight.setValue(settings.horizontal_weight)
        self.vertical_weight.setValue(settings.vertical_weight)
        self.diagonal_weight.setValue(settings.diagonal_weight)
        self._set_image_controls_enabled(True)
        self._sync_custom_color_button()
        self._updating_crop = False
        self.preview_placeholder.set_working(True)
        self._start_preview_job()

    def _select_font(self, family: str, font_file: str | None) -> None:
        index = self.font_input.findText(family)
        if index < 0 and font_file:
            for item in range(self.font_input.count()):
                if self.font_input.itemData(item) == font_file:
                    index = item
                    break
        if index >= 0:
            self.font_input.setCurrentIndex(index)

    def _word_search(self, columns: int, rows: int) -> WordSearch:
        words = [word.upper() for word in self._current_words()]
        percent = self.fill_percent.value()
        if words:
            return generate_word_search(
                columns,
                rows,
                words,
                directions=self._placement_directions(),
                seed=self.seed.value(),
                spread_words=self.spread_words.isChecked(),
                spread_rate=self.spread_rate.value(),
                balance_directions=self.balance_directions.isChecked(),
                direction_weights=self._direction_weights(),
                fill_percent=percent,
                allow_phrases=self.allow_phrases.isChecked(),
            )
        grid = LetterGrid(columns, rows)
        fill_empty_random(grid, seed=self.seed.value(), percent=percent)
        return WordSearch(grid=grid, placements=(), failed_words=())

    def _placement_directions(self):
        return placement_directions(allow_backwards=self.allow_backwards.isChecked())

    def _direction_weights(self):
        weights = direction_weights_from_axes(
            self.horizontal_weight.value(),
            self.vertical_weight.value(),
            self.diagonal_weight.value(),
        )
        if all(abs(weight - 1.0) < 1e-12 for weight in weights.values()):
            return None
        return weights

    def _combined_grid(self):
        if self.source_image is None:
            raise ValueError("Load a photograph first.")
        cropped = crop_region(
            self.source_image,
            self.crop_x.value(),
            self.crop_y.value(),
            self.crop_width.value(),
            self.crop_height.value(),
        )
        columns = self.grid_columns.value()
        rows = self.grid_rows.value()
        sampled = resize_to_grid(cropped, columns, rows)
        quantized = quantize_colors(sampled, int(self.colors_input.currentText()))
        puzzle = self._word_search(columns, rows)
        return combine_grids(grid_from_image(quantized), puzzle.grid), puzzle.failed_words

    def _render_mosaic(self, grid, *, draw_letters: bool):
        try:
            return render_color_grid(
                grid,
                cell_size=self.tile_size.value(),
                draw_letters=draw_letters,
                font=self._selected_font_path(),
                font_size=self.font_size.value(),
                grid_lines=True,
                **self._letter_style(),
            )
        except (OSError, FileNotFoundError):
            return render_color_grid(
                grid,
                cell_size=self.tile_size.value(),
                draw_letters=draw_letters,
                font_size=self.font_size.value(),
                grid_lines=True,
                **self._letter_style(),
            )

    def _render_mosaic_svg(
        self,
        grid,
        *,
        draw_letters: bool,
        font_weight: str | None = None,
    ) -> str:
        return render_color_grid_svg(
            grid,
            cell_size=self.tile_size.value(),
            draw_letters=draw_letters,
            font=self._selected_font_path(),
            font_family=self.font_input.currentText() or "sans-serif",
            font_size=self.font_size.value(),
            grid_lines=True,
            **self._letter_style(font_weight),
        )

    def _preview_settings(self) -> PreviewSettings:
        return PreviewSettings(
            crop_x=self.crop_x.value(),
            crop_y=self.crop_y.value(),
            crop_width=self.crop_width.value(),
            crop_height=self.crop_height.value(),
            columns=self.grid_columns.value(),
            rows=self.grid_rows.value(),
            color_count=int(self.colors_input.currentText()),
            words=tuple(word.upper() for word in self._current_words()),
            seed=self.seed.value(),
            spread_words=self.spread_words.isChecked(),
            spread_rate=self.spread_rate.value(),
            balance_directions=self.balance_directions.isChecked(),
            direction_weights=self._direction_weights(),
            directions=self._placement_directions(),
            fill_percent=self.fill_percent.value(),
            allow_phrases=self.allow_phrases.isChecked(),
            tile_size=self.tile_size.value(),
            font=self._selected_font_path(),
            font_size=self.font_size.value(),
            font_weight=self._selected_font_weight(),
            text_color_mode=self._selected_text_color_mode(),
            text_color=self._custom_text_color,
        )

    def _wait_for_preview_workers(self, timeout_ms: int | None = None) -> None:
        """Finish background preview jobs before using Pillow on this thread."""
        self._preview_timer.stop()
        self._preview_token += 1
        for worker in list(self._preview_workers):
            if worker.isRunning():
                if timeout_ms is None:
                    worker.wait()
                else:
                    worker.wait(timeout_ms)
        self._preview_workers.clear()

    def _schedule_preview(self) -> None:
        if self.source_image is None:
            return
        self.preview_placeholder.set_working(True)
        self._preview_timer.start(PREVIEW_DEBOUNCE_MS)

    def _start_preview_job(self) -> None:
        if self.source_image is None:
            self.preview_placeholder.set_working(False)
            return
        self._preview_token += 1
        token = self._preview_token
        self.preview_placeholder.set_working(True)
        self._preview_workers = [item for item in self._preview_workers if item.isRunning()]
        worker = PreviewWorker(token, self.source_image.copy(), self._preview_settings())
        worker.preview_ready.connect(self._on_preview_ready)
        worker.preview_failed.connect(self._on_preview_failed)
        self._preview_workers.append(worker)
        worker.start()

    def _on_preview_ready(self, image, token: int, failed_words=()) -> None:
        if token != self._preview_token:
            return
        self._show_preview_image(image)
        self._set_unplaced_words(tuple(failed_words or ()))
        if not self._preview_timer.isActive():
            self.preview_placeholder.set_working(False)

    def _on_preview_failed(self, _message: str, token: int) -> None:
        if token != self._preview_token:
            return
        if not self._preview_timer.isActive():
            self.preview_placeholder.set_working(False)

    def flush_preview(self) -> None:
        """Build the preview now. Used after a finished action and in tests."""
        self._refresh_preview()

    def _refresh_preview(self) -> None:
        self._wait_for_preview_workers()
        if self.source_image is None:
            self.preview_placeholder.set_working(False)
            return
        combined, failed = self._combined_grid()
        self._set_unplaced_words(failed)
        self._show_preview_image(self._render_mosaic(combined, draw_letters=True))
        self.preview_placeholder.set_working(False)

    def _show_preview_image(self, image) -> None:
        self.preview_placeholder.set_source_image(
            image,
            columns=self.grid_columns.value(),
            rows=self.grid_rows.value(),
        )

    def _populate_font_input(self) -> None:
        self.font_input.blockSignals(True)
        for family, path in list_system_fonts(regular_only=True):
            self.font_input.addItem(family, str(path))
        self._select_preferred_font()
        self.font_input.blockSignals(False)

    def _select_preferred_font(self) -> None:
        for preferred in ("Segoe UI", "Arial", "Calibri", "DejaVu Sans", "Helvetica"):
            index = self.font_input.findText(preferred)
            if index >= 0:
                self.font_input.setCurrentIndex(index)
                break

    def _selected_font_path(self) -> str | None:
        path = self.font_input.currentData()
        if path:
            return path
        resolved = font_file_for_family(self.font_input.currentText())
        return str(resolved) if resolved is not None else None
