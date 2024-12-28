export http_proxy=http://192.168.31.42:7890
export https_proxy=http://192.168.31.42:7890
cd ~
sudo apt update
sudo apt install git 
sudo apt install snapd
sudo systemctl enable --now snapd.socket
sudo apt install gcc-11
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 50
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 50
#sudo update-alternatives --config gcc
#sudo update-alternatives --config g++
sudo apt install gir1.2-ayatanaappindicator3-0.1
sudo apt install build-essential cmake libfmt-dev libprotobuf-dev libyaml-cpp-dev libboost-dev libboost-system-dev libboost-thread-dev libboost-random-dev pkg-config libgrpc++-dev pybind11-dev protobuf-compiler protobuf-compiler-grpc nlohmann-json3-dev curl openssh-server
sudo apt install libcpprest-dev

# etcd api
git clone -b v0.15.4 https://github.com/etcd-cpp-apiv3/etcd-cpp-apiv3.git
cd etcd-cpp-apiv3
mkdir -p build
cd build
cmake ..
make -j`nproc`
sudo make install

# etcdadm
cd ~
unset http_proxy
unset https_proxy
sudo snap install go --classic
export PATH=$PATH:/snap/bin
git clone https://github.com/Turing-zero/etcdadm.git
go env -w GO111MODULE=on
go env -w GOPROXY=https://goproxy.cn,direct
make
make install
 
export http_proxy=http://192.168.31.42:7890
export https_proxy=http://192.168.31.42:7890
# pybind11
sudo apt install python3-pip
pip install pybind11 --break-system-packages 

# tbkpy
pip install git+https://github.com/Turing-zero/tbkpy.git --break-system-packages

# tzcp
pip install git+https://github.com/Turing-zero/tzcp.git --break-system-packages

cd ~

# tbkcore
git clone -b dev --recurse-submodules https://github.com/Turing-zero/TBK.git
export TBK_INSTALL_PATH=/usr/local/tbk
cd TBK/core
mkdir -p build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$TBK_INSTALL_PATH
cmake --build . -j2
sudo cmake --install .

# tbk-core py
cd ~
export CMAKE_ARGS="-DCMAKE_PREFIX_PATH=$TBK_INSTALL_PATH"
pip install git+https://github.com/Turing-zero/tbkpy-core.git --break-system-packages

# TBK-AGV
cd ~
git clone https://github.com/TnTeQAQ/TBK-AGV
pip install python-can --break-system-packages
pip install numpy --break-system-packages
pip install canalystii --break-system-packages

# 配置usb
# sudo nano /etc/udev/rules.d/99-com.rules
# SUBSYSTEM=="usb", ATTR{idVendor}=="04d8", ATTR{idProduct}=="0053", MODE="0666"