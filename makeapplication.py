### makeapplication.py
from bundlebuilder import buildapp
  
buildapp(
         name='Mapmatcher.app', # what to build
         mainprogram='src/sl/mapmatching/Mapmatcher.py', # your app's main()
         argv_emulation=1, # drag&dropped filenames show up in sys.argv
         iconfile='mapmatcher.icns', # file containing your app's icons
         standalone=1, # make this app self contained.
         includeModules=[
                         'numpy',
                         'numpy.core',
                         'numpy.core.add',
                         'numpy.absolute',
                         'numpy.arccos',
                         'numpy.arccosh',
                        'numpy.arcsin',
'numpy.arcsinh',
'numpy.arctan',
'numpy.arctanh',
'numpy.bitwise_and',
'numpy.bitwise_or',
'numpy.bitwise_xor',
'numpy.bool_',
'numpy.ceil',
'numpy.conjugate',
'numpy.core.absolute',
'numpy.core.add',
'numpy.core.bitwise_and',
'numpy.core.bitwise_or',
'numpy.core.bitwise_xor',
'numpy.core.cdouble',
'numpy.core.complexfloating',
'numpy.core.conjugate',
'numpy.core.csingle',
'numpy.core.divide',
'numpy.core.double',
'numpy.core.equal',
'numpy.core.exp',
'numpy.core.float64',
'numpy.core.float_',
'numpy.core.greater',
'numpy.core.greater_equal',
'numpy.core.inexact',
'numpy.core.intc',
'numpy.core.integer',
'numpy.core.invert',
'numpy.core.isfinite',
'numpy.core.isinf',
'numpy.core.isnan',
'numpy.core.left_shift',
'numpy.core.less',
'numpy.core.less_equal',
'numpy.core.log',
'numpy.core.maximum',
'numpy.core.multiply',
'numpy.core.not_equal',
'numpy.core.number',
'numpy.core.power',
'numpy.core.remainder',
'numpy.core.right_shift',
'numpy.core.signbit',
'numpy.core.sin',
'numpy.core.single',
'numpy.core.sqrt',
'numpy.core.subtract',
'numpy.cosh',
'numpy.divide',
'numpy.e',
'numpy.fabs',
'numpy.float_',
'numpy.floor',
'numpy.floor_divide',
'numpy.fmod',
'numpy.greater',
'numpy.hypot',
'numpy.invert',
'numpy.isinf',
'numpy.left_shift',
'numpy.less',
'numpy.log',
'numpy.logical_and',
'numpy.logical_not',
'numpy.logical_or',
'numpy.logical_xor',
'numpy.maximum',
'numpy.minimum',
'numpy.negative',
'numpy.not_equal',
'numpy.power',
'numpy.random.rand',
'numpy.random.randn',
'numpy.remainder',
'numpy.right_shift',
'numpy.sign',
'numpy.sinh',
'numpy.tan',
'numpy.tanh',
'numpy.true_divide',

                         'yaml',
                         'wx',
                         'setuptools',
                         'scipy'
                         ], # list of additional Modules to force in
         includePackages=['setuptools'
                          'networkx',
                          'numpy',
                          'osgeo',
                          'PyYAML',
                          'Shapely',
                          'RTree',
                          ], # list of additional Packages to force in
         libs=[
               '/Library/Frameworks/GDAL.framework',
               '/usr/local/include/spatialindex',
               ], # list of shared libs or Frameworks to include
         )
### end of makeapplication.py