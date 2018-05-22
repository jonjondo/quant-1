#!/bin/bash
for files in `ls *[1-4].csv`
do
    # 截取文件的前八个字符
	#echo $fname,$1
	# 截取文件的后四个字符
    bname=${files:0-10}
	if [[ ${files:0:8} == $1 ]];then
    # 拼接成文件名
		filename=$2$bname
		# 更改文件名
		echo "mv" $files $filename ${#bname}
		#mv $files $filename
	fi
done