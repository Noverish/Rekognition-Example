# AWS Rekognition Example for Face Recognition

## How To Use

### 1\. Prepare images

You have to prepare two folders.    
One is to train, and the other is to recognize faces.

##### face image folder
```
example directory structure

face_src
|---john.jpg
|---emily.jpg
|---james.jpg
|---park.jpg
...
```
Every image have to contain exactly ONE face    
The name of image is used for labeling faces    
Do not make sub folder

##### input image folder
The images in this folder is to recognize faces


### 2\. Modify config.json

```json
{
  "profile": "noverish",
  "bucket_name": "rekognition-example",
  "bucket_region": "ap-northeast-2",
  "face_src": "./faces",
  "img_src": "./inputs",
  "collection_id": "test_collection"
}
```
**profile** : your aws profile name which is in ~/.aws/credential    
**bucket_name** : name of bucket to save your face images    
**bucket_region** : region of bucket    
**face_src** : relative/absolute path of folder which is consist of face images    
**img_src** : relative/absolute path of folder which is consist of image to recognize faces    
**collection_id** : collection id which is used for rekognition api    

### 3\. Modify code

'process_results' function in main.py handles result of face recognition

**parameters**    
img_path : absolute path of image    
image : Pillow Image    
results : dict array. detail is in below    
```
[
    {
        'left': integer,
        'top': integer,
        'width': integer,
        'height': integer,
        'name': string | null,
        'similarity': double | null,
    }
]
```

### 4\. Run
```shell
$ python3 main.py
```