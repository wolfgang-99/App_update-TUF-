# from pymongo.mongo_client import MongoClient
#
# import os
# from dotenv import load_dotenv
# import gridfs
# from bson import ObjectId
# import hashlib
#
#
# load_dotenv()
# MONGODB_URL = os.getenv("MONGODB_URL")
# client = MongoClient(MONGODB_URL)
# db = client["tuf_repo"]
#
# # Create GridFS instance
# fs = gridfs.GridFS(db)
#
# def upload_file(file_path, category):
#     """
#     Uploads a file to MongoDB GridFS.
#
#     :param file_path: Path to the file to be uploaded.
#     :return: ID of the stored file in GridFS.
#     """
#
#     if category not in ["metadata", "targets"]:
#         print("select a valid category")
#         return
#
#     try:
#         # Open the file in binary mode
#         with open(file_path, "rb") as file:
#             file_data = file.read()
#             sha256_hash = hashlib.sha256(file_data).hexdigest()
#             hash_filename = f"{category}/{sha256_hash}.{file_path.split('/')[-1]}"
#
#             # Store the file in GridFS
#             file_id = fs.put(file_data, filename=hash_filename)
#             print(f"File uploaded successfully with ID: {file_id}")
#             return file_id
#     except Exception as e:
#         print(f"An error occurred: {e}")
#
#
# def download_file(file_id, output_path):
#     """
#     Downloads a file from MongoDB GridFS.
#
#     :param file_id: ID of the file in GridFS.
#     :param output_path: Path to save the downloaded file.
#     """
#     try:
#         # Retrieve the file from GridFS
#         file_data = fs.get(file_id)
#         with open(output_path, "wb") as file:
#             file.write(file_data.read())
#         print(f"File downloaded successfully to: {output_path}")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#
# # Example usage
# # file_id = "675bd653a802140934048f70"
# # file_id = ObjectId(file_id)
# # output_path = "timestamp.json"
# # download_file(file_id, output_path)
#
# file_path = "./server/file.txt"
# upload_file(file_path, category="targets")
#
# # data = db.fs.files.find({"filename": {"$regex": "root.*"}})
# # print(data)
# #
# # file = fs.find_one({"filename": "1.root.json"})
# # file = file.read()
# # print(file)
# #



import requests

url = "http://127.0.0.1:8001/upload"
file_path = "file.txt"
category = "targets"
with open(file_path, "rb") as file:
    file = {"file": file}
    payload = {"category":category }
    res = requests.post(url=url, files=file, data=payload)
    print(res)