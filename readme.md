This project supports cubemos, openpose as the pose extractor, the raw data is rosbag with RGBD information.
## Preliminaries
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
  python main.py -e OPENPOSE -mp BODY_25 -opdir D:\work\openpose\build -i ./bag
  ```

  ​     , which is the path of `build` folder.

  
* Possible bugs:
    * While running, if you got [Check failed: [error == cudaSuccess (2 vs. 0)  out of memory]](https://github.com/CMU-Perceptual-Computing-Lab/openpose/issues/1230), change the `net_resolution, face_resolution, hand_resolution` by

       ```bash
       python main.py  -i ./bag -e OPENPOSE -mp BODY_25 -opdir D:\work\openpose\build --net_resolution 256x256 --face_net_resolution 256x256 --hand_net_resolution 256x256
       ```

       Note that you can change the resolution according to the capacity of your computer, but the smaller the resolution, normally the worse the detection. The resolution is a multiple of 16.

### Cubemos

  The skeleton model of cubemos has [18 keypoints](https://miao-picbed-1305768714.cos.ap-shanghai.myqcloud.com/img/image-20210510121456746.png). 1. use it by

   ```bash
   python main.py -e CUBEMOS -i ./bag
   ```

* Possible bugs