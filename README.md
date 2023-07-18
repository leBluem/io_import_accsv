# Blender Addon to import Assetto Corsa CSV/AI files
 - screenshots: https://www.racedepartment.com/downloads/blender-addon-import-export-csv-and-ai-files.35230/

## Import/Export ai-line from "ideal_line/fast_lane/pit_lane.ai"
 - recorded with in-game AI app

## Import/Export "side_l/r/groove.csv"
 - can be generated with esotics AI-Line helper https://www.racedepartment.com/downloads/ai-line-helper.16016/

***Uses code from***
 - Author Tsuka1427 on RaceDepartment, thank you very much!
 - from this AC app https://www.racedepartment.com/threads/3d-map.148324/page-2#post-3245672

***How to install***
 - goto Blender -> Edit -> preferences -> addons
 - on the top click "Install", then browse for the downloaded zip file and click install
 - you should find it now in the Addon-list as
   "Import-Export: Import AC CSV or AI files"

***How to use***
 - new items in "File -> Import/Export" menu

***History***
 - v0.1 initial version
 - v0.2 fixed version typo
 - v0.3 fixed rotation of ai-line, widened csv file-filter to include ini files
 - v0.4 fixed first vertex missing in mesh when importing CSV data, added import of walls from AI-line, added export-to CSV
 - v0.5 fixed CSV export, now pointOfTrack param in csv is calculated from distance between points
 - v0.6 added export to "fast_lane.ai"; safety check ensures you only overwrite ai line with same number of points; without walls, best to load walls again after this operation, only xyz values for ideal-line will be changed
 - v0.7 fixed ai line export, it was still too closely based on original one, now takes distance btw points in account too like csv export
 - v0.8 idk if this is needed at all, i think it does not really matter, at which order the list of border-vertices is, but i did it anyway; added reverse option for CSV export, added "shiftCount" option for CSV export, so you can change which index in list of vertices is taken first, added (VERRRY slow) option to check for double vertices on CSV import
 - v0.9 fixed first time importing, fixed importing another ai-line after first time import, added optional import/export for the other 18 data points inside the ai-line, plain values along the normal ai-line, idk if its helpfull in any way, added some more output to blender system console
 - v1.0 added multiplier for ai-line-details if enabled, for both import+export, to make it more visible/usefull
 - v1.1 fixed ai-line export for idx!=5 and not ai line itself
 - v1.2 added option for CSV export to sort vertices by converting to curve and back to mesh
 - v1.3 fixed some error introduced by not cleanly packing up new version
 - v1.4 re-added now missing Conver2Curve and back for CSV-export
 - v1.5 fixed last point on CSV export, added option to skip connection from last2first vertex (for a2b tracks)
 - v1.6 fixed stupid version check preventing it to work on Blender 3.0; added option for exporting to CSV to skip PoT value; added importing/exporting from/to camera.ini files (plain axis empties, camera.inis must exist for export)
 - v1.7 fixed errors when importing same named stuff more than once
 - v1.8 fixed errors on CSV import
 - v1.9 fixed INI import/export (camera and overlay.ini), added option to import as mesh instead of empties; ....001/...02 will be recognized/ignored on export
 - v1.9.1 fixed not installing correctly
 - v2.0
 -- added AI line export into new/empty ai-line, afterwards you MUST
 ---either load it into "ksEditor" and save from there again or
 ---use shift on AC start with "side_l/r.csv" in place
 -- fixed incrasing distance not being saved in ai line
 -- minor fixes when exporting to cameras.ini with names like CAMERA_0.001

If you have problems, remove those folders and install again:
c:\Blender\3.1\scripts\addons\io_import_accsv\
c:\Users\yourUser\AppData\Roaming\Blender Foundation\Blender\3.1\scripts\addons\io_import_accsv\

(replace 3.1with your version of course)
