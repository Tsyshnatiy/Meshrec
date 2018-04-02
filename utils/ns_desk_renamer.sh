#!/bin/bash

root=$1
echo $root

echo $root/validation/table
find $root/validation/table -name "night*" | xargs rename s/night_stand/table_n/
find $root/validation/table -name "desk*" | xargs rename s/desk/table_d/

echo $root/test/table
find $root/test/table -name "desk*" | xargs rename s/desk/table_d/

echo $root/validation/dresser
find $root/validation/dresser -name "night*" | xargs rename s/night_stand/dresser_n/

echo $root/test/dresser
find $root/test/dresser -name "night*" | xargs rename s/night_stand/dresser_n/

echo $root/train/table
find $root/train/table -name "night*" | xargs rename s/night_stand/table_n/
