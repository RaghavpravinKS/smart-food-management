import cv2
import pyshine as ps

HTML = './index.html'

def read_html_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()
    
def main():
    StreamProps = ps.StreamProps
    html_content = read_html_file(HTML)
    StreamProps.set_Page(StreamProps, html_content) 
    address = ('10.7.61.104', 9000) 

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

if __name__ == '__main__':
    main()
