import cv2
import argparse

def create_masked_image(image_path,  x1, y1, x2, y2):
    # Load the image
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Could not load the image from {image_path}")
        return None
    
    # Define the coordinates of the text region (top-left and bottom-right)
    x1, y1, x2, y2 = x1, y1, x2, y2

    # Create a mask with the same dimensions as the image
    mask = image.copy()
    cv2.rectangle(mask, (x1, y1), (x2, y2), (0, 0, 0), -1)

    # Apply the mask to the original image
    masked_image = cv2.bitwise_and(image, mask)

    return masked_image

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a masked image from an input image with specified coordinates.")
    parser.add_argument("image_path", help="Path to the input image file")
    parser.add_argument("x1", type=int, help="x1 coordinate")
    parser.add_argument("y1", type=int, help="y1 coordinate")
    parser.add_argument("x2", type=int, help="x2 coordinate")
    parser.add_argument("y2", type=int, help="y2 coordinate")

    args = parser.parse_args()

    masked_image = create_masked_image(args.image_path, args.x1, args.y1, args.x2, args.y2)

    if masked_image is not None:
        cv2.imshow("Masked Image", masked_image)
        cv2.imwrite("output.jpg", masked_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()