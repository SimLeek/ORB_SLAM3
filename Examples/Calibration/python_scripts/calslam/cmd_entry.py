"""
usage: calslam [--version] <command> [<args>...]

common commands are:
    cal       Calibrate the camera using a chessboard
    odom      Visual Odometry
    cam_info  Get camera info
see 'calslam help <command>' for more information on a specific command.
"""
import sys

from docopt import docopt


def main():
    argv = sys.argv[1:]
    argv1 = argv
    argv2 = None
    # preprocess to remove args after command.
    # Even thought docopt has an "options_first" command, it isn't set up to use the options available in a separate
    # file, or ignore invalid options (in the context of this file), so we need to remove those.
    split_pos = -1
    for i, a in enumerate(argv):
        if a in ['cal', 'odom']:
            split_pos = i
    if split_pos != -1:
        argv1 = argv[:split_pos+1]
        argv2 = argv[split_pos:]

    args = docopt(__doc__,
                  version='calslam version 0.1.0',
                  options_first=True,
                  argv=argv1)

    print('global arguments:')
    print(args)

    print('command arguments:')

    com = args['<command>']
    #argv = [args['<command>']] + args['<args>']
    print(argv2)

    if com == 'cal':
        import camera_calibration
        camera_calibration.main(argv2)
    elif com == 'odom':
        import visual_odometry
        visual_odometry.main(argv2)
    elif com == 'cam_info':
        import get_ffmpeg_cam_details
        get_ffmpeg_cam_details.main(argv2)

    if com == 'help':
        pass


if __name__ == '__main__':
    main()
