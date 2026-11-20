
def  response_meter():
    
    response_keys = {
                    '1':{
                                'key_name':'get_power_limit',
                                'reverse':True,
                                'data_len':60,
                                'location':50,
                                'data_bytes':4

                            },
                    '2':{
                                'key_name':'set_power_limit',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                                # AA 09 09 09 09 00 00 01 02 04 FF 02 03 E8 EA 34

                            },
                    '11': {    'key_name':"relay_status",
                                'data_len':60,
                               'location':19,
                               'data_bytes':1
                        },
                        
                    '12':{
                                'key_name':'factory_init_1',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                    '14':{
                                'key_name':'reset',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                    '32':{
                                'key_name':'3p_bundle',
                                # 'no_of_params':4,
                                'data_len':70,
                                'bundle_key':{
                                'active_energy': {
                                                    'date_time':False,
                                                    'location':32,
                                                    'data_bytes':4
                                                    }
                                            }
                            },


                    '33':{
                                'key_name':'get_time',
                                'date_time':True,
                                'data_len':70,
                                'location':0,
                                'data_bytes':4

                            },
                    '34':{
                                'key_name':'set_time',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                    '35':{
                                'key_name':'3p_bundle',
                                # 'no_of_params':4,
                                'data_len':70,
                                'bundle_key':{
                                'active_energy': {
                                                    'date_time':False,
                                                    'location':32,
                                                    'data_bytes':4
                                                    }
                                            }
                            },
                    '37':{
                                'key_name':'factory_init_time_only',
                                'data_len':60,
                                'date_time':True,
                                'reverse':True,
                                'location':36,
                                'data_bytes':4
                            },
                            
                    '38':{
                                'key_name':'set_tariff',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                    '39':{
                                'key_name':'enable_eg_tariff',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                    '40':{
                                'key_name':'enable_dg_tariff',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                
                    '41':{
                                'key_name':'get_dg_tariff_info',
                                # 'no_of_params':4,
                                'data_len':58,
                                'bundle_key':{

                                        'fd_type': {
                                                    'date_time':False,
                                                    'location':0,
                                                    'data_bytes':2
                                                    },
                                        'fd_telescopic': {
                                                    'date_time':False,
                                                    'location':2,
                                                    'data_bytes':2
                                                    },
                                        'mmc_application': {
                                                    'date_time':False,
                                                    'location':4,
                                                    'data_bytes':2
                                                    },
                                        'friendly_hours': {
                                                    'date_time':False,
                                                    'location':6,
                                                    'data_bytes':1
                                                    },
                                        'alert_limit': {
                                                    'date_time':False,
                                                    'location':7,
                                                    'data_bytes':1
                                                    },
                                        'emergency_credit': {
                                                    'date_time':False,
                                                    'location':8,
                                                    'data_bytes':1
                                                    },
                                        'topup_limit': {
                                                    'date_time':True,
                                                    'location':9,
                                                    'data_bytes':1
                                                    },
                                        'mmc': {
                                                    'date_time':False,
                                                    'location':10,
                                                    'data_bytes':2
                                                    },
                                        'fd_price': {
                                                    'date_time':False,
                                                    'location':12,
                                                    'data_bytes':4
                                                    },
                                        'energy_price': {
                                                    'date_time':False,
                                                    'location':36,
                                                    'data_bytes':2
                                                    },
                                        'energy_slab': {
                                                    'date_time':False,
                                                    'location':48,
                                                    'data_bytes':2
                                                    }
                                             }
                                    },
                    '42':{
                                'key_name':'get_tariff_info',
                                # 'no_of_params':4,
                                'data_len':58,
                                'bundle_key':{

                                        'fd_type': {
                                                    'date_time':False,
                                                    'location':0,
                                                    'data_bytes':2
                                                    },
                                        'fd_telescopic': {
                                                    'date_time':False,
                                                    'location':2,
                                                    'data_bytes':2
                                                    },
                                        'mmc_application': {
                                                    'date_time':False,
                                                    'location':4,
                                                    'data_bytes':2
                                                    },
                                        'friendly_hours': {
                                                    'date_time':False,
                                                    'location':6,
                                                    'data_bytes':1
                                                    },
                                        'alert_limit': {
                                                    'date_time':False,
                                                    'location':7,
                                                    'data_bytes':1
                                                    },
                                        'emergency_credit': {
                                                    'date_time':False,
                                                    'location':8,
                                                    'data_bytes':1
                                                    },
                                        'topup_limit': {
                                                    'date_time':True,
                                                    'location':9,
                                                    'data_bytes':1
                                                    },
                                        'mmc': {
                                                    'date_time':False,
                                                    'location':10,
                                                    'data_bytes':2
                                                    },
                                        'fd_price': {
                                                    'date_time':False,
                                                    'location':12,
                                                    'data_bytes':4
                                                    },
                                        'energy_price': {
                                                    'date_time':False,
                                                    'location':36,
                                                    'data_bytes':2
                                                    },
                                        'energy_slab': {
                                                    'date_time':False,
                                                    'location':48,
                                                    'data_bytes':2
                                                    }
                                            }
                                },
                    '43':{
                                'key_name':'get_prepaid_info',
                                # 'no_of_params':4,
                                'data_len':56,
                                'bundle_key':{

                                        'current_active_tariff': {
                                                    'date_time':False,
                                                    'location':0,
                                                    'data_bytes':2
                                                    },
                                        'tariff_change_req': {
                                                    'date_time':False,
                                                    'location':2,
                                                    'data_bytes':2
                                                    },
                                        'prepaid_mode_change_req': {
                                                    'date_time':False,
                                                    'location':4,
                                                    'data_bytes':2
                                                    },
                                        'energy_start_of_month': {
                                                    'date_time':False,
                                                    'location':6,
                                                    'data_bytes':4
                                                    },
                                        'last_billing_time_stamp': {
                                                    'date_time':True,
                                                    'location':10,
                                                    'data_bytes':4
                                                    },
                                        'new_tariff_timestamp': {
                                                    'date_time':True,
                                                    'location':14,
                                                    'data_bytes':4
                                                    },
                                        'change_prepaid_mode_timestamp': {
                                                    'date_time':True,
                                                    'location':18,
                                                    'data_bytes':4
                                                    },
                                        'next_tariff_to_activate': {
                                                    'date_time':False,
                                                    'location':22,
                                                    'data_bytes':2
                                                    },
                                        'prepaid_status': {
                                                    'date_time':False,
                                                    'location':24,
                                                    'data_bytes':2
                                                    },
                                        'account_balance': {
                                                    'date_time':False,
                                                    'location':26,
                                                    'data_bytes':4
                                                    },
                                        'net_positive_recharge': {
                                                    'date_time':False,
                                                    'location':30,
                                                    'data_bytes':4
                                                    },
                                        'net_negative_recharge': {
                                                    'date_time':False,
                                                    'location':34,
                                                    'data_bytes':4
                                                    },
                                        'net_recharge': {
                                                    'date_time':False,
                                                    'location':38,
                                                    'data_bytes':4
                                                    },
                                        'current_account_balance': {
                                                    'date_time':False,
                                                    'location':42,
                                                    'data_bytes':4
                                                    },
                                        'current_FD_cost': {
                                                    'date_time':False,
                                                    'location':46,
                                                    'data_bytes':4
                                                    },
                                        'current_energy_cost': {
                                                    'date_time':False,
                                                    'location':50,
                                                    'data_bytes':4
                                                    },
                                        'status': {
                                                    'date_time':False,
                                                    'location':54,
                                                    'data_bytes':2
                                                    }
                            
                                             }

                        },
                        
                        '44':{
                                'key_name':'recharge',
                                # 'no_of_params':4,
                                'data_len':5,
                                'bundle_key':{

                                        'id': {
                                                    'date_time':False,
                                                    'location':0,
                                                    'data_bytes':4
                                                    },
                                        'status':{
                                                    'date_time':False,
                                                    'location':4,
                                                    'data_bytes':1
                                                    }
                                            }
                            },
                        '45':{
                                'key_name':'3p_assign',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2

                            },
                        '46':{
                                'key_name':'3p_deassign',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2

                            },
                        '47':{
                                'key_name':'3p_live_version',
                                'data_len':60,
                                'location':8,
                                'data_bytes':2
                            },


                        
                        '48':{
                                'key_name':'turn_on_relay',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2

                            },
                        '49':{
                                'key_name':'turn_off_relay',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2

                            },
                        '53':{
                                'key_name':'power_limit_relay_flag_on',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                        '54':{
                                'key_name':'power_limit_relay_flag_off',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                        '55':{
                                'key_name':'c_open_relay_flag_on',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                        '56':{
                                'key_name':'c_open_relay_flag_off',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                        
                        
                        '57':{
                                'key_name':'three_get_info',
                                # 'no_of_params':4,
                                'data_len':60,
                                'bundle_key':{

                                        'Serial_no': {
                                                    'location':0,
                                                    'data_bytes':4
                                                    },
                                        'Meter_addres': {
                                                    'location':4,
                                                    'data_bytes':4
                                                    },
                                        'Live_version': {
                                                    'location':8,
                                                    'data_bytes':2
                                                    },
                                        'External_version': {
                                                    'location':10,
                                                    'data_bytes':4
                                                    },
                                        'maxwell_version': {
                                                    'location':14,
                                                    'data_bytes':1
                                                    },
                                        'maxwell_hardware_version': {
                                                    'location':15,
                                                    'data_bytes':1
                                                    },
                                        'protocol_version': {
                                                    'location':16,
                                                    'data_bytes':1
                                                    },
                                        'relay_status': {
                                                    'date_time':False,
                                                    'location':19,
                                                    'data_bytes':1
                                                    },
                                        'relay_count': {
                                                    'location':20,
                                                    'data_bytes':2
                                                    },
                                        'Billing_count': {
                                                    'location':22,
                                                    'data_bytes':4
                                                    },
                                        'Tamper_count': {
                                                    'location':26,
                                                    'data_bytes':4
                                                    },
                                        'reset_time': {
                                                    'location':36,
                                                    'data_bytes':4
                                                    },
                                        'occurance time': {
                                                    'location':36,
                                                    'data_bytes':4
                                                    },
                                        'restoration time': {
                                                    'location':36,
                                                    'data_bytes':4
                                                    },
                                        'power_on_duration': {
                                                    'location':36,
                                                    'data_bytes':4
                                                    },
                                        'power_off_duration':{
                                                    'location':36,
                                                    'data_bytes':4
                                                    },
                                        'over_power_limit': {
                                                    'date_time':False,
                                                    'location':50,
                                                    'data_bytes':4
                                                    },
                                        'power_relay_control': {
                                                    'date_time':False,
                                                    'location':54,
                                                    'data_bytes':1
                                                    },
                                        'c_open_control': {
                                                    'date_time':False,
                                                    'location':55,
                                                    'data_bytes':1
                                                    },
                                        'prepaid_status': {
                                                    'date_time':False,
                                                    'location':56,
                                                    'data_bytes':1
                                                    },
                                        'c_open_inst': {
                                                    'date_time':False,
                                                    'location':57,
                                                    'data_bytes':1
                                                    },

                                    },
                                },
                        '58':{
                                'key_name':'3p_bundle',
                                # 'no_of_params':4,
                                'data_len':70,
                                'bundle_key':{

                                        'date_time': {
                                                    'date_time':True,
                                                    'location':0,
                                                    'data_bytes':4
                                                    },
                                        'meter_serial_no': {
                                                    'date_time':False,
                                                    'location':4,
                                                    'data_bytes':4
                                                    },
                                        'r_phase_voltage': {
                                                    'date_time':False,
                                                    'location':8,
                                                    'data_bytes':2
                                                    },
                                        'y_phase_voltage': {
                                                    'date_time':False,
                                                    'location':10,
                                                    'data_bytes':2
                                                    },
                                        'b_phase_voltage': {
                                                    'date_time':True,
                                                    'location':12,
                                                    'data_bytes':2
                                                    },
                                        'r_phase_current': {
                                                    'date_time':True,
                                                    'location':14,
                                                    'data_bytes':2
                                                    },
                                        'y_phase_current': {
                                                    'date_time':True,
                                                    'location':16,
                                                    'data_bytes':2
                                                    },
                                        'b_phase_current': {
                                                    'date_time':False,
                                                    'location':18,
                                                    'data_bytes':2
                                                    },
                                        'r_phase_pf': {
                                                    'date_time':False,
                                                    'location':20,
                                                    'data_bytes':2
                                                    },
                                        'y_phase_pf': {
                                                    'date_time':False,
                                                    'location':22,
                                                    'data_bytes':2
                                                    },
                                        'b_phase_pf': {
                                                    'date_time':False,
                                                    'location':24,
                                                    'data_bytes':2
                                                    },
                                        'TotalPf': {
                                                    'date_time':False,
                                                    'location':26,
                                                    'data_bytes':2
                                                    },
                                        'frequency': {
                                                    'date_time':False,
                                                    'location':28,
                                                    'data_bytes':2
                                                    },
                                        'total_real_energy': {
                                                    'date_time':False,
                                                    'location':32,
                                                    'data_bytes':4
                                                    },
                                        'total_apparent_energy': {
                                                    'date_time':False,
                                                    'location':36,
                                                    'data_bytes':4
                                                    },
                                        'total_real_power': {
                                                    'date_time':False,
                                                    'location':40,
                                                    'data_bytes':4
                                                    },
                                        'total_apparent_power': {
                                                    'date_time':False,
                                                    'location':44,
                                                    'data_bytes':4
                                                    },
                                        'tamper_time_stamp': {
                                                    'date_time':False,
                                                    'location':48,
                                                    'data_bytes':4
                                                    },
                                        'reactive_power': {
                                                    'date_time':False,
                                                    'location':52,
                                                    'data_bytes':4
                                                    },
                                        'reactive_energy': {
                                                    'date_time':False,
                                                    'location':56,
                                                    'data_bytes':4
                                                    },
                                        'tamper_count': {
                                                    'date_time':False,
                                                    'location':60,
                                                    'data_bytes':2
                                                    },
                                        'data_valid_status': {
                                                    'date_time':False,
                                                    'location':62,
                                                    'data_bytes':2
                                                    },
                                        'credits_remaining': {
                                                    'date_time':False,
                                                    'location':64,
                                                    'data_bytes':4
                                                    },
                                        'activated_tariff_set': {
                                                    'date_time':False,
                                                    'location':68,
                                                    'data_bytes':1
                                                    },
                                        'account_status': {
                                                    'date_time':False,
                                                    'location':69,
                                                    'data_bytes':1
                                                    },
                                        'total_apparent_power': {
                                                    'date_time':False,
                                                    'location':44,
                                                    'data_bytes':4
                                                    },
                                        'total_apparent_power': {
                                                    'date_time':False,
                                                    'location':44,
                                                    'data_bytes':4
                                                    },
                                        'total_apparent_power': {
                                                    'date_time':False,
                                                    'location':44,
                                                    'data_bytes':4
                                                    }
                            
                                             }

                        }

                        


                     }
    return response_keys
    

                            
                        


                         