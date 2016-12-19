sudo apt-get update
sudo apt-get install -f build-essential python-pip python-dev python-smbus 
git
sudo pip install Flask
git clone https://github.com/xtacocorex/Adafruit_Python_GPIO.git
cd Adafruit_Python_GPIO
sudo python setup.py install
sudo apt-get install python-opencv
#sudo pip install numpy
sudo -H pip install --upgrade numpy
