#!/usr/bin/env python3
"""
Generic professional PDF generator.

Clean, modern design: white backgrounds, blue accents, professional typography.
No branding — designed for any creator to use as-is or customize.

Usage:
    python3 pdf_generator.py --content-file content.json --output output.pdf

JSON content format:
{
    "type": "setup-guide|cheatsheet|quick-reference|how-to-guide|checklist",
    "title": "Document Title",
    "subtitle": "Optional subtitle text",
    "subtitle_bullets": ["Bullet 1", "Bullet 2"],
    "footer_text": "Your Footer Text | 2026",
    "sections": [
        {"type": "section_title", "number": "01", "title": "Section Name"},
        {"type": "body", "text": "Paragraph text."},
        {"type": "heading", "text": "Heading text"},
        {"type": "bullets", "items": ["Item 1", "Item 2"]},
        {"type": "code_block", "code": "code here"},
        {"type": "tip_box", "title": "Pro Tip", "text": "Tip text."},
        {"type": "table", "headers": ["Col 1", "Col 2"], "rows": [["A", "B"]]},
        {"type": "checklist", "items": ["Check item 1", "Check item 2"]},
        {"type": "numbered_steps", "steps": [{"title": "Step 1", "description": "Do this"}]},
        {"type": "two_column", "items": [["Label", "Value"], ["Label2", "Value2"]]},
        {"type": "callout_box", "title": "Important", "items": ["Item 1"]},
        {"type": "resources", "items": ["Resource 1", "Resource 2"]},
        {"type": "page_break"}
    ]
}
"""

import argparse
import json
import sys
from pathlib import Path

from fpdf import FPDF


MAX_PAGES = 6

_FONT_DIR = Path.home() / "Library" / "Fonts"


class ProfessionalDoc(FPDF):
    """Barbenders Belgium — licht thema, goud accent, Montserrat uppercase."""

    # ── Barbenders Belgium kleurpalet (licht, printbaar) ──
    BG_PAGE = (255, 255, 255)          # wit  pagina-achtergrond
    WHITE = (255, 255, 255)            # wit
    LIGHT_BG = (248, 248, 248)         # heel licht grijs  card-achtergrond
    DARK_BG = (240, 240, 240)          # iets donkerder grijs  striping
    CHARCOAL = (13, 13, 13)            # #0D0D0D  primaire tekst
    CHARCOAL_LIGHT = (55, 65, 81)      # donkergrijs  secundaire tekst
    BLUE = (255, 213, 0)               # #FFD500  goud accent
    BLUE_LIGHT = (255, 235, 120)       # lichtgoud
    BLUE_BG = (255, 251, 210)          # zeer lichte goudtint  achtergrond
    AMBER = (255, 213, 0)              # #FFD500  zelfde als goud
    AMBER_BG = (255, 251, 210)         # zeer lichte goudtint  tip-achtergrond
    GRAY = (90, 95, 105)               # donkergrijs  body tekst
    LIGHT_GRAY = (140, 145, 155)       # subtiele tekst
    BORDER = (220, 220, 220)           # lichte rand
    CODE_BG = (31, 41, 55)             # donker voor code blokken (contrast)
    CODE_TEXT = (248, 249, 250)        # lichte code tekst
    ACCENT_FG = (13, 13, 13)           # #0D0D0D  tekst OP goud elementen

    # ── Layout ────────────────────────────────────────────
    MARGIN = 20
    HEADER_BAR_H = 2
    FOOTER_H = 10

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=22)
        self.set_margin(self.MARGIN)
        self._footer_text = "Barbenders Belgium | 2026"
        self._is_cover_page = True
        self._doc_title = ""
        self._bg_drawn_pages = set()
        self._register_fonts()

    def _ensure_dark_bg(self):
        """Teken donkere achtergrond op huidige pagina — betrouwbaar bij automatische paginabreuken."""
        p = self.page_no()
        if p in self._bg_drawn_pages:
            return
        self._bg_drawn_pages.add(p)
        saved_x, saved_y = self.get_x(), self.get_y()
        self.set_fill_color(*self.BG_PAGE)
        self.rect(0, 0, self.w, self.h, style="F")
        # Gouden top-balk op inhoudspagina's
        if not self._is_cover_page:
            self.set_fill_color(*self.BLUE)
            self.rect(0, 0, self.w, self.HEADER_BAR_H, style="F")
            self.set_y(self.HEADER_BAR_H + 2)
            self.set_font("Montserrat", "B", 6.5)
            self.set_text_color(*self.LIGHT_GRAY)
            self.cell(0, 4, self._doc_title.upper()[:60], align="C")
            self.set_y(self.HEADER_BAR_H + 8)
        self.set_xy(saved_x, saved_y)

    def _register_fonts(self):
        fd = _FONT_DIR
        self.add_font("Montserrat", "", str(fd / "Montserrat-Regular.ttf"))
        self.add_font("Montserrat", "B", str(fd / "Montserrat-Bold.ttf"))
        self.add_font("MontserratSB", "", str(fd / "Montserrat-SemiBold.ttf"))
        self.add_font("Poppins", "", str(fd / "Poppins-Regular.ttf"))
        self.add_font("Poppins", "B", str(fd / "Poppins-Bold.ttf"))
        self.add_font("PoppinsMed", "", str(fd / "Poppins-Medium.ttf"))
        self.add_font("PoppinsSB", "", str(fd / "Poppins-SemiBold.ttf"))
        self.add_font("RobotoMono", "", str(fd / "RobotoMono-Regular.ttf"))
        self.add_font("RobotoMono", "B", str(fd / "RobotoMono-Medium.ttf"))

    # ── helpers ───────────────────────────────────────────

    def _color(self, rgb):
        self.set_text_color(*rgb)

    def _bg(self, rgb):
        self.set_fill_color(*rgb)

    def _draw(self, rgb):
        self.set_draw_color(*rgb)

    def _check_page_limit(self):
        return self.page > MAX_PAGES

    def _ensure_space(self, needed_h):
        remaining = self.h - self.b_margin - self.get_y()
        if remaining < needed_h:
            self.add_page()

    @staticmethod
    def _clean(text):
        import re
        text = text.replace('\u2192', '->')
        text = re.sub(
            r'[\U0001F300-\U0001F9FF\U00002702-\U000027B0\U0000FE00-\U0000FE0F'
            r'\U0000200D\U00002600-\U000026FF\U00002B50]+',
            '', text,
        )
        return text.strip()

    def _sharp_rect(self, x, y, w, h, fill_color, border_color=None, border_w=0):
        """Draw a sharp-cornered rectangle with optional border."""
        with self.local_context():
            self._bg(fill_color)
            if border_color and border_w > 0:
                self._draw(border_color)
                self.set_line_width(border_w)
                self.rect(x, y, w, h, style="FD")
            else:
                self.rect(x, y, w, h, style="F")

    def _offset_shadow(self, x, y, w, h, offset=2):
        """Draw a solid offset shadow."""
        with self.local_context():
            self._bg(self.BORDER)
            self.rect(x + offset, y + offset, w, h, style="F")

    def _bordered_card(self, x, y, w, h, fill=None, border_w=1, shadow_offset=2):
        """Draw a card with border and subtle offset shadow."""
        fill = fill or self.WHITE
        self._offset_shadow(x, y, w, h, offset=shadow_offset)
        self._sharp_rect(x, y, w, h, fill, self.BORDER, border_w)

    def _divider(self, y=None):
        """Draw a thin horizontal divider."""
        if y is None:
            y = self.get_y()
        with self.local_context():
            self._draw(self.BORDER)
            self.set_line_width(0.5)
            self.line(self.l_margin, y, self.w - self.r_margin, y)

    # ── page headers & footers ────────────────────────────

    def header(self):
        if self._is_cover_page:
            return
        # Gouden top-balk
        self.set_fill_color(*self.BLUE)
        self.rect(0, 0, self.w, self.HEADER_BAR_H, style="F")
        self.set_y(self.HEADER_BAR_H + 2)
        self.set_font("Montserrat", "B", 6.5)
        self.set_text_color(*self.ACCENT_FG)
        self.cell(0, 4, self._doc_title.upper()[:60], align="C")
        self.set_y(self.HEADER_BAR_H + 8)

    def footer(self):
        self.set_y(-self.FOOTER_H - 2)
        # Divider line
        with self.local_context():
            self._draw(self.BORDER)
            self.set_line_width(0.5)
            self.line(self.MARGIN, self.get_y(), self.w - self.MARGIN, self.get_y())
        self.ln(3)
        self.set_font("Montserrat", "", 6)
        self._color(self.LIGHT_GRAY)
        self.cell(0, 4, self._footer_text.upper(), align="L")
        self.set_x(-self.MARGIN)
        self._color(self.BLUE)
        self.set_font("Montserrat", "B", 7)
        self.cell(0, 4, f"{self.page_no():02d}", align="R")

    # ── Cover Page ────────────────────────────────────────

    def render_cover(self, title, subtitle=None, subtitle_bullets=None,
                     cover_label=None, learn_label=None, series_label=None):
        self.add_page()
        self._is_cover_page = True
        self._doc_title = title

        # ── Volledige donkere achtergrond ────────────────────
        self._sharp_rect(0, 0, self.w, self.h, self.CHARCOAL)

        # ── Top gouden balk met label ─────────────────────────
        top_bar_h = 14
        self._sharp_rect(0, 0, self.w, top_bar_h, self.BLUE)
        self.set_font("Montserrat", "B", 7)
        self._color(self.ACCENT_FG)
        self.set_xy(0, (top_bar_h - 4) / 2)
        self.cell(self.w, 4, (cover_label or "BARBENDERS COACHING").upper(), align="C")

        # ── Titel — wit, groot, uppercase ────────────────────
        title_y = top_bar_h + 36
        self.set_xy(self.l_margin, title_y)
        self.set_font("Montserrat", "B", 36)
        self._color(self.WHITE)
        self.multi_cell(0, 14, title.upper(), align="L")

        # ── Subtitle ─────────────────────────────────────────
        if subtitle:
            self.ln(10)
            self.set_font("Poppins", "", 12)
            self._color(self.LIGHT_GRAY)
            self.multi_cell(self.epw * 0.85, 7, subtitle, align="L")

        # ── Gouden divider ───────────────────────────────────
        self.ln(8)
        divider_y = self.get_y()
        with self.local_context():
            self._draw(self.BLUE)
            self.set_line_width(0.8)
            self.line(self.l_margin, divider_y, self.w - self.r_margin, divider_y)

        # ── "WAT JE LEERT" label ─────────────────────────────
        self.ln(8)
        self.set_font("Montserrat", "B", 8)
        self._color(self.BLUE)
        self.set_x(self.l_margin)
        self.cell(0, 5, (learn_label or "WAT JE LEERT").upper(), new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # ── Bullets — goud vierkantje + witte tekst ───────────
        if subtitle_bullets:
            for item in subtitle_bullets:
                bx = self.l_margin
                by = self.get_y()
                self._sharp_rect(bx, by + 2, 4, 4, self.BLUE)
                self.set_x(bx + 9)
                self._color(self.WHITE)
                self.set_font("Poppins", "", 10.5)
                self.multi_cell(self.epw - 9, 6.5, item)
                self.ln(4)

        # Disable auto page break so bottom-of-cover elements don't trigger spurious new pages
        self.set_auto_page_break(False)

        # ── Decoratief getal in achtergrond ──────────────────
        ghost_y = self.h - 80
        self.set_font("Montserrat", "B", 120)
        self.set_text_color(30, 30, 30)
        self.set_xy(self.w - self.l_margin - 70, ghost_y)
        self.cell(60, 80, "01", align="R")

        # ── Seriesslabel boven de onderste balk ──────────────
        series_bar_y = self.h - 18
        self._sharp_rect(self.l_margin, series_bar_y, self.epw, 10, (30, 30, 30))
        self.set_font("Montserrat", "B", 8)
        self._color(self.BLUE)
        self.set_xy(self.l_margin + 4, series_bar_y + 2.5)
        self.cell(self.epw - 8, 5, (series_label or "START TO CALISTHENICS — DEEL 1/5").upper(), new_x="RIGHT", new_y="TOP")
        self._color(self.LIGHT_GRAY)
        self.set_font("Poppins", "", 7)
        self.cell(0, 5, "barbenderstreetworkout.com", align="R")

        # ── Onderste gouden balk met footer ──────────────────
        bottom_bar_y = self.h - 8
        self._sharp_rect(0, bottom_bar_y, self.w, 8, self.BLUE)
        self.set_font("Montserrat", "B", 7)
        self._color(self.ACCENT_FG)
        self.set_xy(0, bottom_bar_y + 2)
        self.cell(self.w, 4, self._footer_text.upper(), align="C")

        self._is_cover_page = False
        self.set_auto_page_break(True, margin=22)

    # ── Section Title ─────────────────────────────────────

    def render_section_title(self, num, title):
        if self._check_page_limit():
            return
        self._ensure_space(26)
        self.ln(6)

        y = self.get_y()

        # Bottom border
        border_y = y + 14
        with self.local_context():
            self._draw(self.CHARCOAL)
            self.set_line_width(1.5)
            self.line(self.l_margin, border_y, self.w - self.r_margin, border_y)

        # Number — large blue
        self.set_xy(self.l_margin, y)
        self.set_font("Montserrat", "B", 16)
        self._color(self.BLUE)
        num_str = str(num).zfill(2) if num else ""
        if num_str:
            self.cell(12, 12, num_str, new_x="RIGHT", new_y="TOP")

            # Dash
            dash_x = self.get_x() + 2
            with self.local_context():
                self._draw(self.BORDER)
                self.set_line_width(0.5)
                self.line(dash_x, y + 6, dash_x + 6, y + 6)
            self.set_x(dash_x + 9)

        # Title — uppercase, bold
        self._color(self.CHARCOAL)
        self.set_font("Montserrat", "B", 13)
        self.set_y(y + 1)
        if num_str:
            self.set_x(self.l_margin + 30)
        self.cell(0, 12, title.upper(), new_x="LMARGIN", new_y="NEXT")
        self.set_y(border_y + 4)

    # ── Body Text ─────────────────────────────────────────

    def render_body(self, txt):
        if self._check_page_limit():
            return
        self._color(self.GRAY)
        self.set_font("Poppins", "", 9.5)
        self.multi_cell(0, 5.5, txt)
        self.ln(3)

    # ── Heading ───────────────────────────────────────────

    def render_heading(self, txt):
        if self._check_page_limit():
            return
        self.ln(5)
        self.set_font("Montserrat", "B", 10.5)
        self._color(self.CHARCOAL)
        self.cell(0, 7, txt.upper(), new_x="LMARGIN", new_y="NEXT")
        # Blue underline
        with self.local_context():
            self._draw(self.BLUE)
            self.set_line_width(0.8)
            self.line(self.l_margin, self.get_y(), self.l_margin + 30, self.get_y())
        self.ln(3)

    # ── Bullets ───────────────────────────────────────────

    def render_bullet(self, txt, indent=10):
        if self._check_page_limit():
            return
        x = self.l_margin + indent
        y = self.get_y()

        # Blue square bullet
        self._sharp_rect(x, y + 1.5, 2.5, 2.5, self.BLUE)

        self.set_x(x + 6)
        self._color(self.GRAY)
        self.set_font("Poppins", "", 9.5)
        self.multi_cell(self.epw - indent - 6, 5.5, txt)
        self.ln(0.5)

    def render_bullets(self, items, indent=10):
        for item in items:
            self.render_bullet(item, indent)

    # ── Code Block ────────────────────────────────────────

    def render_code_block(self, code):
        if self._check_page_limit():
            return
        code_lines = code.strip().split("\n")
        x = self.l_margin
        w = self.epw
        text_w = w - 16
        line_h = 5

        self.set_font("RobotoMono", "", 8.5)
        total_lines = 0
        for line in code_lines:
            if not line.strip():
                total_lines += 1
            else:
                line_w = self.get_string_width(line)
                total_lines += max(1, int(line_w / text_w) + (1 if line_w % text_w else 0))
        block_h = total_lines * line_h + 8

        self._ensure_space(block_h + 4)
        self.ln(1)
        y = self.get_y()

        # Shadow + dark rect
        self._bordered_card(x, y, w, block_h, fill=self.CODE_BG, border_w=1, shadow_offset=2)

        # Blue left accent bar
        self._sharp_rect(x, y, 3, block_h, self.BLUE)

        # Code text
        self.set_font("RobotoMono", "", 8.5)
        self._color(self.CODE_TEXT)
        self.set_xy(x + 10, y + 4)
        for line in code_lines:
            self.set_x(x + 10)
            if not line.strip():
                self.ln(line_h)
            else:
                self.multi_cell(text_w, line_h, line)

        self.set_y(y + block_h + 6)

    # ── Tip Box ───────────────────────────────────────────

    def render_tip_box(self, title, txt):
        if self._check_page_limit():
            return
        self.set_font("Poppins", "", 9)
        lines = max(len(txt) / 70, 1) + 1
        box_h = max(lines * 5.5 + 18, 22)
        self._ensure_space(box_h + 10)
        self.ln(4)
        x = self.l_margin
        y = self.get_y()
        w = self.epw

        # Amber-tinted background card
        self._bordered_card(x, y, w, box_h, fill=self.AMBER_BG, border_w=1, shadow_offset=2)

        # Amber left accent bar
        self._sharp_rect(x, y, 4, box_h, self.AMBER)

        # Badge label
        badge_x = x + 10
        badge_y = y + 5
        badge_w = self.get_string_width(title.upper()) + 8
        self.set_font("Montserrat", "B", 7)
        self._sharp_rect(badge_x, badge_y, badge_w, 5.5, self.AMBER)
        self._color(self.ACCENT_FG)
        self.set_xy(badge_x + 4, badge_y + 0.5)
        self.cell(badge_w - 8, 4.5, self._clean(title).upper())

        # Body text
        self.set_xy(x + 10, badge_y + 9)
        self._color(self.CHARCOAL)
        self.set_font("Poppins", "", 9)
        self.multi_cell(w - 20, 5, txt)
        self.set_y(y + box_h + 8)

    # ── Table ─────────────────────────────────────────────

    def render_table(self, headers, rows):
        if self._check_page_limit():
            return
        row_h = 8
        header_h = 9
        table_h = header_h + len(rows) * row_h + 4
        self._ensure_space(table_h)
        self.ln(2)
        n_cols = len(headers)
        col_w = self.epw / n_cols
        x_start = self.l_margin
        y_start = self.get_y()

        # Tabel rand
        self._sharp_rect(x_start, y_start, self.epw, table_h, self.LIGHT_BG, self.BORDER, 1)

        # Header rij — goud achtergrond
        self._sharp_rect(x_start, y_start, self.epw, header_h, self.BLUE)
        self._color(self.ACCENT_FG)
        self.set_font("Montserrat", "B", 8)
        self.set_xy(x_start, y_start)
        for h in headers:
            self.cell(col_w, header_h, f"  {h.upper()}", new_x="RIGHT", new_y="TOP")
        self.set_y(y_start + header_h)

        # Data rijen met striping
        for i, row in enumerate(rows):
            bg = self.DARK_BG if i % 2 == 0 else self.LIGHT_BG
            self._bg(bg)
            self._color(self.CHARCOAL)
            self.set_font("Poppins", "", 8.5)
            for val in row:
                self.cell(col_w, row_h, f"  {val}", fill=True, new_x="RIGHT", new_y="TOP")
            self.ln(row_h)
        self.ln(2)

    # ── Checklist ─────────────────────────────────────────

    def render_checklist(self, items):
        if self._check_page_limit():
            return
        for item in items:
            x = self.l_margin + 8
            y = self.get_y()

            # Checkbox with blue border
            with self.local_context():
                self._draw(self.BLUE)
                self.set_line_width(0.8)
                self.rect(x, y + 0.5, 4, 4, style="D")

            self.set_x(x + 7)
            self._color(self.CHARCOAL)
            self.set_font("Poppins", "", 9.5)
            self.multi_cell(0, 5.5, item)
            self.ln(0.5)

    # ── Numbered Steps ────────────────────────────────────

    def render_numbered_steps(self, steps):
        if self._check_page_limit():
            return
        for i, step in enumerate(steps, 1):
            self._ensure_space(20)
            self.ln(1)
            x = self.l_margin
            y = self.get_y()

            # Square with number (blue bg)
            sq_size = 9
            self._sharp_rect(x + 2, y, sq_size, sq_size, self.BLUE)
            self.set_font("Montserrat", "B", 8)
            self._color(self.ACCENT_FG)
            num_str = str(i).zfill(2)
            nw = self.get_string_width(num_str)
            self.set_xy(x + 2 + (sq_size - nw) / 2, y + 1.5)
            self.cell(nw, 6, num_str, align="C")

            # Connecting line to next step
            if i < len(steps):
                with self.local_context():
                    self._draw(self.BORDER)
                    self.set_line_width(1)
                    line_x = x + 2 + sq_size / 2
                    self.line(line_x, y + sq_size + 1, line_x, y + sq_size + 6)

            # Step title
            text_x = x + sq_size + 8
            self.set_xy(text_x, y)
            self._color(self.CHARCOAL)
            self.set_font("Montserrat", "B", 10)
            self.cell(0, 6, step["title"].upper(), new_x="LMARGIN", new_y="NEXT")

            # Step description
            self.set_x(text_x)
            self._color(self.GRAY)
            self.set_font("Poppins", "", 9)
            self.multi_cell(self.epw - (text_x - self.l_margin), 5, step["description"])
            self.ln(4)

    # ── Two Column ────────────────────────────────────────

    def render_two_column(self, items):
        if self._check_page_limit():
            return
        col_w = self.epw / 2
        for i in range(0, len(items), 2):
            left = items[i]
            right = items[i + 1] if i + 1 < len(items) else None
            self.set_font("RobotoMono", "", 8.5)
            self._color(self.BLUE)
            self.set_x(self.l_margin + 5)
            self.cell(col_w - 5, 5.5, left[0].upper(), new_x="RIGHT", new_y="TOP")
            if right:
                self.cell(col_w - 5, 5.5, right[0].upper(), new_x="LMARGIN", new_y="NEXT")
            else:
                self.ln(5.5)
            self.set_font("Poppins", "", 8)
            self._color(self.GRAY)
            self.set_x(self.l_margin + 5)
            self.cell(col_w - 5, 4.5, left[1], new_x="RIGHT", new_y="TOP")
            if right:
                self.cell(col_w - 5, 4.5, right[1], new_x="LMARGIN", new_y="NEXT")
            else:
                self.ln(4.5)
            self.ln(1)

    # ── Callout Box ───────────────────────────────────────

    def render_callout_box(self, title, items):
        if self._check_page_limit():
            return
        box_h = len(items) * 6.5 + 20
        self._ensure_space(box_h + 6)
        self.ln(2)
        x = self.l_margin
        y = self.get_y()
        w = self.epw

        # Bordered card
        self._bordered_card(x, y, w, box_h, fill=self.LIGHT_BG, border_w=1, shadow_offset=2)

        # Gouden top-balk
        self._sharp_rect(x, y, w, 3, self.BLUE)

        # Titel
        self.set_xy(x + 10, y + 7)
        self._color(self.CHARCOAL)
        self.set_font("Montserrat", "B", 10)
        self.cell(0, 6, self._clean(title).upper(), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

        # Items
        self.set_font("Poppins", "", 9)
        self._color(self.GRAY)
        for item in items:
            self.set_x(x + 10)
            self.cell(0, 5.5, item, new_x="LMARGIN", new_y="NEXT")

        self.set_y(y + box_h + 6)

    # ── Resources ─────────────────────────────────────────

    def render_resources(self, items):
        if self._check_page_limit():
            return
        box_h = len(items) * 7 + 22
        self._ensure_space(box_h + 6)
        self.ln(2)
        x = self.l_margin
        y = self.get_y()
        w = self.epw

        # Bordered card
        self._bordered_card(x, y, w, box_h, fill=self.LIGHT_BG, border_w=1, shadow_offset=2)

        # Gouden top-balk
        self._sharp_rect(x, y, w, 3, self.BLUE)

        # Titel
        self.set_xy(x + 10, y + 7)
        self._color(self.CHARCOAL)
        self.set_font("Montserrat", "B", 10)
        self.cell(0, 6, "BRONNEN & LINKS", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

        # Items with blue bullets
        for r in items:
            self.set_x(x + 10)
            bx = self.get_x()
            by = self.get_y() + 1
            self._sharp_rect(bx, by, 2.5, 2.5, self.BLUE)
            self.set_x(bx + 6)
            self._color(self.CHARCOAL)
            self.set_font("Poppins", "", 9)
            self.cell(0, 6, r, new_x="LMARGIN", new_y="NEXT")

        self.set_y(y + box_h + 6)

    # ── Stick Figure Drawing ──────────────────────────────

    def _draw_stick_figure(self, cx, cy, size, pose="stand"):
        """Draw a minimal stick figure at (cx,cy) with given size.
        pose: stand | prone | squat | row | hollow
        """
        with self.local_context():
            self.set_draw_color(*self.CHARCOAL)
            self.set_line_width(0.8)
            head_r = size * 0.18
            body_len = size * 0.35
            limb_len = size * 0.28

            if pose == "prone":
                # Lying face-down, arms bent at elbow (push-up)
                bx, by = cx, cy + size * 0.05
                # Body horizontal
                self.line(bx - body_len, by, bx + body_len * 0.3, by)
                # Head
                self.ellipse(bx + body_len * 0.3, by - head_r, head_r * 2, head_r * 2, style="D")
                # Arms bent downward
                self.line(bx - body_len * 0.4, by, bx - body_len * 0.4, by + limb_len * 0.8)
                self.line(bx - body_len * 0.1, by, bx - body_len * 0.1, by + limb_len * 0.8)
                # Legs (straight back)
                self.line(bx - body_len, by, bx - body_len * 1.3, by + limb_len * 0.2)
                self.line(bx - body_len, by, bx - body_len * 1.3, by - limb_len * 0.2)

            elif pose == "prone_knee":
                # Knee push-up: body angled, knees bent on ground
                bx, by = cx, cy
                # Body diagonal from knees to head
                self.line(bx - body_len * 0.6, by + size * 0.2, bx + body_len * 0.5, by - size * 0.1)
                # Head
                self.ellipse(bx + body_len * 0.5, by - size * 0.1 - head_r * 2, head_r * 2, head_r * 2, style="D")
                # Arms
                self.line(bx + body_len * 0.1, by + size * 0.05, bx + body_len * 0.1, by + size * 0.25)
                self.line(bx + body_len * 0.3, by, bx + body_len * 0.3, by + size * 0.2)
                # Knees on ground
                self.line(bx - body_len * 0.6, by + size * 0.2, bx - body_len * 0.9, by + size * 0.3)
                self.line(bx - body_len * 0.9, by + size * 0.3, bx - body_len * 0.7, by + size * 0.4)

            elif pose == "squat":
                # Bodyweight squat
                bx, by = cx, cy
                # Head
                self.ellipse(bx - head_r, by - head_r, head_r * 2, head_r * 2, style="D")
                # Body (slightly leaning forward)
                self.line(bx, by + head_r * 2, bx - size * 0.05, by + head_r * 2 + body_len * 0.9)
                # Arms forward
                self.line(bx, by + head_r * 2 + body_len * 0.2, bx + limb_len * 0.8, by + head_r * 2 + body_len * 0.5)
                self.line(bx, by + head_r * 2 + body_len * 0.2, bx - limb_len * 0.8, by + head_r * 2 + body_len * 0.5)
                # Legs bent in squat
                hip_y = by + head_r * 2 + body_len * 0.9
                self.line(bx - size * 0.05, hip_y, bx - limb_len * 0.5, hip_y + limb_len * 0.6)
                self.line(bx - limb_len * 0.5, hip_y + limb_len * 0.6, bx - limb_len * 0.3, hip_y + limb_len * 1.0)
                self.line(bx - size * 0.05, hip_y, bx + limb_len * 0.5, hip_y + limb_len * 0.6)
                self.line(bx + limb_len * 0.5, hip_y + limb_len * 0.6, bx + limb_len * 0.3, hip_y + limb_len * 1.0)

            elif pose == "box_squat":
                # Box squat: sitting on a box
                bx, by = cx, cy - size * 0.05
                box_y = by + size * 0.55
                # Box
                self._sharp_rect(bx - limb_len * 0.7, box_y, limb_len * 1.4, size * 0.15, self.BORDER)
                # Head
                self.ellipse(bx - head_r, by - head_r, head_r * 2, head_r * 2, style="D")
                # Body (upright sitting)
                self.line(bx, by + head_r * 2, bx, box_y)
                # Arms resting
                self.line(bx, by + head_r * 2 + body_len * 0.3, bx + limb_len * 0.7, by + head_r * 2 + body_len * 0.6)
                self.line(bx, by + head_r * 2 + body_len * 0.3, bx - limb_len * 0.7, by + head_r * 2 + body_len * 0.6)
                # Legs horizontal (sitting)
                self.line(bx, box_y, bx + limb_len * 0.8, box_y)
                self.line(bx, box_y, bx - limb_len * 0.8, box_y)
                self.line(bx + limb_len * 0.8, box_y, bx + limb_len * 0.6, box_y + limb_len * 0.7)
                self.line(bx - limb_len * 0.8, box_y, bx - limb_len * 0.6, box_y + limb_len * 0.7)

            elif pose == "split_squat":
                # Split squat: one foot forward, one back
                bx, by = cx, cy
                # Head
                self.ellipse(bx - head_r, by - head_r, head_r * 2, head_r * 2, style="D")
                # Body
                self.line(bx, by + head_r * 2, bx, by + head_r * 2 + body_len * 0.9)
                # Arms
                self.line(bx, by + head_r * 2 + body_len * 0.3, bx + limb_len * 0.6, by + head_r * 2 + body_len * 0.5)
                self.line(bx, by + head_r * 2 + body_len * 0.3, bx - limb_len * 0.6, by + head_r * 2 + body_len * 0.5)
                # Front leg
                hip_y = by + head_r * 2 + body_len * 0.9
                self.line(bx, hip_y, bx + limb_len * 0.6, hip_y + limb_len * 0.6)
                self.line(bx + limb_len * 0.6, hip_y + limb_len * 0.6, bx + limb_len * 0.5, hip_y + limb_len * 1.1)
                # Back leg (knee on ground direction)
                self.line(bx, hip_y, bx - limb_len * 0.4, hip_y + limb_len * 0.8)
                self.line(bx - limb_len * 0.4, hip_y + limb_len * 0.8, bx - limb_len * 0.2, hip_y + limb_len * 1.1)

            elif pose == "row":
                # Australian row: hanging under bar, body horizontal
                bx, by = cx, cy + size * 0.05
                # Bar at top
                self.set_draw_color(*self.CHARCOAL)
                self.set_line_width(1.2)
                self.line(bx - body_len * 1.1, by - size * 0.35, bx + body_len * 0.6, by - size * 0.35)
                self.set_line_width(0.8)
                # Head
                self.ellipse(bx + body_len * 0.3, by - head_r * 2 - size * 0.05, head_r * 2, head_r * 2, style="D")
                # Body horizontal
                self.line(bx - body_len * 0.8, by, bx + body_len * 0.4, by)
                # Arms reaching up to bar
                self.line(bx + body_len * 0.15, by, bx + body_len * 0.0, by - size * 0.35)
                self.line(bx - body_len * 0.1, by, bx - body_len * 0.2, by - size * 0.35)
                # Legs
                self.line(bx - body_len * 0.8, by, bx - body_len * 1.15, by + size * 0.1)
                self.line(bx - body_len * 0.8, by, bx - body_len * 1.1, by - size * 0.05)

            elif pose == "row_incline":
                # Inclined row: body more upright, hands at chest height
                bx, by = cx, cy
                # Bar at medium height
                self.set_draw_color(*self.CHARCOAL)
                self.set_line_width(1.2)
                self.line(bx - body_len * 0.3, by - size * 0.15, bx + body_len * 0.7, by - size * 0.15)
                self.set_line_width(0.8)
                # Head
                self.ellipse(bx - head_r, by - size * 0.55 - head_r, head_r * 2, head_r * 2, style="D")
                # Body at ~45 degree angle
                self.line(bx, by - size * 0.55 + head_r, bx, by - size * 0.15)
                # Arms to bar
                self.line(bx, by - size * 0.4, bx + limb_len * 0.4, by - size * 0.15)
                self.line(bx, by - size * 0.4, bx - limb_len * 0.1, by - size * 0.15)
                # Legs to floor
                self.line(bx, by - size * 0.15, bx + limb_len * 0.4, by + size * 0.3)
                self.line(bx, by - size * 0.15, bx - limb_len * 0.1, by + size * 0.3)

            elif pose == "hollow":
                # Hollow body hold: legs extended, lower back pressed flat
                bx, by = cx, cy + size * 0.05
                # Body horizontal, slightly curved
                self.line(bx - body_len * 1.4, by, bx + body_len * 0.4, by)
                # Head (slightly raised)
                self.ellipse(bx + body_len * 0.4, by - head_r * 1.8, head_r * 2, head_r * 2, style="D")
                # Arms overhead
                self.line(bx - body_len * 0.8, by, bx - body_len * 0.8, by - size * 0.22)
                self.line(bx - body_len * 0.8, by - size * 0.22, bx - body_len * 1.3, by - size * 0.28)
                # Legs extended low
                self.line(bx - body_len * 1.4, by, bx - body_len * 1.8, by - size * 0.15)
                self.line(bx - body_len * 1.4, by, bx - body_len * 1.8, by + size * 0.05)

            elif pose == "hollow_tuck":
                # Tuck hollow: knees pulled in
                bx, by = cx, cy + size * 0.05
                # Body shorter
                self.line(bx - body_len * 0.7, by, bx + body_len * 0.4, by)
                # Head
                self.ellipse(bx + body_len * 0.4, by - head_r * 1.8, head_r * 2, head_r * 2, style="D")
                # Arms overhead
                self.line(bx - body_len * 0.3, by, bx - body_len * 0.3, by - size * 0.22)
                self.line(bx - body_len * 0.3, by - size * 0.22, bx - body_len * 0.8, by - size * 0.28)
                # Knees tucked
                self.line(bx - body_len * 0.7, by, bx - body_len * 0.9, by + size * 0.2)
                self.line(bx - body_len * 0.9, by + size * 0.2, bx - body_len * 0.6, by + size * 0.32)

            else:  # stand
                # Upright standing
                self.ellipse(bx - head_r, by - head_r, head_r * 2, head_r * 2, style="D")
                bx, by = cx, cy
                self.line(bx, by + head_r * 2, bx, by + head_r * 2 + body_len)
                self.line(bx, by + head_r * 2 + body_len * 0.25, bx + limb_len * 0.7, by + head_r * 2 + body_len * 0.7)
                self.line(bx, by + head_r * 2 + body_len * 0.25, bx - limb_len * 0.7, by + head_r * 2 + body_len * 0.7)
                self.line(bx, by + head_r * 2 + body_len, bx + limb_len * 0.4, by + head_r * 2 + body_len + limb_len)
                self.line(bx, by + head_r * 2 + body_len, bx - limb_len * 0.4, by + head_r * 2 + body_len + limb_len)

    # ── Progression Ladder ────────────────────────────────

    def render_progression_ladder(self, exercise, muscles, levels, poses=None):
        """Draw a 3-level progression card for one exercise.

        levels: list of dicts with keys: label (MAKKELIJKER/STANDAARD/MOEILIJKER),
                name (exercise name), cue (coaching cue)
        poses: optional list of pose strings for stick figures (one per level)
        """
        if self._check_page_limit():
            return

        LEVEL_COLORS = [
            (34, 197, 94),    # groen — makkelijker
            (255, 213, 0),    # goud  — standaard
            (239, 68, 68),    # rood  — moeilijker
        ]
        LEVEL_TEXT_COLORS = [
            (255, 255, 255),
            (13, 13, 13),
            (255, 255, 255),
        ]

        fig_w = 28          # breedte stickfiguur zone
        badge_w = 28        # breedte niveau-badge
        row_h = 24          # hoogte per rij
        header_h = 10
        card_w = self.epw
        card_h = header_h + len(levels) * row_h + 4
        x = self.l_margin
        self._ensure_space(card_h + 10)
        self.ln(3)
        y = self.get_y()

        # Kaartachtergrond
        self._sharp_rect(x, y, card_w, card_h, self.LIGHT_BG, self.BORDER, 0.7)

        # Header: goud met oefening + spiergroepen
        self._sharp_rect(x, y, card_w, header_h, self.CHARCOAL)
        self.set_font("Montserrat", "B", 8)
        self._color(self.BLUE)
        self.set_xy(x + 4, y + (header_h - 5) / 2)
        self.cell(card_w * 0.55, 5, self._clean(exercise).upper())
        self.set_font("Poppins", "", 7)
        self._color((180, 180, 180))
        self.set_xy(x + card_w * 0.55, y + (header_h - 5) / 2)
        self.cell(card_w * 0.44, 5, self._clean(muscles), align="R")

        # Rijen per progressieniveau
        for i, lev in enumerate(levels):
            ry = y + header_h + i * row_h
            bg = self.WHITE if i % 2 == 0 else self.LIGHT_BG
            self._sharp_rect(x, ry, card_w, row_h, bg)

            # Badge
            badge_color = LEVEL_COLORS[i % 3]
            badge_txt_color = LEVEL_TEXT_COLORS[i % 3]
            self._sharp_rect(x, ry, badge_w, row_h, badge_color)
            self.set_font("Montserrat", "B", 5.5)
            self._color(badge_txt_color)
            self.set_xy(x, ry)
            self.cell(badge_w, row_h, self._clean(lev.get("label", "")), align="C")

            # Stick figure zone
            pose = (poses[i] if poses and i < len(poses) else "stand")
            fig_cx = x + badge_w + fig_w / 2
            fig_cy = ry + row_h / 2
            self._draw_stick_figure(fig_cx, fig_cy, row_h * 0.82, pose)

            # Naam + cue tekst
            tx = x + badge_w + fig_w + 3
            tw = card_w - badge_w - fig_w - 5
            name = self._clean(lev.get("name", ""))
            cue = self._clean(lev.get("cue", ""))
            self.set_font("Montserrat", "B", 7.5)
            self._color(self.CHARCOAL)
            self.set_xy(tx, ry + 4)
            self.cell(tw, 5, name)
            self.set_font("Poppins", "", 6.5)
            self._color(self.GRAY)
            self.set_xy(tx, ry + 10)
            self.multi_cell(tw, 4, cue)

        self.set_y(y + card_h + 5)

    # ── Training Card ─────────────────────────────────────

    def render_training_card(self, title, rows):
        if self._check_page_limit():
            return
        n_cols = max(len(r) for r in rows) if rows else 4
        row_h = 8
        header_h = 9
        card_h = header_h + len(rows) * row_h + 4
        self._ensure_space(card_h + 8)
        self.ln(2)
        x = self.l_margin
        y = self.get_y()
        w = self.epw
        accent_w = 3

        # Kaartachtergrond met rand
        self._sharp_rect(x, y, w, card_h, self.LIGHT_BG, self.BORDER, 0.8)

        # Donkere linker accent-balk
        self._sharp_rect(x, y, accent_w, card_h, self.CHARCOAL)

        # Gouden header-balk
        self._sharp_rect(x + accent_w, y, w - accent_w, header_h, self.BLUE)
        self.set_font("Montserrat", "B", 9)
        self._color(self.ACCENT_FG)
        self.set_xy(x + accent_w + 4, y + (header_h - 5) / 2)
        self.cell(w - accent_w - 8, 5, self._clean(title).upper())

        # Data-rijen met striping
        col_w = (w - accent_w) / max(n_cols, 1)
        for i, row in enumerate(rows):
            row_y = y + header_h + i * row_h
            bg = self.DARK_BG if i % 2 == 0 else self.LIGHT_BG
            self._sharp_rect(x + accent_w, row_y, w - accent_w, row_h, bg)
            self.set_font("Poppins", "", 9)
            self._color(self.CHARCOAL)
            self.set_xy(x + accent_w, row_y)
            for j, cell_val in enumerate(row):
                self.set_xy(x + accent_w + j * col_w + 2, row_y + (row_h - 5) / 2)
                self.cell(col_w - 4, 5, str(cell_val))

        self.set_y(y + card_h + 4)

    # ── main render dispatch ──────────────────────────────

    @classmethod
    def _clean_section(cls, section):
        cleaned = {}
        for k, v in section.items():
            if k in ("code",):
                cleaned[k] = v
            elif isinstance(v, str):
                cleaned[k] = cls._clean(v)
            elif isinstance(v, list):
                cleaned[k] = [
                    cls._clean(i) if isinstance(i, str)
                    else {sk: cls._clean(sv) if isinstance(sv, str) else sv for sk, sv in i.items()} if isinstance(i, dict)
                    else [cls._clean(c) if isinstance(c, str) else c for c in i] if isinstance(i, list)
                    else i
                    for i in v
                ]
            else:
                cleaned[k] = v
        return cleaned

    def render_section(self, section):
        section = self._clean_section(section)
        t = section["type"]
        if t == "section_title":
            self.render_section_title(section["number"], section["title"])
        elif t == "body":
            self.render_body(section["text"])
        elif t == "heading":
            self.render_heading(section["text"])
        elif t == "bullet":
            self.render_bullet(section["text"])
        elif t == "bullets":
            self.render_bullets(section["items"])
        elif t == "code_block":
            self.render_code_block(section["code"])
        elif t == "code":
            self.render_code_block(section.get("code", section.get("text", "")))
        elif t == "tip_box":
            self.render_tip_box(section["title"], section["text"])
        elif t == "table":
            self.render_table(section["headers"], section["rows"])
        elif t == "checklist":
            self.render_checklist(section["items"])
        elif t == "numbered_steps":
            self.render_numbered_steps(section["steps"])
        elif t == "two_column":
            self.render_two_column(section["items"])
        elif t == "callout_box":
            self.render_callout_box(section["title"], section["items"])
        elif t == "resources":
            self.render_resources(section["items"])
        elif t == "training_card":
            self.render_training_card(section["title"], section["rows"])
        elif t == "progression_ladder":
            self.render_progression_ladder(
                section["exercise"],
                section.get("muscles", ""),
                section["levels"],
                section.get("poses"),
            )
        elif t == "page_break":
            if not self._check_page_limit():
                self.add_page()
        else:
            print(f"WARNING: Unknown section type '{t}', skipping.", file=sys.stderr)

    def render_content(self, content: dict):
        if content.get("footer_text"):
            self._footer_text = content["footer_text"]

        self.render_cover(
            content["title"],
            content.get("subtitle"),
            content.get("subtitle_bullets"),
            cover_label=content.get("cover_label"),
            learn_label=content.get("learn_label"),
            series_label=content.get("series_label"),
        )

        for section in content.get("sections", []):
            if self._check_page_limit():
                break
            self.render_section(section)


def main():
    parser = argparse.ArgumentParser(description="Generate a professional PDF from JSON content.")
    parser.add_argument("--content-file", required=True, help="Path to JSON content file")
    parser.add_argument("--output", required=True, help="Output PDF path")
    args = parser.parse_args()

    content_path = Path(args.content_file)
    if not content_path.exists():
        print(f"ERROR: Content file not found: {content_path}", file=sys.stderr)
        sys.exit(1)

    with open(content_path) as f:
        content = json.load(f)

    pdf = ProfessionalDoc()
    pdf.render_content(content)

    if pdf.pages_count > MAX_PAGES:
        print(f"WARNING: PDF has {pdf.pages_count} pages, max is {MAX_PAGES}.", file=sys.stderr)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    print(f"PDF saved to: {output_path}")
    print(f"Pages: {pdf.pages_count}")


if __name__ == "__main__":
    main()
