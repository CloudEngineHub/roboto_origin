import os, sys
this_file = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(os.path.dirname(this_file), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import time
import numpy as np
from multiprocessing import shared_memory
from televuer import TeleVuer
import logging_mp
logging_mp.basicConfig(level=logging_mp.INFO)
logger_mp = logging_mp.getLogger(__name__)

def run_test_TeleVuer():
    # image

    # from image_server.image_client import ImageClient
    # import threading
    # image_client = ImageClient(tv_img_shape = image_shape, tv_img_shm_name = image_shm.name, image_show=True, server_address="127.0.0.1")
    # image_receive_thread = threading.Thread(target = image_client.receive_process, daemon = True)
    # image_receive_thread.daemon = True
    # image_receive_thread.start()

    # xr-mode
    use_hand_track = False
    tv = TeleVuer( use_hand_tracking = use_hand_track, webrtc=False)

    try:
        input("Press Enter to start TeleVuer test...")
        running = True
        while running:
            logger_mp.info("=" * 80)
            logger_mp.info("Position Data:")
            logger_mp.info(f"head_pose: {tv.head_pose}")
            logger_mp.info(f"left_arm_pose: {tv.left_arm_pose}")
            logger_mp.info(f"right_arm_pose: {tv.right_arm_pose}")
            logger_mp.info("=" * 80)

            if use_hand_track:
                logger_mp.info("Hand Tracking Data:")
                logger_mp.info(f"left_hand_positions shape: {tv.left_hand_positions.shape}\n{tv.left_hand_positions}\n")
                logger_mp.info(f"right_hand_positions shape: {tv.right_hand_positions.shape}\n{tv.right_hand_positions}\n")
                logger_mp.info(f"left_hand_orientations shape: {tv.left_hand_orientations.shape}\n{tv.left_hand_orientations}\n")
                logger_mp.info(f"right_hand_orientations shape: {tv.right_hand_orientations.shape}\n{tv.right_hand_orientations}\n")
                logger_mp.info(f"left_hand_pinch_state: {tv.left_hand_pinch_state}")
                logger_mp.info(f"left_hand_pinch_value: {tv.left_hand_pinch_value}")
                logger_mp.info(f"left_hand_squeeze_state: {tv.left_hand_squeeze_state}")
                logger_mp.info(f"left_hand_squeeze_value: {tv.left_hand_squeeze_value}")
                logger_mp.info(f"right_hand_pinch_state: {tv.right_hand_pinch_state}")
                logger_mp.info(f"right_hand_pinch_value: {tv.right_hand_pinch_value}")
                logger_mp.info(f"right_hand_squeeze_state: {tv.right_hand_squeeze_state}")
                logger_mp.info(f"right_hand_squeeze_value: {tv.right_hand_squeeze_value}")
            else:
                # Controller thumbstick positions (for control)
                logger_mp.info(f"left_controller_thumbstick_value: {tv.left_controller_thumbstick_value}")
                logger_mp.info(f"right_controller_thumbstick_value: {tv.right_controller_thumbstick_value}")
            logger_mp.info("=" * 80)
            time.sleep(0.03)
            # time.sleep(1)
    except KeyboardInterrupt:
        running = False
        logger_mp.warning("KeyboardInterrupt, exiting program...")
    finally:
        image_shm.unlink()
        image_shm.close()
        logger_mp.warning("Finally, exiting program...")
        exit(0)

if __name__ == '__main__':
    run_test_TeleVuer()