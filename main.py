import cv2
import pyshine as ps
from HX711 import SimpleHX711, Mass
import threading
import socket

# HTML template for displaying the video stream in a web page
HTML = """<html><head><title>PyShine Live Streaming</title></head><body><center><h1> PyShine Live Streaming using OpenCV </h1></center><center><img src="stream.mjpg" width='640' height='480' autoplay playsinline></center></body></html>"""

# Define the threshold for weight measurement
THRESHOLD_WEIGHT_OZ = 5.0
wifi_server_port = 8500
def video_streaming():
    StreamProps = ps.StreamProps()
    StreamProps.set_Page(StreamProps, HTML)  
    address = ('192.168.25.89', 9000)  
    try:
        StreamProps.set_Mode(StreamProps, 'cv2')  

        capture = cv2.VideoCapture(0)  
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 4)  
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320)  
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)  
        capture.set(cv2.CAP_PROP_FPS, 30)  

        StreamProps.set_Capture(StreamProps, capture)  
        StreamProps.set_Quality(StreamProps, 90)  

        server = ps.Streamer(address, StreamProps)
        print('Server started at', 'http://' + address[0] + ':' + str(address[1]))
        server.serve_forever()

    except KeyboardInterrupt:
        capture.release()
        server.socket.close()

def weight_measurement():
    with SimpleHX711(2, 3, -370, -367471) as hx:
        hx.setUnit(Mass.Unit.GRAM)

        # zero the scale
        hx.zero()

        # Create a socket to send weight data over Wi-Fi
        wifi_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        wifi_socket.connect(('192.168.25.89', wifi_server_port))

        while True:
            weight_oz = hx.weight(35) 

            if weight_oz > THRESHOLD_WEIGHT_OZ:
                print(f'Weight exceeded threshold: {weight_oz} oz')

                # Send the weight data over Wi-Fi
                wifi_socket.send(f'Weight exceeded threshold: {weight_oz} oz'.encode('utf-8'))

if __name__ == '__main__':
    video_thread = threading.Thread(target=video_streaming)
    weight_thread = threading.Thread(target=weight_measurement)

    video_thread.start()
    weight_thread.start()

    video_thread.join()
    weight_thread.join()
