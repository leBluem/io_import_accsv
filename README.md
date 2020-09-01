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
 - new items in "File -> Import" menu

***History***
 - v0.1 initial version
 - v0.2 fixed version typo
 - v0.3 fixed rotation of ai-line, widened csv file-filter to include ini files
 - v0.4 fixed first vertex missing in mesh when importing CSV data, added import of walls from AI-line, added export-to CSV
 - v0.5 fixed CSV export, now pointOfTrack param in csv is calculated from distance between points
 - v0.6 added export to "fast_lane.ai"; safety check ensures you only overwrite ai line with same number of points; without walls, best to load walls again after this operation, only xyz values for ideal-line will be changed
 - v0.7 fixed ai line export, it was still too closely based on original one, now takes distance btw points in account too like csv export
 - v0.8 idk if this is needed at all, i think it does not really matter, at which order the list of border-vertices is, but i did it anyway; added reverse option for CSV export, added "shiftCount" option for CSV export, so you can change which index in list of vertices is taken first, use negative values like "-151" to let its start at vertex-index "0 minus 151";  added (VERRRY slow) option to check for double vertices on CSV import
