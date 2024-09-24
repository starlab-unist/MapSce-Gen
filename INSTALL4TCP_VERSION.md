# Installation Manual

### CUDA Settings

[Install CUDA Toolkit 11.3](XXXX)

```shell
wget XXXX
sudo sh cuda_11.3.1_465.19.01_linux.run
```

Add CUDA Environment

```shell
vim ~/.bashrc
```

```shell
export PATH
export PATH=/usr/local/cuda-11.3/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-11.3/lib64:/lib64:$LD_LIBRARY_PATH
```

### Conda Settings

```shell
conda env create -f environment.yml --name f4a
conda activate f4a
```

### Install Carla

This code uses CARLA 0.9.10.1. You will need to first install CARLA 0.9.10.1, along with the additional maps.
See [link](XXXX) for more instructions.

For convenience, the following commands can be used to install carla 0.9.10.1.

Download CARLA_0.9.10.1.tar.gz and AdditionalMaps_0.9.10.1.tar.gz from [link](XXXX), create directory `~/Documents/Tools/`, and run:
```shell
cd ~/Documents/Tools
mkdir CARLA_0.9.10
tar -xvzf CARLA_0.9.10.1.tar.gz -C CARLA_0.9.10
```

move `AdditionalMaps_0.9.10.1.tar.gz` to `CARLA_0.9.10/Import/` and in the folder `CARLA_0.9.10/` run:
```shell
./ImportAssets.sh
```

### Download a TCP pretrained model
TCP model is one of the models supported to be tested. A pretrained-model's checkpoint can be found [here](XXXX)

Download the model, named "new.ckpt". Move this model's checkpoint to the `AD/TCP/leaderboard/models/`.


## Build Carla PythonAPI

Ref. XXXX

Dependencies
```shell
sudo apt-get update &&
sudo apt-get install wget software-properties-common &&
sudo add-apt-repository ppa:ubuntu-toolchain-r/test &&
wget -O - XXXX apt-key add - &&
sudo apt-add-repository "deb XXXX llvm-toolchain-xenial-8 main" &&
sudo apt-get update
```

Ubuntu 18.04
```shell
sudo apt-get install build-essential clang-8 lld-8 g++-7 cmake ninja-build libvulkan1 python python-pip python-dev python3-dev python3-pip libpng-dev libtiff5-dev libjpeg-dev tzdata sed curl unzip autoconf libtool rsync libxml2-dev libxerces-c-dev &&
pip2 install --user setuptools &&
pip3 install --user -Iv setuptools==47.3.1 &&
pip2 install --user distro &&
pip3 install --user distro
sudo update-alternatives --install /usr/bin/clang++ clang++ /usr/lib/llvm-8/bin/clang++ 180 &&
sudo update-alternatives --install /usr/bin/clang clang /usr/lib/llvm-8/bin/clang 180

```

Build using make
```shell
cd carla
make PythonAPI
``` 

## Setting up docker

Install docker-ce
```shell
sudo apt remove docker docker-engine docker.io
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL XXXX | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository "deb [arch=amd64] XXXX $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker-ce
```

Set up permissions
```shell
sudo groupadd docker
sudo usermod -aG docker ${USER}
sudo su - ${USER}
```

## Setting up nvidia driver

Check recommended driver name such as `nvidia-driver-XXX`
```shell
sudo add-apt-repository ppa:graphics-drivers
sudo apt update
ubuntu-drivers devices
```

Install nvidia driver (Reboot is contained)
```shell
sudo apt install nvidia-driver-XXX
sudo reboot now
nvidia-smi
```

Install nvidia-docker2
```shell
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L XXXX | sudo apt-key add -
curl -s -L XXXX$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install nvidia-docker2
sudo systemctl restart docker
```

## Install Carla 0.9.10.1 Docker Image

Pull docker image
```shell
docker pull carlasim/carla:0.9.10.1
```

