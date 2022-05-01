#!/usr/bin/env python3
from enum import Enum
from common.params import Params
from decimal import Decimal

class LongTunes(Enum):
  PEDAL = 0

class LatTunes(Enum):
  INDI = 0
  LQR = 1
  PID = 2
  PID_A = 3
  PID_B = 4
  PID_C = 5
  PID_D = 6
  PID_E = 7
  PID_F = 8
  PID_G = 9
  PID_H = 10
  PID_I = 11
  PID_J = 12
  PID_K = 13
  PID_L = 14
  PID_M = 15
  TORQUE = 16


###### LONG ######
def set_long_tune(tune, name):
  # Improved longitudinal tune
  if name == LongTunes.PEDAL:
    tune.deadzoneBP = [0., 8.05]
    tune.deadzoneV = [.0, .14]
    tune.kpBP = [0., 5., 20.]
    tune.kpV = [1.3, 1.0, 0.7]
    tune.kiBP = [0., 5., 12., 20., 27.]
    tune.kiV = [.35, .23, .20, .17, .1]
  # Default longitudinal tune
  else:
    raise NotImplementedError('This longitudinal tune does not exist')


###### LAT ######
def set_lat_tune(tune, name, max_lat_accel=2.5, FRICTION=.1):
  params = Params()
  if name == LatTunes.TORQUE:
    TorqueKp = float(Decimal(params.get("TorqueKp", encoding="utf8")) * Decimal('0.1'))
    TorqueKf = float(Decimal(params.get("TorqueKf", encoding="utf8")) * Decimal('0.1'))
    TorqueKi = float(Decimal(params.get("TorqueKi", encoding="utf8")) * Decimal('0.1'))
    TorqueFriction = float(Decimal(params.get("TorqueFriction", encoding="utf8")) * Decimal('0.001'))
    TorqueUseAngle = params.get_bool('TorqueUseAngle')
    max_lat_accel = float(Decimal(params.get("TorqueMaxLatAccel", encoding="utf8")) * Decimal('0.1'))
    tune.init('torque')
    tune.torque.useSteeringAngle = TorqueUseAngle
    tune.torque.kp = TorqueKp / max_lat_accel # 2.0/2.5 = 0.8
    tune.torque.kf = TorqueKf / max_lat_accel # 1.0/2.5 = 0.4
    tune.torque.ki = TorqueKi / max_lat_accel # 0.5/2.5 = 0.2
    tune.torque.friction = TorqueFriction
  elif name == LatTunes.LQR:
    Scale = float(Decimal(params.get("Scale", encoding="utf8")) * Decimal('1.0'))
    LqrKi = float(Decimal(params.get("LqrKi", encoding="utf8")) * Decimal('0.001'))
    DcGain = float(Decimal(params.get("DcGain", encoding="utf8")) * Decimal('0.00001'))
    tune.init('lqr')
    tune.lqr.scale = Scale
    tune.lqr.ki = LqrKi
    tune.lqr.a = [0., 1., -0.22619643, 1.21822268]
    tune.lqr.b = [-1.92006585e-04, 3.95603032e-05]
    tune.lqr.c = [1., 0.]
    tune.lqr.k = [-110., 451.]
    tune.lqr.l = [0.33, 0.318]
    tune.lqr.dcGain = DcGain
  elif name == LatTunes.INDI:
    InnerLoopGain = float(Decimal(params.get("InnerLoopGain", encoding="utf8")) * Decimal('0.1'))
    OuterLoopGain = float(Decimal(params.get("OuterLoopGain", encoding="utf8")) * Decimal('0.1'))
    TimeConstant = float(Decimal(params.get("TimeConstant", encoding="utf8")) * Decimal('0.1'))
    ActuatorEffectiveness = float(Decimal(params.get("ActuatorEffectiveness", encoding="utf8")) * Decimal('0.1'))
    tune.init('indi')
    tune.indi.innerLoopGainBP = [0.]
    tune.indi.innerLoopGainV = [InnerLoopGain] # 4.0, third tune. Highest value that still gives smooth control. Effects turning into curves.
    tune.indi.outerLoopGainBP = [0.]
    tune.indi.outerLoopGainV = [OuterLoopGain] # 3.0, forth tune. Highest value that still gives smooth control. Effects lane centering.
    tune.indi.timeConstantBP = [0.]
    tune.indi.timeConstantV = [TimeConstant] # 1.0, second tune. Lowest value with smooth actuation. Avoid the noise of actuator gears thrashing.
    tune.indi.actuatorEffectivenessBP = [0.]
    tune.indi.actuatorEffectivenessV = [ActuatorEffectiveness] # 1.0, first tune. Lowest value without oversteering. May vary with speed.
    # actuatorEffectiveness
      # As effectiveness increases, actuation strength decreases
      # Too high: weak, sloppy lane centering, slow oscillation, can't follow high curvature, high steering error causes snappy corrections
      # Too low: overpower, saturation, jerky, fast oscillation
      # Just right: Highest still able to maintain good lane centering.
    # timeConstant
      # Extend exponential decay of prior output steer
      # Too high: sloppy lane centering
      # Too low: noisy actuation, responds to every bump, maybe unable to maintain lane center due to rapid actuation
      # Just right: above noisy actuation and lane centering instability
    # innerLoopGain
      # Steer rate error gain
      # Too high: jerky oscillation in high curvature
      # Too low: sloppy, cannot accomplish desired steer angle
      # Just right: brief snap on entering high curvature
    # outerLoopGain
      # Steer error gain
      # Too high: twitchy hyper lane centering, oversteering
      # Too low: sloppy, all over lane
      # Just right: crisp lane centering
  elif 'PID' in str(name):
    if name == LatTunes.PID:
      PidKp = float(Decimal(params.get("PidKp", encoding="utf8")) * Decimal('0.01'))
      PidKi = float(Decimal(params.get("PidKi", encoding="utf8")) * Decimal('0.001'))
      PidKd = float(Decimal(params.get("PidKd", encoding="utf8")) * Decimal('0.01'))
      PidKf = float(Decimal(params.get("PidKf", encoding="utf8")) * Decimal('0.00001'))
      tune.init('pid')
      tune.pid.kpBP = [0., 9.]
      tune.pid.kpV = [0.1, PidKp]
      tune.pid.kiBP = [0., 9.]
      tune.pid.kiV = [0.01, PidKi]
      tune.pid.kdBP = [0.]
      tune.pid.kdV = [PidKd]
      tune.pid.kf = PidKf
    elif name == LatTunes.PID_A:
      tune.init('pid')
      tune.pid.kiBP = [0.0]
      tune.pid.kpBP = [0.0]
      tune.pid.kpV = [0.2]
      tune.pid.kiV = [0.05]
      tune.pid.kf = 0.00003
    elif name == LatTunes.PID_C:
      tune.init('pid')
      tune.pid.kiBP = [0.0]
      tune.pid.kpBP = [0.0]
      tune.pid.kpV = [0.6]
      tune.pid.kiV = [0.1]
      tune.pid.kf = 0.00006
    elif name == LatTunes.PID_D:
      tune.init('pid')
      tune.pid.kiBP = [0.0]
      tune.pid.kpBP = [0.0]
      tune.pid.kpV = [0.6]
      tune.pid.kiV = [0.1]
      tune.pid.kf = 0.00007818594
    elif name == LatTunes.PID_F:
      tune.init('pid')
      tune.pid.kiBP = [0.0]
      tune.pid.kpBP = [0.0]
      tune.pid.kpV = [0.723]
      tune.pid.kiV = [0.0428]
      tune.pid.kf = 0.00006
    elif name == LatTunes.PID_G:
      tune.init('pid')
      tune.pid.kiBP = [0.0]
      tune.pid.kpBP = [0.0]
      tune.pid.kpV = [0.18]
      tune.pid.kiV = [0.015]
      tune.pid.kf = 0.00012
    elif name == LatTunes.PID_H:
      tune.init('pid')
      tune.pid.kiBP = [0.0]
      tune.pid.kpBP = [0.0]
      tune.pid.kpV = [0.17]
      tune.pid.kiV = [0.03]
      tune.pid.kf = 0.00006
    elif name == LatTunes.PID_I:
      tune.init('pid')
      tune.pid.kiBP = [0.0]
      tune.pid.kpBP = [0.0]
      tune.pid.kpV = [0.15]
      tune.pid.kiV = [0.05]
      tune.pid.kf = 0.00004
    elif name == LatTunes.PID_J:
      tune.init('pid')
      tune.pid.kiBP = [0.0]
      tune.pid.kpBP = [0.0]
      tune.pid.kpV = [0.19]
      tune.pid.kiV = [0.02]
      tune.pid.kf = 0.00007818594
    elif name == LatTunes.PID_L:
      tune.init('pid')
      tune.pid.kiBP = [0.0]
      tune.pid.kpBP = [0.0]
      tune.pid.kpV = [0.3]
      tune.pid.kiV = [0.05]
      tune.pid.kf = 0.00006
    elif name == LatTunes.PID_M:
      tune.init('pid')
      tune.pid.kiBP = [0.0]
      tune.pid.kpBP = [0.0]
      tune.pid.kpV = [0.3]
      tune.pid.kiV = [0.05]
      tune.pid.kf = 0.00007
    elif name == LatTunes.PID_N:
      tune.init('pid')
      tune.pid.kiBP = [0.0]
      tune.pid.kpBP = [0.0]
      tune.pid.kpV = [0.35]
      tune.pid.kiV = [0.15]
      tune.pid.kf = 0.00007818594
    else:
      raise NotImplementedError('This PID tune does not exist')
  else:
    raise NotImplementedError('This lateral tune does not exist')
