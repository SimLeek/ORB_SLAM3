"""
usage: calslam cal [options] [--]

    -w CHESS_WIDTH --chess_width=CHESS_WIDTH        Number of columns on the chessboard [default: 8]
    -h CHESS_HEIGHT --chess_height=CHESS_HEIGHT     Number of rows on the chessboard [default: 8]
    -i REQ_IMAGES --required_images=REQ_IMAGES      Required number of valid images to use for calibration [default: 7]
    -o FILE, --output=FILE                          Calibration output filename
    -c CAM, --camera=CAM                            Number or filename representing a camera or video [default: 0]
    -u UID, --uid=UID                               A unique identifier to represent this camera
    -v, --visualize                                 Creates a window showing the calibration algorithm.
    -q, --quiet                                     Stops the output from filling up the command window.
    -h, --help
"""

# todo:  on linux, use camera uid info if None default is detected
# todo: make min ROI size and max error arguments with defaults
import numpy as np
from displayarray import display, read_updates
import cv2 as cv
import pickle
from docopt import docopt
from pathlib import Path
import os
import warnings
import get_ffmpeg_cam_details as cam_info


class CalibrationSetup(object):

    def __init__(self, cw, ch):
        self.criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        # (an actual chessboard would be 7 by 7)
        self.cw = cw - 1
        self.ch = ch - 1

        self.objp = np.zeros((self.cw * self.ch, 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:self.cw, 0:self.ch].T.reshape(-1, 2)


class CalibrationOutput(object):
    def __init__(self):
        # store the camera resolution we're calibrating for
        # other resolutions may assume that they're just scaled, but this may not be the case,
        # especially for different aspect ratios
        self.w = None
        self.h = None

        self.camera = None
        self.uid = None

        # Arrays to store object points and image points from all the images.
        self.objpoints = []  # 3d point in real world space
        self.imgpoints = []  # 2d points in image plane.

        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = [None] * 5
        self.newcameramtx, self.roi = None, None
        self.mapx, self.mapy = None, None

        self.fov_x, self.fov_y, self.focal_len, self.principle_pt, self.aspect_ratio = [None] * 5

        self.roi_size = 0
        self.mean_error = float('inf')


class MultiResCalibrationOutput(object):
    def __init__(self):
        self.calibration_dict = dict()


def calibrate(c, resolutions, chess_w, chess_h, num_required_images, fname, u=None, visualize=False, quiet=False):
    arr = None
    displayer = None

    cs = CalibrationSetup(chess_w, chess_h)
    mco = MultiResCalibrationOutput()

    try:
        c = int(c)
    except ValueError as e:
        pass

    if u:
        cu = u
    else:
        cu = c

    print(f"Calibrating camera {cu} for resolutions:")
    int_resolutions = []
    for r in resolutions:
        int_resolutions.append((int(r[0]), int(r[1])))
        print(f"\t{r[0]}x{r[1]}")

    if visualize:
        displayer = display()
    for r in int_resolutions:
        co = CalibrationOutput()

        co.camera = c
        if u is None:
            co.uid = ''
        else:
            co.uid = u

        calibrated = False

        out_image_path = Path(f"./calibration_images_cam_{cu}")

        out_image_path.mkdir(parents=True, exist_ok=True)

        if displayer.exited:
            displayer = display()

        #prev_rup = None
        rupd = read_updates(c, size=(r[0], r[1]))
        for rup in rupd:
            if rup and (arr is None or arr.shape != rup['0'][0].shape):
                arr = np.zeros_like(rup['0'][0])
                #prev_rup = np.zeros_like(rup['0'][0])
                print(f"Started calibrating for resolution {r[0]}x{r[1]}. Please move chessboard into view.")
            if rup and arr is not None:
                #if np.all(prev_rup == rup['0'][0]):
                #    continue
                #else:
                arr[:] = rup['0'][0]
                #    prev_rup[:] = rup['0'][0]

                if not calibrated:
                    gray = cv.cvtColor(rup['0'][0], cv.COLOR_BGR2GRAY)
                    ret, corners = cv.findChessboardCorners(gray, (cs.cw, cs.ch), None)

                    if ret:
                        print("Chessboard found!", end=' ')
                        co.objpoints.append(cs.objp)
                        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), cs.criteria)
                        co.imgpoints.append(corners)
                        if visualize:
                            # Draw and display the corners
                            cv.drawChessboardCorners(arr, (cs.cw, cs.ch), corners2, ret)

                        co.ret, co.mtx, co.dist, co.rvecs, co.tvecs = \
                            cv.calibrateCamera(co.objpoints, co.imgpoints, gray.shape[::-1], None, None)
                        co.h, co.w = arr.shape[:2]
                        co.newcameramtx, co.roi = \
                            cv.getOptimalNewCameraMatrix(co.mtx, co.dist, (co.w, co.h), 1, (co.w, co.h))

                        # since we don't give camera aperture size, focal len is in pixels. it's also f_x.
                        co.fov_x, co.fov_y, co.focal_len, co.principle_pt, co.aspect_ratio = \
                            cv.calibrationMatrixValues(co.mtx, gray.shape[::-1], 0, 0)

                        x, y, w_new, h_new = co.roi

                        if w_new * h_new > co.roi_size or (w_new > co.w * .9 and h_new > co.h * .9):
                            print("Valid roi size.", end=' ')
                            co.roi_size = w_new * h_new

                            total_error = 0
                            for i in range(len(co.objpoints)):
                                imgpoints2, _ = cv.projectPoints(co.objpoints[i], co.rvecs[i], co.tvecs[i], co.mtx,
                                                                 co.dist)
                                error = cv.norm(co.imgpoints[i], imgpoints2, cv.NORM_L2) / len(imgpoints2)
                                total_error += error
                            mean_error = total_error / len(co.objpoints)

                            if mean_error < .1:
                                print("Valid error.")
                                co.mean_error = mean_error
                                print(
                                    f"Adding calibration frame. Mean error: [{mean_error}]. Num frames: [{len(co.objpoints)}/{num_required_images}]")

                                cv.imwrite(
                                    str(out_image_path.absolute()) + os.sep + f"cam_{cu}_{r[0]}x{r[1]}_cal_{len(co.objpoints)}.jpg",
                                    rup['0'][0])

                                if len(co.objpoints) >= num_required_images:
                                    # set undistort
                                    co.mapx, co.mapy = cv.initUndistortRectifyMap(co.mtx, co.dist, None,
                                                                                  co.newcameramtx,
                                                                                  (co.w, co.h), 5)

                                    calibrated = True
                                    # save here
                                    mco.calibration_dict[r] = co

                                    if visualize:
                                        print("calibration complete. Press escape to quit.")
                                    else:
                                        print("calibration complete.")
                            else:
                                print("Error to large.", end='\r')
                                co.objpoints.pop()
                                co.imgpoints.pop()
                        else:
                            print("ROI too small.", end='\r')
                            co.objpoints.pop()
                            co.imgpoints.pop()
                    else:
                        print("Chessboard not found.", end='\r')
                else:
                    if visualize:
                        x, y, w, h = co.roi
                        dst = cv.remap(rup['0'][0], co.mapx, co.mapy, cv.INTER_LINEAR)
                        arr[:] = dst

                        start_point = (x, y)
                        end_point = (x + w, y + h)
                        color = (255, 0, 0)
                        thickness = 2
                        arr[:] = cv.rectangle(arr, start_point, end_point, color, thickness)
                    else:
                        break

                if displayer is not None:
                    if displayer.exited:
                        displayer.end()
                        break
                    else:
                        displayer.update(arr, 'output')
        rupd.end()
        del rupd
    displayer.end()
    with open(fname, 'wb') as f:
        pickle.dump(mco, f)


def main(argv=None):
    args = docopt(__doc__, argv=argv)
    resos = cam_info.get_ffmpeg_cam_details()

    c = args['--camera']
    u = args['--uid']
    u, c = cam_info.handle_uid_vs_cam(u, c, resos=resos)

    cw = int(args['--chess_width'])
    ch = int(args['--chess_height'])
    ri = int(args['--required_images'])
    fname = args['--output']
    if fname is None:
        if u is None:
            fname = f"calibration_output_cam_{c}"
        else:
            fname = f"calibration_output_cam_{u}"
    visualize = args['--visualize']
    quiet = args['--quiet']

    resolutions = cam_info.get_opencv_options(resos)
    try:
        resolutions = resolutions[c]
    except KeyError:
        resolutions = list(resolutions.values())[0]

    calibrate(c, resolutions, cw, ch, ri, fname, u, visualize, quiet)


if __name__ == '__main__':
    main()
