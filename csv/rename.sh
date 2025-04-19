#!/bin/bash

old_prefix="$1"
new_prefix="$2"

if [[ -z "$old_prefix" || -z "$new_prefix" ]]; then
  echo "Usage: $0 old_prefix new_prefix"
  exit 1
fi

for file in ${old_prefix}*; do
  new_name="${file/$old_prefix/$new_prefix}"
  mv "$file" "$new_name"
done
