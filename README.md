# Simplace-Python
 Run and control Simplace crop models directly from Python. This framework allows easy setup, execution, and analysis of Simplace simulations for applications in crop modelling, yield forecasting, and climate impact studies.

## For external Users - no access to simplace_run

1. Download simplace_portable_v5.1.zip
2. Unzip simplace_portable_v5.1.zip
3. Notice: you should have two folders: "eclipse" and "workspace", both should be in a common folder on the same level
   e.g. MyDocuments
        - eclipse
        - workspace
4. Go into the folder eclipse and doubleclick on eclipse.exe
5. A dialog appears, asking you for a workspace folder.
6. Please use the default "../workspace" (notice: two dots and a slash!!!)
7. After eclipse starts, it may take some time until it finishes some background tasks.
8. If it shows a Welcome window or a Donate window, you can close it.
9. On the left hand you should see the Project explorer window. The project explorer should show the
folders (projects) 
  - lapclient
  - simplace_core
  - simplace_modules
  - simplace_run
If not, you may have chosen the wrong workspace. Please restart eclipse and chose the right one.


Some additional tasks may be required:
- go to the Menu Project > Clean ... > Check [x] Clean all and click on the button Clean, - wait one or two minutes for the build to finish
- right click on simplace_core and then chose from the context menu Team > Refresh/Cleanup
- do the same for simplace_modules and lapclient
- go to all projects, right click and choose Team -> Update to HEAD

### Remote System - for connecting to HPC servers

- This package includes the Remote System plugins, so that you can connect to linux servers (e.g. Bonna or Marvin HPC)
- To connect to a server, please open the RemoteSystem view, add a connection by including host, user, pw information etc.

### Notes

- The workspace holds the source code of Simplace Version 5.1 (simplace_core, simplace_modules, lapclient)
- This package comes with eclipse 2024-03 and includes a java runtime version 17
- When running simplace inside eclipse it will use the included java runtime. If you want to run simplace outside eclipse (e.g. console, from python or R), then you need Java 17 installed on your system. (We recommend
https://adoptium.net/de/temurin/releases/?version=17).
- There is no Redmine/Mylyn-plugin for recent eclipse versions. Therefore you can't include your tickets from Redmine as a task list in eclipse. If you want to keep this feature, you have to stay with eclipse 2022-03.
