#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pushd ../res/csv/ > /dev/null
find-and-replace Mum Ruth
find-and-replace "ALRRDCC" "Abi|Laith|Rachel|Ryan|David|Chris|Connie"
find-and-replace "ALRRD" "Abi|Laith|Rachel|Ryan|David"
find-and-replace "RRDCC" "Rachel|Ryan|David|Chris|Connie"
find-and-replace ALDCC "Abi|Laith|David|Chris|Connie"
find-and-replace AL "Abi|Laith"
popd > /dev/null
