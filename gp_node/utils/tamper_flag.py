class TamperFlag:

    """ 
    Represents tamper flags sent by Maxwell board.
    Only a select few flag names are permitted. If a flag is 
    created with an unknown flag name, then an exception of type
    FlagError is raised.
    Possible tamper flags are:
    
    - EARTH
    - LINE_LOAD_REVERSAL
    - MAGNETIC
    - COVER_OPEN
    - NEUTRAL_MISSING
    - NEUTRAL_DISTURBANCE

    Usage: flag = TamperFlag('EARTH')
    """

    VALID_FLAG_NAMES = ['EARTH',
                        'LINE_LOAD_REVERSAL',
                        'MAGNETIC',
                        'COVER_OPEN',
                        'NEUTRAL_MISSING',
                        'NEUTRAL_DISTURBANCE']

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
