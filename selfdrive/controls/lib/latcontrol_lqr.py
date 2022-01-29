import math
import numpy as np

from common.numpy_fast import clip, interp
from common.realtime import DT_CTRL
from cereal import log
from selfdrive.controls.lib.drive_helpers import get_steer_max
from selfdrive.controls.lib.latcontrol import LatControl, MIN_STEER_SPEED
from selfdrive.config import Conversions as CV
from selfdrive.ntune import nTune
from selfdrive.controls.lib.latcontrol import LatControl, MIN_STEER_SPEED

# TORQUE_SCALE_BP = [0., 30., 80., 100., 110., 120., 150.]
# TORQUE_SCALE_V = [0.2, 0.35, 0.68, 0.78, 0.8, 0.83, 0.85]

class LatControlLQR(LatControl):
  def __init__(self, CP, CI):
    super().__init__(CP, CI)
    self.scale = CP.lateralTuning.lqr.scale
    self.ki = CP.lateralTuning.lqr.ki

    self.A = np.array(CP.lateralTuning.lqr.a).reshape((2, 2))
    self.B = np.array(CP.lateralTuning.lqr.b).reshape((2, 1))
    self.C = np.array(CP.lateralTuning.lqr.c).reshape((1, 2))
    self.K = np.array(CP.lateralTuning.lqr.k).reshape((1, 2))
    self.L = np.array(CP.lateralTuning.lqr.l).reshape((2, 1))
    self.dc_gain = CP.lateralTuning.lqr.dcGain

    self.x_hat = np.array([[0], [0]])
    self.i_unwind_rate = 0.3 * DT_CTRL
    self.i_rate = 1.0 * DT_CTRL

    self.reset()
    self.tune = nTune(CP, self)

  def reset(self):
    super().reset()
    self.i_lqr = 0.0

  def update(self, active, CS, CP, VM, params, last_actuators, desired_curvature, desired_curvature_rate):
    self.tune.check()
    lqr_log = log.ControlsState.LateralLQRState.new_message()

    steers_max = get_steer_max(CP, CS.vEgo)

    if CS.vEgo < 85. * CV.KPH_TO_MS:
      torque_scale = (0.45 + CS.vEgo / 60.0)**2  # Scale actuator model with speed
    else:
      torque_scale = (0.13 + CS.vEgo / 60.0)**0.8 # Scale actuator model with speed

    # torque_scale = interp(CS.vEgo*3.6, TORQUE_SCALE_BP, TORQUE_SCALE_V)

    # Subtract offset. Zero angle should correspond to zero torque
    steering_angle_no_offset = CS.steeringAngleDeg - params.angleOffsetAverageDeg

    desired_angle = math.degrees(VM.get_steer_from_curvature(-desired_curvature, CS.vEgo, params.roll))

    instant_offset = params.angleOffsetDeg - params.angleOffsetAverageDeg
    desired_angle += instant_offset  # Only add offset that originates from vehicle model errors
    lqr_log.steeringAngleDesiredDeg = desired_angle

    # Update Kalman filter
    angle_steers_k = float(self.C.dot(self.x_hat))
    e = steering_angle_no_offset - angle_steers_k
    self.x_hat = self.A.dot(self.x_hat) + self.B.dot(CS.steeringTorqueEps / torque_scale) + self.L.dot(e)

    if CS.vEgo < MIN_STEER_SPEED or not active:
      lqr_log.active = False
      lqr_output = 0.
      output_steer = 0.
      self.reset()
    else:
      lqr_log.active = True

      # LQR
      u_lqr = float(desired_angle / self.dc_gain - self.K.dot(self.x_hat))
      lqr_output = torque_scale * u_lqr / self.scale

      # Integrator
      if CS.steeringPressed:
        self.i_lqr -= self.i_unwind_rate * float(np.sign(self.i_lqr))
      else:
        error = desired_angle - angle_steers_k
        i = self.i_lqr + self.ki * self.i_rate * error
        control = lqr_output + i

        if (error >= 0 and (control <= steers_max or i < 0.0)) or \
           (error <= 0 and (control >= -steers_max or i > 0.0)):
          self.i_lqr = i

      output_steer = lqr_output + self.i_lqr
      output_steer = clip(output_steer, -steers_max, steers_max)

    lqr_log.steeringAngleDeg = angle_steers_k
    lqr_log.i = self.i_lqr
    lqr_log.output = output_steer
    lqr_log.lqrOutput = lqr_output
    lqr_log.saturated = self._check_saturation(steers_max - abs(output_steer) < 1e-3, CS)
    return output_steer, desired_angle, lqr_log
