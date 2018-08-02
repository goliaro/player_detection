# player_detection
This code aims to associate observations of moving entities around a robot to either players and/or objects in the surrounding space.
- A first approach was to use Overlapping Mixtures of Gaussian Process Experts (OMGP), as in the 2011 [paper](//arxiv.org/abs/1108.3372) by Lázaro-Gredilla et al.
- A second approach consists in re-using the code and ideas from Ewerton Lopes' repository [lda-player-model](//github.com/ewerlopes/lda-player-model) and identifying the players from the detections of moving objects through an analysis of Gramian Angular Field Images. 
- The robot is powered by the Robotics Operating System (ROS) and needs to be able to interact with the player and play a dynamic game. It uses lasers and a Microsoft Kinect ® camera to perform SLAM and to locate the player(s) 

The OMGP code is not too fast yet (because of the slowless of the np.linalg.solve function, see [cProfile results](//github.com/gabrieleoliaro/player_detection/blob/master/snakeviz%20cProfile.pdf)), and needs to be optimized.

**Files:**<br/>
* `covariance.py` -- Contains all the functions to generate the covariance matrices, test set covariances, and derivative matrices. <br/>
* `minimize.py` -- Allows you to minimize a differentiable multivariate function using conjugate gradients.  <br/>
* `omgp.py` -- The main function setting up the initial hyperparameters and calling omgpEinc and omgp_bound in turns to solve the problem and make probabilistic predictions.  <br/>
* `omgp_load.py` -- Used to generate random input or parse it from file. <br/>
* `omgpbound.py` -- Allows you to computes the negative of the Marginalized Variational Bound (F) and its derivatives wrt loghyper (dF). <br/>
* `omgpEinc.py` -- Performs the E-step.  <br/>
* `parser.py` -- Draft of CSV parser for ROS log file coming from [Ewerton Lopes](//github.com/ewerlopes)'s player_tracker code. Eventually it will probably be included into the omgp_load file.  <br/>
* `quality.py` -- Computes NMSE and NLPD measures for test data. <br/>
* `sq_dist.py` -- a function to compute a matrix of all pairwise squared distances
    between two sets of vectors, stored in the columns of the two matrices, a
    (of size D by n) and b (of size D by m). If only a single argument is given
    or the second matrix is empty, the missing matrix is taken to be identical
    to the first.. <br/>
* `test_omgp.py` -- The main module used to run the OMGP program.  <br/>
* `test.py` -- Module to read and print matrixes from and to xlsx files through pandas.  <br/>
* `lda_launcher.py` -- The main module used to run the lda-player-model program .  <br/>

**Parameters in test_omgp:**<br/>
* `n` -- The number of points to generate for each GP.  <br/>
* `D` -- The number of dimensions for the regression. To load a log file generated by the ROS code in [player-tracker](//github.com/ewerlopes/leg_tracker/tree/player_tracker) you have to set D = 2 <br/>
* `M` -- The number of GPs/trajectories for the regression.  <br/>
* `omgp_mode` -- Set this to OMGP_LOAD to load data from a log file or to OMGP_GENERATE to do a demo regression on randomly generated values.  <br/>

Dependencies
============
* Matplotlib
* Numpy
* CSV

Acknowledgement
-------------------
The code performing the OMGP regression is a translation of the version in Matlab written by Lázaro Gredilla et al. for the paper in the reference below

Reference
-------------------
Lázaro-Gredilla, Van Vaerenbergh, & Lawrence. (2011). Overlapping Mixtures of Gaussian Processes for the data association problem. Pattern Recognition, 45(4), 1386-1395.
