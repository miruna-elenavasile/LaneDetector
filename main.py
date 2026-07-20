import cv2
import numpy as np
cam = cv2.VideoCapture('Lane Detection Test Video 01.mp4')

while True:

    ret, frame = cam.read()

    # ret (bool): Return code of the `read` operation. Did we get an image or not?
    #             (if not maybe the camera is not detected/connected etc.)

    # frame (array): The actual frame as an array.
    #                Height x Width x 3 (3 colors, BGR) if color image.
    #                Height x Width if Grayscale
    #                Each element is 0-255.
    #                You can slice it, reassign elements to change pixels, etc.

    if ret is False:
        break

# task 2-resize
    frame = cv2.resize(frame, (320, 180))
#task 3-grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#task 4-only the road
    mask = np.zeros(gray.shape, dtype=np.uint8)
    height, width = gray.shape
    pt1 = (int(width * 0.58), int(height * 0.60))
    pt2 = (int(width * 0.42), int(height * 0.60))
    pt3 = (int(width * 0.20), height)
    pt4 = (int(width * 0.80), height)
    points = np.array([pt1, pt2, pt3, pt4], dtype=np.int32)
    cv2.fillConvexPoly(mask, points, 1)
    road = gray * mask

#task5- birds eye view
    frame_bounds = np.array([
        (width, 0),  # top right
        (0, 0),  # top left
        (0, height),  # bottom left
        (width, height)  # bottom right
    ], dtype=np.int32)
    trapezoid_bounds = np.float32(points)
    frame_bounds = np.float32(frame_bounds)
    magic_matrix = cv2.getPerspectiveTransform(
        trapezoid_bounds,
        frame_bounds
    )
    top_view = cv2.warpPerspective(
        road,
        magic_matrix,
        (width, height)
    )

#task 6-blur
    blurred = cv2.blur(top_view, ksize=(5, 5))
#task 7-Sobel Edge Detection
    sobel_vertical = np.array([
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1]
    ], dtype=np.float32)
    sobel_horizontal = np.transpose(sobel_vertical)
    blurred_float = np.float32(blurred)
    vertical_edges = cv2.filter2D(
        blurred_float,
        -1,
        sobel_vertical
    )

    horizontal_edges = cv2.filter2D(
        blurred_float,
        -1,
        sobel_horizontal
    )
    edges = np.sqrt(
        vertical_edges ** 2 +
        horizontal_edges ** 2
    )
    edges = cv2.convertScaleAbs(edges)

#task 8-binarizare
    threshold = 115
    _, binary = cv2.threshold(
        edges,
        threshold,
        255,
        cv2.THRESH_BINARY
    )

    cv2.imshow("Binary", binary)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
