# Video Time Label Tool

## Git Clone in your computers
```
git clone https://github.com/MioYeh/GM-Label-Tool.git
```
## Use Anaconda env
### Using environment.yml to create
```
conda env create -f environment.yml
```
### Not using environment.yml to create
```
conda create --name video_label python=3.8
conda activate video_label
pip install pyqt5
pip install opencv-python
```

## Not using Anaconda
```
pip install pyqt5
pip install opencv-python
```


## Run Code
```
python main.py
```

## How to Use
![image](https://github.com/MioYeh/GM-Label-Tool/blob/main/label_ui.png)

`讀取紀錄`

`輸出紀錄`

`Open file` 代表

`Open floder` 

`Play`

`Pause`

`Stop`

`Record method`: Pressing 'C' will record the start time. Pressing it again will display the time range from start to end in the log, for example: '00:10 - 00:20'
