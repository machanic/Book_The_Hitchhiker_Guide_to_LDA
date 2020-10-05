import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from distutils.extension import Extension
from distutils import sysconfig

ldshared = sysconfig.get_config_var('LDSHARED')
cflags = sysconfig.get_config_var('CFLAGS')
opt = sysconfig.get_config_var('OPT')
sysconfig._config_vars['LDSHARED'] = ldshared.replace(' -g ', ' ')
sysconfig._config_vars['CFLAGS'] = cflags.replace(' -g ', ' ')
sysconfig._config_vars['OPT'] = opt.replace(' -g ', ' ')

extensions = [
    Extension("gibbs", ["doc_quality/gibbs.c"],
        include_dirs=["./doc_quality/include/include"],
        libraries=["python2.7"],
        library_dirs=["./doc_quality/lib"],
        extra_compile_args=["-fPIC","-O3" ],
        extra_link_args=["-fPIC", "-O3"],
        language='c',
        )
]
setup(name='doc_quality',
        version='1.4',
        packages=["doc_quality"],
        install_requires=["pymemcache>=1.2.8"],
        #py_modules=['scoring_content','save_to_memcached',"test_client"],
        description='scoring document based on its content quality',
        author='ma chen',
        author_email='sharpstill@163.com',
        #package_data={"include": ["doc_quality/include/%s"%f for f in os.listdir("doc_quality/include")],
        #                "lib": ["doc_quality/lib/%s"%f for f in os.listdir("doc_quality/lib")],
        #            },
        #data_files=[("include",["doc_quality/include/%s"%f for f in os.listdir("doc_quality/include")]),
        #            ("lib", ["doc_quality/lib/%s"%f for f in os.listdir("doc_quality/lib")])],
        #            #("doc_quality/data", ["doc_quality/data/%s"%f for f in os.listdir("doc_quality/data")]),
        #            ],
        ext_modules=extensions,
     )

