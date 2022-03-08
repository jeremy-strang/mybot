# Change Log
Changes! 

 
## [Unreleased] - 2/5/2022
 
!!!
 
### Added
- walking pather for in town
- mas + api modules for loading data from MapAssist via pythonnet c# interface
- light sorc profiles
- overlay for debugging paths and monsters
- started a new pickit, currently disabled though, something wrong with map assist coodinates vs raw mem coords 

### Changed
 
 - no more json http request, just load json from the variables exposed in c#
 - changed act 1 3 5 to use a new waypoint check based on UI menus


### Fixed
 
- pathing works pretty well in town albiet a bit quirky, the movement function is stand alone
- mapassist now only starts once not every run
- no map assist icon in task manager or window, runs hidden
- exposed more mapassist info (items)


### ToDo
 
- map assist and botty need to be updated to latest live builds... again, maybe for better item/player location + OCR stuff
- pickitv2
- replace more town pathing location and vendor actions with mem functions
- better overlay
- necro class is next to add