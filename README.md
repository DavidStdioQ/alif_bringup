# alif_bringup

### Prepare the environment:

`. <(curl https://aka.ms/vcpkg-init.sh -L)`

`. ~/.vcpkg/vcpkg-init`

`vcpkg activate` <sub> Should download packages 
                      prescribed in vcpkg-configuration.json i.e. 
                      ctools 1.7.0, cmake, ninja, arm-none-abi-gcc compiler </sub>

ctools 1.7.0 is an old version of cmsis-tools.  
If it will be decided to use latest version   
of cmsis-tools the cproject.yaml should be renamed to cproject.cprojct.yaml  
and csolution.yaml should be updated accordingly:  

```
  projects:
       - project: cproject.yaml
```

should be replaced with 
```
  projects:
     - project: cproject.cproject.yaml
```
due to changes in csolution.schemaVERSION=3.10.12

### Build the project:

```
cpackget init https://keil.com/pack/index.pidx;
cpackget init https://sadevicepacksdqaus.blob.core.windows.net/idxfile/index.pid
cpackget add https://github.com/ARM-software/CMSIS_5/releases/download/5.9.0/ARM.CMSIS.5.9.0.pack;
cpackget add .alif/AlifSemiconductor.Ensemble.0.9.0-p1.pack;
csolution convert -s csolution.yaml -c cproject+HP
cbuild cproject+HP.cprj
```

The project is built now, next step is to load it to the alif eval board.  
There alif provided python scripts for this.  
You have to install python 3.10 if you don't have it already installed.  
Python3.10 installation on linux:  
```
VERSION=3.10.12
wget https://www.python.org/ftp/python/$VERSION/Python-$VERSION.tgz
tar -xf Python-$VERSION.tgz
cd  Python-$VERSION/
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall
```
Install pip3.10
```
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
```

Install required python packages  
```
pip3.10 install cryptography
pip3.10 install pyserial
```
Download built binary into the eval board with alif SE tools
```
cp out/cproject/HP/cproject.bin app-release-python/build/images/alif-img.bin
cp .alif/m55-hp_cfg.json app-release-python/alif-img.json
python3.10 app-gen-toc.py -f alif-img.json
python3.10 app-write-mram.py -p
```
