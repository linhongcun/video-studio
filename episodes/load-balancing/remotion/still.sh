#!/bin/bash
# render all Still compositions in Root.tsx
for id in $(rg --no-filename -o 'id="([A-Za-z0-9-]+)"' -r '$1' src/Root.tsx); do npx remotion still src/index.ts $id stills/$id.png --log=error >/tmp/still-$id.log 2>&1 && echo ok $id || { echo FAIL $id; tail -5 /tmp/still-$id.log; }; done
