from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal

from services.documents.workspace_port import DocumentWorkspacePort


class SearchResultListModel(QAbstractListModel):
    countChanged = Signal()

    FILE_INDEX_ROLE = Qt.ItemDataRole.UserRole.value + 1
    MATCH_INDEX_ROLE = FILE_INDEX_ROLE + 1
    DOCUMENT_ID_ROLE = FILE_INDEX_ROLE + 2
    FILE_ROLE = FILE_INDEX_ROLE + 3
    LINE_ROLE = FILE_INDEX_ROLE + 4
    TEXT_ROLE = FILE_INDEX_ROLE + 5
    DISPLAY_TEXT_ROLE = FILE_INDEX_ROLE + 6
    START_ROLE = FILE_INDEX_ROLE + 7
    END_ROLE = FILE_INDEX_ROLE + 8
    BEFORE_ROLE = FILE_INDEX_ROLE + 9
    MATCH_ROLE = FILE_INDEX_ROLE + 10
    AFTER_ROLE = FILE_INDEX_ROLE + 11
    REPLACEMENT_ROLE = FILE_INDEX_ROLE + 12

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[dict[str, str | int]] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._rows):
            return None
        row = self._rows[index.row()]
        if role == self.FILE_INDEX_ROLE:
            return row["fileIndex"]
        if role == self.MATCH_INDEX_ROLE:
            return row["matchIndex"]
        if role == self.DOCUMENT_ID_ROLE:
            return row["documentId"]
        if role == self.FILE_ROLE:
            return row["file"]
        if role == self.LINE_ROLE:
            return row["line"]
        if role == self.TEXT_ROLE:
            return row["text"]
        if role == self.DISPLAY_TEXT_ROLE or role == Qt.ItemDataRole.DisplayRole:
            return row["displayText"]
        if role == self.START_ROLE:
            return row["start"]
        if role == self.END_ROLE:
            return row["end"]
        if role == self.BEFORE_ROLE:
            return row["before"]
        if role == self.MATCH_ROLE:
            return row["match"]
        if role == self.AFTER_ROLE:
            return row["after"]
        if role == self.REPLACEMENT_ROLE:
            return row["replacement"]
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.FILE_INDEX_ROLE: QByteArray(b"fileIndex"),
            self.MATCH_INDEX_ROLE: QByteArray(b"matchIndex"),
            self.DOCUMENT_ID_ROLE: QByteArray(b"documentId"),
            self.FILE_ROLE: QByteArray(b"file"),
            self.LINE_ROLE: QByteArray(b"line"),
            self.TEXT_ROLE: QByteArray(b"text"),
            self.DISPLAY_TEXT_ROLE: QByteArray(b"displayText"),
            self.START_ROLE: QByteArray(b"start"),
            self.END_ROLE: QByteArray(b"end"),
            self.BEFORE_ROLE: QByteArray(b"before"),
            self.MATCH_ROLE: QByteArray(b"match"),
            self.AFTER_ROLE: QByteArray(b"after"),
            self.REPLACEMENT_ROLE: QByteArray(b"replacement"),
        }

    @property
    def count(self) -> int:
        return len(self._rows)

    def reset_from_files(self, files: DocumentWorkspacePort) -> None:
        rows: list[dict[str, str | int]] = []
        for file_index, document in enumerate(files.documents()):
            if not document.is_active:
                continue
            file_label = document.relative_path or document.file_name
            for preview in document.match_previews:
                line = int(preview.get("line", 0) or 0)
                match_index = int(preview.get("index", 0) or 0)
                text = str(preview.get("lineText", "") or "")
                rows.append(
                    {
                        "fileIndex": file_index,
                        "matchIndex": match_index,
                        "documentId": document.id,
                        "file": file_label,
                        "line": line,
                        "text": text,
                        "displayText": f"[{file_label}] [{line if line > 0 else '?'}] {text}",
                        "start": int(preview.get("start", 0) or 0),
                        "end": int(preview.get("end", 0) or 0),
                        "before": str(preview.get("before", "") or ""),
                        "match": str(preview.get("match", "") or ""),
                        "after": str(preview.get("after", "") or ""),
                        "replacement": str(preview.get("replacement", "") or ""),
                    }
                )

        self.beginResetModel()
        self._rows = rows
        self.endResetModel()
        self.countChanged.emit()
