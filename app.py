# from flask import Flask, request, jsonify
# import argparse
# import sys
# from pathlib import Path

# from src.entry import entry_point
# from src.logger import logger


# app = Flask(__name__)
# import os
# import urllib.request
# import shutil
# import json
# import requests
# from urllib.parse import urlparse
# def create_folder(folder_path):
#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)

# def save_file_from_url(url, file_path):
#     try:
#         response = requests.get(url)
#         file_name = os.path.basename(urlparse(url).path)
#         file_path = os.path.join(file_path, file_name)

#         with open(file_path, 'wb') as file:
#             file.write(response.content)
        
#         print(f"File saved successfully at '{file_path}'.")
#     except Exception as e:
#         print(f"Error saving file: {str(e)}")

    
    

# def parse_args_from_payload(payload):
#     argparser = argparse.ArgumentParser()

#     argparser.add_argument(
#         "-i",
#         "--inputDir",
#         default=payload.get("input_paths", ["inputs"]),
#         nargs="*",
#         required=False,
#         type=str,
#         dest="input_paths",
#         help="Specify an input directory.",
#     )

#     argparser.add_argument(
#         "-d",
#         "--debug",
#         required=False,
#         dest="debug",
#         action="store_false",
#         help="Enables debugging mode for showing detailed errors",
#     )

#     argparser.add_argument(
#         "-o",
#         "--outputDir",
#         default=payload.get("output_dir", "outputs"),
#         required=False,
#         dest="output_dir",
#         help="Specify an output directory.",
#     )

#     argparser.add_argument(
#         "-a",
#         "--autoAlign",
#         required=False,
#         dest="autoAlign",
#         action="store_true",
#         help="(experimental) Enables automatic template alignment - \
#         use if the scans show slight misalignments.",
#     )

#     argparser.add_argument(
#         "-l",
#         "--setLayout",
#         required=False,
#         dest="setLayout",
#         action="store_true",
#         help="Set up OMR template layout - modify your json file and \
#         run again until the template is set.",
#     )

#     args = vars(argparser.parse_args([]))  # Replace '[]' with actual arguments

#     return args


# @app.route('/', methods=['GET'])
# def index():
#      return "If You can see This message You are in Matrix. Escape it. They are using You"




# @app.route('/outputs/<path:filename>')
# def serve_output_file(filename):
#     from flask import send_from_directory
#     return send_from_directory('outputs/CheckedOMRs', filename)

# @app.route('/omrchecker', methods=['POST'])
# def omr_checker():
#     payload = request.get_json()
    
#     args = parse_args_from_payload(payload)
    
#     url = payload['url']
#     folder_name = payload['folder_name']
#     templete = payload['templete']
#     fileName = payload['fileName']


#     # Specify the path of the parent folder



#     # Check if the folder exists
#     current_directory = os.getcwd()
#     inputs_folder = os.path.join(current_directory, "inputs")
#     outputs_folder = os.path.join(current_directory, "outputs")
#     folder_path = os.path.join(inputs_folder, folder_name+"/")
#     if os.path.exists(folder_path):
#             # If the folder exists, delete it and its contents recursively
#             shutil.rmtree(folder_path)
#             print(f"Folder '{os.path.abspath(folder_path)}' deleted.")

#         # Create the folder
#     os.makedirs(folder_path)
    
#     # Save the file from the URL into the created folder
#     save_file_from_url(url, folder_path)
    
#     # Print a message indicating that the folder has been created
#     print(f"Folder '{folder_path}' created.")

#     #     # Write the JSON object to the file
#     with open(folder_path+"/"+"template.json", 'w') as file:
#         json.dump(templete, file)


#     file_name = 'template.json'

#     try:
#         with open(folder_path, 'w') as file:
#             # Perform operations on the file here
#                 json.dump(data, file)

#         print(f"File '{folder_path}' created successfully!")
#     except OSError as e:
#         print(f"An error occurred while creating file '{folder_path}': {e}")
#         try:        
#             response_dict=entry_point_for_args(args)
#             sorted_dict = {key[1:]: value for key, value in sorted(response_dict.items())}

#             file_url = f"{request.url_root}outputs/{fileName}"
#             return jsonify({"status":200,"message":"success",'data': sorted_dict,"file_url":file_url})

#         except :
#             return jsonify({"status":400,'message': "cannot Read Data From Image","data":{}})

# def entry_point_for_args(args):
#     if args["debug"] is True:
#         sys.tracebacklimit = 0
#     for root in args["input_paths"]:
#         return entry_point(Path(root), args)

# if __name__ == '__main__':
#     app.run(debug=True,host='0.0.0.0', port=5050)
from flask import Flask, request, jsonify
import argparse
import sys
from pathlib import Path

from src.entry import entry_point
from src.logger import logger

import os
import shutil
import json
import requests
from urllib.parse import urlparse
import cv2
import numpy as np
from skimage.filters import threshold_sauvola

app = Flask(__name__)

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def SauvolaModBinarization(image, n1=51, n2=51, k1=0.3, k2=0.3, default=True):
    '''
    Binarization using Sauvola's algorithm
    @name : SauvolaModBinarization
    parameters
    @param image (numpy array of shape (3/1) of type np.uint8): color or gray scale image
    optional parameters
    @param n1 (int) : window size for running sauvola during the first pass
    @param n2 (int): window size for running sauvola during the second pass
    @param k1 (float): k value corresponding to sauvola during the first pass
    @param k2 (float): k value corresponding to sauvola during the second pass
    @param default (bool) : boolean variable to set the above parameter as default.

    @param default is set to True : thus default values of the above optional parameters (n1,n2,k1,k2) are set to
    n1 = 5 % of min(image height, image width)
    n2 = 10 % of min(image height, image width)
    k1 = 0.5
    k2 = 0.5
    Returns
    @return A binary image of same size as @param image

    @cite https://drive.google.com/file/d/1D3CyI5vtodPJeZaD2UV5wdcaIMtkBbdZ/view?usp=sharing
    '''

    if default:
        n1 = int(0.05 * min(image.shape[0], image.shape[1]))
        if n1 % 2 == 0:
            n1 = n1 + 1
        n2 = int(0.1 * min(image.shape[0], image.shape[1]))
        if n2 % 2 == 0:
            n2 = n2 + 1
        k1 = 0.5
        k2 = 0.5
    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = np.copy(image)
    T1 = threshold_sauvola(gray, window_size=n1, k=k1)
    max_val = np.amax(gray)
    min_val = np.amin(gray)
    C = np.copy(T1)
    C = C.astype(np.float32)
    C[gray > T1] = (gray[gray > T1] - T1[gray > T1]) / (max_val - T1[gray > T1])
    C[gray <= T1] = 0
    C = C * 255.0
    new_in = np.copy(C.astype(np.uint8))
    T2 = threshold_sauvola(new_in, window_size=n2, k=k2)
    binary = np.copy(gray)
    binary[new_in <= T2] = 0
    binary[new_in > T2] = 255
    return binary

def save_file_from_url(url, file_path):
    try:
        response = requests.get(url)
        image = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_COLOR)  # Load image from response content

        # Apply image enhancement
        enhanced_image = SauvolaModBinarization(image)

        file_name = os.path.basename(urlparse(url).path)
        file_path = os.path.join(file_path, file_name)

        # Save the enhanced image
        cv2.imwrite(file_path, enhanced_image)

        print(f"File saved successfully at '{file_path}'.")
    except Exception as e:
        print(f"Error saving file: {str(e)}")

def parse_args_from_payload(payload):
    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "-i",
        "--inputDir",
        default=payload.get("input_paths", ["inputs"]),
        nargs="*",
        required=False,
        type=str,
        dest="input_paths",
        help="Specify an input directory.",
    )

    argparser.add_argument(
        "-d",
        "--debug",
        required=False,
        dest="debug",
        action="store_false",
        help="Enables debugging mode for showing detailed errors",
    )

    argparser.add_argument(
        "-o",
        "--outputDir",
        default=payload.get("output_dir", "outputs"),
        required=False,
        dest="output_dir",
        help="Specify an output directory.",
    )

    argparser.add_argument(
        "-a",
        "--autoAlign",
        required=False,
        dest="autoAlign",
        action="store_true",
        help="(experimental) Enables automatic template alignment - \
        use if the scans show slight misalignments.",
    )

    argparser.add_argument(
        "-l",
        "--setLayout",
        required=False,
        dest="setLayout",
        action="store_true",
        help="Set up OMR template layout - modify your json file and \
        run again until the template is set.",
    )

    args = vars(argparser.parse_args([]))  # Replace '[]' with actual arguments

    return args


@app.route('/', methods=['GET'])
def index():
     return "If You can see This message You are in Matrix. Escape it. They are using You"

@app.route('/outputs/<path:filename>')
def serve_output_file(filename):
    from flask import send_from_directory
    return send_from_directory('outputs/CheckedOMRs', filename)

@app.route('/omrchecker', methods=['POST'])
def omr_checker():
    payload = request.get_json()
    
    args = parse_args_from_payload(payload)
    
    url = payload['url']
    folder_name = payload['folder_name']
    templete = payload['templete']
    fileName = payload['fileName']


    # Specify the path of the parent folder

    # Check if the folder exists
    current_directory = os.getcwd()
    inputs_folder = os.path.join(current_directory, "inputs")
    outputs_folder = os.path.join(current_directory, "outputs")
    folder_path = os.path.join(inputs_folder, folder_name+"/")
    if os.path.exists(folder_path):
        # If the folder exists, delete it and its contents recursively
        shutil.rmtree(folder_path)
        print(f"Folder '{os.path.abspath(folder_path)}' deleted.")

    # Create the folder
    os.makedirs(folder_path)
    
    # Save the file from the URL into the created folder
    save_file_from_url(url, folder_path)
    
    # Print a message indicating that the folder has been created
    print(f"Folder '{folder_path}' created.")

    # Write the JSON object to the file
    with open(os.path.join(folder_path, "template.json"), 'w') as file:
        json.dump(templete, file)

    file_name = 'template.json'

    try:
        with open(os.path.join(folder_path, "template.json"), 'w') as file:
            # Perform operations on the file here
            json.dump(data, file)

        print(f"File '{folder_path}' created successfully!")
    except OSError as e:
        print(f"An error occurred while creating file '{folder_path}': {e}")
        try:        
            response_dict = entry_point_for_args(args)
            sorted_dict = {key[1:]: value for key, value in sorted(response_dict.items())}

            file_url = f"{request.url_root}outputs/{fileName}"
            return jsonify({"status": 200, "message": "success", 'data': sorted_dict, "file_url": file_url})

        except Exception as e:
            print(f"Error processing OMR: {str(e)}")
            return jsonify({"status": 400, 'message': "cannot Read Data From Image", "data": {}})

def entry_point_for_args(args):
    if args["debug"] is True:
        sys.tracebacklimit = 0
    for root in args["input_paths"]:
        return entry_point(Path(root), args)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
