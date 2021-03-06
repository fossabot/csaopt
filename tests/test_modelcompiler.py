import pytest
import os
from collections import defaultdict

import context


@pytest.fixture
def conf():
    conf = defaultdict(str)
    conf['build.exec_paths'] = []
    return conf


@pytest.fixture
def internal_conf():
    internal_conf = defaultdict(str)

    internal_conf['build.exec_names'] = ['cmake', 'make']
    internal_conf['build.required_artifacts'] = 'model.o'
    internal_conf['build.timeouts.cmake'] = 30
    internal_conf['build.timeouts.make'] = 30
    return internal_conf


@pytest.fixture(scope='session')
def working_dir(tmpdir_factory):
    fn = tmpdir_factory.mktemp('csaopt-model')
    context.copy_folder_contents('app/model/', os.path.join(fn.dirname, 'model'))
    return fn


def test_build(working_dir, conf, internal_conf):
    context.copy_folder_contents('tests/testmodel', os.path.join(working_dir.dirname, 'usersrc'))
    model_proj_path = ''
    model_compiler = context.ModelCompiler(model_proj_path, conf, internal_conf)

    result = model_compiler.build()

    assert result.failed()
