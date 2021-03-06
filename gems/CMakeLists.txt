cmake_minimum_required(VERSION 3.5)
project(gems)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})
include_directories(interfaces)

# find ITK if we're building independently of freesurfer
if(NOT ITK_FOUND)
  find_package(ITK REQUIRED)
endif()
include(${ITK_USE_FILE})

# same with zlib
if(NOT ZBLIB_FOUND)
  find_package(ZLIB REQUIRED)
endif()

option(GEMS_BUILD_SHARED_LIBS "Build GEMS with shared libraries" OFF)
option(GEMS_BUILD_EXECUTABLES "Build command line executables" OFF)
option(GEMS_BUILD_TESTING "Build tests" OFF)
option(GEMS_BUILD_GUI "Build GUI components (requires FLTK and VTK)" OFF)
option(GEMS_BUILD_MATLAB "Build Matlab wrappers" OFF)
option(GEMS_BUILD_CUDA "Build CUDA stuff" OFF)

set(GEMS_RUNTIME_PATH ${CMAKE_CURRENT_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${GEMS_RUNTIME_PATH})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${GEMS_RUNTIME_PATH})
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${GEMS_RUNTIME_PATH})

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_FLAGS "-fPIC -fpermissive -msse2 -mfpmath=sse")

add_compile_options(-Wno-inconsistent-missing-override -Wno-self-assign-field)

if(GEMS_BUILD_EXECUTABLES OR GEMS_BUILD_GUI)
  add_definitions(-DUSE_DYNAMIC_MESH)
  message(WARNING "Since you're building executables to compute meshes, ITK dynamic meshes will"
    "be used (internally using std::map instead of std::vector to store lists of points, cells, etc)."
    "Everything will still work, but anything that only uses existing meshes will be"
    "slower than it could be (up to 100% slower)"
  )    
endif()

if(GEMS_BUILD_CUDA)
  find_package(CUDA REQUIRED)
  set(CMAKE_CXX_FLAGS "-g ${CMAKE_CXX_FLAGS} -std=c++11")
  include_directories(${CUDA_INCLUDE_DIRS})
  set(CMAKE_CXX_FLAGS "-DCUDA_FOUND ${CMAKE_CXX_FLAGS}")
  include_directories(cuda)
  add_subdirectory(cuda)
endif()

# source
set(SOURCES
  gzstream.C
  itkMGHImageIO.cxx
  itkMGHImageIOFactory.cxx
  kvlAtlasMeshAlphaDrawer.cxx
  kvlAtlasMeshCollection.cxx
  kvlAtlasMeshCollectionValidator.cxx
  kvlAtlasMeshDeformationConjugateGradientOptimizer.cxx
  kvlAtlasMeshDeformationFixedStepGradientDescentOptimizer.cxx
  kvlAtlasMeshDeformationGradientDescentOptimizer.cxx
  kvlAtlasMeshDeformationLBFGSOptimizer.cxx
  kvlAtlasMeshDeformationOptimizer.cxx
  kvlAtlasMeshLabelImageStatisticsCollector.cxx
  kvlAtlasMeshMultiAlphaDrawer.cxx
  kvlAtlasMeshPositionCostAndGradientCalculator.cxx
  kvlAtlasMeshProbabilityImageStatisticsCollector.cxx
  kvlAtlasMeshRasterizor.cxx
  kvlAtlasMeshSmoother.cxx
  kvlAtlasMeshStatisticsCollector.cxx
  kvlAtlasMeshSummaryDrawer.cxx
  kvlAtlasMeshToIntensityImageCostAndGradientCalculator.cxx
  kvlAtlasMeshToLabelImageCostAndGradientCalculator.cxx
  kvlAtlasMeshToPointSetCostAndGradientCalculator.cxx
  kvlAtlasMeshVisitCounter.cxx
  kvlAtlasMeshValueDrawer.cxx
  kvlAtlasParameterEstimator.cxx
  kvlAverageAtlasMeshPositionCostAndGradientCalculator.cxx
  kvlCompressionLookupTable.cxx
  kvlConditionalGaussianEntropyCostAndGradientCalculator.cxx
  kvlCroppedImageReader.cxx
  kvlHistogrammer.cxx
  kvlMutualInformationCostAndGradientCalculator.cxx
  kvlAtlasMeshJacobianDeterminantDrawer.cxx
)

# gems libary
add_library(kvlGEMSCommon ${SOURCES})
target_link_libraries(kvlGEMSCommon ${ITK_LIBRARIES} ${ZLIB_LIBRARIES})

# build command line executables
if(GEMS_BUILD_EXECUTABLES)
  add_subdirectory(Executables)
endif()

# build tests
if(GEMS_BUILD_TESTING)
  add_subdirectory(Testing)
endif()

# build GUI
if(GEMS_BUILD_GUI)
  add_subdirectory(GUI)
endif()

# build Matlab wrappers
if(GEMS_BUILD_MATLAB)
  add_subdirectory(Matlab)
endif()
