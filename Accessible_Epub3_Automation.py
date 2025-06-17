# ------------ Revision History---------------------------------------------
#  16-05-2025 | v1.0.0.0 | Sudhakar V | Initial Development
# --------------------------------------------------------------------------
import sys
import os
from os.path import basename, dirname, join, exists
import zipfile
import shutil
import re
from iModule.Basic import _open_utf8, _save_utf8, _get_file_list

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


    # Step 3.6: Append .break CSS rule to stylesheet.css
    css_file = _get_file_list(styles_path, 1, 0, '.css$')
    if css_file:
        stylesheet_css = join(styles_path, css_file[0])

        additional_css = """
@charset "UTF-8";
/*  blitz â€” CSS framework for reflowable eBooks
    Version 0.95 by Jiminy Panoz
    Codename: Blonde Rock & Roll
    License: MIT (https://opensource.org/licenses/MIT)   */
/* NAMESPACES */
@namespace h "http://www.w3.org/1999/xhtml/";
@namespace epub "http://www.idpg.org/2007/ops";
/* if you need to style epub:type */
@namespace m "http://www.w3.org/1998/Math/MathML/";
/* if you need to style MathML */
@namespace svg "http://www.w3.org/2000/svg";
/* if you need to style SVG */
html {
  /* Don't use it for styling, used as selector which can take a punch if anything goes wrong above */
}
/* Begin CSS */
/* Reset */
/* So here's the trick, we must reset to manage a number of problems once and for all:
- HTML5 backwards compatibility (EPUB 3 file in EPUB 2 app);
- user settings (e.g. line-height on Kobo and Kindle);
- CSS bloat (DRY);
- KFX for which a reset using `border: 0` seems to disable support;
- etc.
It all started as a normalize and became a reset given the magnitude of the task.
*/
html, body, div, span, applet, object, iframe,
h1, h2, h3, h4, h5, h6, p, blockquote, pre,
a, abbr, acronym, address, big, cite, code,
del, dfn, em, img, ins, kbd, q, s, samp,
small, strike, strong, sub, sup, tt, var,
b, u, i, center,
dl, dt, dd, ol, ul, li,
fieldset, form, label, legend,
table, caption, tbody, tfoot, thead, tr, th, td,
article, aside, canvas, details, embed,
figure, figcaption, footer, header, hgroup,
menu, nav, output, ruby, section, summary,
time, mark, audio, video {
 margin:0;
 padding:0;
  /* RS may apply vertical padding to el such as p */
 border: 0;
  /* Font size in pixel disable the user setting in legacy RMSDK */
  line-height: inherit;
  /* Kindle ignores it, Kobo needs it. If you donâ€™t use inherit, the user setting may be disabled on some Kobo devices */
 vertical-align: baseline;
 -webkit-hyphens:none;
 -moz-hyphens:none;
 hyphens:none;
}

@page
{
 margin: 1.5em;
}
body
{
 margin-top: 0.1em;
 margin-right: 0.5em;
}
img
{
 max-width: 98%;
 max-height: 100%;
}
a
{
 text-decoration:underline;
}
table
{
 margin-top: 0.5em;
 vertical-align:top;
 border-collapse:collapse;
}
td
{
 vertical-align:top;
 border-collapse:collapse;
 padding: 0.2em;
}
.cover
{
 height: 99vh;
 margin: 0em;
 padding: 0em;
}
.cover-pg
{
 text-align: center;
 margin: 0em;
 padding: 0em;
}
ol.none
{
 list-style-type: none;
}
.ul-no-mark{list-style-type: none;padding-left: 0;}
.ul-no-mark ul, .ul-no-mark ol{margin-left: 0;}
.hidden
{
 display: none;
}
.sup
{
 font-size: 70%;
 line-height: 0.8em;
 vertical-align: super;
}
.sub
{
 font-size: 70%;
 line-height: 0.8em;
 vertical-align: sub;
}
.break
{
 display: block;
}
.padding1
{
padding-left:1em;
}
.image {
display:block;
background: transparent url('images/com-01.jpg') no-repeat center;
height:2em;
border:0;
}
.blankSpace {
border:0px;
height:1.5em;
}"""

        if exists(stylesheet_css):
            with open(stylesheet_css, 'r', encoding='utf-8') as f:
                original_content = f.read()

            with open(stylesheet_css, 'w', encoding='utf-8') as f:
                f.write(additional_css.strip() + '\n' + original_content)

    css_filename = 'synth.css'
    tool_path = dirname(sys.argv[0])
    source_css = join(tool_path, css_filename)

    if exists(source_css):
        os.makedirs(styles_path, exist_ok=True)
        target_css = join(styles_path, css_filename)
        if not exists(target_css):
            shutil.copy2(source_css, target_css)

    landmark_cnt = """<ol class="none">
<li><a epub:type="cover" href="xhtml/cover.xhtml">Cover</a></li>
<li><a epub:type="title" href="xhtml/title.xhtml">Title Page</a></li>
<li><a epub:type="copyright-page" href="xhtml/copyright.xhtml">Copyright Page</a></li>
<li><a epub:type="toc" href="xhtml/contents.xhtml">Contents</a></li>
<li><a epub:type="preface" href="xhtml/preface.xhtml">Preface</a></li>
<li><a epub:type="bodymatter" href="xhtml/chapter1.xhtml">Start of Content</a></li>
<li><a epub:type="index" href="xhtml/index.xhtml">Index</a></li>
</ol>"""
    xhtml_file = _get_file_list(content_dir, 1, 1, '.xhtml$')
    if xhtml_file:
        for filename in xhtml_file:
            chapter_id = 'ch00'
            base = basename(filename)
            match = re.search(r'ch(?:apter)?(\d+)\.xhtml', base, re.IGNORECASE)
            if match:
                chapter_num = int(match.group(1))
                chapter_id = f'ch{chapter_num:02d}'  # pad to 2 digits

            xhtml_cnt = _open_utf8(filename)
            # Common Conversion
            if not re.search(r'<\?xml version="1\.0" encoding="UTF-8"\?>', xhtml_cnt, re.I | re.S):
                xhtml_cnt = re.sub(r'<!DOCTYPE html(?: [^>]*)?>\s*<html(?: [^>]*)?>', r'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en" lang="en">', xhtml_cnt, 1, re.I | re.S)
            else:
                xhtml_cnt = re.sub(r'<!DOCTYPE html(?: [^>]*)?>\s*<html(?: [^>]*)?>',r'<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en" lang="en">', xhtml_cnt, 1, re.I | re.S)
            xhtml_cnt = re.sub(r'(<body>)\s*<p(?: [^>]*)?>&#x00A0;</p>', r'\g<1>', xhtml_cnt, 1, re.I | re.S)
            xhtml_cnt = re.sub(r'<br/>', r'<span class="break"/>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'<a id="(?:pg|page)_([^"]*)"\s*/>', r'<span id="pg_\g<1>" role="doc-pagebreak" epub:type="pagebreak" aria-label=" Page \g<1>. "/>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'<a id="(?:pg|page)_([^"]*)"></a>', r'<span id="pg_\g<1>" role="doc-pagebreak" epub:type="pagebreak" aria-label=" Page \g<1>. "/>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'<samp', r'<span', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'</samp>', r'</span>', xhtml_cnt, 0, re.I | re.S)
            if not re.search(r'<link rel="stylesheet" type="text/css" href="\.\./styles/synth\.css"/>', xhtml_cnt, re.I | re.S):
                xhtml_cnt = re.sub(r'</head>',r'<link rel="stylesheet" type="text/css" href="../styles/synth.css"/>\n</head>', xhtml_cnt, 1, re.I | re.S)
            xhtml_cnt = re.sub(r'<p((?: [^>]*)?>\s*<img(?: [^>]*)?>(?:(?!</p>).)*)</p>', r'<figure\g<1></figure>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'&#160;', r'<span class="space1"/>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'&#173;', r'<span class="space1"/>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'&#x2005;&#x2005;&#x2005;&#x2005;&#x2005;&#x2005;&#x2005;', r'<span class=”padding1”/>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'<span class="sup"(?: [^>]*)?>((?:(?!</span>).)*)</span>', lambda m: re.sub(r'(<a(?: [^>]*)?epub:type="noteref"(?: [^>]*)?>)((?:(?!</a>).)*)(</a>)', r'\g<1><span class="sup">\g<2></span>\g<3>', m.group(1),0, re.I | re.S), xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'<em>',  r'<i>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'</em>',  r'</i>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'<strong>',  r'<b>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'</strong>',  r'</b>', xhtml_cnt, 0, re.I | re.S)
            xhtml_cnt = re.sub(r'<link rel="stylesheet" type="application/vnd\.adobe-page-template\+xml" href="\.\./styles/page-template\.xpgt"/>\s*',  r'', xhtml_cnt, 0, re.I | re.S)


            # Chapter Page
            if not re.search(r'cover\.xhtml', filename, re.I | re.S):
                xhtml_cnt = re.sub(r'(<body(?: [^>]*)?>)', rf'\g<1>\n<section epub:type="chapter" role="doc-chapter" aria-labelledby="{chapter_id}">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'</body>', r'</section>\n</body>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<body>\s*<section(?: [^>]*)?>)\s*(<h2(?: [^>]*)?>(?:(?!</h2>).)*</h2>)', r'\g<1>\n<header>\n\g<2>\n</header>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<section(?: [^>]*)?>\s*)((?:<header>)?\s*<h\d+(?: [^>]*)?>\s*)(<span id="pg_\d+" role="doc-pagebreak" epub:type="pagebreak"(?: [^>]*)?>)', r'\g<1>\g<3>\n\g<2>', xhtml_cnt, 0, re.I | re.S)

                xhtml_cnt = re.sub(r'<p class="([^"]*)"(?: [^>]*)?>\s*(<span id="pg_(?:[^"]*)"(?: [^>]*)?/>)', rf'\g<2>\n<h1 epub:type="titlepage" class="\g<1>" id="{chapter_id}">', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<h1(?: [^>]*)?>(?:(?!</p>).)*)(</p>)', r'\g<1></h1>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<h1(?: [^>]*)?>(?:(?!</h1>).)*</h1>', lambda m: re.sub(r'<span(?: [^>]*)?>((?:(?!</span>).)*)</span>', r'\g<1>', m.group(), 0, re.I | re.S), xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'<p class="H1[^"]*">((?:(?!</p>).)*)</p>', r'<section epub:type="title">\n<h2 epub:type="title" class="H1">\g<1></h2>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'<p class="H2[^"]*">((?:(?!</p>).)*)</p>', r'<section epub:type="title">\n<h3 epub:type="title" class="H1">\g<1></h3>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'<p class="H3[^"]*">((?:(?!</p>).)*)</p>', r'<section epub:type="title">\n<h4 epub:type="title" class="H1">\g<1></h4>', xhtml_cnt, 0, re.I | re.S)

                xhtml_cnt = re.sub(r'<h3 class="([^"]*)">((?:(?!</h3>).)*)</h3>',r'<section epub:type="title">\n<h3 epub:type="title" class="\g<1>">\g<2></h3>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'<h4 class="([^"]*)">((?:(?!</h4>).)*)</h4>',r'<section epub:type="title">\n<h4 epub:type="title" class="\g<1>">\g<2></h4>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'<h5 class="([^"]*)">((?:(?!</h5>).)*)</h5>',r'<section epub:type="title">\n<h5 epub:type="title" class="\g<1>">\g<2></h5>', xhtml_cnt, 0, re.I | re.S)


                xhtml_cnt = re.sub(r'(<section epub:type="title">\s*<h2(?: [^>]*)?>)', r'</section>\n\g<1>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'(<section epub:type="title">\s*<h3(?: [^>]*)?>)', r'</section>\n\g<1>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'(<section epub:type="title">\s*<h4(?: [^>]*)?>)', r'</section>\n\g<1>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'<h\d+(?: [^>]*)?>(?:(?!</h\d+>).)*</h\d+>', lambda m: re.sub(r'<span(?: [^>]*)?>((?:(?!</span>).)*)</span>', r'\g<1>', m.group(),0, re.I | re.S), xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'<h\d+(?: [^>]*)?>(?:(?!</h\d+>).)*</h\d+>', lambda m: re.sub(r'<span(?: [^>]*)?>', r'', m.group(),0, re.I | re.S), xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'(<p class="CAP">(?:(?!</p>).)*</p>)', r'<figcaption>\g<1></figcaption>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'(<p class="figcap">(?:(?!</p>).)*</p>)', r'<figcaption>\g<1></figcaption>', xhtml_cnt, 0, re.I | re.S)
                if re.search(r'<(h2|h3|h4)(?: [^>]*)?>', xhtml_cnt, re.I | re.S):
                    xhtml_cnt = re.sub(r'(<body>\s*<section(?: [^>]*)?>(?:(?!</section>).)*)</section>\s*', r'\g<1>', xhtml_cnt, 1, re.I | re.S)
                    xhtml_cnt = re.sub(r'</section>\n</body>', r'</section>\n</section>\n</body>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'</figure>(\s*<figcaption>(?:(?!</figcaption>).)*</figcaption>)', r'\g<1></figure>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'(<h1 epub:type="titlepage"(?: [^>]*)?>(?:(?!</p>).)*)</p>', r'<header>\n\g<1>\n</header>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'<h1 epub:type="titlepage"(?: [^>]*)?>(?:(?!</header>).)*</header>', lambda m: re.sub(r'</h1>', r' ', m.group(),0, re.I | re.S), xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<h1 epub:type="titlepage"(?: [^>]*)?>)((?:(?!</header>).)*)(</header>)', lambda m: m.group(1) + re.sub(r'<[^>]*>', r'', m.group(2),0, re.I | re.S) + '</h1>\n' + m.group(3), xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<p class="fnote"(?: [^>]*)?>(?:(?!</p>).)*</p>)', rf'<p class="line"/>\n<aside id="{chapter_id}fnote_1" role="doc-footnote">\n\g<1></aside>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'</header>\s*</section>', r'</header>', xhtml_cnt, 1, re.I | re.S)
                xhtml_cnt = re.sub(r'(<h\d+(?: [^>]*)?>\s*)<b>((?:(?!</h\d+>).)*)</b>(\s*</h\d+>)', r'\g<1>\g<2>\g<3>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'<h(\d+)([^>]*)>', lambda m: f'<h{m.group(1)}{m.group(2)}{" epub:type=\"title\"" if "epub:type=" not in m.group(2) else ""}>', xhtml_cnt, re.I | re.S)
                xhtml_cnt = re.sub(r'<h(\d+)([^>]*)>', lambda m: f'<h{m.group(1)}{m.group(2)}{f' id="{chapter_id}"' if "id=" not in m.group(2) else ""}>', xhtml_cnt, re.I | re.S)
                counter = {'val': 1}

                def update_id(match):
                    tag_start = match.group(1)  # e.g., <h3 class="..."
                    rest_attrs = match.group(2)  # everything after id="..."
                    new_id = f'id="lev{counter["val"]:02d}"'
                    counter["val"] += 1
                    return f'{tag_start} {new_id}{rest_attrs}'

                xhtml_cnt = re.sub(r'(<section epub:type="title">.*?<h\d[^>]*?)\s+id="[^"]*"([^>]*>)',
                    update_id,
                    xhtml_cnt,
                    flags=re.I | re.S
                )

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
                xhtml_cnt = re.sub(r'(<h1(?: [^>]*)?>(?:(?!</h1>).)*</h1>\s*)<p(?: [^>]*)?>((?:(?!</p>).)*)</p>', r'\g<1><p class="subtitle" epub:type="subtitle" role="doc-subtitle">\g<2></p>', xhtml_cnt, 1, re.I | re.S)

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
                xhtml_cnt = re.sub(r'<p class="IX"((?: [^>]*)?>(?:(?!</p>).)*)</p>', r'<li class="IX"\g<1></li>', xhtml_cnt, 0, re.I | re.S)
                xhtml_cnt = re.sub(r'((<a(?: [^>]*)?href="[^"]*_)\d+"(?: [^>]*)?>\d+)&#x2013;(\d+)</a>', r'\g<1></a>&#x2013;\g<2>\g<3>">\g<3></a>', xhtml_cnt, 0, re.I | re.S)

                def fix_page_ranges(txt):
                    # Match <a [attrs] href="prefix_###">###</a>&#8211;##
                    m = re.search(
                        r'<a(?P<attrs>[^>]*)href="(?P<hrefprefix>[^"]*_)(?P<start>\d+)"(?P<extra>[^>]*)>(?P<display>\d+)</a>&#8211;(?P<endpart>\d+)',
                        txt, re.I | re.S
                    )
                    if m:
                        attrs = m.group('attrs') or ''
                        extra = m.group('extra') or ''
                        hrefprefix = m.group('hrefprefix')
                        start = int(m.group('start'))  # e.g., 279
                        display = int(m.group('display'))  # inner text, also 279
                        endpart = int(m.group('endpart'))  # e.g., 81

                        # Extract last digits from display to determine difference
                        digits = len(str(endpart))
                        suffix_of_start = int(str(display)[-digits:])
                        delta = endpart - suffix_of_start
                        end_full = start + delta

                        # Rebuild final string
                        return (
                            f'<a{attrs}href="{hrefprefix}{start}"{extra}>{start}</a>'
                            f'&#8211;<a{attrs}href="{hrefprefix}{end_full}"{extra}>{end_full}</a>'
                        )
                    return txt

                xhtml_cnt = re.sub(r'<a(?: [^>]*)?href="[^"]*_\d+"(?: [^>]*)?>(?:(?!</a>).)*</a>&#8211;\d+', lambda m: fix_page_ranges(m.group()), xhtml_cnt, 0, re.I | re.S)

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

            xhtml_cnt = re.sub(r'(<body>\s*<section(?: [^>]*)?>\s*)<section(?: [^>]*)?>\s*', r'\g<1>', xhtml_cnt, 0, re.I | re.S)
            _save_utf8(filename, xhtml_cnt)

        # Nav xhtml
        nav_page_list = ''
        nav_xhtml = _get_file_list(OutputDir, 1, 1, 'nav.xhtml$')
        if nav_xhtml:
            nav_cnt = _open_utf8(nav_xhtml[0])
            nav_cnt = re.sub(r'(<title(?: [^>]*)?>)((?:(?!</title>).)*)(</title>)', r'\g<1>Navigational Table of Contents\g<3>', nav_cnt,1, re.I | re.S)
            nav_cnt = re.sub(r'<nav epub:type="toc">', r'<nav aria-labelledby="toc" epub:type="toc" role="doc-toc">', nav_cnt,1, re.I | re.S)
            nav_cnt = re.sub(r'<nav epub:type="landmarks">', r'<nav aria-labelledby="h-landmarks" epub:type="landmarks">', nav_cnt,1, re.I | re.S)
            nav_cnt = re.sub(r'(<nav aria-labelledby="toc" epub:type="toc" role="doc-toc">\s*)<h\d+(?: [^>]*)?>((?:(?!</h\d+>).)*)</h\d+>', r'\g<1><h1 class="h1ch" epub:type="title" id="toc">\g<2></h1>', nav_cnt,1, re.I | re.S)
            nav_cnt = re.sub(r'(<nav aria-labelledby="h-landmarks" epub:type="landmarks">\s*)<h2>((?:(?!</h2>).)*)</h2>',r'\g<1><h1 class="h1ch" epub:type="title" id="h-landmarks">\g<2></h1>', nav_cnt, 1, re.I | re.S)
            nav_cnt = re.sub(r'<ol epub:type="list">', r'<ol class="none">', nav_cnt,0, re.I | re.S)
            nav_list = re.search(r'<nav aria-labelledby="toc" epub:type="toc" role="doc-toc">((?:(?!</nav>).)*)</nav>', nav_cnt, re.I | re.S)
            if nav_list:
                nav_list = nav_list.group()
                for file in re.finditer(r'<a href="xhtml/([^"]*)"', nav_list, re.I | re.S):
                    xhtml = _get_file_list(content_dir, 1, 1, file.group(1))
                    if xhtml:
                        xhtml_cnt = _open_utf8(xhtml[0])
                        base = basename(xhtml[0])
                        for pg in re.finditer(r'<span id="(pg_([^"]*))"(?: [^>]*)?>', xhtml_cnt, re.I | re.S):
                            nav_page_list += (f'<li><a href="xhtml/{base}#{pg.group(1)}"'
                                              f''
                                              f'>{pg.group(2)}</a></li>\n')
            nav_cnt = re.sub(r'(<nav aria-labelledby="h-landmarks" epub:type="landmarks">(?:(?!</nav>).)*</nav>)', rf'\g<1>\n<nav epub:type="page-list" class="hidden" role="doc-pagelist" aria-labelledby="ric-9781421450513-r6YpO5Tyq7">\n<h1 epub:type="title" class="title" id="ric-9781421450513-r6YpO5Tyq7">Page List</h1>\n<ol class="none">\n{nav_page_list}</ol>\n</nav>', nav_cnt, 1, re.I | re.S)
            nav_cnt = re.sub(r'<nav aria-labelledby="h-landmarks" epub:type="landmarks">(?:(?!</nav>).)*</nav>', lambda m: re.sub(r'<ol(?: [^>]*)?>(?:(?!</ol>).)*</ol>', landmark_cnt, m.group(), 1, re.I | re.S), nav_cnt, 1, re.I | re.S)

            def sub_level_title(txt):
                final_cnt = ''
                for li in re.finditer(r'<li><a href="xhtml/(ch(?:apter)?\d+\.xhtml)">(?:(?!</a>).)*</a></li>', txt, re.I | re.S):
                    chapter = _get_file_list(OutputDir, 1, 1, li.group(1))
                    if chapter:
                        chap_cnt = _open_utf8(chapter[0])
                        title_cnt = re.search(r'</header>(?:(?!</body>).)*</body>', chap_cnt, re.I | re.S)
                        if title_cnt:
                            for idx, heading in enumerate(re.finditer(r'<h\d+(?: [^>]*)?>((?:(?!</h\d+>).)*)</h\d+>', title_cnt.group(), re.I | re.S), start=1):
                                anchor = f'#lev{idx:02d}'
                                final_cnt += f'<li><a href="xhtml/{li.group(1)}{anchor}">{heading.group(1)}</a></li>\n'
                            txt = re.sub(r'(<li><a href="xhtml/ch(?:apter)?\d+\.xhtml">(?:(?!</a>).)*</a>)</li>', rf'\g<1>\n<ol class="none">\n{final_cnt}</ol>\n</li>', txt, 1, re.I | re.S)
                            final_cnt = ''
                return txt

            nav_cnt = re.sub(r'<nav aria-labelledby="toc" epub:type="toc" role="doc-toc">(?:(?!</nav>).)*</nav>', lambda m: sub_level_title(m.group()), nav_cnt, 1, re.I | re.S)
            _save_utf8(nav_xhtml[0], nav_cnt)

        # package.opf
        pack_opf = _get_file_list(OutputDir, 1, 1, '.opf$')
        if pack_opf:
            from datetime import datetime
            now = datetime.now()
            opf_cnt = _open_utf8(pack_opf[0])
            opf_cnt = re.sub(r'<package(?: [^>]*)?>', r'<package xmlns="http://www.idpf.org/2007/opf" prefix="a11y: http://www.idpf.org/epub/vocab/package/a11y/#" unique-identifier="e9781421422039" version="3.0" xml:lang="en">', opf_cnt, 1, re.I | re.S)
            opf_cnt = re.sub(r'<metadata(?: [^>]*)?>', r'<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf" xml:lang="en">', opf_cnt, 1, re.I | re.S)
            opf_cnt = re.sub(r'(<dc:title id="title"(?: [^>]*)?>((?!</dc:title>).)*</dc:title>)', r'\g<1>\n<meta refines="#t1" property="title-type">main</meta>\n<meta refines="#t1" property="display-seq">1</meta>', opf_cnt, 1, re.I | re.S)
            opf_cnt = re.sub(r'(<meta property="dcterms:modified">)((?:(?!</meta>).)*)(</meta>)', rf'\g<1>{now.strftime("%Y-%m-%dT%H:%M:%SZ")}\g<3>', opf_cnt, 1, re.I | re.S)
            opf_cnt = re.sub(r'<guide(?: [^>]*)?>(?:(?!</guide>).)*</guide>', r'', opf_cnt, 0, re.I | re.S)
            opf_cnt = re.sub(r'(</manifest>\s*)<spine toc="toc">', r'\g<1><spine xmlns="http://www.idpf.org/2007/opf" toc="ncx">', opf_cnt, 1, re.I | re.S)
            opf_cnt = re.sub(r'<meta property="rendition:orientation">((?!</meta>).)*</meta>', r'<dc:source id="src-id">urn:isbn:0000000000000</dc:source>', opf_cnt, 1, re.I | re.S)
            opf_cnt = re.sub(r'<meta property="rendition:spread">((?!</meta>).)*</meta>', r'<meta property="source-of" refines="#src-id">pagination</meta>', opf_cnt, 1, re.I | re.S)
            opf_cnt = re.sub(r'<meta property="dcterms:date">((?!</meta>).)*</meta>', rf'<dc:format>application/epub</dc:format>\n<dc:date>{now.strftime("%Y-%m-%dT%H:%M:%SZ")}</dc:date>', opf_cnt, 1, re.I | re.S)
            opf_cnt = re.sub(r'<meta property="dcterms:date">((?!</meta>).)*</meta>', rf'<dc:format>application/epub</dc:format>\n<dc:date>{now.strftime("%Y-%m-%dT%H:%M:%SZ")}</dc:date>', opf_cnt, 1, re.I | re.S)
            opf_cnt = re.sub(r'(<meta name="cover" content="cover-image"/>)', r'\g<1>\n<meta property="schema:accessMode">visual</meta>\n<meta property="schema:accessModeSufficient">textual,visual</meta>\n<meta property="schema:accessModeSufficient">textual</meta>\n<meta property="schema:accessibilityFeature">alternativeText</meta>\n<meta property="schema:accessibilityFeature">displayTransformability</meta>\n<meta property="schema:accessibilityFeature">pageBreakMarkers</meta>\n<meta property="schema:accessibilityFeature">readingOrder</meta>\n<meta property="schema:accessibilityFeature">structuralNavigation</meta>\n<meta property="schema:accessibilityFeature">ARIA</meta>\n<meta property="schema:accessibilityFeature">index</meta>\n<meta property="schema:accessibilityFeature">tableOfContents</meta>\n<meta property="schema:accessibilityHazard">none</meta>\n<meta property="schema:accessibilitySummary">A Moderate book with some images, This title is defined with accessible structural markup. This book contains various accessibility features such as alternative text for images, table of content, page-list, landmark, reading order, Structural Navigation, and semantic structure. This publication conforms to WCAG 2.2 Level AA. There is a page list and embedded page-breaks within this EPUB to aid in the ability to go to a specific page. A number of blank pages in the print equivalent book have been removed resulting in some pages not appearing in this EPUB.</meta>', opf_cnt, 1, re.I | re.S)
            # opf_cnt = re.sub(r'<item id="cover-image" href="images/9781421422039.jpg" media-type="image/jpeg"/>', r'<item id="cover-image" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>', opf_cnt, 1, re.I | re.S)
            opf_cnt = re.sub(r'(<item id="cover-image"[^>]*)(/>)', lambda m: m.group(0) if 'properties="cover-image"' in m.group(1) else f'{m.group(1)} properties="cover-image"{m.group(2)}', opf_cnt, 1, re.I | re.S)
            opf_cnt = re.sub(r'<dc:creator id="creator"(?: [^>]*)?>((?!</dc:creator>).)*</dc:creator>', r'<dc:creator id="creator1">[Author Name]</dc:creator>\n<meta refines="#creator1" property="role" scheme="marc:relators">aut</meta>\n<meta refines="#creator1" property="file-as">[Name, Author]</meta>', opf_cnt, 1, re.I | re.S)
            _save_utf8(pack_opf[0], opf_cnt)

        # ncx file
        # ncx_file = _get_file_list(OutputDir, 1, 1, '.ncx$')
        # if ncx_file:
        #     ncx_cnt = _open_utf8(ncx_file[0])


try:
    _epub_extraction()
except Exception as e:
    print(e)
    sys.exit()

sys.exit("\n\t\t Process completed...!!!\n")

