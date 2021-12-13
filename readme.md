This project supports cubemos, openpose, google posenet as the pose extractor. The raw data is rosbag with RGBD information. Since data are captured by Intel realsense, the pyrealsense is taken as the processing tool.
## Preliminaries
### Install pyrealsense

Download SDK from [here](https://github.com/IntelRealSense/librealsense/releases/tag/v2.44.0). To compile `pyrealsense` from [source](https://github.com/IntelRealSense/librealsense), the two guides may help.
* https://dev.intelrealsense.com/docs/compiling-librealsense-for-windows-guide
* https://github.com/IntelRealSense/librealsense/issues/980#issuecomment-356097825

### Install pyopenpose

**Prepare**: visual studio, [cmake](https://cmake.org/download/), python (better >=py36), cuda (if your PC has Nvidia GPU), opencv (python). Armed with these tools, you can download [source code](https://github.com/CMU-Perceptual-Computing-Lab/openpose) and compile following this [guide](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation/0_index.md#compiling-and-running-openpose-from-source).
    
1. Suppose the build folder is `openpose-master/build`. To compile python package, set `BUILD_PYTHON=True` while configuring.
<img src="https://miao-picbed-1305768714.cos.ap-shanghai.myqcloud.com/img/image-20210510144927530.png" alt="image-20210510144927530" style="zoom:25%;" />

* While generating, if [`CMake Error at python/openpose/CMakeLists.txt:6 (pybind11_add_module): Unknown CMake command "pybind11_add_module".`](https://github.com/CMU-Perceptual-Computing-Lab/openpose/issues/1068)
  
    run `git clone https://github.com/pybind/pybind11.git`

2. After generating, open visual studio and `build solution`. Note: be sure to click `build solution` otherwise the generated solution is incompleted.
    
3. Copy the built openpose folder `openpose-master/build` (the folder you set to build) to the openpose installation folder (denoted as `Openpose_Root_DIR`).

     E.g., my installation folder of openpose is `D:\work\openpose`, then the build folder is put as `D:\work\openpose\build`, aka `Openpose_Root_DIR=D:\work\openpose\build`

4. Note the `/models` folder from source code `openpose-master/models` is copied to `$Openpose_Root_DIR/../`. Looks like this:

  <img src="https://miao-picbed-1305768714.cos.ap-shanghai.myqcloud.com/img/image-20210510110409615.png" alt="image-20210510110409615" style="zoom:50%;" />

  ​			The original `/models` folder is in the source code:

  <img src="https://miao-picbed-1305768714.cos.ap-shanghai.myqcloud.com/img/image-20210510145610949.png" alt="image-20210510145610949" style="zoom:30%;" />

### Cubemos
**Prepare**: Download sdk from [here](https://framos-my.sharepoint.com/:f:/p/c_scheubel/Em4eCGd-pctJnxkyG_pxRIgBcueMBoF5EuWtCYwGFEldsA?e=2XZZZB) and get a cubemos activation key (you can apply for a trial key). Install it following [installation guide](https://download-skeleton-tracking-sdk.s3.eu-central-1.amazonaws.com/GettingStartedGuide.pdf).
1. After installation, run `SkeletonTracking/scripts/post_installation.bat`, then you can activate cubemos with your key.
2. After the activation, check if the environment variable `CUBEMOS_SKEL_SDK` is added and `path` is modified, normally after restarting PC, all required environment variables will be set.
* Some bugs

     * If you have installed the cubemos before and activated with a different activation key. The best way to make sure all works is to uninstall and then reinstall and activate it with new key.

## How to use?
Collect your rosbag files and put them under a path. Below all codes suppose that the bag file path is `./bag`
### Openpose

Be sure to set the root directory of openpose by `-opdir`. Pose model `BODY_25` will detect the [25 joints skeleton](https://user-images.githubusercontent.com/9403813/87262012-6d802d80-c486-11ea-9629-107e09d5c255.png). Switch to the directory where `main.py` is, run

  ```bash
  python main_old.py -e OPENPOSE -mp BODY_25 -opdir D:\work\openpose\build -i ./vsi
  ```

  ​     , which is the path of `build` folder.

  
* Possible bugs:
    * While running, if you got [Check failed: [error == cudaSuccess (2 vs. 0)  out of memory]](https://github.com/CMU-Perceptual-Computing-Lab/openpose/issues/1230), change the `net_resolution, face_resolution, hand_resolution` by

       ```bash
       python main_old.py  -i ./vsi -e OPENPOSE -mp BODY_25 -opdir D:\work\openpose\build --net_resolution 256x256 --face_net_resolution 256x256 --hand_net_resolution 256x256
       ```

       Note that you can change the resolution according to the capacity of your computer, but the smaller the resolution, normally the worse the detection. The resolution is a multiple of 16.

### Cubemos

  The skeleton model of cubemos has [18 keypoints](https://miao-picbed-1305768714.cos.ap-shanghai.myqcloud.com/img/image-20210510121456746.png). Use it by

   ```bash
   python main_old.py -e CUBEMOS -i ./vsi
   ```

* Possible bugs

## Dataset
The dataset consists of 300 simulation videos, captured at CRIUGM and organized as rosbag, which are stored [here]().

[comment]: <> ([here]&#40;https://udemontreal-my.sharepoint.com/:f:/g/personal/perla_nehme_umontreal_ca/EvSGDcC3ub9DrfzVEfdGZjkBpD0bBcqFk7uq-_VDydzWEw?e=vhbDKp&#41;)

### Camera
The camera used is: [Intel realsense D455](https://www.intelrealsense.com/depth-camera-d455/), which is an RGBD camera that captures a color image, and a depth map.

### Visualization
To view those rosbag firstly and thus have a first look, one suggestion is the Intel® RealSense ™ Viewer software available on [this site](https://www.intelrealsense.com/sdk-2/). 

Concretely, open the software then click on *+ Add Source* and choose *Load Recorded Sequence*. 

There are two types of images: color and depth (distance to the camera displayed in pseudocolor).

### Description
#### Scenarios
**Normal daily activities (scenarios 1 to 10).**
1. Sit on the couch and dial a phone number.

2. Pull a chair in the kitchen and sit down at the table.

3. Turning on the fan located in the living room area.

4. Lie down on the couch and opening the television with the remote control.

5. Lean in the middle of the room and tying your shoelace.

6. Go to the kitchen table and drink from a cup on the table.

7. Go to the living room, take a tissue from the tissue box on the coffee table and simulate the action of blowing your nose.

8. Go to the bathroom door, open it, then close it.

9. Pick up a book from a shelf, look at it, then put it back in its place.

10. Go to the kitchen table, then clean it with a cloth previously placed on the table.

**Near falls (scenarios 11 to 20).**

11. Go to the middle of the room, bend down to tie your shoelace and loss of balance, but put hands on the ground to avoid falling (protective reaction, e.g. lowering of the center of mass and tilting of the trunk).

12. Walk to the bathroom and trip over the mat, without falling. (Unexpected movement of the arms and / or legs, unexpected change in stride length and trunk tilt)

13. Walk and slide with loss of balance, without falling. (Unexpected change in stride length, unexpected movement of arms and / or legs, and unexpected change in pace).

14. Walk to the book shelf, loss of balance backwards during the action. (Inclination of the trunk and lowering of the center of mass)

15. Walk involuntarily crossing your feet (stumble) and trip, without falling to the ground. (Unexpected movement of the arms and / or legs, unforeseen change in stride length and trunk tilt)

16. Walking around the room with a sudden change in walking speed due to loss of balance. (Unexpected change in pace and change in stride length.)

17. Loss of balance when straightening up after picking up a box of tissue, without support (Tilting of the trunk and unexpected movement of the arms and / or legs.)

18. Bumping your foot on the coffee table and loss of balance (Unexpected movement of the upper limbs and / or lower limbs and tilting of the trunk.)

19. Dusting causing a loss of balance on the side and hold on to the wall (Unexpected movement of upper limbs and / or lower limbs and unexpected change in stride length)

20. Perform a seated → standing transfer, dizziness and loss of balance, hold onto the armrest of the couch. (Tilt of the trunk and unexpected movement of upper limbs and / or lower limbs.)

#### Labels
The files have names similar to this: `20210327_115917_p2s11r1e2.bag`, among which, `20210327` represents the acquisition date March 27, 2021, `115917` represents the time 11:59 and lasts for 17 seconds, `p2s11r1e2` represents phase 2 scenario 11 repetition 1 student 2.

Phase 1 is a set of 100 videos which are used to "train" the algorithm by choosing the best parameters etc. There are only NORMAL activities in these videos. Phase 2 is made up of 100 normal videos (like phase 1) and 100 abnormal videos. This phase is used to test the algorithms. Of course you can split the dataset otherwise if you wish.

The ultimate goal is to classify the Phase 2 videos as "abnormal" or "normal" based on algorithms developed from the Phase 1 videos.

### Skeletons
Those joints with importance score less than JOINT_CONFIDENCE (defined in config.py) will be set as 1e6, and their importance score will be set as -1 to indicate these joints cannot be used.


## To generate vsi data
Run scripts
`python main.py bag -c ./config/bag_config.yml --showFlag False`

## To generate kinetics data
Run scripts
`python main.py video -c ./config/kinetics_config.yml --showFlag False`

## To generate ntu data
Run scripts
`python main.py skeleton -c ./config/ntu_config.yml --showFlag False`

