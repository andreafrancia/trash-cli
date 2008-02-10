# $Id: test-functions.inc 416 2007-01-04 00:50:14Z sfsetse $
# vim:syntax=sh:sts=2

#
# constants
#

# configure debugging. set the DEBUG environment variable to any
# non-empty value to enable debug output, or TRACE to enable trace
# output.
TRACE=${TRACE:+'tf_trace '}
[ -n "${TRACE}" ] && DEBUG=1
[ -z "${TRACE}" ] && TRACE=':'

DEBUG=${DEBUG:+'tf_debug '}
[ -z "${DEBUG}" ] && DEBUG=':'

#
# variables
#

tf_RANDOM=0

#
# functions
#

# message functions
tf_trace() { echo "${MY_NAME}:TRACE $@" >&2; }
tf_debug() { echo "${MY_NAME}:DEBUG $@" >&2; }
tf_info() { echo "${MY_NAME}:INFO $@" >&2; }
tf_warn() { echo "${MY_NAME}:WARN $@" >&2; }
tf_error() { echo "${MY_NAME}:ERROR $@" >&2; }
tf_fatal() { echo "${MY_NAME}:FATAL $@" >&2; }

# generate a random number
tf_generateRandom()
{
  tfgr_random=${tf_RANDOM}

  while [ "${tfgr_random}" = "${tf_RANDOM}" ]; do
    if [ -n "${RANDOM:-}" ]; then
      # $RANDOM works
      tfgr_random=${RANDOM}${RANDOM}${RANDOM}$$
    elif [ -r '/dev/urandom' ]; then
      tfgr_random=`od -vAn -N4 -tu4 </dev/urandom |sed 's/^[^0-9]*//'`
    else
      tfgr_date=`date '+%H%M%S'`
      tfgr_random=`expr ${tfgr_date} \* $$`
      unset tfgr_date
    fi
    [ "${tfgr_random}" = "${tf_RANDOM}" ] && sleep 1
  done

  tf_RANDOM=${tfgr_random}
  unset tfgr_random
}

# this section returns the data section from the specified section of a file. a
# datasection is defined by a [header], one or more lines of data, and then a
# blank line.
tf_getDataSect()
{
  tf_sgrep "\\[$1\\]" "$2" |sed '1d'
}

# this function greps a section from a file. a section is defined as a group of
# lines preceeded and followed by blank lines.
tf_sgrep()
{
  tf_pattern=$1
  shift

  sed -e '/./{H;$!d;}' -e "x;/${tf_pattern}/"'!d;' $@ |sed '1d'

  unset tf_pattern
}

#
# main
#

${TRACE} 'trace output enabled'
${DEBUG} 'debug output enabled'
