import cv2

img = cv2.imread('C:/Users/ragha/Documents/OcEO/smart-food-management/load_cell.jpg')
cv2.imshow("image",img)
cv2.waitKey(0)
cv2.destroyAllWindows()
print(img)