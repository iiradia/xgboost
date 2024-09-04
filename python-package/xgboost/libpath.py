# coding: utf-8
"""Find the path to xgboost dynamic library files."""

import os
import platform
import sys
from typing import List


class XGBoostLibraryNotFound(Exception):
    """Error thrown by when xgboost is not found"""


def find_lib_path() -> List[str]:
    """Find the path to xgboost dynamic library files.

    Supports use of XGBOOST_LIBRARY_PATH environment variable as a
    a custom directory for dynamic library file location.

    Returns
    -------
    lib_path
       List of all found library path to xgboost
    """
    curr_path = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
    dll_path = [
        # normal, after installation `lib` is copied into Python package tree.
        os.path.join(curr_path, "lib"),
        # editable installation, no copying is performed.
        os.path.join(curr_path, os.path.pardir, os.path.pardir, "lib"),
        # use libxgboost from a system prefix, if available.  This should be the last
        # option.
        os.path.join(sys.base_prefix, "lib"),
    ]

    custom_xgboost_path = os.environ.get("XGBOOST_LIBRARY_PATH")
    if custom_xgboost_path is not None:
        dll_path.extend([os.path.join(custom_xgboost_path, "lib")])

    if sys.platform == "win32":
        # On Windows, Conda may install libs in different paths
        dll_path.extend(
            [
                os.path.join(sys.base_prefix, "bin"),
                os.path.join(sys.base_prefix, "Library"),
                os.path.join(sys.base_prefix, "Library", "bin"),
                os.path.join(sys.base_prefix, "Library", "lib"),
                os.path.join(sys.base_prefix, "Library", "mingw-w64"),
                os.path.join(sys.base_prefix, "Library", "mingw-w64", "bin"),
                os.path.join(sys.base_prefix, "Library", "mingw-w64", "lib"),
            ]
        )
        dll_path = [os.path.join(p, "xgboost.dll") for p in dll_path]
    elif sys.platform.startswith(("linux", "freebsd", "emscripten")):
        dll_path = [os.path.join(p, "libxgboost.so") for p in dll_path]
    elif sys.platform == "darwin":
        dll_path = [os.path.join(p, "libxgboost.dylib") for p in dll_path]
    elif sys.platform == "cygwin":
        dll_path = [os.path.join(p, "cygxgboost.dll") for p in dll_path]
    if platform.system() == "OS400":
        dll_path = [os.path.join(p, "libxgboost.so") for p in dll_path]

    lib_path = [p for p in dll_path if os.path.exists(p) and os.path.isfile(p)]

    # XGBOOST_BUILD_DOC is defined by sphinx conf.
    if not lib_path and not os.environ.get("XGBOOST_BUILD_DOC", False):
        link = "https://xgboost.readthedocs.io/en/stable/install.html"
        msg = (
            "Cannot find XGBoost Library in the candidate path.  "
            + "List of candidates:\n- "
            + ("\n- ".join(dll_path))
            + "\nXGBoost Python package path: "
            + curr_path
            + "\nsys.base_prefix: "
            + sys.base_prefix
            + "\nSee: "
            + link
            + " for installing XGBoost."
        )
        raise XGBoostLibraryNotFound(msg)
    return lib_path
