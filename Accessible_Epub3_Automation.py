# ------------ Revision History---------------------------------------------
#  16-05-2025 | v1.0.0.0 | Sudhakar V | Initial Development
# --------------------------------------------------------------------------
import sys
import os
from os.path import basename, dirname, join, exists
import zipfile
import shutil
import re
from iModule.Basic import _open_utf8, _save_utf8, _get_file_list, _element_leveling

os.system("cls")

ToolVersion = "1.0.0.0"

print(f"\n\n\tAccessible_Epub3_Automation v{ToolVersion} is Running...")

if len(sys.argv) != 2:
    sys.exit("\n\tSyntax: Accessible_Epub3_Automation.exe <epub file>\n")

if not (os.path.isdir(sys.argv[1]) or re.match(r'.*\.epub$', sys.argv[1], re.I)):
    sys.exit("\n\tSyntax: Accessible_Epub3_Automation.exe <epub file>\n")

# Supporting file checking
ToolPath = dirname(sys.argv[0])
ToolPath = re.sub(r'\/', r'\\', ToolPath, 0)
input_path = dirname(sys.argv[1])
input_path = re.sub(r'\/', r'\\', input_path, 0)


def _epub_extraction():
    folder_path = sys.argv[1]
    Epub_filename = folder_path
    DirZipFile = Epub_filename.replace(".epub", ".zip")
    filenameoutput = basename(DirZipFile)
    filenameoutput1 = filenameoutput.replace(".zip", "")
    OutputDir = dirname(Epub_filename) + "\\" + filenameoutput1

    # Step 1: Unzip the .epub file
    with zipfile.ZipFile(Epub_filename, "r") as zip_ref:
        zip_ref.extractall(OutputDir)

    # Step 2: Identify directory (ops or OEBPS, case insensitive)
    possible_dirs = ['ops', 'OEBPS']
    content_dir = None
    for root, dirs, _ in os.walk(OutputDir):
        for d in dirs:
            if d.lower() in ['ops', 'oebps']:
                content_dir = os.path.join(root, d)
                break
        if content_dir:
            break

    if not content_dir:
        raise FileNotFoundError("No 'ops' or 'OEBPS' folder found in the extracted EPUB.")

    # Step 3: Convert .html files to .xhtml
    for root, _, files in os.walk(content_dir):
        for file in files:
            if file.lower().endswith('.html'):
                old_path = os.path.join(root, file)
                new_filename = re.sub(r'\.html$', '.xhtml', file, flags=re.IGNORECASE)
                new_path = os.path.join(root, new_filename)
                os.rename(old_path, new_path)

    # Step 3.5: Copy synth.css into styles folder if not present
    styles_path = join(content_dir, 'styles')
    css_filename = 'synth.css'
    tool_path = dirname(sys.argv[0])
    source_css = join(tool_path, css_filename)

    if exists(source_css):
        os.makedirs(styles_path, exist_ok=True)
        target_css = join(styles_path, css_filename)
        if not exists(target_css):
            shutil.copy2(source_css, target_css)

    # Step 3.6: Append .break CSS rule to stylesheet.css
    stylesheet_css = join(styles_path, 'stylesheet.css')
    if exists(stylesheet_css):
        with open(stylesheet_css, 'a', encoding='utf-8') as f:
            f.write('\n.break\n{\n   display: block;\n}\n')

    xhtml_file = _get_file_list(content_dir, 1, 1, '.xhtml$')
    if xhtml_file:
        nav_map = ''
        for filename in xhtml_file:
            chapter_id = 'ch00'
            base = basename(filename)
            match = re.search(r'chapter(\d+)\.xhtml', base, re.IGNORECASE)
            if match:
                chapter_num = int(match.group(1))
                chapter_id = f'ch{chapter_num:02d}'  # pad to 2 digits

            xhtml_cnt = _open_utf8(filename)
            xhtml_cnt = re.sub(r'<!DOCTYPE html>\s*<html(?: [^>]*)?>', r'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en" lang="en">', xhtml_cnt, 1, re.I | re.S)
            xhtml_cnt = re.sub(r'(<body>)\s*<p(?: [^>]*)?>&#x00A0;</p>', r'\g<1>', xhtml_cnt, 1, re.I | re.S)
            xhtml_cnt = re.sub(r'<br/>', r'<span class="break"/>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'<a id="pg_([^"]*)"\s*/>', r'<span id="pg_\g<1>" role="doc-pagebreak" epub:type="pagebreak" aria-label="Page \g<1>."/>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'<samp', r'<span', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'</samp>', r'</span>', xhtml_cnt, 0, re.I | re.S)
            if not re.search(r'<link rel="stylesheet" type="text/css" href="\.\./styles/synth\.css"/>', xhtml_cnt, re.I | re.S):
                xhtml_cnt = re.sub(r'</head>',r'<link rel="stylesheet" type="text/css" href="../styles/synth.css"/>\n</head>', xhtml_cnt, 1, re.I | re.S)
            xhtml_cnt = re.sub(r'<p((?: [^>]*)?>\s*<img(?: [^>]*)?>(?:(?!</p>).)*)</p>', r'<figure\g<1></figure>', xhtml_cnt, 0, re.I | re.S)

            # Chapter Page
            if re.search(r'chapter\d+\.xhtml', filename, re.I | re.S):
                xhtml_cnt = re.sub(r'(<body(?: [^>]*)?>)', rf'\g<1>\n<section epub:type="chapter" role="doc-chapter" aria-labelledby="{chapter_id}">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'</body>', r'</section>\n</body>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<p class="([^"]*)"(?: [^>]*)?>\s*(<span id="pg_(?:[^"]*)"(?: [^>]*)?/>)', rf'\g<2>\n<h1 epub:type="titlepage" class="\g<1>" id="{chapter_id}">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<h1(?: [^>]*)?>(?:(?!</p>).)*)(</p>)', r'\g<1></h1>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<h1(?: [^>]*)?>(?:(?!</h1>).)*</h1>', lambda m: re.sub(r'<span(?: [^>]*)?>((?:(?!</span>).)*)</span>', r'\g<1>', m.group(), 0, re.I | re.S), xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'<p class="H1[^"]*">((?:(?!</p>).)*)</p>', r'<section>\n<h2 epub:type="title" class="H1">\g<1></h2>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'<p class="H2[^"]*">((?:(?!</p>).)*)</p>', r'<section>\n<h3 epub:type="title" class="H1">\g<1></h3>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'<p class="H3[^"]*">((?:(?!</p>).)*)</p>', r'<section>\n<h4 epub:type="title" class="H1">\g<1></h4>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'(<section>\s*<h2(?: [^>]*)?>)', r'</section>\n\g<1>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'(<section>\s*<h3(?: [^>]*)?>)', r'</section>\n\g<1>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'(<section>\s*<h4(?: [^>]*)?>)', r'</section>\n\g<1>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'<h\d+(?: [^>]*)?>(?:(?!</h\d+>).)*</h\d+>', lambda m: re.sub(r'<span(?: [^>]*)?>((?:(?!</span>).)*)</span>', r'\g<1>', m.group(),0, re.I | re.S), xhtml_cnt, 0, re.I | re.S)
                if re.search(r'<(h2|h3|h4)(?: [^>]*)?>', xhtml_cnt, re.I | re.S):
                    xhtml_cnt = re.sub(r'</section>\s*(<section>\s*<h2(?: [^>]*)?>)', r'\g<1>', xhtml_cnt, 1, re.I | re.S)
                    xhtml_cnt = re.sub(r'</section>\n</body>', r'</section>\n</section>\n</body>', xhtml_cnt, 1, re.I | re.S)

            # Cover Page
            if re.search(r'cover\.xhtml', filename, re.I | re.S):
                xhtml_cnt = re.sub(r'(<title(?: [^>]*)?>)((?:(?!</title>).)*)(</title>)', r'\g<1>Cover Page\g<3>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<body(?: [^>]*)?>', r'<body epub:type="cover" class="cover-pg">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<img(?: [^>]*)?src="([^"]*)"(?: [^>]*)?>', r'<img aria-label="cover" class="cover" role="doc-cover" src="\g<1>" alt="Image"/>', xhtml_cnt, 1, re.I | re.S)

            # Title Page
            if re.search(r'title\.xhtml', filename, re.I | re.S):
                xhtml_cnt = re.sub(r'(<title(?: [^>]*)?>)((?:(?!</title>).)*)(</title>)', r'\g<1>Title Page\g<3>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<body(?: [^>]*)?>)', r'\g<1>\n<section epub:type="titlepage" aria-labelledby="title">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'</body>', r'</section>\n</body>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<p class="([^"]*)"(?: [^>]*)?>\s*(<span id="pg_(?:[^"]*)"(?: [^>]*)?/>)', r'\g<2>\n<h1 epub:type="titlepage" class="\g<1>" id="title">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<h1(?: [^>]*)?>(?:(?!</p>).)*)(</p>)', r'\g<1></h1>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<h1(?: [^>]*)?>(?:(?!</h1>).)*</h1>', lambda m: re.sub(r'<span(?: [^>]*)?>((?:(?!</span>).)*)</span>', r'\g<1>', m.group(), 0, re.I | re.S), xhtml_cnt, 1, re.I | re.S)

            # Halftitle Page
            if re.search(r'halftitle\.xhtml', filename, re.I | re.S):
                xhtml_cnt = re.sub(r'(<title(?: [^>]*)?>)((?:(?!</title>).)*)(</title>)', r'\g<1>Half Title Page\g<3>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<body(?: [^>]*)?>)', r'\g<1>\n<section epub:type="halftitlepage" aria-labelledby="half">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'</body>', r'</section>\n</body>', xhtml_cnt, 1, re.I | re.S)

            # Copyright Page
            if re.search(r'copy(right)?\.xhtml', filename, re.I | re.S):
                xhtml_cnt = re.sub(r'(<title(?: [^>]*)?>)((?:(?!</title>).)*)(</title>)', r'\g<1>Copyright Page\g<3>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<body(?: [^>]*)?>)', r'\g<1>\n<section epub:type="copyright-page" aria-labelledby="Copyright Page">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'</body>', r'</section>\n</body>', xhtml_cnt, 1, re.I | re.S)

            # Acknowledgement Page
            if re.search(r'ack(nowledgments?)?\.xhtml', filename, re.I | re.S):
                xhtml_cnt = re.sub(r'(<title(?: [^>]*)?>)((?:(?!</title>).)*)(</title>)', r'\g<1>Acknowledgments\g<3>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<body(?: [^>]*)?>)', r'\g<1>\n<section epub:type="acknowledgments" role="doc-acknowledgments" aria-labelledby="ack">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'</body>', r'</section>\n</body>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<p class="([^"]*)"(?: [^>]*)?>\s*(<span id="pg_(?:[^"]*)"(?: [^>]*)?/>)', r'\g<2>\n<h1 epub:type="title" class="\g<1>" id="ack">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<h1(?: [^>]*)?>(?:(?!</p>).)*)(</p>)', r'\g<1></h1>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<h1(?: [^>]*)?>(?:(?!</h1>).)*</h1>', lambda m: re.sub(r'<span(?: [^>]*)?>((?:(?!</span>).)*)</span>', r'\g<1>', m.group(), 0, re.I | re.S), xhtml_cnt, 1, re.I | re.S)

            # index Page
            if re.search(r'index\.xhtml', filename, re.I | re.S):
                xhtml_cnt = re.sub(r'(<body(?: [^>]*)?>)', r'\g<1>\n<section epub:type="index" role="doc-index" aria-labelledby="index">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'</body>', r'</section>\n</body>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<p class="([^"]*)"(?: [^>]*)?>\s*(<span id="pg_(?:[^"]*)"(?: [^>]*)?/>)', r'\g<2>\n<h1 epub:type="title" class="\g<1>" id="index">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<h1(?: [^>]*)?>(?:(?!</p>).)*)(</p>)', r'\g<1></h1>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<h1(?: [^>]*)?>(?:(?!</h1>).)*</h1>', lambda m: re.sub(r'<span(?: [^>]*)?>((?:(?!</span>).)*)</span>', r'\g<1>', m.group(), 0, re.I | re.S), xhtml_cnt, 1, re.I | re.S)

            # Preface Page
            if re.search(r'preface\.xhtml', filename, re.I | re.S):
                xhtml_cnt = re.sub(r'(<body(?: [^>]*)?>)', r'\g<1>\n<section epub:type="preface" role="doc-preface" aria-labelledby="pre">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'</body>', r'</section>\n</body>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<p class="([^"]*)"(?: [^>]*)?>\s*(<span id="pg_(?:[^"]*)"(?: [^>]*)?/>)', r'\g<2>\n<h1 epub:type="title" class="\g<1>" id="pre">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<h1(?: [^>]*)?>(?:(?!</p>).)*)(</p>)', r'\g<1></h1>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<h1(?: [^>]*)?>(?:(?!</h1>).)*</h1>', lambda m: re.sub(r'<span(?: [^>]*)?>((?:(?!</span>).)*)</span>', r'\g<1>', m.group(), 0, re.I | re.S), xhtml_cnt, 1, re.I | re.S)

            # Content Page or TOC
            if re.search(r'(contents?|toc)\.xhtml', filename, re.I | re.S):
                xhtml_cnt = re.sub(r'(<title(?: [^>]*)?>)((?:(?!</title>).)*)(</title>)', r'\g<1>Contents\g<3>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<body(?: [^>]*)?>)', r'\g<1>\n<section epub:type="toc" role="doc-toc" aria-labelledby="toc">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'</body>', r'</section>\n</body>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<p class="([^"]*)"(?: [^>]*)?>\s*(<span id="pg_(?:[^"]*)"(?: [^>]*)?/>)', r'\g<2>\n<h1 epub:type="title" class="\g<1>" id="toc">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<h1(?: [^>]*)?>(?:(?!</p>).)*)(</p>)', r'\g<1></h1>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<h1(?: [^>]*)?>(?:(?!</h1>).)*</h1>', lambda m: re.sub(r'<span(?: [^>]*)?>((?:(?!</span>).)*)</span>', r'\g<1>', m.group(), 0, re.I | re.S), xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<h1(?: [^>]*)?>(?:(?!</h1>).)*</h1>)', r'\g<1>\n<ol class="ul-no-mark">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(</section>\s*</body>)', r'</ol>\n\g<1>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<ol class="ul-no-mark">(?:(?!</ol>).)*</ol>', lambda m: re.sub(r'(<p(?: [^>]*)?>((?:(?!</p>).)*)</p>)', r'<li>\g<1></li>', m.group(), 0, re.I | re.S), xhtml_cnt, 1, re.I | re.S)

            for pg in re.finditer(r'<span id="pg_[^"]* hk7f')
            _save_utf8(filename, xhtml_cnt)

try:
    _epub_extraction()
except Exception as e:
    print(e)
    sys.exit()

sys.exit("\n\t\t Process completed...!!!\n")

