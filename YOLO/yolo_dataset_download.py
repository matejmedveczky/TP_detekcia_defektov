import os
from dotenv import load_dotenv
from roboflow import Roboflow

load_dotenv()
api_key = os.getenv("ROBOFLOW_API_KEY")

def download_dataset():
    rf = Roboflow(api_key=api_key)
    project = rf.workspace("hemorrhagesegmentation").project("tp26_detection")
    version = project.version(1)
    dataset = version.download("yolov11")

    return dataset, version, project 
                