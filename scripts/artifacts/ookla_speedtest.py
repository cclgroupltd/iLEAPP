import glob
import os
import pathlib
import plistlib
import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows 


def get_safariHistory(files_found, report_folder, seeker):
	file_found = str(files_found[0])
	db = sqlite3.connect(file_found)
	cursor = db.cursor()

	cursor.execute(
	"""
	SELECT
		DATETIME(HISTORY_VISITS.VISIT_TIME+978307200,'UNIXEPOCH') AS "VISIT TIME",
		HISTORY_ITEMS.URL AS "URL",
		HISTORY_ITEMS.VISIT_COUNT AS "VISIT COUNT",
		HISTORY_VISITS.TITLE AS "TITLE",
		CASE HISTORY_VISITS.ORIGIN
			WHEN 1 THEN "ICLOUD SYNCED DEVICE"
			WHEN 0 THEN "VISITED FROM THIS DEVICE"
			ELSE HISTORY_VISITS.ORIGIN
		END "ICLOUD SYNC",
		HISTORY_VISITS.LOAD_SUCCESSFUL AS "LOAD SUCCESSFUL",
		HISTORY_VISITS.id AS "VISIT ID",
		HISTORY_VISITS.REDIRECT_SOURCE AS "REDIRECT SOURCE",
		HISTORY_VISITS.REDIRECT_DESTINATION AS "REDIRECT DESTINATION",
		HISTORY_VISITS.ID AS "HISTORY ITEM ID"
	FROM HISTORY_ITEMS
	LEFT OUTER JOIN HISTORY_VISITS ON HISTORY_ITEMS.ID == HISTORY_VISITS.HISTORY_ITEM
	"""
	)

	all_rows = cursor.fetchall()
	usageentries = len(all_rows)
	data_list = []    
	if usageentries > 0:
		for row in all_rows:
			data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
	
		description = ''
		report = ArtifactHtmlReport('Ookla Speedtest')
		report.start_artifact_report(report_folder, 'Ookla Speedtest', description)
		report.add_script()
		data_headers = ('Date','External IP Address','Carrier Name','Device Model','Internal IP Address','ISP','WAN Type','WIFI SSID' )     
		report.write_artifact_data_table(data_headers, data_list, file_found)
		report.end_artifact_report()
		
		tsvname = 'Ookla Speedtest History'
		tsv(report_folder, data_headers, data_list, tsvname)
	else:
		logfunc('No data available in table')
	
	db.close()
	return 
	
