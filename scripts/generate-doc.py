#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**********************************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/ebu/OSCIED

import glob, re, shutil, os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from os.path import basename, dirname, join, splitext
from common import (
    REPORT_TOOLS_PLANTUML_BINARY, DAVID_REPORT_PATH, DAVID_REPORT_BUILD_PATH,
    DAVID_REPORT_RELEASE_PATH, DAVID_REPORT_SOURCE_PATH, DAVID_REPORT_UML_PATH,
    DAVID_REPORT_COMMON_FILE, DAVID_REPORT_REFERENCES_FILE, DAVID_REPORT_LINKS_FILE,
    WIKI_BUILD_PATH, WIKI_SOURCE_PATH, xprint
)
from pyutils.py_filesystem import try_makedirs, try_remove
from pyutils.py_subprocess import cmd
from pyutils.py_unicode import configure_unicode

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
        xprint(u'At least one target must be enabled')

    revision = cmd(u"git log --pretty=format:'%H' -n 1", fail=False)['stdout']
    if not revision:
        xprint(u'Unable to detect local copy revision number !')

    print(u'Generate images from textual UMLs')
    if cmd([u'java', u'-jar', REPORT_TOOLS_PLANTUML_BINARY, DAVID_REPORT_UML_PATH,
            u'-failonerror'], fail=False)[u'returncode'] != 0:
        xprint(u'Unable to generate images from UML diagrams')

    print('Append hooks UMLs images together')
    os.chdir(DAVID_REPORT_UML_PATH)
    for name in (u'orchestra', u'webui', u'storage', u'transform', u'publisher'):
        a = u'activity-{0}-install.png'.format(name)
        b = u'activity-{0}-config-changed.png'.format(name)
        c = u'activity-{0}-start.png'.format(name)
        d = u'activity-{0}-stop.png'.format(name)
        e = u'activity-{0}-hooks.png'.format(name)
        if cmd([u'convert', a, b, c, d, 'u+append', e], fail=False)[u'returncode'] != 0:
            if cmd([u'convert', a, c, d, u'+append', e], fail=False)[u'returncode'] != 0:
                xprint(u"Unable to append {0}'s hooks UMLs images".format(name))
        (try_remove(f) for f in (a, b, c, d))

    print(u'Generate reStructuredText from templates')
    for template_filename in glob.glob(join(DAVID_REPORT_SOURCE_PATH, u'*.rst.template')):
        rst_filename = join(dirname(template_filename), splitext(template_filename)[0])
        with open(template_filename) as template_file:
            data = template_file.read().replace(u'SVN_REVISION', revision)
            with open(rst_filename, u'w', u'utf-8') as rst_file:
                rst_file.write(data)

    print(u'Generate links into common file')
    common_data = references_data = u''
    with open(DAVID_REPORT_LINKS_FILE) as links_file:
        for columns in [line.split(u';') for line in links_file.readlines()]:
            if len(columns) == 1:
                references_data += columns[0]
            else:
                name, replace, url = columns
                if replace:
                    common_data += u'.. |{0}| replace:: {1}\n'.format(name, replace)
                if url != u'\n':
                    common_data += u'.. _{0}: {1}'.replace(name, url)
                    common_data += u'.. |{0}_link| replace:: [{1}] {2}'.replace(name, name, url)
                    references_data += '* |{0}_link|\n'.replace(name)
    with open(DAVID_REPORT_COMMON_FILE, u'w', u'utf-8') as common_file:
        common_file.write(common_data)
    with open(DAVID_REPORT_REFERENCES_FILE, u'w', u'utf-8') as references_file:
        references_file.write(references_data)

    print(u'Append header files into common file')
    for header_filename in glob.glob(join(DAVID_REPORT_SOURCE_PATH, u'*.rst.header')):
        rst_filename = join(dirname(header_filename), splitext(header_filename)[0])
        with open(rst_filename, u'rw+', u'utf-8') as rst_file:
            data = rst_file.read()
            with open(header_filename) as header_file:
                rst_file.seek(0)
                rst_file.write(header_file.read() + data)

    # FIXME echo about.rst -> index.rst for html version at least
    shutil.rmtree(DAVID_REPORT_BUILD_PATH, ignore_errors=True)
    try_makedirs(DAVID_REPORT_BUILD_PATH)
    os.chdir(DAVID_REPORT_PATH)

    if args.html:
        print(HELP_HTML)
        result = cmd(u'make html', fail=False)
        with open(u'build_html.log', u'w', u'utf-8') as log_file:
            log_file.write(u'Output:\n{0}\nError:\n{1}'.format(result[u'stdout'], result[u'stderr']))
        if result[u'returncode'] != 0:
            xprint(u'Unable to generate HTML version of the report, see build_html.log')

    if args.pdf:
        print(HELP_PDF)
        result = cmd(u'make latexpdf', fail=False)
        with open(u'build_pdf.log', u'w') as log_file:
            log_file.write(u'Output:\n{0}\nError:\n{1}'.format(result['stdout'], result['stderr']))
        if result['returncode'] != 0:
            xprint(u'Unable to generate PDF version of the report, see build_pdf.log')
        print(u'Move PDF into releases directory')
        for pdf_filename in glob.glob(join(DAVID_REPORT_BUILD_PATH, u'*.pdf')):
            os.move(pdf_filename, DAVID_REPORT_RELEASE_PATH)

    #pecho 'Compress report'
    #cd "$DAVID_REPORT_RELEASE_PATH" || xecho "Unable to find path $DAVID_REPORT_RELEASE_PATH"
    #gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH \
    #  -sOutputFile=MA_DavidFischer_OSCIED_compressed.pdf MA_DavidFischer_OSCIED.pdf

    if args.wiki:
        print(HELP_WIKI)
        file_regex = re.compile(r':file:`([^`]*)`')
        include_regex = re.compile(r'(?P<space>\s*)\.\. literalinclude::\s+(?P<link>\S+)\s*')
        option_regex = re.compile(r'(?P<space>\s*):(?P<name>\S+):\s+(?P<value>\S+)\s*')
        c_data = u''.join(filter(lambda l: u':orphan:' not in l, open(DAVID_REPORT_COMMON_FILE)))
        for rst_src_filename in glob.glob(join(WIKI_SOURCE_PATH, u'*.rst')):
            rst_dst_filename = join(WIKI_BUILD_PATH, basename(rst_src_filename))
            with open(rst_src_filename) as rst_src_file:
                data = u'{0}\n{1}'.format(c_data, rst_src_file.read())
                # Replace :file: directives by ``
                data = file_regex.sub(r'``\1``', data, re.MULTILINE)
                # Replace literalinclude directives by code-block
                include = {u'space': None, u'link': None}
                options = {}
                for line in data.split('\n'):
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
                            # with open(join(DAVID_REPORT_SOURCE_PATH, include['link'])) as f:
                            #     data = f.read()
                            #     # TODO -> write to dest
                            # include['link'] = None
                with open(rst_dst_filename, u'w', u'utf-8') as rst_dst_file:
                    rst_dst_file.write(data)

    print(u'Remove intermediate files')
    for png_filename in glob.glob(join(DAVID_REPORT_UML_PATH, u'*.png')):
        os.remove(png_filename)
    for template_filename in glob.glob(join(DAVID_REPORT_SOURCE_PATH, u'*.rst.template')):
        os.remove(join(dirname(template_filename), splitext(template_filename)[0]))
