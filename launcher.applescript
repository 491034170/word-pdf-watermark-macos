on fileExists(posixPath)
	try
		do shell script "/usr/bin/test -f " & quoted form of posixPath
		return true
	on error
		return false
	end try
end fileExists

on directoryExists(posixPath)
	try
		do shell script "/usr/bin/test -d " & quoted form of posixPath
		return true
	on error
		return false
	end try
end directoryExists

on bundledPythonScriptPath()
	try
		return POSIX path of (path to resource "word_pdf_watermark.py")
	on error
		return missing value
	end try
end bundledPythonScriptPath

on pythonScriptPath()
	set bundledPath to my bundledPythonScriptPath()
	if bundledPath is not missing value then return bundledPath
	
	set meDir to do shell script "/usr/bin/dirname " & quoted form of (POSIX path of (path to me))
	set candidate1 to meDir & "/word_pdf_watermark.py"
	if my fileExists(candidate1) then return candidate1
	
	set parentDir to do shell script "cd " & quoted form of (meDir & "/..") & " && pwd"
	set candidate2 to parentDir & "/word_pdf_watermark.py"
	if my fileExists(candidate2) then return candidate2
	
	error "无法定位 word_pdf_watermark.py"
end pythonScriptPath

on pythonLibDirPath()
	set scriptPath to my pythonScriptPath()
	set resourceDir to do shell script "/usr/bin/dirname " & quoted form of scriptPath
	set libsPath to resourceDir & "/python-libs"
	if my directoryExists(libsPath) then return libsPath
	return ""
end pythonLibDirPath

on askWatermark()
	set dialogResult to display dialog "请输入水印文字" default answer "仅供内部使用" buttons {"取消", "确定"} default button "确定"
	return text returned of dialogResult
end askWatermark

on buildCommand(droppedItems, watermarkText)
	set scriptPath to my pythonScriptPath()
	set libsPath to my pythonLibDirPath()
	
	if libsPath is not "" then
		set cmd to "PYTHONPATH=" & quoted form of (libsPath & ":${PYTHONPATH:-}")
		set cmd to cmd & space & quoted form of "/usr/bin/env" & space & quoted form of "python3"
	else
		set cmd to quoted form of "/usr/bin/env" & space & quoted form of "python3"
	end if
	
	set cmd to cmd & space & quoted form of scriptPath
	set cmd to cmd & space & "--no-ui"
	set cmd to cmd & space & "--watermark"
	set cmd to cmd & space & quoted form of watermarkText
	repeat with oneItem in droppedItems
		set cmd to cmd & space & quoted form of POSIX path of oneItem
	end repeat
	return cmd
end buildCommand

on processFiles(droppedItems)
	set watermarkText to my askWatermark()
	if watermarkText is "" then error "水印文字不能为空。"
	set resultText to do shell script my buildCommand(droppedItems, watermarkText)
	if resultText is not "" then
		display dialog "已生成以下文件：" & linefeed & resultText with title "处理完成" buttons {"好"} default button "好"
	end if
end processFiles

on run
	try
		set droppedItems to choose file with prompt "请选择 Word 或 PDF 文件" multiple selections allowed true
		my processFiles(droppedItems)
	on error errMsg number errNum
		if errNum is -128 then return
		display dialog errMsg with title "处理失败" buttons {"好"} default button "好"
	end try
end run

on open droppedItems
	try
		if (count of droppedItems) is 0 then return
		my processFiles(droppedItems)
	on error errMsg number errNum
		if errNum is -128 then return
		display dialog errMsg with title "处理失败" buttons {"好"} default button "好"
	end try
end open
