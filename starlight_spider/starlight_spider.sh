#!/usr/bin/env bash

set -x

LOG='log.txt'
HOST='https://www.example.com'

USER_AGENT='Mozilla/5.0 (compatible; starlightbot/0.1; +http://www.example.com/bot.html)'

if [ `which lynx` = '' ]; then
    echo 'ERROR: You need to install lynx!'
    exit 1
fi

get_url() {
    #if [ -z ${1} ]; then return; fi
    
    # уже были на такой странице
    grep "${1};" ${LOG} > /dev/null
    if [[ $? -eq 0 ]]; then
        echo "ignore ${1}"
        return
    fi
    
    headers=`lynx -useragent="${USER_AGENT}" -dump -head ${1} 2> /dev/null`
    if [[ $? -eq 0 && ${headers} =~ 'Content-Type: text/html' ]]; then
        r=`lynx -useragent="${USER_AGENT}" -dump -listonly ${1} 2> /dev/null`
        if [ -z ${r} ]; then  # todo
            sleep 0.5
            r=`lynx -useragent="${USER_AGENT}" -dump -listonly ${1} 2> /dev/null`
        fi
        for i in ${r}; do
            if [[ ${i} =~ 'http' ]]; then
                echo "${1};${i}"
                echo "${1};${i}" >> ${LOG}
                if [[ ${i} =~ ${HOST} ]]; then
                    get_url ${i}
                fi
            fi
        done
    else
        echo "fail head ${1}"
    fi
}

get_url ${HOST}
