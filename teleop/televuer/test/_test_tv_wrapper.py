import os, sys
this_file = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(os.path.dirname(this_file), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import numpy as np
import time
from multiprocessing import shared_memory
from televuer import TeleVuerWrapper
import logging_mp
logging_mp.basicConfig(level=logging_mp.INFO)
logger_mp = logging_mp.getLogger(__name__)


def run_test_tv_wrapper():
    image_shape = (480, 640 * 2, 3)
    image_shm = shared_memory.SharedMemory(create=True, size=np.prod(image_shape) * np.uint8().itemsize)
    image_array = np.ndarray(image_shape, dtype=np.uint8, buffer=image_shm.buf)

    # from image_server.image_client import ImageClient
    # import threading
    # image_client = ImageClient(tv_img_shape = image_shape, tv_img_shm_name = image_shm.name, image_show=True, server_address="127.0.0.1")
    # image_receive_thread = threading.Thread(target = image_client.receive_process, daemon = True)
    # image_receive_thread.daemon = True
    # image_receive_thread.start()
    
    use_hand_track=False
    tv_wrapper = TeleVuerWrapper( use_hand_tracking=use_hand_track, 
                                   return_state_data=True, return_hand_rot_data = True)
    try:
        input("Press Enter to start tv_wrapper test...")
        running = True
        loop_count = 0
        logger_mp.info("=== Starting main loop ===")
        while running:
            loop_count += 1
            start_time = time.time()

            logger_mp.info(f"[Loop {loop_count}] Calling get_motion_state_data()...")
            try:
                teleData = tv_wrapper.get_motion_state_data()
                logger_mp.info(f"[Loop {loop_count}] get_motion_state_data() returned successfully")
            except Exception as e:
                logger_mp.error(f"[Loop {loop_count}] get_motion_state_data() failed with error: {e}")
                import traceback
                logger_mp.error(traceback.format_exc())
                time.sleep(0.1)
                continue

            if teleData is None:
                logger_mp.warning(f"[Loop {loop_count}] teleData is None!")
                time.sleep(0.1)
                continue

            logger_mp.info(f"[Loop {loop_count}] === TeleData Snapshot ===")
            logger_mp.info(f"[Loop {loop_count}] [Head Rotation Matrix]:\n{teleData.head_pose}")
            logger_mp.info(f"[Loop {loop_count}] [Left EE Pose]:\n{teleData.left_arm_pose}")
            logger_mp.info(f"[Loop {loop_count}] [Right EE Pose]:\n{teleData.right_arm_pose}")

            # if use_hand_track:
            #     logger_mp.info(f"[Left Hand Position] shape {teleData.left_hand_pos.shape}:\n{teleData.left_hand_pos}")
            #     logger_mp.info(f"[Right Hand Position] shape {teleData.right_hand_pos.shape}:\n{teleData.right_hand_pos}")
                
            #     if teleData.left_hand_rot is not None:
            #         logger_mp.info(f"[Left Hand Rotation] shape {teleData.left_hand_rot.shape}:\n{teleData.left_hand_rot}")
            #     if teleData.right_hand_rot is not None:
            #         logger_mp.info(f"[Right Hand Rotation] shape {teleData.right_hand_rot.shape}:\n{teleData.right_hand_rot}")
                
            #     if teleData.left_pinch_value is not None:
            #         logger_mp.info(f"[Left Pinch Value]: {teleData.left_pinch_value:.2f}")
            #     if teleData.right_pinch_value is not None:
            #         logger_mp.info(f"[Right Pinch Value]: {teleData.right_pinch_value:.2f}")
                
            #     if teleData.tele_state:
            #         state = teleData.tele_state
            #         logger_mp.info("[Hand State]:")
            #         logger_mp.info(f"  Left Pinch state: {state.left_pinch_state}")
            #         logger_mp.info(f"  Left Squeeze: {state.left_squeeze_state} ({state.left_squeeze_value:.2f})")
            #         logger_mp.info(f"  Right Pinch state: {state.right_pinch_state}")
            #         logger_mp.info(f"  Right Squeeze: {state.right_squeeze_state} ({state.right_squeeze_value:.2f})")
            # else:
            #     logger_mp.info(f"[Left Trigger Value]: {teleData.left_trigger_value:.2f}")
            #     logger_mp.info(f"[Right Trigger Value]: {teleData.right_trigger_value:.2f}")
                
            #     if teleData.tele_state:
            #         state = teleData.tele_state
            #         logger_mp.info("[Controller State]:")
            #         logger_mp.info(f"  Left Trigger: {state.left_trigger_state}")
            #         logger_mp.info(f"  Left Squeeze: {state.left_squeeze_ctrl_state} ({state.left_squeeze_ctrl_value:.2f})")
            #         logger_mp.info(f"  Left Thumbstick: {state.left_thumbstick_state} ({state.left_thumbstick_value})")
            #         logger_mp.info(f"  Left A/B Buttons: A={state.left_aButton}, B={state.left_bButton}")
            #         logger_mp.info(f"  Right Trigger: {state.right_trigger_state}")
            #         logger_mp.info(f"  Right Squeeze: {state.right_squeeze_ctrl_state} ({state.right_squeeze_ctrl_value:.2f})")
            #         logger_mp.info(f"  Right Thumbstick: {state.right_thumbstick_state} ({state.right_thumbstick_value})")
            #         logger_mp.info(f"  Right A/B Buttons: A={state.right_aButton}, B={state.right_bButton}")

            current_time = time.time()
            time_elapsed = current_time - start_time
            sleep_time = max(0, 0.033 - time_elapsed)
            time.sleep(sleep_time)
            logger_mp.debug(f"main process sleep: {sleep_time}")

    except KeyboardInterrupt:
        running = False
        logger_mp.warning("KeyboardInterrupt, exiting program...")
    finally:
        image_shm.unlink()
        image_shm.close()
        logger_mp.warning("Finally, exiting program...")
        exit(0)

if __name__ == '__main__':
    run_test_tv_wrapper()