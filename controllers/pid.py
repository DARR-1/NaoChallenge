"""PID controller utilities.

This project uses `RobotInterface.move(x, y, theta)` as a *velocity* command in
simulation (QiBullet) and for NAOqi we typically map it to `ALMotion.moveToward`
or `ALMotion.setWalkTargetVelocity`.

The helpers below implement a small, dependency-free PID that can be used by
behaviors to drive the robot towards a target distance/position.
"""

import time


def _clamp(value, vmin, vmax):
	if vmin is not None and value < vmin:
		return vmin
	if vmax is not None and value > vmax:
		return vmax
	return value


class PID(object):
	"""Simple PID controller.

	Notes:
	  - Use `update(error, dt)` where error is (setpoint - measurement).
	  - Call `reset()` when (re)starting a behavior.
	  - Anti-windup is implemented by clamping the integrator and optionally
		stopping integration whenever the output saturates.
	"""

	def __init__(self, kp, ki=0.0, kd=0.0, out_min=None, out_max=None,
				 integrator_min=None, integrator_max=None,
				 derivative_on_measurement=False, freeze_integrator_on_saturation=True):
		self.kp = kp
		self.ki = ki
		self.kd = kd
		self.out_min = out_min
		self.out_max = out_max
		self.integrator_min = integrator_min
		self.integrator_max = integrator_max
		self.derivative_on_measurement = derivative_on_measurement
		self.freeze_integrator_on_saturation = freeze_integrator_on_saturation
		self._integrator = 0.0
		self._prev_error = None
		self._prev_measurement = None

	def reset(self):
		self._integrator = 0.0
		self._prev_error = None
		self._prev_measurement = None

	def update(self, error, dt, measurement=None):
		if dt <= 0:
			# Avoid div-by-zero and keep controller stable.
			dt = 1e-6

		# Derivative term.
		d = 0.0
		if self.kd != 0.0:
			if self.derivative_on_measurement:
				if measurement is not None and self._prev_measurement is not None:
					d = -(measurement - self._prev_measurement) / dt
				self._prev_measurement = measurement
			else:
				if self._prev_error is not None:
					d = (error - self._prev_error) / dt
				self._prev_error = error

		# Candidate integrator update.
		i_candidate = self._integrator + error * dt
		i_candidate = _clamp(i_candidate, self.integrator_min, self.integrator_max)

		# Compute unclamped output.
		u_unclamped = self.kp * error + self.ki * i_candidate + self.kd * d

		# Clamp output.
		u = _clamp(u_unclamped, self.out_min, self.out_max)

		# Anti-windup: if output is saturated, optionally don't integrate.
		if self.ki != 0.0 and self.freeze_integrator_on_saturation and u != u_unclamped:
			# Keep previous integrator.
			pass
		else:
			self._integrator = i_candidate

		return u