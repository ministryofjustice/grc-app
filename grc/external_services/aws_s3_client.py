import io
import base64
import logging
import boto3
from flask import current_app
from botocore.client import Config
from grc.utils.logger import LogLevel, Logger

logger = Logger()


class AwsS3Client:
    def __init__(self, external=False):
        self.external = external
        self.s3 = boto3.client(
            's3',
            region_name=current_app.config.get('AWS_REGION'),
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = current_app.config.get('BUCKET_NAME')

    def upload_fileobj(self, file, object_name):
        try:
            file.seek(0)
            self.s3.upload_fileobj(file, self.bucket_name, object_name)

        except Exception as e:
            logging.error(e)
            logger.log(LogLevel.ERROR, e)
            return False

        return True

    def download_object_data(self, object_name):
        data = None
        width = 0
        height = 0

        try:
            file_type = ''
            if '.' in object_name:
                file_type = object_name[object_name.rindex('.') + 1:].lower()

            if file_type in ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'bmp']:
                byte_value = self.download_object(object_name)
                if byte_value is not None:
                    from PIL import Image
                    img = Image.open(byte_value)
                    width, height = img.size

                    byte_value = byte_value.getvalue()

                    if file_type in ['tif', 'tiff', 'bmp']:
                        jpg = io.BytesIO()
                        img.save(jpg, 'JPEG', quality=80)
                        byte_value = jpg.getvalue()
                        jpg.close()
                        file_type = 'jpeg'

                    byte_base64 = base64.b64encode(byte_value)
                    data = byte_base64.decode('utf-8')
                    if data:
                        if file_type == 'jpg':
                            file_type = 'jpeg'
                        data = 'data:image/' + file_type + ';base64, ' + data

        except Exception as e:
            logging.error(e)
            logger.log(LogLevel.ERROR, e)
            data = None
            width = 0
            height = 0

        return data, width, height

    def download_object(self, object_name):
        logger.log(LogLevel.INFO, f"Downloading {object_name}")
        data = None
        try:
            bytes_buffer = io.BytesIO()
            self.s3.download_fileobj(Bucket=self.bucket_name, Key=object_name, Fileobj=bytes_buffer)
            data = bytes_buffer

        except Exception as e:
            logging.error(e)
            logger.log(LogLevel.ERROR, e)
            data = None

        return data

    def stream_upload_object(self, file, object_name):
        from smart_open import open

        try:
            url = f's3://{self.bucket_name}/{object_name}'
            with open(url, 'wb', transport_params={'client': self.s3}) as fout:     # transport_params={'client': self.s3, 'multipart_upload_kwargs': {'ServerSideEncryption': 'aws:kms', 'SSEKMSKeyId': key}}
                for data in file:
                    fout.write(data)

        except Exception as e:
            logging.error(e)
            logger.log(LogLevel.ERROR, e)
            return False

        return True

    def stream_download_object(self, object_name):
        try:
            infile_object = self.s3.get_object(Bucket=self.bucket_name, Key=object_name)
            yield infile_object.get('Body', '').read()

        except Exception as e:
            logging.error(e)
            logger.log(LogLevel.ERROR, message=f'{e}')
            return False

        return True

    def delete_object(self, object_name):
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_name)

        except Exception as e:
            logging.error(e)
            logger.log(LogLevel.ERROR, message=f'{e}')
            return False

        return True

    def list_objects(self):
        try:
            files_info = []
            continuationToken = None
            is_complete = False

            while not is_complete:
                if continuationToken:
                    response = self.s3.list_objects_v2(Bucket=self.bucket_name, ContinuationToken=continuationToken)
                else:
                    response = self.s3.list_objects_v2(Bucket=self.bucket_name)

                files_info.extend(response['Contents'])
                if response['IsTruncated']:
                    continuationToken = response['NextContinuationToken']
                else:
                    is_complete = True

            return files_info

        except Exception as e:
            logging.error(e)
            logger.log(LogLevel.ERROR, message=f'{e}')
            return []
