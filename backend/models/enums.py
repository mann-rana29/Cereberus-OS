from enum import Enum

class WorkType(str, Enum):
    hot_work = "HOT_WORK"
    confined_space = "CONFINED_SPACE"
    electrical = "ELECTRICAL"
    cold_work = "COLD_WORK"
    welding = "WELDING"

class PermitStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"

class GasType(str, Enum):
    CO = "CO"
    H2S = "H2S"
    CH4 = "CH4"
    O2 = "O2"
    SO2 = "SO2"