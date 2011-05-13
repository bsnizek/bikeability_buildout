### makeapplication.py
from bundlebuilder import buildapp
  
buildapp(
         name='MapMmtcher.app', # what to build
         mainprogram='src/sl/mapmatching/Mapmatcher.py', # your app's main()
         argv_emulation=1, # drag&dropped filenames show up in sys.argv
         # iconfile='myapp.icns', # file containing your app's icons
         standalone=1, # make this app self contained.
         includeModules=[], # list of additional Modules to force in
         includePackages=[
                          'PyYAML',
                          'Shapely',
                          'RTree',
                          ], # list of additional Packages to force in
         libs=[
               'spatialindex',
               ], # list of shared libs or Frameworks to include
         )
### end of makeapplication.py