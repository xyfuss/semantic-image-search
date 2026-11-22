import time


def process_image(image_id: int) -> None:
    print(f"processing image {image_id}")
    time.sleep(3)
    print(f"done with image {image_id}")
