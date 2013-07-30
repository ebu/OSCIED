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

from __future__ import print_function

import glob, re, shutil, os
from os.path import basename, dirname, join, splitext
from common import (
    REPORT_TOOLS_PLANTUML_BINARY, DAVID_REPORT_PATH, DAVID_REPORT_BUILD_PATH,
    DAVID_REPORT_RELEASE_PATH, DAVID_REPORT_SOURCE_PATH, DAVID_REPORT_UML_PATH,
    DAVID_REPORT_COMMON_FILE, DAVID_REPORT_REFERENCES_FILE, DAVID_REPORT_LINKS_FILE,
    WIKI_BUILD_PATH, WIKI_SOURCE_PATH, xprint
)
from pyutils.filesystem import try_makedirs, try_remove
from pyutils.pyutils import cmd

if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    HELP_HTML = 'Build HTML from source reStructuredText files'
    HELP_PDF = 'Build PDF from source reStructuredText files'
    HELP_WIKI = 'Build Wiki from source reStructuredText files'

    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        epilog='''Generate OSCIED project documentation from source reStructuredText files.''')
    parser.add_argument('--html', help=HELP_HTML, action='store_true')
    parser.add_argument('--pdf', help=HELP_PDF, action='store_true')
    parser.add_argument('--wiki', help=HELP_WIKI, action='store_true')
    args = parser.parse_args()

    if not args.html and not args.pdf and not args.wiki:
        parser.print_help()
        print('')
        xprint('At least one target must be enabled')

    revision = cmd("git log --pretty=format:'%H' -n 1", fail=False)['stdout']
    if not revision:
        xprint('Unable to detect local copy revision number !')

    print('Generate images from textual UMLs')
    if cmd(['java', '-jar', REPORT_TOOLS_PLANTUML_BINARY, DAVID_REPORT_UML_PATH,
            '-failonerror'], fail=False)['returncode'] != 0:
        xprint('Unable to generate images from UML diagrams')

    print('Append hooks UMLs images together')
    os.chdir(DAVID_REPORT_UML_PATH)
    for name in ('orchestra', 'webui', 'storage', 'transform', 'publisher'):
        a = 'activity-%s-install.png' % name
        b = 'activity-%s-config-changed.png' % name
        c = 'activity-%s-start.png' % name
        d = 'activity-%s-stop.png' % name
        e = 'activity-%s-hooks.png' % name
        if cmd(['convert', a, b, c, d, '+append', e], fail=False)['returncode'] != 0:
            if cmd(['convert', a, c, d, '+append', e], fail=False)['returncode'] != 0:
                xprint("Unable to append %s's hooks UMLs images" % name)
        (try_remove(f) for f in (a, b, c, d))

    print('Generate reStructuredText from templates')
    for template_filename in glob.glob(join(DAVID_REPORT_SOURCE_PATH, '*.rst.template')):
        rst_filename = join(dirname(template_filename), splitext(template_filename)[0])
        with open(template_filename) as template_file:
            data = template_file.read().replace('SVN_REVISION', revision)
            with open(rst_filename, 'w') as rst_file:
                rst_file.write(data)

    print('Generate links into common file')
    common_data = references_data = ''
    with open(DAVID_REPORT_LINKS_FILE) as links_file:
        for columns in [line.split(';') for line in links_file.readlines()]:
            if len(columns) == 1:
                references_data += columns[0]
            else:
                name, replace, url = columns
                if replace:
                    common_data += '.. |%s| replace:: %s\n' % (name, replace)
                if url != '\n':
                    common_data += '.. _%s: %s' % (name, url)
                    common_data += '.. |%s_link| replace:: [%s] %s' % (name, name, url)
                    references_data += '* |%s_link|\n' % name
    with open(DAVID_REPORT_COMMON_FILE, 'w') as common_file:
        common_file.write(common_data)
    with open(DAVID_REPORT_REFERENCES_FILE, 'w') as references_file:
        references_file.write(references_data)

    print('Append header files into common file')
    for header_filename in glob.glob(join(DAVID_REPORT_SOURCE_PATH, '*.rst.header')):
        rst_filename = join(dirname(header_filename), splitext(header_filename)[0])
        with open(rst_filename, 'rw+') as rst_file:
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
        result = cmd('make html', fail=False)
        with open('build_html.log', 'w') as log_file:
            log_file.write('Output:\n%s\nError:\n%s' % (result['stdout'], result['stderr']))
        if result['returncode'] != 0:
            xprint('Unable to generate HTML version of the report, see build_html.log')

    if args.pdf:
        print(HELP_PDF)
        result = cmd('make latexpdf', fail=False)
        with open('build_pdf.log', 'w') as log_file:
            log_file.write('Output:\n%s\nError:\n%s' % (result['stdout'], result['stderr']))
        if result['returncode'] != 0:
            xprint('Unable to generate PDF version of the report, see build_pdf.log')
        print('Move PDF into releases directory')
        for pdf_filename in glob.glob(join(DAVID_REPORT_BUILD_PATH, '*.pdf')):
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
        c_data = ''.join(filter(lambda l: ':orphan:' not in l, open(DAVID_REPORT_COMMON_FILE)))
        for rst_src_filename in glob.glob(join(WIKI_SOURCE_PATH, '*.rst')):
            rst_dst_filename = join(WIKI_BUILD_PATH, basename(rst_src_filename))
            with open(rst_src_filename) as rst_src_file:
                data = '%s\n%s' % (c_data, rst_src_file.read())
                # Replace :file: directives by ``
                data = file_regex.sub(r'``\1``', data, re.MULTILINE)
                # Replace literalinclude directives by code-block
                include = {'space': None, 'link': None}
                options = {}
                for line in data.split('\n'):
                    match = include_regex.match(line)
                    if match:
                        include = match.groupdict()
                    elif include['link']:
                        match = option_regex.match(line)
                        if match:
                            option = match.groupdict()
                            options[option['name']] = option['value']
                        else:
                            pass  # FIXME TODO
                            # # Here all lines of literalinclude are scanned
                            # with open(join(DAVID_REPORT_SOURCE_PATH, include['link'])) as f:
                            #     data = f.read()
                            #     # TODO -> write to dest
                            # include['link'] = None
                with open(rst_dst_filename, 'w') as rst_dst_file:
                    rst_dst_file.write(data)

    print('Remove intermediate files')
    for png_filename in glob.glob(join(DAVID_REPORT_UML_PATH, '*.png')):
        os.remove(png_filename)
    for template_filename in glob.glob(join(DAVID_REPORT_SOURCE_PATH, '*.rst.template')):
        os.remove(join(dirname(template_filename), splitext(template_filename)[0]))
