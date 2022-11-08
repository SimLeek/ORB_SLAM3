/**
 * File: Demo.cpp
 * Date: November 2011
 * Author: Dorian Galvez-Lopez
 * Description: demo application of DBoW2
 * License: see the LICENSE.txt file
 */

#include <iostream>
#include <vector>
#include <filesystem>

// DBoW2
#include <DBoW2/DBoW2.h> // defines OrbVocabulary and OrbDatabase

// OpenCV
#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/features2d.hpp>

using namespace DBoW2;
using namespace std;

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

void loadFeatures(vector<vector<cv::Mat>> &features, std::string &vid_file, int frame_skip);
void changeStructure(const cv::Mat &plain, vector<cv::Mat> &out);
void createVocabulary(const vector<vector<cv::Mat>> &features, const std::string &voc_filename);
void modifyVocabulary(const vector<vector<cv::Mat>> &features, const std::string &voc_filename);

// ----------------------------------------------------------------------------

int main(int argc, char **argv)
{
  if (argc < 2)
  {
    cerr << endl
         << "Usage: ./dbow2_builder path_to_vid [path_to_vocab_file] [frame_skip_count=0]" << endl;
    return 1;
  }

  auto vid_file = std::string(argv[1]);
  auto vocab_file = std::string("vocab.yml.gz");
  int frame_skip_count = 0;
  if (argc >= 4)
  {
    frame_skip_count = atoi(argv[3]);
  }

  vector<vector<cv::Mat>> features;
  loadFeatures(features, vid_file, frame_skip_count);

  if (argc >= 3)
  {
    vocab_file = std::string(argv[2]);

    if (std::filesystem::exists(vocab_file))
    {
      modifyVocabulary(features, vocab_file);
    }
    else
    {
      createVocabulary(features, vocab_file);
    }
  }
  else
  {
    createVocabulary(features, vocab_file);
  }

  cout << endl
       << "Vocab File is now available at " << vocab_file << endl;

  return 0;
}

// ----------------------------------------------------------------------------

void loadFeatures(vector<vector<cv::Mat>> &features, std::string &vid_file, int frame_skip = 0)
{
  cv::VideoCapture cap;
  int apiID = cv::CAP_ANY;
  cap.open(vid_file.c_str(), apiID);

  features.clear();

  auto n_images = (int)(cap.get(cv::VideoCaptureProperties::CAP_PROP_FRAME_COUNT));
  if (n_images == 0)
  {
    cout << "failed to get video frame count. Autodetecting frames instead." << endl;
  }
  else
  {
    int true_res;
    if (frame_skip){
      cerr << "WARNING: frame skipping may be slow, as opencv has to build up the frame from compressed video."
           << "Alternatively, you can specify a frameskip in the python make_vid dataset->video or video->video program." << endl;
      true_res = n_images/frame_skip+1;
    }else{
      true_res = n_images;
    }
    cout << "Reserving space for " << true_res << "frames" << endl;
    features.reserve(true_res);
  }

  cv::Mat im;
  cv::Ptr<cv::ORB> orb = cv::ORB::create();
  bool ret;

  cout << "Extracting ORB features..." << endl;
  for (int i = 0;;)
  {
    
    if(frame_skip && n_images){
      i += frame_skip;
      cap.set(cv::VideoCaptureProperties::CAP_PROP_POS_FRAMES, i);
    }else{
      i++;
    }
    ret = cap.read(im);
        
    if (ret)
    {
      cv::imshow("Video", im);
      if (cv::waitKey(1) > 0)
        break;
    }
    else
      break;

    if (i % frame_skip == 0)
    {
      cv::Mat mask;
      vector<cv::KeyPoint> keypoints;
      cv::Mat descriptors;

      orb->detectAndCompute(im, mask, keypoints, descriptors);

      features.push_back(vector<cv::Mat>());
      changeStructure(descriptors, features.back());
    }
  }
}

// ----------------------------------------------------------------------------

void changeStructure(const cv::Mat &plain, vector<cv::Mat> &out)
{
  out.resize(plain.rows);

  for (int i = 0; i < plain.rows; ++i)
  {
    out[i] = plain.row(i);
  }
}

// ----------------------------------------------------------------------------

void createVocabulary(const vector<vector<cv::Mat>> &features, const std::string &voc_filename)
{
  // branching factor and depth levels
  const int k = 10;                    // 9;
  const int L = 6;                     // 3;
  const WeightingType weight = TF_IDF; // this is 0
  const ScoringType scoring = L1_NORM; // this is also 0

  OrbVocabulary voc(k, L, weight, scoring);

  cout << "Creating a " << k << "^" << L << " vocabulary..." << endl;
  voc.create(features);
  cout << "... done!" << endl;

  cout << "Vocabulary information: " << endl
       << voc << endl
       << endl;

  // lets do something with this vocabulary
  /*cout << "Matching images against themselves (0 low, 1 high): " << endl;
  BowVector v1, v2;
  for(int i = 0; i < NIMAGES; i++)
  {
    voc.transform(features[i], v1);
    for(int j = 0; j < NIMAGES; j++)
    {
      voc.transform(features[j], v2);

      double score = voc.score(v1, v2);
      cout << "Image " << i << " vs Image " << j << ": " << score << endl;
    }
  }*/

  // save the vocabulary to disk
  cout << endl
       << "Saving vocabulary..." << endl;
  voc.save(voc_filename);
  cout << "Done" << endl;
}

// ----------------------------------------------------------------------------

void modifyVocabulary(const vector<vector<cv::Mat>> &features, const std::string &voc_filename)
{
  cout << "Loading vocab from disk..." << endl;

  // load the vocabulary from disk
  OrbVocabulary voc(voc_filename);

  OrbDatabase db(voc, false, 0); // false = do not use direct index
  // (so ignore the last param)
  // The direct index is useful if we want to retrieve the features that
  // belong to some vocabulary node.
  // db creates a copy of the vocabulary, we may get rid of "voc" now

  // add images to the database
  cout << "Adding new images to database..." << endl;
  for (int i = 0; i < features.size(); i++)
  {
    db.add(features[i]);
  }

  cout << "... done!" << endl;

  cout << "Database information: " << endl
       << db << endl;

  // and query the database
  /*cout << "Querying the database: " << endl;

  QueryResults ret;
  for(int i = 0; i < NIMAGES; i++)
  {
    db.query(features[i], ret, 4);

    // ret[0] is always the same image in this case, because we added it to the
    // database. ret[1] is the second best match.

    cout << "Searching for Image " << i << ". " << ret << endl;
  }

  cout << endl;*/

  // we can save the database. The created file includes the vocabulary
  // and the entries added
  cout << "Saving database..." << endl;
  db.save(voc_filename);
  cout << "... done!" << endl;

  // once saved, we can load it again
  /*cout << "Retrieving database once again..." << endl;
  OrbDatabase db2("small_db.yml.gz");
  cout << "... done! This is: " << endl << db2 << endl;*/
}

// ----------------------------------------------------------------------------
