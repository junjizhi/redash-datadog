#! /bin/bash

# script source: https://exchange.nagios.org/directory/Plugins/Operating-Systems/Linux/check_proc_age-2Esh/details

# Nagios plugin
# created 09.01.2011 by symphonic.mushroom@gmail.com
# modified 04.24.2012 by symphonic.mushroom@gmail.com with the advices from formwandler
# check if processes matching to a pattern are exceeding a given elapsed time
# return a Nagios exit code depending on the result
# 0 = OK
# 1 = WARNING
# 2 = CRITICAL
# 3 = UNKNOWN


#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


# for help printing
print_help() {
	echo "This Nagios plugin check if processes matching to a pattern are exceeding a given elapsed time"
	echo "Usage : $0 -p <process_name> -w <seconds> -c <seconds> "
	echo " -p parameter : name of the monitoring process"
	echo " -c parameter : minimal elapsed time for status CRITICAL on NAGIOS"
	echo " -w parameter : minimal elapsed time for status WARNING on NAGIOS"
	exit 3
}

# check if there is at least one argument
if [ -z $1 ]
	then echo "Missing arguments"
	echo "try \'$0 --help\' for help"
    	exit 3
fi

# print help
if [[ ( $1 = "--help" || $1 = "-h" ) ]]
	then print_help
	exit 3
fi

# assign value to arguments
# print an error in case of unkown argument
while getopts ":w:c:p:" options
do
    case $options in
        w ) warning=$OPTARG ;;
        c ) critical=$OPTARG ;;
	p ) proc=$OPTARG ;;
        * ) echo "Unknown argument"
	echo "try \'$0 --help\' for help"
    	exit 3 ;;
    esac
done

# check if all arguments are present
if [[ ( -z $warning || -z $critical || -z $proc ) ]]
	then echo "Missing argument"
	echo "try \'$0 --help\' for help"
    	exit 3
fi

#calculate number of process
nbproc=$(ps -A -o comm | grep -w $proc | grep -v $0 | wc -l)
if [ $nbproc -gt 0 ]
	then

#calculate age of oldest process
	ageproc=$(ps -A -o etime,comm,args | grep $proc | grep -v $0 | gawk '{split($1,t,":");split(t[1],td,"-");if (td[2]) {ta=td[1]*86400; t[1]=td[2]} else {ta=0}; if (t[3]) {$1=(t[1]*60+t[2])*60+t[3]+ta} else {$1=t[1]*60+t[2]};if (NR==1) {maxi=$1;} else {if ($1>maxi){maxi=$1;}}};END {print maxi}')
	case $ageproc in
        	?|[0-5]? ) maxage=$ageproc" Seconds";;
		??|???|[0-2]???|3[0-5]?? ) maxage=$(($ageproc/60))" Minutes";;
		* ) maxage=$(($ageproc/3600))" Hours "$(($ageproc % 3600 / 60))" minutes";;
	esac
	 msg="$nbproc:$ageproc"
		if [ $ageproc -gt $critical ]
			then echo "CRITICAL:"$msg
			exit 2
		elif [ $ageproc -gt $warning ]
			then echo "WARNING:"$msg
			exit 1
		else echo "OK:"$msg
		exit 0
		fi
	else
	echo "NO_PROC:0:0"
	exit 0
fi

