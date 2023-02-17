from typing import Tuple
import math

Quaternion = Tuple[float, float, float, float]

Vector3 = Tuple[float, float, float]

Matrix3 = Tuple[float, float, float, float, float, float, float, float, float]


def quaternion_from_angles(roll: float, pitch: float, yaw: float) -> Quaternion:
    # работает
    cr: float = math.cos(roll  * 0.5)
    sr: float = math.sin(roll  * 0.5)
    cp: float = math.cos(pitch * 0.5)
    sp: float = math.sin(pitch * 0.5)
    cy: float = math.cos(yaw   * 0.5)
    sy: float = math.sin(yaw   * 0.5)

    return cr * cp * cy + sr * sp * sy, \
           sr * cp * cy - cr * sp * sy, \
           cr * sp * cy + sr * cp * sy, \
           cr * cp * sy - sr * sp * cy


def quaternion_from_axis(angle: float, axis: Vector3) -> Quaternion:
    angle *= 0.5
    return math.cos(angle), \
          -axis[1] * math.sin(angle),\
          -axis[2] * math.sin(angle),\
          -axis[3] * math.sin(angle)
    

def inv_quaternion(q: Quaternion) -> Quaternion:
    # работает
    norm = 1.0 / math.sqrt(sum(v ** 2 for v in q))
    return q[0] * norm, -q[1] * norm, -q[2] * norm, -q[3] * norm


def quaternion_mul(q1: Quaternion, q2: Quaternion) -> Quaternion:
    # работает
    # qw, qx, qy, qz = q1
    # _qw, _qx, _qy, _qz = q2
    return q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2] - q1[3] * q2[3],\
           q1[0] * q2[1] + q1[1] * q2[0] - q1[2] * q2[3] + q1[3] * q2[2],\
           q1[0] * q2[2] + q1[1] * q2[3] + q1[2] * q2[0] - q1[3] * q2[1],\
           q1[0] * q2[3] - q1[1] * q2[2] + q1[2] * q2[1] + q1[3] * q2[0]


def quaternion_rot(v: Tuple[float, float, float], q: Quaternion) -> \
        Tuple[float, float, float]:
    return quaternion_mul(quaternion_mul(q, (0.0, v[0], v[1], v[2])), inv_quaternion(q))[1:]


def quaternion_to_euler(q: Quaternion) -> Vector3:
    # работает
    w, x, y, z = q
    ax = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    ay = math.asin(2.0 * (w * y - z * x))
    az = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    return ax, ay, az


def rot_m_to_quaternion(rm: Matrix3) -> Quaternion:
    # работает
    m00, m01, m02 = rm[0], rm[1], rm[2]
    m10, m11, m12 = rm[3], rm[4], rm[5]
    m20, m21, m22 = rm[6], rm[7], rm[8]

    qw = math.sqrt(max(0.0, 1.0 + m00 + m11 + m22)) * 0.5
    qx = math.sqrt(max(0.0, 1.0 + m00 - m11 - m22)) * 0.5
    qy = math.sqrt(max(0.0, 1.0 - m00 + m11 - m22)) * 0.5
    qz = math.sqrt(max(0.0, 1.0 - m00 - m11 + m22)) * 0.5

    qx = math.copysign(qx, m21 - m12)
    qy = math.copysign(qy, m02 - m20)
    qz = math.copysign(qz, m10 - m01)
    norm = 1.0 / math.sqrt(sum(v ** 2 for v in (qw, qx, qy, qz)))
    return qw * norm, qx * norm, qy * norm, qz * norm


def quaternion_to_rot_m(q: Quaternion):
    ew, ex, ey, ez = q
    xx = ex * ex * 2.0
    xy = ex * ey * 2.0
    xz = ex * ez * 2.0

    yy = ey * ey * 2.0
    yz = ey * ez * 2.0
    zz = ez * ez * 2.0

    wx = ew * ex * 2.0
    wy = ew * ey * 2.0
    wz = ew * ez * 2.0
    return (1.0 - (yy + zz), xy + wz, xz - wy), \
           (xy - wz, 1.0 - (xx + zz), yz + wx), \
           (xz + wy, yz - wx, 1.0 - (xx + yy))


def cross(a: Vector3, b: Vector3) -> Vector3:
    return a[2] * b[1] - a[1] * b[2], \
           a[0] * b[2] - a[2] * b[0], \
           a[1] * b[0] - a[0] * b[1]


def dot(a: Vector3, b: Vector3):
    return sum(ai * bi for ai, bi in zip(a, b))


def inv_norm(a: Vector3) -> float:
    return 1.0 / math.sqrt(sum(p * p for p in a))


def normalize(a: Vector3) -> Vector3:
    n = inv_norm(a)
    return a[0] * n, a[1] * n, a[2] * n


def direction(a: Vector3, b: Vector3):
    return normalize((b[0] - a[0], b[1] - a[1], b[2] - a[2]))


def build_rot_m(ey: Vector3, ez: Vector3 = None) -> Tuple[Vector3, Vector3, Vector3]:
    if ez is None:
        ez = (0.0, 0.0, 1.0)

    ey = normalize(ey)
    ez = normalize(ez)
    ex = normalize(cross(ez, ey))
    ez = normalize(cross(ey, ex))

    return (ex[0], ex[1], ex[2]), \
           (ey[0], ey[1], ey[2]), \
           (ez[0], ez[1], ez[2])
