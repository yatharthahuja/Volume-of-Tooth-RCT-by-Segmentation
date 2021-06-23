# !/bin/bash
#pwd
#3.0625=1.75 x 1.75

#pre-scan-analysis:
python RCT_VOLUME_ESTIMATE.py -s='pre' -i=550 -n=550 -a=3.0625 -t=14 -dc="/home/yatharth/Desktop/rct/pre-scan-canvas/" -d="/home/yatharth/Desktop/rct/pre-scan-dataset/"
#i=550 n =879

#post-scan-analysis:
python RCT_VOLUME_ESTIMATE.py -s='post' -i=200 -n=200 -a=3.0625 -t=14 -dc="/home/yatharth/Desktop/rct/post-scan-canvas/" -d="/home/yatharth/Desktop/rct/post-scan-dataset/"
#i=200 n=550 or 529(to balance)

#final resutls:
python RCT_VOLUME_CHANGE.py