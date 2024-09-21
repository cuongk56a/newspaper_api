
from django.db import connections
import cloudinary
import cloudinary.api
import cloudinary.uploader

import os
from dotenv import load_dotenv

load_dotenv()

import logging
logger = logging.getLogger("project")


class BaseService:
    @staticmethod
    def last_query():
        print(connections["default"].queries)

    @classmethod
    def log_exception(cls, exc, full_trace=True):
        logger.error(exc, exc_info=True, stack_info=full_trace)

    @classmethod
    def log_info(cls, message):
        logger.info(message)

    @classmethod
    def log_debug(cls, message):
        logger.debug(message)

    @classmethod
    def log(cls, message):
        logger.error(message)

    class Meta:
        abstract = True

class CloudinaryService:
    @classmethod
    def upload_avatar_user_image(cls, image):
        return cloudinary.uploader.upload(image, folder=os.getenv('CLOUDINARY_AVATAR_USER_FOLDER'))

    @classmethod
    def delete_image(cls, pub_id):
        return cloudinary.uploader.destroy(pub_id, folder=os.getenv('CLOUDINARY_AVATAR_USER_FOLDER'))
