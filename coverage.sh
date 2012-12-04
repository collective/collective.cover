#! /bin/sh
# checks for report created with createzopecoverage and evaluate the result

# default minimum coverage is 80%
DEFAULT=80
REPORT="coverage/reports/all.html"

if [ "$1" -ge 0 ] && [ "$1" -le 100 ]; then
    MINIMUM=$1
else
    echo "Invalid value for minimum coverage; using default: $DEFAULT%"
    MINIMUM=$DEFAULT
fi

if [ ! -f "$REPORT" ]; then
    bin/createzopecoverage 1>/dev/null
fi

# find first percentage value in file (module test coverage) and return it
COVERAGE=`grep "[0-9]\{1,3\}[%]" ${REPORT} -m 1 -o | grep "[0-9]\{1,3\}" -o`

if [ $COVERAGE -lt $MINIMUM ]; then
    echo "Insufficient test coverage: $COVERAGE% (minimum acceptable is $MINIMUM%)"
    exit 1
else
    exit 0
fi
