import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from pypdf import PdfReader, PdfWriter

from merge_pdfs import App, merge_pdfs


# ── helpers ──────────────────────────────────────────────────────────────────

def _blank_pdf(path, pages=1):
    w = PdfWriter()
    for _ in range(pages):
        w.add_blank_page(width=72, height=72)
    with open(path, "wb") as f:
        w.write(f)


def _sized_pdf(path, width, height):
    w = PdfWriter()
    w.add_blank_page(width=width, height=height)
    with open(path, "wb") as f:
        w.write(f)


class _FakeListbox:
    """Minimal Listbox replacement for testing App logic without a display."""

    def __init__(self, names=None):
        self._items = list(names or [])
        self._selection = None

    def insert(self, pos, item):
        if pos == "end":
            self._items.append(item)
        else:
            self._items.insert(pos, item)

    def delete(self, pos):
        del self._items[pos]

    def get(self, pos):
        return self._items[pos]

    def curselection(self):
        return (self._selection,) if self._selection is not None else ()

    def select_set(self, pos):
        self._selection = pos

    def size(self):
        return len(self._items)


def _bare_app(paths=None):
    """Create an App instance bypassing all Tk initialisation."""
    app = object.__new__(App)
    app._paths = list(paths or [])
    app.lb = _FakeListbox([os.path.basename(p) for p in app._paths])
    return app


# ── merge_pdfs() ─────────────────────────────────────────────────────────────

class TestMergePdfs(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _p(self, name):
        return os.path.join(self.tmp, name)

    def test_output_file_is_created(self):
        a = self._p("a.pdf"); _blank_pdf(a)
        out = self._p("out.pdf")
        merge_pdfs([a], out)
        self.assertTrue(os.path.exists(out))

    def test_page_count_equals_number_of_inputs(self):
        a = self._p("a.pdf"); _blank_pdf(a)
        b = self._p("b.pdf"); _blank_pdf(b)
        out = self._p("out.pdf")
        merge_pdfs([a, b], out)
        self.assertEqual(len(PdfReader(out).pages), 2)

    def test_multipage_sources_are_counted_correctly(self):
        a = self._p("a.pdf"); _blank_pdf(a, pages=3)
        b = self._p("b.pdf"); _blank_pdf(b, pages=2)
        out = self._p("out.pdf")
        merge_pdfs([a, b], out)
        self.assertEqual(len(PdfReader(out).pages), 5)

    def test_preserves_order(self):
        sizes = [(72, 72), (100, 100), (200, 200)]
        paths = []
        for i, (w, h) in enumerate(sizes):
            p = self._p(f"{i}.pdf")
            _sized_pdf(p, w, h)
            paths.append(p)
        out = self._p("ordered.pdf")
        merge_pdfs(paths, out)
        reader = PdfReader(out)
        for i, page in enumerate(reader.pages):
            self.assertAlmostEqual(float(page.mediabox.width), sizes[i][0])

    def test_single_file(self):
        a = self._p("single.pdf"); _blank_pdf(a)
        out = self._p("out.pdf")
        merge_pdfs([a], out)
        self.assertEqual(len(PdfReader(out).pages), 1)

    def test_creates_output_subdirectory(self):
        a = self._p("a.pdf"); _blank_pdf(a)
        out = os.path.join(self.tmp, "sub", "dir", "out.pdf")
        merge_pdfs([a], out)
        self.assertTrue(os.path.exists(out))


# ── App — list management ─────────────────────────────────────────────────────

class TestAppListManagement(unittest.TestCase):

    def test_swap_updates_paths_and_listbox(self):
        app = _bare_app(["/a.pdf", "/b.pdf", "/c.pdf"])
        app._swap(0, 1)
        self.assertEqual(app._paths, ["/b.pdf", "/a.pdf", "/c.pdf"])
        self.assertEqual(app.lb._items, ["b.pdf", "a.pdf", "c.pdf"])

    def test_move_up_shifts_item(self):
        app = _bare_app(["/a.pdf", "/b.pdf"])
        app.lb._selection = 1
        app._up()
        self.assertEqual(app._paths, ["/b.pdf", "/a.pdf"])
        self.assertEqual(app.lb._selection, 0)

    def test_move_up_on_first_item_is_noop(self):
        app = _bare_app(["/a.pdf", "/b.pdf"])
        app.lb._selection = 0
        app._up()
        self.assertEqual(app._paths, ["/a.pdf", "/b.pdf"])

    def test_move_down_shifts_item(self):
        app = _bare_app(["/a.pdf", "/b.pdf"])
        app.lb._selection = 0
        app._down()
        self.assertEqual(app._paths, ["/b.pdf", "/a.pdf"])
        self.assertEqual(app.lb._selection, 1)

    def test_move_down_on_last_item_is_noop(self):
        app = _bare_app(["/a.pdf", "/b.pdf"])
        app.lb._selection = 1
        app._down()
        self.assertEqual(app._paths, ["/a.pdf", "/b.pdf"])

    def test_remove_selected_item(self):
        app = _bare_app(["/a.pdf", "/b.pdf"])
        app.lb._selection = 0
        app._remove()
        self.assertEqual(app._paths, ["/b.pdf"])
        self.assertEqual(app.lb._items, ["b.pdf"])

    def test_remove_with_no_selection_is_noop(self):
        app = _bare_app(["/a.pdf"])
        app.lb._selection = None
        app._remove()
        self.assertEqual(app._paths, ["/a.pdf"])

    def test_add_ignores_duplicate_paths(self):
        app = _bare_app()
        with patch("merge_pdfs.filedialog.askopenfilenames", return_value=["/a.pdf", "/a.pdf", "/b.pdf"]):
            app._add()
        self.assertEqual(app._paths, ["/a.pdf", "/b.pdf"])
        self.assertEqual(len(app.lb._items), 2)

    def test_add_does_not_re_add_existing_path(self):
        app = _bare_app(["/a.pdf"])
        with patch("merge_pdfs.filedialog.askopenfilenames", return_value=["/a.pdf"]):
            app._add()
        self.assertEqual(len(app._paths), 1)


# ── App — merge validation ────────────────────────────────────────────────────

class TestAppMergeValidation(unittest.TestCase):

    def _app(self, paths, output):
        app = _bare_app(paths)
        app.out_var = MagicMock()
        app.out_var.get.return_value = output
        return app

    def test_warns_when_list_is_empty(self):
        app = self._app([], "out.pdf")
        with patch("merge_pdfs.messagebox.showwarning") as warn:
            app._merge()
            warn.assert_called_once()

    def test_warns_when_output_path_is_blank(self):
        app = self._app(["/a.pdf"], "   ")
        with patch("merge_pdfs.messagebox.showwarning") as warn:
            app._merge()
            warn.assert_called_once()

    def test_calls_merge_pdfs_with_correct_arguments(self):
        app = self._app(["/a.pdf", "/b.pdf"], "/tmp/out.pdf")
        with patch("merge_pdfs.merge_pdfs") as mock_merge, \
             patch("merge_pdfs.messagebox.showinfo"):
            app._merge()
            mock_merge.assert_called_once_with(["/a.pdf", "/b.pdf"], "/tmp/out.pdf")

    def test_shows_success_message(self):
        app = self._app(["/a.pdf"], "/tmp/out.pdf")
        with patch("merge_pdfs.merge_pdfs"), \
             patch("merge_pdfs.messagebox.showinfo") as info:
            app._merge()
            info.assert_called_once()

    def test_shows_error_on_exception(self):
        app = self._app(["/a.pdf"], "/tmp/out.pdf")
        with patch("merge_pdfs.merge_pdfs", side_effect=OSError("disk full")), \
             patch("merge_pdfs.messagebox.showerror") as err:
            app._merge()
            self.assertIn("disk full", err.call_args[0][1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
