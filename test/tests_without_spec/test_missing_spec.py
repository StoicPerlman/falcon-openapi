import json
import os
import sys
from shutil import copytree

import pytest

sys.path.insert(0, '../..')
from falcon_openapi import OpenApiRouter  # isort:skip


class TestRouter():
    def test_missing_default(self):
        with pytest.raises(FileNotFoundError):
            OpenApiRouter()

    def test_bad_file(self):
        with pytest.raises(FileNotFoundError):
            OpenApiRouter(file_path='kdjh.yaml')
