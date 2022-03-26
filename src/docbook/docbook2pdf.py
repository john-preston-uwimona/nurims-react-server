import subprocess
import tempfile
import os

from markdown2 import markdown, markdown_path
from weasyprint import HTML, CSS

# from exceptions import ValidationError

OS_ENV = {**os.environ, 'JAVA_HOME': '/etc/alternatives/jre_11/'}


def docbook2pdf(pdf_file_path, docbook_xml_file=None, xslt_file=None, xml_file_path=None,
                xml_template_file=None, html=None, html_file_path=None, log=None):
    """
    Converts input pdf to styled HTML and renders it to a PDF file.

    Args:
        pdf_file_path: output PDF file path.
        docbook_xml_file: input pdf raw string content.
        xslt_file: input styles path (CSS).
        log: logging stream.
        xml_file_path: input pdf file path.
        xml_template_file: absolute base path for pdf linked content (as images).
        html: raw html.
        html_file_path: input html file path.

    Returns:
        None

    Raises:
        ValueError: if md_content and md_file_path are empty.
    """
    if xslt_file is None:
        raise ValueError('No xslt file specified')
    if docbook_xml_file is None:
        raise ValueError('No docbook file specified')

    fo_file = tempfile.NamedTemporaryFile(mode="r+b", suffix=".fo")

    command = ["/usr/bin/xsltproc", "--nonet", "--noout", "--output", fo_file.name, xslt_file, docbook_xml_file]
    if log:
        log.trace("spawning command - {}".format(" ".join(command)))
    result = subprocess.run(command, env=OS_ENV, text=True, capture_output=True)
    if result.returncode:
        raise subprocess.CalledProcessError(
            returncode=result.returncode,
            cmd=result.args,
            stderr=result.stderr
        )
    if result.stdout and log:
        log.trace("{}".format(result.stdout))
    if result.stderr and log:
        log.trace("{}".format(result.stderr))

    command = ["/usr/bin/fop", "-c", "/home/jp/SourceCode/nurims-react/server/config/docbook/fopconfig.xml", fo_file.name, pdf_file_path]
    if log:
        log.trace("spawning command - {}".format(" ".join(command)))
    result = subprocess.run(command, env=OS_ENV, text=True, capture_output=True)
    if result.returncode:
        raise subprocess.CalledProcessError(
            returncode=result.returncode,
            cmd=result.args,
            stderr=result.stderr
        )
    if result.stdout and log:
        log.trace("{}".format(result.stdout))
    if result.stderr and log:
        log.trace("{}".format(result.stderr))

    return result
