from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PySide6.QtCore import QCoreApplication

from features.file_management.application.service import FileManagementService
from features.file_management.infrastructure.document_repository import FileRepository
from features.file_management.presentation.import_change_watcher import ImportChangeWatcher
from services.documents.collection import DocumentCollection


class ImportChangeWatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._application = QCoreApplication.instance() or QCoreApplication([])

    def test_external_change_is_reported_once_until_acknowledged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text('{"value": 1}', encoding="utf-8")
            watcher = ImportChangeWatcher()
            detected: list[list[str]] = []
            watcher.changed.connect(detected.append)
            watcher.watch_paths([path])

            path.write_text('{"value": 2}', encoding="utf-8")
            watcher._on_file_changed(str(path))
            watcher._on_file_changed(str(path))

            self.assertEqual(detected, [[str(path.resolve())]])
            watcher.acknowledge([path])
            path.write_text('{"value": 3}', encoding="utf-8")
            watcher._on_file_changed(str(path))
            self.assertEqual(detected, [[str(path.resolve())], [str(path.resolve())]])

    def test_reimport_replaces_the_disk_baseline_and_preserves_document_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text('{"value": 1}', encoding="utf-8")
            documents = DocumentCollection()
            service = FileManagementService(documents, FileRepository())
            self.assertEqual(service.add_paths([path]).added, 1)
            imported = documents.document_at(0)
            assert imported is not None
            original_id = imported.id

            path.write_text('{"value": 2}', encoding="utf-8")
            result = service.reload_paths([path])
            reimported = documents.document_at(0)

            self.assertEqual(result.added, 1)
            assert reimported is not None
            self.assertEqual(reimported.id, original_id)
            self.assertIn('2', reimported.text)
            self.assertFalse(reimported.is_dirty)
            self.assertEqual(reimported.initial_text, reimported.text)


if __name__ == "__main__":
    unittest.main()
