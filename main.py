from boto3.session import Session
from sys import exit
from os import walk, makedirs
from os.path import join, basename, normpath, dirname, exists
from PIL import Image, ImageDraw
import datetime
import json

from src.s3 import create_bucket, bucket_exists
from src.rekognition import collection_exists, create_collection, upload_face
from src.rekognition.recognize import recognize_face




def process_results(img_path, image, results):
    draw = ImageDraw.Draw(image)

    for result in results:
        left = result['left']
        top = result['top']
        width = result['width']
        height = result['height']

        rect = [left, top, left + width, top + height]
        draw.rectangle(rect, outline="red")

        pos = (left, top + height)
        text = result['name'] + ' ' + str(result['similarity'])
        draw.text(pos, text)

    rel_path = img_path.replace(normpath(config['img_src']), "")[1:]
    save_path = join('outputs', rel_path)
    save_dir = dirname(save_path)

    if not exists(save_dir):
        makedirs(save_dir)

    image.save(save_path, "JPEG")

    print(current_timestamp(), img_path, '({}/{})'.format(i, len(img_paths)))


def current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def is_image(img_path):
    file_name = basename(img_path)
    ext = file_name.split(".")[-1]
    return ext.lower() in ['jpg', 'png', 'jpeg']


if __name__ == '__main__':
    with open('config.json') as f:
        config = json.loads(f.read())

    bucket_name = config['bucket_name']
    bucket_region = config['bucket_region']
    face_dir_path = config['face_src']
    collection_id = config['collection_id']

    session = Session(profile_name=config['profile'])
    rekognition = session.client('rekognition')
    s3 = session.client('s3')

    # Check bucket exist. create it if not exist
    if not bucket_exists(s3, bucket_name):
        success = create_bucket(s3, bucket_name, bucket_region)
        if not success:
            exit(0)

    # Check collection exist. create it if not exist
    if not collection_exists(rekognition, collection_id):
        create_collection(rekognition, collection_id)

    # Get face image list
    face_paths = []
    for root, dirs, files in walk(config['face_src']):
        for name in files:
            path = join(root, name)
            if is_image(path):
                face_paths.append(path)
    face_paths.sort()

    # Upload face image to s3
    for i, face_path in enumerate(face_paths):
        key = face_path.replace(normpath(config['face_src']), "")[1:]
        s3.upload_file(face_path, bucket_name, key)
        print(current_timestamp(), "Uploaded face image to S3 - {} ({}/{})".format(key, i + 1, len(face_paths)))

    # Put face image(s3 object) to collection
    for i, face_path in enumerate(face_paths):
        key = face_path.replace(normpath(config['face_src']), "")[1:]
        upload_face(rekognition, collection_id, bucket_name, key)
        print(current_timestamp(), "Put face to collection - {} ({}/{})".format(key, i + 1, len(face_paths)))

    # Get image list
    img_paths = []
    for root, dirs, files in walk(config['img_src']):
        for name in files:
            path = join(root, name)
            if is_image(path):
                img_paths.append(path)
    img_paths.sort()

    # Search face
    for i, img_path in enumerate(img_paths):
        image = Image.open(img_path)

        results = recognize_face(rekognition, collection_id, image)

        process_results(img_path, image, results)
