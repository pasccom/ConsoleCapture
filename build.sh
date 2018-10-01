#!/bin/sh

test -d dist || mkdir dist
zip -r -FS dist/console_capture.xpi manifest.json capture_console.js
