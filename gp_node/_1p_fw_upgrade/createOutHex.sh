if [-n "$1"] ; then
  PROGRAMMER="$1"
else 
  PROGRAMMER="/dev/ttyACM0"
fi

rm maxwell_household_meter.txt
rm out.txt
cp ~/grampower/node_fw/projects/maxwell_household_meter/Debug_f6733/maxwell_household_meter.txt  maxwell_household_meter.txt
python make_image.py maxwell_household_meter.txt --bsl_file node_bsl.txt
mspdebug tilib -d /dev/ttyACM* --allow-fw-update "opt enable_bsl_access true" "erase all" "prog out.txt"

