# Installation Instructions

## Create conda environment

```
conda env create -f environment.yml 
conda activate programmatic-representations
```

(It throws an error but it works anyway)

## Download models (Aesthetic and CLIP)

```
curl --header 'Host: raw.githubusercontent.com' --header 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36' --header 'Accept: */*' --header 'Accept-Language: pt-PT,pt;q=0.6' --header 'Referer: https://github.com/christophschuhmann/improved-aesthetic-predictor/blob/main/sac%2Blogos%2Bava1-l14-linearMSE.pth' 'https://raw.githubusercontent.com/christophschuhmann/improved-aesthetic-predictor/refs/heads/main/sac%2Blogos%2Bava1-l14-linearMSE.pth' -L -o 'sac+logos+ava1-l14-linearMSE.pth'
  
curl --header 'Host: openaipublic.azureedge.net' --header 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36' --header 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8' --header 'Accept-Language: pt-PT,pt;q=0.6' --header 'Referer: https://github.com/' 'https://openaipublic.azureedge.net/clip/models/b8cca3fd41ae0c99ba7e8951adf17d267cdb84cd88be6f7c2e0eca1737a03836/ViT-L-14.pt' -L -o 'ViT-L-14.pt'
```

## Install packages
```
pip install git+https://github.com/openai/CLIP.git tensorflow==2.16.2
```

## Install hal-cgp

```
git clone https://github.com/Happy-Algorithms-League/hal-cgp.git
cd hal-cgp/
pip install .
cd ..
```

## Install libpng12 on Ubuntu < 20.0 (Try this first)

```
sudo add-apt-repository ppa:linuxuprising/libpng12
sudo apt update
sudo apt install libpng12-0
```

## Install libpng12 on Ubuntu > 20.0

```
sudo apt install build-essential zlib1g-dev
wget https://ppa.launchpadcontent.net/linuxuprising/libpng12/ubuntu/pool/main/libp/libpng/libpng_1.2.54.orig.tar.xz
tar Jxfv libpng_1.2.54.orig.tar.xz
cd libpng-1.2.54/
./configure
make
sudo make install
sudo ln -s /usr/local/lib/libpng12.so.0.54.0 /usr/lib/libpng12.so
sudo ln -s /usr/local/lib/libpng12.so.0.54.0 /usr/lib/libpng12.so.0
```
