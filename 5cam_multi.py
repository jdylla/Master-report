import os
from datetime import datetime
import cv2
from vimba import Vimba, PixelFormat, Camera
import multiprocessing
import time

def capture_callback(cam: Camera, frame):
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    filename = f"{timestamp}_cam_{cam.get_id()}.png"
    parent_directory = cam.parent_directory
    image_path = os.path.join(parent_directory, filename)

    frame.convert_pixel_format(PixelFormat.Mono8)
    image = frame.as_opencv_image()
    cv2.imwrite(image_path, image)
    print(f"Image saved at {image_path}")

def capture_image(cam_id, exposure_time, parent_directory):
    with Vimba.get_instance() as vmb:
        cam = vmb.get_camera_by_id(cam_id)
        with cam:
            cam.ExposureTime.set(exposure_time)
            cam.TriggerSource.set('Software')
            cam.TriggerMode.set('On')
            cam.TriggerSelector.set('FrameStart')
            cam.parent_directory = parent_directory  # Store parent directory for later use
            cam.start_streaming(handler=capture_callback)
            cam.TriggerSoftware.run()
            cam.stop_streaming()

def capture_images_for_exposure(vmb, exposure_time, parent_directory):
    cams = vmb.get_all_cameras()
    processes = []
    for cam in cams:
        p = multiprocessing.Process(target=capture_image, args=(cam.get_id(), exposure_time, parent_directory))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

def main():
    with Vimba.get_instance() as vmb:
        cams = vmb.get_all_cameras()
        if len(cams) != 5:
            print(f"Error: Expected 5 cameras but found {len(cams)}.")
            return

        print(f"{len(cams)} cameras connected.")
        for cam in cams:
            print(f"- {cam.get_id()}")

        # Set the parent directory to the specified path
        parent_directory = "./"
        os.makedirs(parent_directory, exist_ok=True)

        exposure_times = [800, 1300, 1500]

        proceed_with_capture = 'yes'  # Proceed with capture automatically
        if proceed_with_capture == 'yes':
            for exposure_time in exposure_times:
                print(f"Capturing images with exposure time: {exposure_time}")
                capture_images_for_exposure(vmb, exposure_time, parent_directory) 
if __name__ == "__main__":
    main()
