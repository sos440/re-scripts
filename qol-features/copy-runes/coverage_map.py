from PIL import Image, ImageDraw
import json


def overlay_squares_on_map(map_path: str, output_path: str, json_srcs: list[str], opacity: int = 128):
    """
    Overlays semi-transparent white squares onto a map image.

    Args:
        map_path (str): Path to the input map image (e.g., 'map.png').
        output_path (str): Path to save the resulting image (e.g., 'map_with_overlay.png').
        centers (list): A list of (x, y) tuples for the center of each square.
        square_size (int): The side length of the squares in pixels.
        opacity (int): The opacity of the squares, from 0 (transparent) to 255 (opaque).
    """
    try:
        # Load centers from JSON files
        centers = []
        for json_src in json_srcs:
            with open(json_src, "r") as f:
                data = json.load(f)
                for entry in data:
                    centers.append(entry["position"])

        # Open the base map image and ensure it's in RGBA mode for transparency
        base_image = Image.open(map_path).convert("RGBA")

        # Create a new, fully transparent image of the same size as the map
        # This will be our drawing layer.
        overlay = Image.new("RGBA", base_image.size, (255, 255, 255, 0))

        # Create a drawing context for the overlay layer
        draw = ImageDraw.Draw(overlay)

        # Define the semi-transparent white color
        # Format is (Red, Green, Blue, Alpha/Opacity)
        fill_color = (255, 255, 255, opacity)

        # Draw each square on the overlay layer
        for cx, cy in centers:
            # Calculate the top-left and bottom-right corners from the center
            x1 = cx - 99
            y1 = cy - 99
            x2 = cx + 100
            y2 = cy + 100

            draw.rectangle([(x1, y1), (x2, y2)], fill=fill_color)

        # Composite the overlay onto the base map image using alpha blending
        combined_image = Image.alpha_composite(base_image, overlay)

        # Save the final image
        combined_image.save(output_path)
        print(f"✅ Successfully saved the image to {output_path}")

        # Optionally, display the image
        # combined_image.show()

    except FileNotFoundError:
        print(f"❌ Error: The file at {map_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


# --- --- --- EXAMPLE USAGE --- --- ---
if __name__ == "__main__":
    overlay_squares_on_map(
        map_path="assets/map_1.png",
        output_path="outputs/map_1.png",
        json_srcs=[f"assets/idoc_tram_{i}.json" for i in range(1, 7)],
        opacity=100,
    )

    overlay_squares_on_map(
        map_path="assets/map_3.png",
        output_path="outputs/map_3.png",
        json_srcs=[f"assets/idoc_malas_{i}.json" for i in range(1, 3)],
        opacity=100,
    )