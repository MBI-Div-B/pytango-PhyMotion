from .PhyMotionAxis import PhyMotionAxis
from .PhyMotionCtrl import PhyMotionCtrl


def main():
    import sys
    import tango.server

    args = ["PhyMotion"] + sys.argv[1:]
    tango.server.run((PhyMotionCtrl, PhyMotionAxis), args=args)
