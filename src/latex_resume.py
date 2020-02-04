import argh

import markdown, mdx_latex
latex_mdx = mdx_latex.LaTeXExtension()
md = markdown.Markdown()
latex_mdx.extendMarkdown(md, markdown.__dict__)

section_format = """
\\input{default}
\\renewcommand{\\optionA}{
OPTIONA
}
"""


def get_markdown(section, output):
    with open(section, 'r') as in_file:
        md_text = in_file.read().strip()
        with open(output, 'w') as out_file:
            text = md.convert(md_text)
            text = text.replace("<root>", "").replace("</root>", "")
            if text:
                text = section_format.replace("OPTIONA", text)
            else:
                text = section_format
            out_file.write(text)



if __name__ == "__main__":
    p = argh.ArghParser()
    p.add_commands([get_markdown])
    p.dispatch()

