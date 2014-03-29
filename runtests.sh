#!/bin/sh
coverage run --source=connections runtests.py --nologcapture --nocapture "$@"
result=$?
echo
coverage report -m
echo
exit $result
