'''Constant definitions used by siemens_to_ismrmrd.'''

# Repackage some ISMRMRD constants to provide a consistant interface
from ismrmrd.constants import ACQ_IS_NOISE_MEASUREMENT, \
ACQ_IS_PARALLEL_CALIBRATION, ACQ_LAST_IN_MEASUREMENT, ACQ_IS_DUMMYSCAN_DATA, \
ACQ_IS_SURFACECOILCORRECTIONSCAN_DATA, ACQ_IS_HPFEEDBACK_DATA, \
ACQ_IS_RTFEEDBACK_DATA, ACQ_IS_NAVIGATION_DATA, ACQ_IS_PHASECORR_DATA, \
ACQ_IS_REVERSE, ACQ_IS_PARALLEL_CALIBRATION_AND_IMAGING, \
ACQ_LAST_IN_REPETITION, ACQ_LAST_IN_SLICE, ACQ_FIRST_IN_SLICE

# Versioning information
SIEMENS_TO_ISMRMRD_VERSION_MAJOR = 1
SIEMENS_TO_ISMRMRD_VERSION_MINOR = 0
SIEMENS_TO_ISMRMRD_VERSION_PATCH = 1

ISMRMRD_VERSION_MAJOR = 0
ISMRMRD_VERSION_MINOR = 0
ISMRMRD_VERSION_PATCH = 0

# Some masks
MDH_DMA_LENGTH_MASK = 0x01FFFFFF
MDH_ENABLE_FLAGS_MASK = 0xFC000000
MYSTERY_BYTES_EXPECTED = 160