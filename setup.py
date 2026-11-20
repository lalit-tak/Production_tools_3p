import os
from setuptools import setup

setup(name='gp_node',
    version='41',
    description='GP Node',
    url='https://github.com/GramPower/gp_node',
    author='Gram Power',
    author_email='technical@grampower.com',
    license='GP License',
    packages=['gp_node',
        'gp_node._1p_fw_upgrade',
        'gp_node._3p_fw_upgrade',
        'gp_node._3p_fw_upgrade.experiments',
        'gp_node.HW_Watchdog',
        'gp_node.maxwell',
        'gp_node.maxwell.calibrator',
        'gp_node.maxwell.packet',
        'gp_node.maxwell.simulator',
        'gp_node.maxwell_3_phase',
        'gp_node.maxwell_3_phase.packet',
        'gp_node.maxwell_3_phase.simulator',
        'gp_node.mri',
        'gp_node.network',
        'gp_node.network.circular_log',
        'gp_node.network.circular_log._1p',
        'gp_node.network.circular_log._3p',
        'gp_node.network.circular_log.common',
        'gp_node.network.circular_log.energy_cop',
        'gp_node.network.network_log',
        'gp_node.network.protocols',
        'gp_node.network.protocols._1p',
        'gp_node.network.protocols._3p',
        'gp_node.network.protocols.common',
        'gp_node.network.protocols.energy_cop',
        'gp_node.network.protocols.packets',
        'gp_node.network.protocols.packets._1p',
        'gp_node.network.protocols.packets._3p',
        'gp_node.network.protocols.packets.energy_cop',
        'gp_node.node_shell',
	    'gp_node.request_handler',
        'gp_node.utils'
    ],
    install_requires=[
    'PyYAML>=6.0',
    'jinja2>=3.1',
    'colorama>=0.4.6',
    'pyserial>=3.5',
    'crc16',
    'python-dateutil',
    ],
    include_package_data = True,
    scripts=[
        'bin/serial_sniffer.py',
        'bin/tap_monitor.py',
        'bin/rc_shell.py',
        'bin/tapcat.py',
        'bin/trace_path.py',
    ],
    zip_safe=False,
    entry_points = """

    [console_scripts]
    1p-maxwell-packet-monitor = gp_node.maxwell.packet.monitor:run
    1p-maxwell-simulator = gp_node.maxwell.simulator.maxwell_simulator:run
    3p-maxwell-packet-monitor = gp_node.maxwell_3_phase.packet.monitor:run
    3p-maxwell-simulator = gp_node.maxwell_3_phase.simulator.maxwell_simulator:run
    maxwell-calibrator = gp_node.maxwell.calibrator.maxwell_calibrator:run
    fw-upgrade = gp_node.fw_upgrade.fw_upgrade:run
    node-shell = gp_node.node_shell.node_shell:run
    make-image = gp_node.fw_upgrade.make_image:run
    mri = gp_node.mri.mri:run
    """
)
