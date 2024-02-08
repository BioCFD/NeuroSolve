#!/bin/bash

start_time="$(date -u +%s)"
##remove any spaces in files name 
for f in *\ *; do mv "$f" "${f// /_}"; done

##Find the STL file NAME 
myarray=(`find ./ -maxdepth 1 -name "*.stl"`)
if [ ${#myarray[@]} -gt 0 ]; then 
    echo true 
    echo $myarray
else 
    echo false
fi
stlfile=$(echo "${myarray#./}")

## copy parameters file
cp -r ../../case_templates/parameters.json .
##changing stl file name in parameters file 
sed -i "s/stl_name/$stlfile/g" parameters.json

echo $'\n\tNeuroCFD\n'

echo $'\n\tOpenFOAMv2012\n'
. /usr/lib/openfoam/openfoam2012/etc/bashrc

# change to . ../NeroFoam/etc/bashrc
. ../../etc/bashrc


#run main
runNeuroCFD parameters.json  --meshOnly 
runNeuroCFD parameters.json  --solverOnly

end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"
echo "Total of $elapsed seconds elapsed for process"
