# Utils module initialization

from .layer import set_layer
from .hatch import create_hatch
from .block import insert_block
from .filename import generate_filename
from .retry import retry
from .line_with_dimension import LD
from .arc_with_dimension import AD
from .circle_with_dimension import CD
from .save_drawing import save_drawing
from .date_name import date_name
from .draw_center_line import CL
from .retry_decorator import safe_acad_retry
from .open_template import _open_template
from .initial_cad_connection import _initialize_acad

# COM接口和CAD工厂
from .com_interface import Autocad, APoint, aDouble
from .cad_factory import get_cad, detect_cad

__all__ = [
    'set_layer',
    'create_hatch',
    'insert_block',
    'generate_filename',
    'retry',
    'LD',
    'AD',
    'CD',
    'save_drawing',
    'date_name',
    'CL',
    'safe_acad_retry',
    '_open_template',
    '_initialize_acad',
    # COM接口
    'Autocad',
    'APoint',
    'aDouble',
    # CAD工厂（只导出最必要的）
    'get_cad',
    'detect_cad',
]

__version__ = "0.3.0"
