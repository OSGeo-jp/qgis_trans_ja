#!/bin/sh
for path in source/*.po; do
  segmented=${path%.po}-segmented.po
  posegment $path $segmented
  po2tmx -l ja $segmented tm/`basename -s .po $path`.tmx
  rm -f $segmented
done

