"""
Base geometry primitives library
"""
__version__ = '0.1.25'
__license__ = "GNU Lesser General Public License v3"
from .common import NUMERICAL_MAX_VALUE, NUMERICAL_MIN_VALUE, PI, TWO_PI, HALF_PI
from .common import NUMERICAL_ACCURACY, NUMERICAL_FORMAT_4F, NUMERICAL_FORMAT_8F
from .common import DEG_TO_RAD, RAD_TO_DEG, parallel_range, fast_math, parallel, indent, set_indent_level
from .perspective_transform_2d import PerspectiveTransform2d, perspective_transform_test
from .transform_3d import Transform3d, deg_to_rad, transform_3d_test
from .transform_2d import Transform2d, transform_2d_test
from .bounding_rect import BoundingRect
from .bounding_box import BoundingBox
from .quaternion import Quaternion, quaternion_4_test
from .vector4 import Vector4, vector_4_test
from .vector3 import Vector3, vector_3_test
from .vector2 import Vector2, vector_2_test
from .matrix4 import Matrix4, matrix_4_test
from .matrix3 import Matrix3, matrix_3_test
from .camera import Camera
from .plane import Plane
from .voxel import Voxel
from .ray import Ray
from .mutils import dec_to_rad, rad_to_dec, compute_derivatives_2_at_pt, compute_derivatives_at_pt
from .mutils import linear_regression, bi_linear_regression, n_linear_regression
from .mutils import compute_derivatives_2, compute_derivatives, compute_normals
from .mutils import square_equation, clamp, dec_to_rad_pt, rad_to_dec_pt
from .mutils import second_order_surface, quadratic_shape_fit
from .mutils import poly_regression, quadratic_regression_2d
from .mutils import poly_fit, polynom, quadratic_shape_fit
from .fourier import fft, fft_2d, ifft, ifft_2d
from .interpolators import bi_linear_cut_along_curve, bi_cubic_interp_derivatives_pt, bi_cubic_interp_derivatives2_pt
from .interpolators import bi_cubic_interp_derivatives, bi_cubic_interp_derivatives2, bi_qubic_interp, bi_qubic_cut
from .interpolators import bi_linear_interp_derivatives2_pt, bi_linear_interp_derivatives, bi_qubic_cut_along_curve
from .interpolators import bi_linear_interp_derivatives2, bi_linear_interp, bi_linear_cut
from .interpolators import bi_linear_interp_pt, bi_linear_interp_derivatives_pt
