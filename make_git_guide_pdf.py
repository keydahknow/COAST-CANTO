"""
Generates 'Git_Guide.pdf' - a printable team cheat sheet of the git/GitHub
commands we use, grouped by function, plus new-computer setup instructions.

Run it once:
    pip install fpdf2
    python make_git_guide_pdf.py

Output: Git_Guide.pdf in the project folder. You can delete this script
afterwards, or keep it to regenerate the PDF if the instructions change.
"""

from fpdf import FPDF

# --- Colors ---
INK = (25, 30, 40)
ACCENT = (10, 90, 170)
CODE_BG = (240, 242, 245)
CODE_INK = (20, 20, 20)
NOTE_INK = (110, 70, 0)


class Guide(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"C.O.A.S.T. - Git Guide   |   Page {self.page_no()}",
                  align="C")

    def doc_title(self, text):
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(*ACCENT)
        self.multi_cell(0, 9, text)
        self.ln(1)

    def subtitle(self, text):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(90, 95, 105)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def section(self, text):
        if self.get_y() > 250:
            self.add_page()
        self.ln(2)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*ACCENT)
        self.multi_cell(0, 7, text)
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.4)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(3)

    def body(self, text):
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(*INK)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def note(self, text):
        self.set_font("Helvetica", "I", 9.5)
        self.set_text_color(*NOTE_INK)
        self.multi_cell(0, 5, "Note: " + text)
        self.ln(1)

    def code(self, lines):
        self.set_font("Courier", "", 10)
        self.set_text_color(*CODE_INK)
        self.set_fill_color(*CODE_BG)
        for line in lines:
            self.cell(0, 6, "  " + line, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)


pdf = Guide()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

pdf.doc_title("C.O.A.S.T. - Git and GitHub Cheat Sheet")
pdf.subtitle("Team: The Buoyz. Keep this handy. The two commands you use most: "
             "'git pull' to start, and add/commit/push to save.")

pdf.section("A. First-time setup on a NEW computer")
pdf.body("Do this once per machine (a teammate getting started, or you on a "
         "second laptop). First install these once:")
pdf.body("- Git:  https://git-scm.com/download/win  (accept defaults)")
pdf.body("- Python 3.12:  https://www.python.org/downloads/windows/  and TICK "
         "'Add python.exe to PATH'. Use 3.12 specifically (not 3.13/3.14).")
pdf.body("Then get the project and set it up:")
pdf.code([
    "git clone https://github.com/<your-username>/CANTO.git",
    "cd CANTO",
    "py -3.12 -m venv .venv",
    ".\\.venv\\Scripts\\Activate.ps1",
    "pip install -r requirements.txt",
])
pdf.note("If PowerShell blocks the activate line, run once: "
         "Set-ExecutionPolicy -Scope CurrentUser RemoteSigned  (type Y), then retry.")
pdf.note("On Mac/Linux the venv lines differ: 'python3 -m venv .venv' then "
         "'source .venv/bin/activate'.")

pdf.section("B. Starting every work session")
pdf.body("Run these each time you sit down, to get the latest code and turn on "
         "your environment (look for '(.venv)' in your prompt afterwards):")
pdf.code([
    "git checkout main",
    "git pull",
    ".\\.venv\\Scripts\\Activate.ps1",
])

pdf.section("C. Saving & pushing your changes (the constant one)")
pdf.body("The cycle you run many times a day:")
pdf.code([
    "git add .",
    'git commit -m "Short description of what you changed"',
    "git push",
])
pdf.body("- git add .  = stage all your changes")
pdf.body("- git commit = save a snapshot with a short, specific message")
pdf.body("- git push   = upload to GitHub so teammates can see it")

pdf.section("D. Working with branches (once you're two programmers)")
pdf.body("Start a new feature on its own branch:")
pdf.code([
    "git checkout main",
    "git pull",
    "git checkout -b feature/your-feature-name",
])
pdf.body("Push that branch the first time (sets its GitHub home):")
pdf.code([
    "git push -u origin feature/your-feature-name",
])
pdf.body("After that first push, plain 'git push' works for that branch. Then "
         "open a Pull Request on GitHub ('Compare & pull request') so a "
         "teammate reviews before it merges into main.")

pdf.section("E. Getting a teammate's latest work into your branch")
pdf.body("If main moved forward while you were working, pull it into your branch:")
pdf.code([
    "git checkout main",
    "git pull",
    "git checkout feature/your-feature-name",
    "git merge main",
])

pdf.section("F. Checking what's going on (safe, read-only - use often)")
pdf.body("These never change anything; run them anytime to orient yourself:")
pdf.code([
    "git status              # what changed / staged / current branch",
    "git branch              # list branches (* marks current)",
    "git log --oneline -10   # last 10 commits",
    "git diff                # exact lines changed but not committed",
])

pdf.section("G. Common 'oops' fixes")
pdf.code([
    "git checkout -- <file>   # discard uncommitted changes to ONE file",
    "git switch main          # jump back to the main branch",
    "git pull                 # if push is rejected, pull first, then push",
])
pdf.note("If 'git push' is rejected, a teammate pushed first. Fix: run "
         "'git pull', resolve any conflicts, then 'git push' again.")

pdf.section("The two you'll use 95% of the time")
pdf.body("- Start work:  git pull")
pdf.body("- Save work:   git add .   ->   git commit -m \"...\"   ->   git push")

pdf.output("Git_Guide.pdf")
print("[OK] Created Git_Guide.pdf")
