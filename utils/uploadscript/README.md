### Introduction
This Python script assists with uploading a media file directly to NRT services without the need of mobile devices. 
It will also create a patient ID (noteID) and queue the stream to be processed by the NRT scheduler which runs in 10 min interval.
There are a few Python files in the project,
  - *main.py* : takes necessary parameters and call the API's regarding authentication, patient creation and NRT core with proper logging.
  - *nrt_core.py*: consists of functions which can be called to interact with the NRT server. It can be used seperately for other testing purposes.
  - *authentication.py*: created a valid auth token based on the providers credential.
  - *patient_creation.py*: creates and maps newly generated noteID with the specific provider.
 
This code will generate _streamID_, _noteID_ and log it in the console which can be used for further debugging with the help of the server logs.

### Prerequisite.
  - *Python3*
  - *ffmpeg* (optional)
  - *ffprobe* (optional)

### How to run the code?
Download the python files (main.py, nrt_core.py, authentication.py, patient_creation.py) on the same directory. 
For help type the following command,
```
python3 main.py -h
```

The follwing command will upload the file to NRT server.

```
python3 main.py -url [nrt-url] \
                -email [provider-email-id] \
                -pass [provider-password] \
                -stype [streaming-type] \
                -mtype [media-type] \
                -file [file-path] \
                -auth [jwt-url] \
                -patient [note-id-creation-url] \
                -name [patient-name]

```
Here is an example for the DEV NRT server,
```
 python3 main.py -url https://mcu-test1.augmedix.com:30010 \
                 -email 'mashroor_dev_02@augmedix.com' \
                 -pass 'superSecret' \
                 -stype dictation \
                 -mtype audio \
                 -file '0000001.mp4' \
                 -auth 'https://dev2.augmedix.com:50000/token?grantType=password&idp=com.augmedix.legacy' \
                 -patient 'https://dev2.augmedix.com:50001' \
                 -name 'this name will be visible in SCP UI'
```

### Constants
- NRT Server URL
    - DEV: https://mcu-test1.augmedix.com:30010
    - STAGING: https://staging-api.augmedix.com:50010
    - PROD: https://api.augmedix.com:50010
- Authentication URL
    - DEV: https://dev2.augmedix.com:50000/token?grantType=password&idp=com.augmedix.legacy
    - STAGING: https://stage-api2.augmedix.com/auth/v1/token?grantType=password&idp=com.augmedix.legacy
    - PROD: https://api.augmedix.com:50000/token?grantType=password&idp=com.augmedix.legacy
- Patient Creation URL
    - DEV: https://dev2.augmedix.com:50001
    - STAGING: https://staging-api.augmedix.com:50001
    - PROD: https://api.augmedix.com:50001
- STREAMING TYPE: recording, visit, dictation
- MEDIA TYPE: audio, video

### Constrains
  - *JWT token for corresponding NRT server* : NRT server can not be accessed without a valid auth token. Please make sure to use the correct token for the corresponding environment (dev, staging, prod)
  - *Must be a Valid mp4 container with the following codec*
     - *audio codec: AAC*
     - *video codec: h264*
  - Transcoding is required if the file is in any other format.
     -  ffmpeg -i [some-media-file] output.mp4
     -  ffmpeg -i [some-media-file] -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 160k -vf format=yuv420p -movflags +faststart output.mp4
  - Integraty of the file can be checked with ffprobe
     - ffprobe -i [some-media-file]
     - if this command does not output any error or warning and the codec type is acc or h264 then is should not create any issues.
