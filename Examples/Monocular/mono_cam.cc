/**
* This file is part of ORB-SLAM3
*
* Copyright (C) 2017-2021 Carlos Campos, Richard Elvira, Juan J. Gómez Rodríguez, José M.M. Montiel and Juan D. Tardós, University of Zaragoza.
* Copyright (C) 2014-2016 Raúl Mur-Artal, José M.M. Montiel and Juan D. Tardós, University of Zaragoza.
*
* ORB-SLAM3 is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
* License as published by the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* ORB-SLAM3 is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
* the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License along with ORB-SLAM3.
* If not, see <http://www.gnu.org/licenses/>.
*/

#include<iostream>
#include<algorithm>
#include<fstream>
#include<chrono>
#include<iomanip>
#include <filesystem>

#include<opencv2/core/core.hpp>
#include <boost/dll/runtime_symbol_info.hpp>


#include"System.h"

using namespace std;

int main(int argc, char **argv)
{
    int cam_id = 0;
    //specifically get the exe path, not the current directory. That way settings/vocab can always be found relative to the exe
    boost::system::error_code ec;
    boost::filesystem::path exe_path = boost::dll::program_location(ec);
    std::string vocab_file = "vocab.yml.gz";
    std::string settings_file = "mono_settings.yaml";
    std::string vocab_path_str;
    std::string settings_path_str;
    boost::filesystem::path dir;
    if(!ec){
        dir = exe_path.parent_path();
    }else{
        cerr<<"Warning: could not retrieve exe path. settings/data files can only be found in the current directory now." << endl <<
            ec.message() << endl;
        dir = boost::filesystem::current_path();
    }
    

    if(argc >= 2)
    {
        cam_id = atoi(argv[1]);
    }
    cout << "Using camera " << to_string(cam_id) << "." << endl;
    if(argc >= 3){
        vocab_path_str = std::string(argv[2]);
        if(argc >= 4){
            settings_path_str = std::string(argv[3]);
        }else{
            boost::filesystem::path settings_path = dir/boost::filesystem::path(settings_file);
            settings_path_str = settings_path.string();
        }
    }else{
        boost::filesystem::path settings_path = dir/boost::filesystem::path(settings_file);
        settings_path_str = settings_path.string();
        boost::filesystem::path vocab_path = dir/boost::filesystem::path(vocab_file);
        vocab_path_str = vocab_path.string();
    }
    if(!std::filesystem::exists(settings_path_str)){
        cerr << "Settings file does not exist: " << settings_path_str << endl;
        cerr << "To generate one, please run pycalibrate with your camera, then choose your desired resolution." << endl;
        cerr << "Once generated, move it into the same folder as mono_cam.exe" << endl;
        exit(-1);
    }
    if(!std::filesystem::exists(vocab_path_str)){
        cerr << "Vocab file does not exist: " << vocab_path_str << endl;
        cerr << "To generate one, please find a video of an environment similar to the one you want to recognize, and give it to dbow2_builder.exe" << endl;
        cerr << "Once generated, move it into the same folder as mono_cam.exe" << endl;
        exit(-1);
    }

    // Retrieve paths to images
    //LoadImages(string(argv[3]), vstrImageFilenames, vTimestamps);

    // Create SLAM system. It initializes all system threads and gets ready to process frames.
    ORB_SLAM3::System* SLAM = new ORB_SLAM3::System(vocab_path_str,settings_path_str,ORB_SLAM3::System::MONOCULAR,true);
    float imageScale = SLAM->GetImageScale();

    // Main loop
    double t_resize = 0.f;
    double t_track = 0.f;

    cv::Mat* im = new cv::Mat(); // ensure large images are on heap
    cv::VideoCapture cap;
    int apiID = cv::CAP_ANY;
    cap.open(cam_id, apiID);
    if (!cap.isOpened()) {
        cerr << "ERROR! Unable to open camera\n";
        return -1;
    }
    cap.set(cv::VideoCaptureProperties::CAP_PROP_FOURCC, cv::VideoWriter::fourcc('M', 'J', 'P', 'G')); // usually speed up a lot
    cap.set(cv::VideoCaptureProperties::CAP_PROP_FRAME_WIDTH, 320); // todo: either a settings class or ORB_SLAM3::System should give the desired camera
    cap.set(cv::VideoCaptureProperties::CAP_PROP_FRAME_HEIGHT, 240);
    cout << "Now Tracking." << endl
        << "Press any key to terminate" << endl;
    int frame_i = 0;
    for(;;)
    {
        // Read image from file
        cap.read(*im);
        if(im->empty()){
            cerr << "ERROR! blank frame grabbed\n";
            break;
        }

        //double tframe = vTimestamps[ni];
        cv::imshow("Live", *im);
        if (cv::waitKey(1) > 0){
            cout << "User exited.";
            break;
        }
            

        if(imageScale != 1.f)
        {
#ifdef REGISTER_TIMES
            std::chrono::steady_clock::time_point t_Start_Resize = std::chrono::steady_clock::now();
#endif
            int width = im->cols * imageScale;
            int height = im->rows * imageScale;
            cv::resize(*im, *im, cv::Size(width, height));
#ifdef REGISTER_TIMES
            std::chrono::steady_clock::time_point t_End_Resize = std::chrono::steady_clock::now();
            t_resize = std::chrono::duration_cast<std::chrono::duration<double,std::milli> >(t_End_Resize - t_Start_Resize).count();
            SLAM.InsertResizeTime(t_resize);
#endif
        }

        std::chrono::steady_clock::time_point t1 = std::chrono::steady_clock::now();

        double current_time = std::chrono::duration_cast<std::chrono::duration<double> >(t1.time_since_epoch()).count();

        // Pass the image to the SLAM system
        SLAM->TrackMonocular(*im,current_time,vector<ORB_SLAM3::IMU::Point>(), std::to_string(frame_i));

        std::chrono::steady_clock::time_point t2 = std::chrono::steady_clock::now();

#ifdef REGISTER_TIMES
            t_track = t_resize + std::chrono::duration_cast<std::chrono::duration<double,std::milli> >(t2 - t1).count();
            SLAM.InsertTrackTime(t_track);
#endif

        frame_i++;
       
    }

    // Stop all threads
    SLAM->Shutdown();

    // Save camera trajectory
    SLAM->SaveKeyFrameTrajectoryTUM("KeyFrameTrajectory.txt");    

    free(SLAM);
    free(im);

    return 0;
}

