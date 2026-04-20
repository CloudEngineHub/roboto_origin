# Modified from Unitree xr_teleoperate for Atom robot teleoperation.
from pathlib import Path

import casadi
import meshcat.geometry as mg
import numpy as np
import pinocchio as pin
from pinocchio import casadi as cpin
from pinocchio.visualize import MeshcatVisualizer

import logging_mp

from teleop.utils.weighted_moving_filter import WeightedMovingFilter


logger_mp = logging_mp.getLogger(__name__)


def _asset_paths(unit_test: bool) -> tuple[str, str]:
    repo_root = Path(__file__).resolve().parents[2]
    if unit_test:
        repo_root = repo_root.parent
    urdf_path = repo_root / "assets" / "Atom01_urdf" / "urdf" / "atom01.urdf"
    meshes_path = repo_root / "assets" / "Atom01_urdf" / "meshes"
    return str(urdf_path), str(meshes_path)


class Atom_23_ArmIK:
    def __init__(self, Unit_Test: bool = False, Visualization: bool = False):
        np.set_printoptions(precision=5, suppress=True, linewidth=200)

        self.Unit_Test = Unit_Test
        self.Visualization = Visualization

        urdf_path, meshes_path = _asset_paths(Unit_Test)
        self.robot = pin.RobotWrapper.BuildFromURDF(urdf_path, meshes_path)

        self.mixed_jointsToLockIDs = [
            "left_thigh_yaw_joint",
            "left_thigh_roll_joint",
            "left_thigh_pitch_joint",
            "left_knee_joint",
            "left_ankle_pitch_joint",
            "left_ankle_roll_joint",
            "right_thigh_yaw_joint",
            "right_thigh_roll_joint",
            "right_thigh_pitch_joint",
            "right_knee_joint",
            "right_ankle_pitch_joint",
            "right_ankle_roll_joint",
            "torso_joint",
        ]

        self.reduced_robot = self.robot.buildReducedRobot(
            list_of_joints_to_lock=self.mixed_jointsToLockIDs,
            reference_configuration=np.array([0.0] * self.robot.model.nq),
        )

        self.reduced_robot.model.addFrame(
            pin.Frame(
                "L_ee",
                self.reduced_robot.model.getJointId("left_elbow_yaw_joint"),
                pin.SE3(np.eye(3), np.array([0.15, 0.0, 0.0]).T),
                pin.FrameType.OP_FRAME,
            )
        )
        self.reduced_robot.model.addFrame(
            pin.Frame(
                "R_ee",
                self.reduced_robot.model.getJointId("right_elbow_yaw_joint"),
                pin.SE3(np.eye(3), np.array([0.15, 0.0, 0.0]).T),
                pin.FrameType.OP_FRAME,
            )
        )

        self.cmodel = cpin.Model(self.reduced_robot.model)
        self.cdata = self.cmodel.createData()
        self.cq = casadi.SX.sym("q", self.reduced_robot.model.nq, 1)
        self.cTf_l = casadi.SX.sym("tf_l", 4, 4)
        self.cTf_r = casadi.SX.sym("tf_r", 4, 4)
        cpin.framesForwardKinematics(self.cmodel, self.cdata, self.cq)

        self.L_hand_id = self.reduced_robot.model.getFrameId("L_ee")
        self.R_hand_id = self.reduced_robot.model.getFrameId("R_ee")

        self.translational_error = casadi.Function(
            "translational_error",
            [self.cq, self.cTf_l, self.cTf_r],
            [
                casadi.vertcat(
                    self.cdata.oMf[self.L_hand_id].translation - self.cTf_l[:3, 3],
                    self.cdata.oMf[self.R_hand_id].translation - self.cTf_r[:3, 3],
                )
            ],
        )
        self.rotational_error = casadi.Function(
            "rotational_error",
            [self.cq, self.cTf_l, self.cTf_r],
            [
                casadi.vertcat(
                    cpin.log3(self.cdata.oMf[self.L_hand_id].rotation @ self.cTf_l[:3, :3].T),
                    cpin.log3(self.cdata.oMf[self.R_hand_id].rotation @ self.cTf_r[:3, :3].T),
                )
            ],
        )

        self.opti = casadi.Opti()
        self.var_q = self.opti.variable(self.reduced_robot.model.nq)
        self.var_q_last = self.opti.parameter(self.reduced_robot.model.nq)
        self.param_tf_l = self.opti.parameter(4, 4)
        self.param_tf_r = self.opti.parameter(4, 4)
        self.translational_cost = casadi.sumsqr(
            self.translational_error(self.var_q, self.param_tf_l, self.param_tf_r)
        )
        self.rotation_cost = casadi.sumsqr(
            self.rotational_error(self.var_q, self.param_tf_l, self.param_tf_r)
        )
        self.regularization_cost = casadi.sumsqr(self.var_q)
        self.smooth_cost = casadi.sumsqr(self.var_q - self.var_q_last)

        self.opti.subject_to(
            self.opti.bounded(
                self.reduced_robot.model.lowerPositionLimit,
                self.var_q,
                self.reduced_robot.model.upperPositionLimit,
            )
        )
        self.opti.minimize(
            50 * self.translational_cost
            + 0.5 * self.rotation_cost
            + 0.02 * self.regularization_cost
            + 0.1 * self.smooth_cost
        )

        opts = {
            "ipopt": {
                "print_level": 0,
                "max_iter": 50,
                "tol": 1e-6,
            },
            "print_time": False,
            "calc_lam_p": False,
        }
        self.opti.solver("ipopt", opts)

        self.init_data = np.zeros(self.reduced_robot.model.nq)
        self.smooth_filter = WeightedMovingFilter(np.array([0.4, 0.3, 0.2, 0.1]), 10)
        self.vis = None

        if self.Visualization:
            self.vis = MeshcatVisualizer(
                self.reduced_robot.model,
                self.reduced_robot.collision_model,
                self.reduced_robot.visual_model,
            )
            self.vis.initViewer(open=True)
            self.vis.loadViewerModel("pinocchio")
            self.vis.displayFrames(True, frame_ids=[49, 50], axis_length=0.15, axis_width=5)
            self.vis.display(pin.neutral(self.reduced_robot.model))

            frame_axis_positions = np.array(
                [
                    [0, 0, 0],
                    [1, 0, 0],
                    [0, 0, 0],
                    [0, 1, 0],
                    [0, 0, 0],
                    [0, 0, 1],
                ],
                dtype=np.float32,
            ).T
            frame_axis_colors = np.array(
                [
                    [1, 0, 0],
                    [1, 0.6, 0],
                    [0, 1, 0],
                    [0.6, 1, 0],
                    [0, 0, 1],
                    [0, 0.6, 1],
                ],
                dtype=np.float32,
            ).T
            for frame_viz_name in ["L_ee_target", "R_ee_target"]:
                self.vis.viewer[frame_viz_name].set_object(
                    mg.LineSegments(
                        mg.PointsGeometry(
                            position=0.1 * frame_axis_positions,
                            color=frame_axis_colors,
                        ),
                        mg.LineBasicMaterial(linewidth=20, vertexColors=True),
                    )
                )

    def scale_arms(
        self,
        human_left_pose: np.ndarray,
        human_right_pose: np.ndarray,
        human_arm_length: float = 0.45,
        robot_arm_length: float = 0.50,
    ) -> tuple[np.ndarray, np.ndarray]:
        scale_factor = robot_arm_length / human_arm_length
        robot_left_pose = human_left_pose.copy()
        robot_right_pose = human_right_pose.copy()
        robot_left_pose[:3, 3] *= scale_factor
        robot_right_pose[:3, 3] *= scale_factor
        return robot_left_pose, robot_right_pose

    def solve_ik(
        self,
        left_wrist: np.ndarray,
        right_wrist: np.ndarray,
        current_lr_arm_motor_q: np.ndarray | None = None,
        current_lr_arm_motor_dq: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        if current_lr_arm_motor_q is not None:
            self.init_data = current_lr_arm_motor_q
        self.opti.set_initial(self.var_q, self.init_data)

        left_wrist, right_wrist = self.scale_arms(left_wrist, right_wrist)
        if self.Visualization:
            self.vis.viewer["L_ee_target"].set_transform(left_wrist)
            self.vis.viewer["R_ee_target"].set_transform(right_wrist)

        self.opti.set_value(self.param_tf_l, left_wrist)
        self.opti.set_value(self.param_tf_r, right_wrist)
        self.opti.set_value(self.var_q_last, self.init_data)

        try:
            self.opti.solve()
            sol_q = self.opti.value(self.var_q)
            self.smooth_filter.add_data(sol_q)
            sol_q = self.smooth_filter.filtered_data

            if current_lr_arm_motor_dq is not None:
                velocity = current_lr_arm_motor_dq * 0.0
            else:
                velocity = (sol_q - self.init_data) * 0.0

            self.init_data = sol_q
            sol_tauff = pin.rnea(
                self.reduced_robot.model,
                self.reduced_robot.data,
                sol_q,
                velocity,
                np.zeros(self.reduced_robot.model.nv),
            )

            if self.Visualization:
                self.vis.display(sol_q)

            return sol_q, sol_tauff
        except Exception as exc:
            logger_mp.error(f"IK solve failed, using current joints. {exc}")

            if current_lr_arm_motor_q is None:
                current_lr_arm_motor_q = self.init_data.copy()

            try:
                sol_q = self.opti.debug.value(self.var_q)
                self.smooth_filter.add_data(sol_q)
                fallback_q = self.smooth_filter.filtered_data
            except Exception:
                fallback_q = current_lr_arm_motor_q

            self.init_data = fallback_q
            logger_mp.error(
                "IK fallback. motorstate=%s left_pose=%s right_pose=%s",
                current_lr_arm_motor_q,
                left_wrist,
                right_wrist,
            )
            return current_lr_arm_motor_q, np.zeros(self.reduced_robot.model.nv)
