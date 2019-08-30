# AudioSet-downloader
Download [AudioSet](https://research.google.com/audioset/index.html) with online-trimming by *ffmpeg*. Files will be converted into \*.wav form for convenient usage.  
*Librosa* is applied here to resample the wav file with sampling rate = 22050.  
The code was tested on *Windows 7*.
## Usage
> `$ python audioset_downloader.py`
## Environment
>*Python=3.5.2  
librosa=0.7.0  
ffmpy=0.2.2  
pafy=0.5.3.1  
youtube-dl=2019.8.13  
ffmpeg=ffmpeg-20190826-0821bc4-win64-static*
