"""
usage: calslam cam_info [options] [--]

    -c CAM, --camera=CAM                                Only get info for specific camera if specified
    -u UID, --uid=UID                                   Get info for specific UID only if specified
    -d, --get_uids                                     Get opencv pin to camera uid table
    -o, --get_options                                  Get resolution options per pin
    -l, --get_long_names                               Get camera info used for UID hashes
    -h, --help
"""

import subprocess as sp
import hashlib
import sys

from docopt import docopt
import warnings


def get_ffmpeg_cam_details():
    command = "ffmpeg -list_devices true -f dshow -i dummy -hide_banner".split(' ')

    pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, bufsize=10 ** 8)
    names = []
    while pipe.poll() is None:
        data = pipe.stderr.read().decode()
        line_data = data.splitlines()
        for l in line_data:
            name_pos = l.find('] "')
            alt_name_pos = l.find(']   Alternative name "')
            if name_pos != -1:
                name_full = l[name_pos + 3:]
                name_end = name_full.find('"')
                if name_end != -1:
                    name_full = name_full[:name_end]
                    names.append(name_full)
                else:
                    continue
            elif alt_name_pos != -1:
                name_full = l[alt_name_pos + 22:]
                name_end = name_full.find('"')
                if name_end != -1:
                    name_full = name_full[:name_end]
                    names[-1] = (names[-1], name_full)
                else:
                    continue
            else:
                continue

    resos = dict()
    for name in names:
        if isinstance(name, tuple):
            n = name[0]
        else:
            n = name
        command = ['ffmpeg', '-list_options', 'true', '-f', 'dshow', '-i', f'video={n}', '-hide_banner']
        pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, bufsize=10 ** 8)
        resos[name] = list()

        while pipe.poll() is None:
            data = pipe.stderr.read().decode()
            line_data = data.splitlines()

            for l in line_data:
                alt_name_pos = l.find('(alternative pin name "')
                if alt_name_pos != -1:
                    name_full = l[alt_name_pos + 23:]
                    name_end = name_full.find('"')
                    if name_end != -1:
                        name_full = name_full[:name_end]
                        try:
                            name_full = int(name_full)
                        except ValueError:
                            pass
                        resos[name].insert(0, name_full)
                    else:
                        continue

                codec_pos = l.find('vcodec=')
                if codec_pos == -1:
                    codec_pos = l.find('pixel_format=')
                    if codec_pos == -1:
                        continue
                    codec_pos += 13
                else:
                    codec_pos += 7

                min_res_pos = l.find('min s=')
                if min_res_pos == -1:
                    continue
                min_res_pos += 6
                min_fps_pos = l.find('fps=')
                if min_fps_pos == -1:
                    continue
                min_fps_pos += 4
                max_res_pos = l.find('max s=')
                if max_res_pos == -1:
                    continue
                max_res_pos += 6
                max_fps_pos = l.rfind('fps=')
                if max_fps_pos == -1:
                    continue
                max_fps_pos += 4

                codec_str = l[codec_pos:min_res_pos]
                min_res_str = l[min_res_pos:min_fps_pos]
                min_fps_str = l[min_fps_pos:max_res_pos]
                max_res_str = l[max_res_pos:max_fps_pos]
                max_fps_str = l[max_fps_pos:]

                codec_str = codec_str[:codec_str.find(' ')]
                min_res_str = min_res_str[:min_res_str.find(' ')]
                min_fps_str = min_fps_str[:min_fps_str.find(' ')]
                max_res_str = max_res_str[:max_res_str.find(' ')]
                end_space = max_fps_str.find(' ')
                if end_space != -1:
                    max_fps_str = max_fps_str[:end_space]

                x_pos = min_res_str.find('x')
                min_res_w_str = min_res_str[:x_pos]
                min_res_h_str = min_res_str[x_pos + 1:]

                x_pos = max_res_str.find('x')
                max_res_w_str = max_res_str[:x_pos]
                max_res_h_str = max_res_str[x_pos + 1:]

                option_info = {
                    'codec': codec_str,
                    'min_w': min_res_w_str,
                    'min_h': min_res_h_str,
                    'min_fps': min_fps_str,
                    'max_w': max_res_w_str,
                    'max_h': max_res_h_str,
                    'max_fps': max_fps_str
                }

                if option_info not in resos[name]:
                    resos[name].append(option_info)
    return resos


def get_opencv_pin_long_info(resos):
    cv_uids = dict()
    for k, v in resos.items():
        if v:  # v will be empty on devices with no video info, like microphones
            pin = v[0]
            cv_uids[pin] = k
    return cv_uids


def get_opencv_pin_uids(resos):
    uids = get_opencv_pin_long_info(resos)
    cv_uids = dict()
    for k, v in uids.items():
        # hash isn't same between runs: cv_uids[k] = hash(v)
        cv_uids[k] = hashlib.md5(str(v).encode()).hexdigest()
    return cv_uids


def get_opencv_options(resos):
    cv_opts = dict()
    for k, v in resos.items():
        if v:  # v will be empty on devices with no video info, like microphones
            pin = v[0]
            cv_opts[pin] = list()
            for opt in v[1:]:
                res = (opt['min_w'], opt['min_h'])
                if res not in cv_opts[pin]:
                    cv_opts[pin].append(res)
    return cv_opts


def handle_uid_vs_cam(u, c, empty_allowed=False, resos=None):
    if c is not None:
        try:
            c = int(c)
        except ValueError:
            pass
    if u is not None:
        if c is not None:
            warnings.warn("Either camera or UID arguments should be used, not both.")
        if resos is None:
            resos = get_ffmpeg_cam_details()
        pin_uids = get_opencv_pin_long_info(resos)
        c2 = None
        for k, v in pin_uids:
            if v == u:
                c2 = k
        if c2 is None:
            raise ValueError("Pin for camera with given UID could not be found. Is it plugged in?")
        if c is not None and c2 != c:
            raise ValueError(f"Camera pin and camera UID pin mismatch. camera was {c} while pin gives {c2}")
        c = c2
    else:
        if c is None:
            if empty_allowed:
                return None, None
            else:
                raise ValueError("Either camera or UID arguments must be defined.")
        resos = get_ffmpeg_cam_details()
        pin_uids = get_opencv_pin_uids(resos)
        u2 = None
        for k, v in pin_uids.items():
            if k == c:
                u2 = v

        if u2 is None:
            print("Camera with given pin could not be found. Is it plugged in?", file=sys.stderr)
            print("Selecting based on order.", file=sys.stderr)
            u2 = list(pin_uids.values())[c]
        u = u2

    return u, c


def print_full_details(c=None):
    resos = get_ffmpeg_cam_details()

    gl = get_opencv_pin_long_info(resos)
    gu = get_opencv_pin_uids(resos)
    go = get_opencv_options(resos)

    def print_long_info(k):
        nonlocal gl, gu, go

        print(f"Camera Pin Name: {k}")
        long_info = gl[k]
        if isinstance(long_info, tuple):
            print(f"\tShort Name:")
            print(f"\t\t{long_info[0]}")
            print(f"\tLong Name:")
            print(f"\t\t{long_info[1]}")
        else:
            print(f"\tName:")
            print(f"\t\t{long_info}")

        print(f"\tUID:")
        print(f"\t\t{gu[k]}")

        print(f"\tResolutions:")
        for r in go[k]:
            print(f"\t\t{r[0]}x{r[1]}")

    if c is not None:
        print_long_info(c)
    else:
        for k in gu.keys():
            print_long_info(k)


def print_uids(c=None):
    resos = get_ffmpeg_cam_details()

    gu = get_opencv_pin_uids(resos)

    def print_info(k):
        nonlocal gu

        print(k)
        print(f"\t{gu[k]}")

    if c is not None:
        print_info(c)
    else:
        for k in gu.keys():
            print_info(k)


def print_options(c=None):
    resos = get_ffmpeg_cam_details()

    go = get_opencv_options(resos)

    def print_info(k):
        nonlocal go

        print(k)
        for r in go[k]:
            print(f"\t{r[0]}x{r[1]}")

    if c is not None:
        print_info(c)
    else:
        for k in go.keys():
            print_info(k)


def print_long_names(c=None):
    resos = get_ffmpeg_cam_details()

    gl = get_opencv_pin_long_info(resos)

    def print_info(k):
        nonlocal gl

        print(k)
        long_info = gl[k]
        if isinstance(long_info, tuple):
            print(f"\t{long_info[0]}")
            print(f"\t{long_info[1]}")
        else:
            print(f"\t{long_info}")

    if c is not None:
        print_info(c)
    else:
        for k in gl.keys():
            print_info(k)


def main(argv=None):
    if argv is None:
        import sys
        argv = sys.argv[1:]
    if argv:
        args = docopt(__doc__, argv=argv)

        c = args['--camera']
        u = args['--uid']
        u, c = handle_uid_vs_cam(u, c, empty_allowed=True)

        gu = args['--get_uids']
        go = args['--get_options']
        gl = args['--get_long_names']

        count = int(gu) + int(go) + int(gl)
        if count == 0:
            print_full_details(c)
        elif count == 1:
            if gu:
                print_uids(c)
            elif gl:
                print_long_names(c)
            elif go:
                print_options(c)
        else:
            raise ValueError("At most one of get_uids, get_options, get_long_names should be specified.")
    else:
        print_full_details()


if __name__ == '__main__':
    main()
