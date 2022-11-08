"""
usage: calslam odom [options] [--]

    -w WIDTH --width=WIDTH                              Desired resolution width of the camera [default: 99999]
    -h HEIGHT --height=HEIGHT                           Desired resolution height of the camera [default: 99999]
    -c CAM, --camera=CAM                                Number or filename representing a camera or video [default: 0]
    -os OUTPUT_STREAM --output_stream=OUTPUT_STREAM     Output stream and channel for publishing on ZMQ [default: idfk]
    -cf CAL_FILE, --calibration_file=CAL_FILE           Camera calibration file.
    -v, --visualize                                     Creates a window showing the odometry algorithm.
    -vb, --verbose                                      Prints odometry velocity to the command line.
    -h, --help
"""
import sys

from docopt import docopt
import pickle
import camera_calibration as cc
from displayarray import display, read_updates
import numpy as np
import cv2 as cv
from copy import deepcopy, copy

def get_match_points(matches, kp_a, kp_b):
    a = []
    b = []
    for m in matches:
        a_idx = m.queryIdx
        b_idx = m.trainIdx

        a.append(list(kp_a[a_idx].pt))
        b.append(list(kp_b[b_idx].pt))

    return np.asarray(a), np.asarray(b)

# optimize, sorted by priority:
#  cam width and height (set up for multi-resolution. res switching takes to long, so should be manual, but available.)
#   get all available resolutions
#   change calibration to run for all resolutions
#   set up res switching by zmq pubsub
#  adaptive tune brisk setThreshold and setOctaves for >15fps and >10 matches
# adaptive tune kp limits for >15fps and >10 matches (num_pass)
#  response, size, octave, min no of keypoints
# parameter optimization, optimize for reliability and fps
# cam width and height

# brisk threshold (setThreshold)
# brisk octaves (setOctaves)
# sort keypoints by response and limit: sorted(kpnew, key=lambda  x: -x.response)
# sort keypoints by size or limit to min size (if there are enough keypoints otherwise)
# sort keypoints by octave and limit (if there are enough keypoints otherwise)
# determine usefulness by mask2 percent 1 or 0, or num_pass
# determine usefulness by distance from instant IMU prediction. below certain dist/error may mean 0 nn train
# findEssentialMat prob, threshold, maxIters

#  auto set default kp useful distance based on size (create multiplier value for default)
#  limit kpnew pt location based on rotation and what would be visible to a keyframe. potentially compare to 2 keyframes
#  don't use keypoints at all if they're >50% over useful distance
#  create/switch key frame if rot>=45 or if >=50% of usually useful keypoints are no longer useful for multiple frames (or >=90%)
#  record useful distance for key points. boost/decay less if outside of useful distance
#  use provided keypoints from key frame: https://stackoverflow.com/a/19594439
#  make new keygrame if too few keypoint matches
#  boost/decay keypoints from keyframe depending on if nearby poses can match it
#  kp angle difference could be used by itself vs keyframe keypoints to determine camera roll


def odometry(c, w, h, co, os, visualize, quiet):
    arr = None
    prev_arr = None
    displayer = None
    out_arr = None

    sift = cv.BRISK_create(75)
    bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)

    kpold, desold = None, None

    try:
        c = int(c)
    except Exception as e:
        pass

    for r in read_updates(c, size=(w, h)):
        if r and arr is None:
            arr = np.zeros_like(r['0'][0])
            prev_arr = np.zeros_like(r['0'][0])
            if visualize:
                displayer = display(arr)
        if arr is not None:
            arr[:] = r['0'][0]
            kpnew, desnew = sift.detectAndCompute(arr, None)

            # Matching descriptor vectors using Brute Force Matcher
            if desold is not None:
                matches = bf.match(queryDescriptors=desnew, trainDescriptors=desold)

                #matches = matches[:100]  # clip for processing speed

                #matches = sorted(matches, key=lambda x: x.distance)

                a, b = get_match_points(matches, kpnew, kpold)

                if a.size:
                    essential_matrix, mask = cv.findEssentialMat(a, b, co.mtx, cv.FM_RANSAC, 0.99, 3)
                else:
                    continue # no points, nothing to do
                mask2 = deepcopy(mask)
                try:
                    num_pass, rot, t, mask2 = cv.recoverPose(essential_matrix, a, b, co.mtx, mask=mask2)
                except cv.error as e:
                    continue
                # todo: mask1 and mask2 may be used to find objects in scene that are moving.
                #  then findHomography on image sections, solvePnPRansac, or other methods may be used to detect moving
                #  objects
                for i, m in enumerate(mask2[:, 0]):
                    if m:
                        cv.circle(arr, tuple(a[i].astype(int)), 5, (0,0,255))
                        cv.circle(arr, tuple(b[i].astype(int)), 5, (0, 255, 255))
                        cv.line(arr, tuple(a[i].astype(int)), tuple(b[i].astype(int)), (0,127,255))


                print(num_pass, rot, t)





            kpold, desold = copy(kpnew), deepcopy(desnew)

            prev_arr[:] = r['0'][0]

        if displayer is not None:
            if displayer.exited:
                displayer.end()
                break
            else:
                displayer.update_frames()


def main(argv=None):
    args = docopt(__doc__, argv=argv)

    w = int(args['--width'])
    h = int(args['--height'])
    c = args['--camera']
    cf = args['--calibration_file']
    if cf is None:
        print("Calibration file is required.", file=sys.stderr)
        raise SystemExit(-1)
    else:
        with open(cf, 'rb') as f:
            cal_file: cc.CalibrationOutput = pickle.load(f)
    os = args['--output_stream']
    #if os is None:
    #    fname = f"calibration_output_cam_{c}_{u}"
    visualize = args['--visualize']
    quiet = args['--verbose']

    odometry(c, w, h, cal_file, os, visualize, quiet)


if __name__ == '__main__':
    main()
