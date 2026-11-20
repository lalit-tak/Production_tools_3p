class TamperFlag_3P:

    """ 
    Represents tamper flags sent by Maxwell board.
    Only a select few flag names are permitted. If a flag is 
    created with an unknown flag name, then an exception of type
    FlagError is raised.
    Possible tamper flags are:

    ['R_PHASE_MISSING',
    'Y_PHASE_MISSING',
    'B_PHASE_MISSING',
    'CURRENT_BYPASS',
    'R_PHASE_REVERSE_CURRENT',
    'Y_PHASE_REVERSE_CURRENT',
    'B_PHASE_REVERSE_CURRENT',
    'MAGNETIC',
    'R_PHASE_CT_OPEN',
    'Y_PHASE_CT_OPEN',
    'B_PHASE_CT_OPEN',
    'CURRENT_UNBALANCE',
    'VOLTAGE_UNBALANCE']

    Usage: flag = TamperFlag('VOLTAGE_UNBALANCE')
    """

    VALID_FLAG_NAMES = ['R_PHASE_MISSING',
                        'Y_PHASE_MISSING',
                        'B_PHASE_MISSING',
                        'CURRENT_BYPASS',
                        'R_PHASE_REVERSE_CURRENT',
                        'Y_PHASE_REVERSE_CURRENT',
                        'B_PHASE_REVERSE_CURRENT',
                        'MAGNETIC',
                        'R_PHASE_CT_OPEN',
                        'Y_PHASE_CT_OPEN',
                        'B_PHASE_CT_OPEN',
                        'CURRENT_UNBALANCE',
                        'VOLTAGE_UNBALANCE',
                        'R_PHASE_ND',
                        'Y_PHASE_ND',
                        'B_PHASE_ND',
                        'LOW_VOLTAGE_R_PHASE',
                        'LOW_VOLTAGE_Y_PHASE',
                        'LOW_VOLTAGE_B_PHASE',
                        'OVER_VOLTAGE_R_PHASE',
                        'OVER_VOLTAGE_Y_PHASE',
                        'OVER_VOLTAGE_B_PHASE',
                        'OVER_CURRENT_R_PHASE',
                        'OVER_CURRENT_Y_PHASE',
                        'OVER_CURRENT_B_PHASE',
                        'LOW_PF_R_PHASE',
                        'LOW_PF_Y_PHASE',
                        'LOW_PF_B_PHASE',
                        'NEUTRAL_DISTURBANCE',
                        'LOW_VOLTAGE',
                        'OVER_VOLTAGE',
                        'OVER_CURRENT',
                        'LOW_PF',
                        'LOAD_CONNECTED',
                        'LOAD_DISCONNECTED',
                        'COVER_OPEN',
                        'POWER_FAILURE_RESTORATION',
                        'EVT_RTC',
                        'EVT_DEMAND_INTEGRATION_PERIOD',
                        'EVT_PROFILE_CAPTURE_PERIOD',
                        'EVT_SA_BILLING_SCHEULE',
                        'EVT_ACTIVE_CALENDER_TZ',
                        'EVT_RS485_DEVICE_ADDRESS'
                        ]

    def __init__(self, flag_name):
        if not isinstance(flag_name, str):
            raise TypeError("flag_name should be a string")
        if flag_name in self.VALID_FLAG_NAMES:
                self.flag_name = flag_name
        else:
            error_string = "Unknown flag name: " + flag_name
            raise ValueError(error_string)

    def __eq__(self, other):
        return (self.flag_name == other.flag_name)

    def __str__(self):
        return self.flag_name

    def __repr__(self):
        return self.flag_name
