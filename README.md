# spaceowls
1) sudo apt install python3-opencv
2) sudo apt install git
3) git clone https://github.com/touniez/spaceowls.git
4) sudo apt-get install libatlas-base-dev
5) CORAL: https://coral.ai/docs/accelerator/get-started/#runtime-on-linux
6) may need to remove new version of tflite: sudo apt remove tensorflow-lite


pi password: owls
pi username: pi


# set up env to retrain model:
pip install pycocotools
pip install -q tflite-model-maker

# Run new cv for coral
sudo python3 newcv.py
