"""
usage: calslam db [options] [--]

    -w CAM_WIDTH --cam_width=CAM_WIDTH              Requested camera width
    -h CAM_HEIGHT --cam_height=CAM_HEIGHT           Requested camera height
    -i CAL_FILE --input=CAL_FILE                    Override calibration database file to read from.
    -r --resolutions                                Output the available camera resolutions in the database.
    -f FORMAT, --format=FORMAT                      output format. [default: json]
    -c CAM, --camera=CAM                            Number or filename representing a camera or video [default: 0]
    -u UID, --uid=UID                               A unique identifier to represent this camera
    -h, --help
"""


import pathlib
import sys

import numpy as np
from displayarray import display, read_updates
import cv2 as cv
import pickle
from docopt import docopt
from pathlib import Path
import os
import warnings
import get_ffmpeg_cam_details as cam_info
from camera_calibration import MultiResCalibrationOutput, CalibrationOutput

fdir = pathlib.Path(__file__).parent.resolve()


def print_resolutions(mco):
    print("available resolutions for database are:")
    for k in mco.calibration_dict.keys():
        print(f"\t{k[0]} x {k[1]}")
    exit(0)

def main(argv=None):
    args = docopt(__doc__, argv=argv)
    resos = cam_info.get_ffmpeg_cam_details()


    c = args['--camera']
    u = args['--uid']
    u, c = cam_info.handle_uid_vs_cam(u, c, resos=resos)
    our_cam_details = None
    for k, v in resos.items():
        if len(v)==0:
            continue
        if v[0] == c:
            our_cam_details = v
    if our_cam_details is None:
        our_cam_details = list(resos.values())[c]

    iname = args['--input']
    format = args['--format']
    if iname is None:
        if u is None:
            iname = str(fdir) + os.sep + f"calibration_output_cam_{c}"
        else:
            iname = str(fdir) + os.sep + f"calibration_output_cam_{u}"

    if u not in iname:
        print(f"Warning, camera UID does not match calibration database.", file=sys.stderr)

    try:
        with open(iname, 'rb') as f:
            mco: MultiResCalibrationOutput = pickle.load(f)
    except FileNotFoundError as fe:
        print("Calibration database file does not exist for given camera. Perhaps create one?", file=sys.stderr)
        raise fe


    r = args['--resolutions']
    if r:
        print_resolutions(mco)

    try:
        cw = int(args['--cam_width'])
        ch = int(args['--cam_height'])
    except TypeError:
        raise ValueError("Camera width and height must be entered as an integer")

    our_cam_details_2 = []
    for ocd in our_cam_details:
        if isinstance(ocd, str):
            continue
        if int(ocd['min_w'])==cw and int(ocd['min_h'])==ch:
            our_cam_details_2.append(ocd)

    if len(our_cam_details_2)==0:
        warnings.warn("Camera does not support requested resolution.")
        warnings.warn("Defaulting to 30fps since camera settings for resolution weren't found.")
        best_fps = 30
    else:
        best_fps = 0
        for ocd2 in our_cam_details_2:
            if 'min_fps' in ocd2.keys() and float(ocd2['min_fps'])>best_fps:
                best_fps = float(ocd2['min_fps'])

    request_res = (cw, ch)
    if request_res not in mco.calibration_dict.keys():
        print(f"Requested resolution [{cw},{ch}] for camera [{c},{u}] isn't in calibration file [{iname}].", file=sys.stderr)
        print_resolutions(mco)
    else:
        val: CalibrationOutput = mco.calibration_dict[request_res]
        print("Camera calibration for resolution...")
        #print("Camera ID: " + c)
        #print("Camera UID: " + u)
        #print("Camera Resolution: " + r)
        print('Camera.type: "PinHole"')
        print("")
        print(f"Camera.fx: {val.mtx[0,0]}")
        print(f"Camera.fy: {val.mtx[1,1]}")
        print(f"Camera.cx: {val.mtx[0,2]}")
        print(f"Camera.cy: {val.mtx[1,2]}")
        print("")
        print(f"Camera.k1: {val.dist[0,0]}")
        print(f"Camera.k2: {val.dist[0,1]}")
        print(f"Camera.p1: {val.dist[0,2]}")
        print(f"Camera.p2: {val.dist[0,3]}")
        print(f"Camera.k3: {val.dist[0,4]}")
        print("")
        print("Camera.bFishEye: 0")
        print("")
        print(f"Camera.width: {cw}")
        print(f"Camera.height: {ch}")
        print("")
        print(f"Camera.fps: {best_fps}")
        print("")
        print("# Color order of the images (0: BGR, 1: RGB. It is ignored if images are grayscale)")
        print("Camera.RGB: 0")


if __name__ == "__main__":
    main()