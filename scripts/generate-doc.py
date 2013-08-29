#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : David Fischer (david.fischer.ch@gmail.com)
#  Copyright       : Copyright (c) 2012-2013 EBU. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of EBU Technology & Innovation OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/ebu/OSCIED

from __future__ import print_function

import glob, re, shutil, os, sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from codecs import open
from os.path import basename, dirname, join, splitext
from library.oscied_lib.pyutils.py_console import print_error
from library.oscied_lib.pyutils.py_filesystem import try_makedirs, try_remove
from library.oscied_lib.pyutils.py_subprocess import cmd
from library.oscied_lib.pyutils.py_unicode import configure_unicode

SCRIPTS_PATH = os.getcwd()
BASE_PATH = dirname(SCRIPTS_PATH)
DOCS_PATH = join(BASE_PATH, u'docs')
TOOLS_PATH = join(BASE_PATH, u'tools')

# Reports related configuration (e.g. listing of components)
REPORT_TOOLS_PLANTUML_BINARY = join(TOOLS_PATH, u'plantuml.jar')
DAVID_REPORT_RELEASE_PATH = join(DOCS_PATH, u'david', u'master_thesis')
DAVID_REPORT_PATH = join(DOCS_PATH, u'david', u'master_thesis_rst')
DAVID_REPORT_BUILD_PATH = join(DAVID_REPORT_PATH, u'build')
DAVID_REPORT_SOURCE_PATH = join(DAVID_REPORT_PATH, u'source')
DAVID_REPORT_UML_PATH = join(DAVID_REPORT_PATH, u'uml')
DAVID_REPORT_COMMON_FILE = join(DAVID_REPORT_SOURCE_PATH, u'common.rst')
DAVID_REPORT_LINKS_FILE = join(DAVID_REPORT_SOURCE_PATH, u'common.rst.links')
DAVID_REPORT_REFERENCES_FILE = join(DAVID_REPORT_SOURCE_PATH, u'appendices-references.rst')

WIKI_BUILD_PATH = join(DOCS_PATH, u'wiki', u'build')
WIKI_SOURCE_PATH = join(DOCS_PATH, u'wiki', u'source')


if __name__ == u'__main__':
    configure_unicode()

    HELP_HTML = u'Build HTML from source reStructuredText files'
    HELP_PDF = u'Build PDF from source reStructuredText files'
    HELP_WIKI = u'Build Wiki from source reStructuredText files'

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        epilog=u'''Generate OSCIED project documentation from source reStructuredText files.''')
    parser.add_argument(u'--html', help=HELP_HTML, action=u'store_true')
    parser.add_argument(u'--pdf',  help=HELP_PDF,  action=u'store_true')
    parser.add_argument(u'--wiki', help=HELP_WIKI, action=u'store_true')
    args = parser.parse_args()

    if not args.html and not args.pdf and not args.wiki:
        parser.print_help()
        print(u'')
        print_error(u'At least one target must be enabled')

    revision = cmd(u"git log --pretty=format:'%H' -n 1", fail=False)[u'stdout']
    if not revision:
        print_error(u'Unable to detect local copy revision number !')

    print(u'Generate images from textual UMLs')
    result = cmd([u'java', u'-jar', REPORT_TOOLS_PLANTUML_BINARY, DAVID_REPORT_UML_PATH, u'-failonerror'], fail=False)
    if result[u'returncode'] != 0:
        print_error(u'Unable to generate images from UML diagrams, reason: {0}.'.format(result[u'stderr']))

    print(u'Append hooks UMLs images together')
    os.chdir(DAVID_REPORT_UML_PATH)
    for name in (u'orchestra', u'webui', u'storage', u'transform', u'publisher'):
        a = u'activity-{0}-install.png'.format(name)
        b = u'activity-{0}-config-changed.png'.format(name)
        c = u'activity-{0}-start.png'.format(name)
        d = u'activity-{0}-stop.png'.format(name)
        e = u'activity-{0}-hooks.png'.format(name)
        results = [0] * 2
        results[0] = cmd([u'convert', a, b, c, d, u'+append', e], fail=False)
        if results[0][u'returncode'] != 0:
            results[1] = cmd([u'convert', a, c, d, u'+append', e], fail=False)
            if results[1][u'returncode'] != 0:
                print_error(u"Unable to append {0}'s hooks UMLs images, reasons: {1}, {2}.".format(name,
                       results[0][u'stderr'], results[1][u'stderr']))
        (try_remove(f) for f in (a, b, c, d))

    print(u'Generate reStructuredText from templates')
    for template_filename in glob.glob(join(DAVID_REPORT_SOURCE_PATH, u'*.rst.template')):
        rst_filename = join(dirname(template_filename), splitext(template_filename)[0])
        with open(template_filename, u'r',  u'utf-8') as template_file:
            data = template_file.read().replace(u'SVN_REVISION', revision)
            with open(rst_filename, u'w', u'utf-8') as rst_file:
                rst_file.write(data)

    print(u'Generate links into common file')
    common_data = references_data = u''
    with open(DAVID_REPORT_LINKS_FILE, u'r', u'utf-8') as links_file:
        for columns in [line.split(u';') for line in links_file.readlines()]:
            if len(columns) == 1:
                references_data += columns[0]
            else:
                name, replace, url = columns
                if replace:
                    common_data += u'.. |{0}| replace:: {1}\n'.format(name, replace)
                if url != u'\n':
                    common_data += u'.. _{0}: {1}'.format(name, url)
                    common_data += u'.. |{0}_link| replace:: [{0}] {1}'.format(name, url)
                    references_data += u'* |{0}_link|\n'.format(name)
    with open(DAVID_REPORT_COMMON_FILE, u'w', u'utf-8') as common_file:
        common_file.write(common_data)
    with open(DAVID_REPORT_REFERENCES_FILE, u'w', u'utf-8') as references_file:
        references_file.write(references_data)

    print(u'Append header files into common file')
    for header_filename in glob.glob(join(DAVID_REPORT_SOURCE_PATH, u'*.rst.header')):
        rst_filename = join(dirname(header_filename), splitext(header_filename)[0])
        with open(rst_filename, u'rw+', u'utf-8') as rst_file:
            data = rst_file.read()
            with open(header_filename, u'r', u'utf-8') as header_file:
                rst_file.seek(0)
                rst_file.write(header_file.read() + data)

    # FIXME echo about.rst -> index.rst for html version at least
    shutil.rmtree(DAVID_REPORT_BUILD_PATH, ignore_errors=True)
    try_makedirs(DAVID_REPORT_BUILD_PATH)
    os.chdir(DAVID_REPORT_PATH)

    if args.html:
        print(HELP_HTML)
        result = cmd(u'sudo make html', fail=False)
        with open(u'build_html.log', u'w', u'utf-8') as log_file:
            log_file.write(u'Output:\n{0}\nError:\n{1}'.format(result[u'stdout'], result[u'stderr']))
        if result[u'returncode'] != 0:
            print_error(u'Unable to generate HTML version of the report, see build_html.log')

    if args.pdf:
        print(HELP_PDF)
        result = cmd(u'sudo make latexpdf', fail=False)
        with open(u'build_pdf.log', u'w', u'utf-8') as log_file:
            log_file.write(u'Output:\n{0}\nError:\n{1}'.format(result[u'stdout'], result[u'stderr']))
        if result[u'returncode'] != 0:
            print_error(u'Unable to generate PDF version of the report, see build_pdf.log')
        print(u'Move PDF into releases directory')
        for pdf_filename in glob.glob(join(DAVID_REPORT_BUILD_PATH, u'*.pdf')):
            os.move(pdf_filename, DAVID_REPORT_RELEASE_PATH)

    #pecho u'Compress report'
    #cd "$DAVID_REPORT_RELEASE_PATH" || xecho "Unable to find path $DAVID_REPORT_RELEASE_PATH"
    #gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH \
    #  -sOutputFile=MA_DavidFischer_OSCIED_compressed.pdf MA_DavidFischer_OSCIED.pdf

    if args.wiki:
        print(HELP_WIKI)
        file_regex = re.compile(ur':file:`([^`]*)`')
        include_regex = re.compile(ur'(?P<space>\s*)\.\. literalinclude::\s+(?P<link>\S+)\s*')
        option_regex = re.compile(ur'(?P<space>\s*):(?P<name>\S+):\s+(?P<value>\S+)\s*')
        c_data = u''.join(filter(lambda l: u':orphan:' not in l, open(DAVID_REPORT_COMMON_FILE, u'r', u'utf-8')))
        for rst_src_filename in glob.glob(join(WIKI_SOURCE_PATH, u'*.rst')):
            rst_dst_filename = join(WIKI_BUILD_PATH, basename(rst_src_filename))
            with open(rst_src_filename, u'r', u'utf-8') as rst_src_file:
                data = u'{0}\n{1}'.format(c_data, rst_src_file.read())
                # Replace :file: directives by ``
                data = file_regex.sub(ur'``\1``', data, re.MULTILINE)
                # Replace literalinclude directives by code-block
                include = {u'space': None, u'link': None}
                options = {}
                for line in data.split(u'\n'):
                    match = include_regex.match(line)
                    if match:
                        include = match.groupdict()
                    elif include[u'link']:
                        match = option_regex.match(line)
                        if match:
                            option = match.groupdict()
                            options[option[u'name']] = option[u'value']
                        else:
                            pass  # FIXME TODO
                            # # Here all lines of literalinclude are scanned
                            # with open(join(DAVID_REPORT_SOURCE_PATH, include[u'link'])) as f:
                            #     data = f.read()
                            #     # TODO -> write to dest
                            # include[u'link'] = None
                with open(rst_dst_filename, u'w', u'utf-8') as rst_dst_file:
                    rst_dst_file.write(data)

    print(u'Remove intermediate files')
    for png_filename in glob.glob(join(DAVID_REPORT_UML_PATH, u'*.png')):
        os.remove(png_filename)
    for template_filename in glob.glob(join(DAVID_REPORT_SOURCE_PATH, u'*.rst.template')):
        os.remove(join(dirname(template_filename), splitext(template_filename)[0]))
