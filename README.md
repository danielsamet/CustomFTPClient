# CustomFTPClient
This program is a specialised FTP synchronisation program. It's intended use is to download files from a specified FTP server location whenever new files are found at the remote location (whilst not re-downloading a file if it has been moved/deleted from the local location and still at remote location). More specifically, this has been designed to download files from a seedbox for SickRage to process.


Author: Daniel Samet


To Do:
-Add data validation
-Add RegEx filter interface for allowed/blocked files
-Make Tutorial
-Add concurrent downloads settings
-Add speedlimit settings
-Find out how to securely save passwords when hashing is not possible
-Add interface for data purging

Interface:
-Add/Edit/Delete FTP server settings
-Add remote locations to watch
-Add local location to download to
-Add temp folder for downloads (so files aren't processed whilst not fully downloaded)
-SET number of files to remember for not re-downloading files if not present in local folder / date for purging 	!!! Needs attention
-SET default actions for file exist

Notes:
-'.!sync' is appended to every file until end of download session at which point all downloaded files will be iterated through to remove '.!sync'
