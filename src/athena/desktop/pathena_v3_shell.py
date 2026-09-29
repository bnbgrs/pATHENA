        inspector.setMinimumWidth(300)
        inspector.setMaximumWidth(380)
        inspector.hide()

        body_layout.addWidget(main, 1)
        body_layout.addWidget(inspector)
        root.addWidget(body, 1)

        legacy_shell.setParent(shell)
        legacy_shell.hide()
        window.setCentralWidget(shell)
        window.resize(1580, 960)
        window.setMinimumSize(1120, 720)

    def _build_rail(self) -> QWidget:
        rail = QFrame()
        rail.setObjectName("v3Rail")
        rail.setFixedWidth(76)

        layout = QVBoxLayout(rail)
        layout.setContentsMargins(8, 18, 8, 16)
        layout.setSpacing(4)

        mark = QLabel("P")
        mark.setObjectName("v3Mark")
        mark.setFixedSize(34, 34)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setToolTip("pATHENA")
        layout.addWidget(mark, 0, Qt.AlignmentFlag.AlignHCenter)

        layout.addSpacing(14)

        for index in range(5):
            layout.addWidget(
                self._make_nav_button(index, _PAGE_NAMES[index]),
                0,
                Qt.AlignmentFlag.AlignHCenter,
            )

        layout.addSpacing(4)
        divider = QFrame()