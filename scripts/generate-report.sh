#!/usr/bin/env bash

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/EBU-TI/OSCIED

. ./common.sh

main()
{
  #revision=$(svn info | grep -m 1 '.*vision.*: *[0-9]*$')
  #revision=$(expr match "$revision" '[^0-9]*\([0-9]*\)[^0-9]*')
  revision=$(git log --pretty=format:'%H' -n 1)
  if [ ! "$revision" ]; then
    xecho 'Unable to detect local copy revision number !'
  fi

  # Generate images from textual UMLs
  java -jar "$REPORT_TOOLS_PLANTUML_BINARY" "$DAVID_REPORT_UML_PATH" \
    -failonerror || xecho 'Unable to generate images from UML diagrams'

  cd "$DAVID_REPORT_UML_PATH" || xecho "Unable to find path $DAVID_REPORT_UML_PATH"

  # Append hooks UMLs images together !
  for name in 'orchestra' 'webui' 'storage' 'transform' 'publisher'
  do
    a="activity-$name-install.png"
    b="activity-$name-config-changed.png"
    c="activity-$name-start.png"
    d="activity-$name-stop.png"
    e="activity-$name-hooks.png"
    convert $a $b $c $d +append $e || convert $a $c $d +append $e || \
      xecho "Unable to append $name's hooks UMLs images"
    rm $a $b $c $d 2>/dev/null
  done

  cd "$DAVID_REPORT_PATH" || xecho "Unable to find path $DAVID_REPORT_PATH"

  listing=/tmp/$$.list
  tmpfile=/tmp/$$
  trap "rm -f '$listing' '$tmpfile' 2>/dev/null" INT TERM EXIT
  find . -type f -name "*.rst.template" | sort > $listing
  while read template
  do
    rest=$(dirname "$template")/$(basename "$template" .template)
    sed "s:SVN_REVISION:$revision:g" "$template" > "$rest"
  done < $listing

  common=''
  references=''
  savedIFS=$IFS
  IFS=';'
  while read name replace url
  do
    if [ ! "$replace" -a ! "$url" ]; then
      references="$references$name\n"
    fi
    if [ "$replace" ]; then
      common="$common.. |$name| replace:: $replace\n"
    fi
    if [ "$url" ]; then
      common="$common.. _$name: $url\n"
      common="$common.. |${name}_link| replace:: [$name] $url\n"
      references="$references* |${name}_link|\n"
    fi
  done < 'source/common.rst.links'
  IFS=$savedIFS
  echo $e_ "$common" > 'source/common.rst'
  echo $e_ "$references" > 'source/appendices-references.rst'

  find . -type f -name "*.rst.header" | sort > $listing
  while read header
  do
    rest=$(dirname "$header")/$(basename "$header" .header)
    cat "$header" "$rest" > "$tmpfile"
    mv "$tmpfile" "$rest"
  done < $listing

  # FIXME echo about.rst -> index.rst for html version at least
  $udo rm -rf build/* 2>/dev/null
  make html || xecho 'Unable to generate HTML version of the report'
  make latexpdf || xecho 'Unable to generate PDF version of the report'

  find "$DAVID_REPORT_BUILD_PATH" -type f -name "*.pdf" -exec mv {} "$DAVID_REPORT_RELEASE_PATH" \;

  # Compress report
  #cd "$DAVID_REPORT_RELEASE_PATH" || xecho "Unable to find path $DAVID_REPORT_RELEASE_PATH"
  #gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dQUIET -dBATCH \
  #  -sOutputFile=MA_DavidFischer_OSCIED_compressed.pdf MA_DavidFischer_OSCIED.pdf

  # Remove intermediate files
  #find "$DAVID_REPORT_UML_PATH" -type f -name "*.png" -exec rm -f {} \;
  #find "$DAVID_REPORT_PATH" -type f -name "*.rst.template" | while read template
  #do
  #  rm -f "$(dirname "$template")/$(basename "$template" .template)"
  #done
}

main "$@"
