import cv2
import argparse

def create_masked_image(image_path, coordinates):
    # Load the image
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Could not load the image from {image_path}")
        return None
    
    # Create a mask with the same dimensions as the image
    mask = image.copy()

    # Iterate through the list of coordinates and draw rectangles on the mask
    for coord in coordinates:
        x1, y1, x2, y2 = coord
        cv2.rectangle(mask, (x1, y1), (x2, y2), (0, 0, 0), -1)

    # Apply the mask to the original image
    masked_image = cv2.bitwise_and(image, mask)

    return masked_image

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a masked image from an input image with specified coordinates.")
    parser.add_argument("image_path", help="Path to the input image file")
    parser.add_argument("coordinates_file", help="Path to a text file containing coordinates (x1, y1, x2, y2) on each line")
    parser.add_argument("output_image", help="Path to save the masked image")
    
    args = parser.parse_args()

    # Read the coordinates from the file
    coordinates = []
    with open(args.coordinates_file, 'r') as file:
        for line in file:
            x1, y1, x2, y2 = map(int, line.strip().split())
            coordinates.append((x1, y1, x2, y2))

    masked_image = create_masked_image(args.image_path, coordinates)

    if masked_image is not None:
        cv2.imwrite(args.output_image, masked_image)
        cv2.imshow("Masked Image", masked_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
