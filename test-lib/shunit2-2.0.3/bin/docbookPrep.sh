#! /bin/sh
# $Id: docbookPrep.sh 44 2007-04-10 20:23:18Z sfsetse $

XML_VERSION='4.4'
XML_FILE="docbook-xml-${XML_VERSION}"
XML_URL="http://www.docbook.org/xml/${XML_VERSION}/${XML_FILE}.zip"

XSL_VERSION='1.72.0'
XSL_FILE="docbook-xsl-${XSL_VERSION}"
XSL_URL="http://downloads.sourceforge.net/docbook/${XSL_FILE}.tar.bz2"

#-----------------------------------------------------------------------------
# do no edit below here
#-----------------------------------------------------------------------------

PATH="${PATH}:${MY_DIR}"
PWD=${PWD:-`pwd`}

MY_BASE=`basename "$0"`
MY_DIR=`dirname "$0"`

# load shlib
. "${MY_DIR}/../lib/sh/shlib"

BASE_DIR=`shlib_relToAbsPath "${MY_DIR}/.."`
DL_DIR="${BASE_DIR}/tmp"
DOCBOOK_DIR="${BASE_DIR}/share/docbook"

CURL_OPTS='-C - -Os'
WGET_OPTS='-cq'

METHOD_NONE=0
METHOD_WGET=1
METHOD_CURL=2

get_url()
{
  url=$1
  case ${method} in
    ${METHOD_CURL}) ${curl} ${CURL_OPTS} "${url}" ;;
    ${METHOD_WGET}) ${wget} ${WGET_OPTS} "${url}" ;;
  esac
}

# determine method
method=${METHOD_NONE}
wget=`which wget`
[ $? -eq 0 ] && method=${METHOD_WGET}
curl=`which curl`
[ $? -eq 0 -a ${method} -eq ${METHOD_NONE} ] && method=${METHOD_CURL}
if [ ${method} -eq ${METHOD_NONE} ]; then
  echo "unable to locate wget or curl. cannot continue"
  exit 1
fi

# create download dir
mkdir -p "${DL_DIR}"

# get the docbook xml files
echo 'Docbook XML'
echo '  downloading'
cd ${DL_DIR}
get_url "${XML_URL}"
if [ -f "${DL_DIR}/${XML_FILE}.zip" ]; then
  echo '  extracting'
  xml_dir="${DOCBOOK_DIR}/docbook-xml/${XML_VERSION}"
  rm -fr "${xml_dir}"
  mkdir -p "${xml_dir}"
  cd "${xml_dir}"
  unzip -oq "${DL_DIR}/${XML_FILE}.zip"
  cd ..
  rm -f current
  ln -s "${XML_VERSION}" current
else
  echo "error: unable to extract (${XML_FILE}.zip)" >&2
  exit 1
fi

# get the docbook xslt files
echo 'Docbook XSLT'
echo '  downloading'
cd ${DL_DIR}
get_url "${XSL_URL}"
if [ -f "${DL_DIR}/${XSL_FILE}.tar.bz2" ]; then
  echo '  extracting'
  xsl_dir="${DOCBOOK_DIR}/docbook-xsl"
  mkdir -p "${xsl_dir}"
  cd "${xsl_dir}"
  rm -fr ${XSL_VERSION}
  bzip2 -dc "${DL_DIR}/${XSL_FILE}.tar.bz2" |tar xf -
  mv ${XSL_FILE} ${XSL_VERSION}
  rm -f current
  ln -s "${XSL_VERSION}" current
else
  echo "error: unable to extract (${XSL_FILE}.tar.bz2)" >&2
  exit 1
fi
