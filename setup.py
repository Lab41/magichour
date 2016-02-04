from setuptools import setup, find_packages

setup(
    name='magichour',
    description='Lab41 challenge dealing with log file analysis',
    version='0.0.1',
    author='Lab41',
    author_email='kylez@lab41.org',
    url='https://github.com/Lab41/magichour',
    packages=find_packages(),
    package_dir={'magichour.lib.LogCluster': 'magichour/lib/LogCluster'},
    package_data={'magichour.lib.LogCluster': ['logcluster-0.03/*'],
                  'magichour.api.local.sample.data': ['auditd_template_ids.csv',
                                                      'sample.transforms']},
)
