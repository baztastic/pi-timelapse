from picamera import PiCamera
import errno
import os
import subprocess
from shutil import copyfile
import sys
import threading
from datetime import datetime
from time import sleep
import yaml

config = yaml.safe_load(open(os.path.join(sys.path[0], "config.yml")))
image_number = 0
os.chdir("/home/pi/pi-timelapse/")

def create_timestamped_dir(dir):
    try:
        os.makedirs(dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def set_camera_options(camera):
    # Set camera resolution.
    if config['resolution']:
        camera.resolution = (
            config['resolution']['width'],
            config['resolution']['height']
        )

    # Set ISO.
    if config['iso']:
        camera.iso = config['iso']

    # Set shutter speed.
    if config['shutter_speed']:
        camera.shutter_speed = config['shutter_speed']
        # Sleep to allow the shutter speed to take effect correctly.
        sleep(1)
        camera.exposure_mode = 'off'

    # Set white balance.
    if config['white_balance']:
        camera.awb_mode = 'off'
        camera.awb_gains = (
            config['white_balance']['red_gain'],
            config['white_balance']['blue_gain']
        )

    # Set camera rotation
    if config['rotation']:
        camera.rotation = config['rotation']

    return camera


def capture_image():
#    try:
        global image_number

        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        print(now, "- Capturing image", str(image_number), "of", str(config['total_images']))

        # Set a timer to take another picture at the proper interval after this
        # picture is taken.
        if (image_number < (config['total_images'] - 1)):
            thread = threading.Timer(config['interval'], capture_image).start()

        # Start up the camera.
        camera = PiCamera()
        set_camera_options(camera)

        # Capture a picture.
        camera.capture(dir + '/image{0:08d}.jpg'.format(image_number))
        camera.close()
        if (image_number % 5 == 0):
            html = "<h3>" + str(image_number) + " " + now + "</h3>\n<img src='image.jpg'>"
            copyfile(dir + '/image{0:08d}.jpg'.format(image_number), 'image.jpg')
            os.system("echo '" + html + "' > timelapse.html")

        if (image_number < (config['total_images'] - 1)):
            image_number += 1
        else:
            print ('\nTime-lapse capture complete!\n')
            # TODO: This doesn't pop user into the except block below :(.
            # sys.exit()

#    except (KeyboardInterrupt):
#        print ("\nTime-lapse capture cancelled.\n")
#    except (SystemExit):
#        print ("\nTime-lapse capture stopped.\n")

#Initialize the path for files to be saved
dir_path = (str(config['dir_path']))

# Create directory based on current timestamp.
dir = os.path.join(
    sys.path[0],
    str(dir_path) +'series-' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
)
# Create directory with current time stamp
create_timestamped_dir(dir)

# Print where the files will be saved
print("\nFiles will be saved in: " + str(dir_path) + str(dir) + "\n")

# Kick off the capture process.
try:
    capture_image()
except KeyboardInterrupt:
    print("\nTime-lapse capture cancelled.\n")
finally:
    print("\nTime-lapse capture stopped.\n")

# TODO: These may not get called after the end of the threading process...
# Create an animated gif (Requires ImageMagick).
if config['create_gif']:
    print ('\nCreating animated gif.\n')
    subprocess.Popen(args=['convert -resize 20% -delay 10 -loop 0 ' + dir + '/image*.jpg ' + dir + '-timelapse.gif'], shell = True)
#    os.system('convert -resize 20% -delay 10 -loop 0 ' + dir + '/image*.jpg ' + dir + '-timelapse.gif')  # noqa

# Create a video (Requires avconv - which is basically ffmpeg).
if config['create_video']:
    print ('\nCreating video.\n')
    os.system('avconv -framerate 20 -i ' + dir + '/image%08d.jpg -vf format=yuv420p ' + dir + '/timelapse.mp4')  # noqa
