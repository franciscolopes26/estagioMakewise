import json
import os

from pathlib import Path
from cv2 import cv2


class LoadModel:
    def __init__(self, file_name: str):
        config_file_path =Path(file_name)
        if not config_file_path.is_file():
            raise ValueError("Invalide configuration file: %s" % file_name)
        with open(file_name,'r') as f:
            self.config = json.loads(f.read())
            for s in ['model','config','labels','input_params']:
                if s not in self.config:
                    raise ValueError("Invalide configuration: missing %s" % s)

            self.lables = self.config['labels']
            if 'size' in self.config['input_params']:
                self.size = tuple(self.config['input_params']['size'])
            self.model_file =str(config_file_path.parent.joinpath(self.config['model']));
            self.model_config = str(config_file_path.parent.joinpath(self.config['config']));



    def create(self):
        detection_model = cv2.dnn_DetectionModel(self.model_file, self.model_config)
        if self.size:
            detection_model.setInputSize(self.size)
        if 'input_params' in self.config:
            input_params = self.config['input_params']
            if 'scale' in input_params:
                detection_model.setInputScale(input_params['scale'])
            if 'mean' in input_params:
                detection_model.setInputMean(input_params['mean'])
            if 'swapRB' in input_params:
                detection_model.setInputSwapRB(input_params['swapRB'])
            if 'crop' in input_params:
                detection_model.setInputCrop(input_params['crop'])

        return detection_model

    def get_labels(self):
        return self.lables

    def get_net_input_size(self):
        if self.size :
            return  self.size
        else:
            return None

    def get_label(self,id:int):
        return self.lables[id]

