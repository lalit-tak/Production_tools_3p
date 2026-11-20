
def  response_meter():
    
    response_keys = {
                        '1':{
                                'key_name':'set_serial_number',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                        '2':{
                                'key_name':'get_serial_num',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                                
                        
                        
                        '3':{
                                'key_name':'slab_disable',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2

                            },

                        '4':{
                                'key_name':'fd_disable',
                               'data_len':2,
                                'location':0,
                                'data_bytes':2

                            },


                        '5':{
                                'key_name':'relay_manual_control',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },

                        '6':{
                                'key_name':'recharge_50',
                                'data_len':5,
                                'location':0,
                                'data_bytes':4
                            },

                        '7':{
                                'key_name':'get_credits',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },

                        '8':{
                                'key_name':'get_live_tamper',
                                 'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },

                        '9':{
                                'key_name':'relay_auto_control',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },

                        '10':{
                                'key_name':'get_credits',
                                 'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },

                        '11':{
                                'key_name':'relay_status',
                                # 'no_of_params':4,
                                'data_len':4,
                                'bundle_key':{

                                        'control_mode': {
                                                    'date_time':False,
                                                    'location':0,
                                                    'data_bytes':1
                                                    },
                                        'control_state': {
                                                    'date_time':False,
                                                    'location':1,
                                                    'data_bytes':1
                                                    },
                                        'relay_state': {
                                                    'date_time':False,
                                                    'location':2,
                                                    'data_bytes':1
                                                    },
                                        'switch_off_reason': {
                                                    'date_time':False,
                                                    'location':3,
                                                    'data_bytes':1
                                                    }
                                                }
                                
                            },

                        '12':{
                                'key_name':'factory_init_1',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                        '13':{
                                'key_name':'factory_init_2',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },

                        '14':{
                                'key_name':'reset',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                            },
                        '15':{
                                'key_name':'get_billing_timestamp',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },
                        '16':{
                                'key_name':'get_billing_date_all',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },
                        '17':{
                                'key_name':'get_billing_info',
                                # 'no_of_params':4,
                                'data_len':23,
                                'bundle_key':{

                                        'total_billing_count': {
                                                    'date_time':False,
                                                    'location':0,
                                                    'data_bytes':1
                                                    },
                                        'demand_integration_period': {
                                                    'date_time':False,
                                                    'location':1,
                                                    'data_bytes':1
                                                    },
                                        'total_programming_count': {
                                                    'date_time':False,
                                                    'location':2,
                                                    'data_bytes':1
                                                    },
                                        'total_meter_power_up_count': {
                                                    'date_time':False,
                                                    'location':3,
                                                    'data_bytes':2
                                                    },
                                        'first_power_up_timestamp': {
                                                    'date_time':False,
                                                    'location':5,
                                                    'data_bytes':4
                                                    },
                                        'power_on_timestamp': {
                                                    'date_time':False,
                                                    'location':9,
                                                    'data_bytes':4
                                                    },
                                        'total_meter_on_duration': {
                                                    'date_time':False,
                                                    'location':13,
                                                    'data_bytes':4
                                                    },
                                        'power_failure_duration': {
                                                    'date_time':False,
                                                    'location':17,
                                                    'data_bytes':4
                                                    },
                                        
                                            }
                              },

                        '18':{
                                'key_name':'get_cumulative_programming_count',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },
                        '19':{
                                'key_name':'get_power_failure_count',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },

                        '20':{
                                'key_name':'get_power_failure_duration',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },
                            
                        '21':{
                                'key_name':'get_system_power_factor_all',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },

                        '22':{
                                'key_name':'get_current_active_MD',
                                'data_len':12,
                                'location':1,
                                'data_bytes':2
                            },

                        '23':{
                                'key_name':'get_current_apparent_MD',
                                'data_len':12,
                                'location':1,
                                'data_bytes':2
                            },

                        '24':{
                                'key_name':'get_current_reactive_MD',
                                'data_len':12,
                                'location':1,
                                'data_bytes':2
                            },

                        '25':{
                                'key_name':'get_past_active_MD_all',
                                'data_len':12,
                                'location':1,
                                'data_bytes':2
                            },

                        '26':{
                                'key_name':'get_past_apparent_MD_all',
                                'data_len':12,
                                'location':1,
                                'data_bytes':2
                            },

                        '27':{
                                'key_name':'get_past_reactive_MD_all',
                                'data_len':12,
                                'location':1,
                                'data_bytes':2
                            },

                        '28':{
                                'key_name':'get_active_energy_history_all',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },

                        '29':{
                                'key_name':'get_apparent_energy_history_all',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },

                        '30':{
                                'key_name':'get_reactive_lag_energy_history_all',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },

                        '31':{
                                'key_name':'get_reactive_lead_energy_history_all',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4
                            },

                        '32':{
                                'key_name':'set_MD_avg_period',
                                'data_len':2,
                                'location':1,
                                'data_bytes':1

                            },

                        '33':{
                                'key_name':'get_time',
                                'date_time':True,
                                'data_len':4,
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
                                'key_name':'get_1p_metering_data',
                                # 'no_of_params':4,
                                'data_len':66,
                                'bundle_key':{

                                        'voltage': {
                                                    'date_time':False,
                                                    'location':0,
                                                    'data_bytes':4
                                                    },
                                        'current': {
                                                    'date_time':False,
                                                    'location':4,
                                                    'data_bytes':4
                                                    },
                                        'neutral current': {
                                                    'date_time':False,
                                                    'location':8,
                                                    'data_bytes':4
                                                    },

                                        'active_power': {
                                                    'date_time':False,
                                                    'location':12,
                                                    'data_bytes':4
                                                    },
                                        'apparent_power': {
                                                    'date_time':False,
                                                    'location':16,
                                                    'data_bytes':4
                                                    },
                                        'reactive_power': {
                                                    'date_time':False,
                                                    'location':20,
                                                    'data_bytes':4
                                                    },
                                        'frequency': {
                                                    'date_time':False,
                                                    'location':24,
                                                    'data_bytes':4
                                                    },
                                        'power_factor': {
                                                    'date_time':False,
                                                    'location':28,
                                                    'data_bytes':4
                                                    },
                                        'active_energy': {
                                                    'date_time':False,
                                                    'location':32,
                                                    'data_bytes':4
                                                    },
                                        'apparent_energy': {
                                                    'date_time':False,
                                                    'location':36,
                                                    'data_bytes':4
                                                    },
                                        'reactive_energy': {
                                                    'date_time':False,
                                                    'location':40,
                                                    'data_bytes':4
                                                    },
                                        'reactive_energy exp': {
                                                    'date_time':False,
                                                    'location':44,
                                                    'data_bytes':4
                                                    },
                                        'active_hr_energy imp': {
                                                    'date_time':False,
                                                    'location':48,
                                                    'data_bytes':4
                                                    },
                                        'apparent_hr_energy imp': {
                                                    'date_time':False,
                                                    'location':52,
                                                    'data_bytes':4
                                                    },
                                        'reactive_hr_energy imp': {
                                                    'date_time':False,
                                                    'location':56,
                                                    'data_bytes':4
                                                    },
                                        'reactive_hr_energy exp': {
                                                    'date_time':False,
                                                    'location':60,
                                                    'data_bytes':4
                                                    },
                                        'tamper_events': {
                                                    'date_time':True,
                                                    'location':64,
                                                    'data_bytes':2
                                                    }
                                        }
                           },

                    '36':{
                                'key_name':'set_MD_avg_period',
                                'data_len':29,
                                'location':0,
                                'data_bytes':4
                            },
                    '37':{
                                'key_name':'only_factory_init_time',
                                'date_time':True,
                                'data_len':41,
                                'location':37,
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
                                                    'date_time':False,
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
                                                    'date_time':False,
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
                                'data_len':9,
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
                                                    },
                                        'amount':{
                                                    'date_time':False,
                                                    'location':5,
                                                    'data_bytes':4
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

                        },
                        '48':{
                                'key_name':'turn_relay_on',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2

                            },
                        '49':{
                                'key_name':'turn_relay_off',
                                'data_len':2,
                                'location':0,
                                'data_bytes':2

                            },
                        '50':{
                                'key_name':'3pget_time',
                                'date_time':True,
                                'data_len':70,
                                'location':0,
                                'data_bytes':4

                            },
                        '51':{
                                'key_name':'num_servey',
                                'data_len':4,
                                'location':0,
                                'data_bytes':4

                            },
                        '52':{
                                'key_name':'get_num_event',
                                # 'no_of_params':4,
                                'data_len':14,
                                'bundle_key':{

                                        'current_event': {
                                                    'date_time':False,
                                                    'location':0,
                                                    'data_bytes':4
                                                    },
                                        'power_event': {
                                                    'date_time':False,
                                                    'location':4,
                                                    'data_bytes':4
                                                    },
                                        'transaction_event': {
                                                    'date_time':False,
                                                    'location':8,
                                                    'data_bytes':4
                                                    },
                                        'other_event': {
                                                    'date_time':False,
                                                    'location':12,
                                                    'data_bytes':4
                                                    },
                                        'non_rollover': {
                                                    'date_time':True,
                                                    'location':16,
                                                    'data_bytes':4
                                                    }
                                            }
                                    },
                            '53':{
                                'data_len':2,
                                'location':0,
                                'data_bytes':2
                                
                                },
                            '54':{
                                'key_name':'get_num_event',
                                # 'no_of_params':4,
                                'data_len':30,
                                'bundle_key':{

                                        'timestamp': {
                                                    'date_time':True,
                                                    'location':0,
                                                    'data_bytes':4
                                                    },
                                        'current': {
                                                    'date_time':False,
                                                    'location':4,
                                                    'data_bytes':4
                                                    },
                                        'voltage': {
                                                    'date_time':False,
                                                    'location':8,
                                                    'data_bytes':4
                                                    },
                                        'block_real_energy': {
                                                    'date_time':False,
                                                    'location':12,
                                                    'data_bytes':4
                                                    }
                                        
                                            }
                                    }
                            '55':{
                                'key_name':'BILLING BY INDEX',
                                # 'no_of_params':4,
                                'data_len':44,
                                'bundle_key':{

                                     'billing date_time': {
                                                    'date_time':True,
                                                    'location':0,
                                                    'data_bytes':4
                                                    },
                                        'real_MD_timestamp': {
                                                    'date_time':False,
                                                    'location':4,
                                                    'data_bytes':4
                                                    },
                                        'real_MD_value': {
                                                    'date_time':False,
                                                    'location':8,
                                                    'data_bytes':4
                                                    },
                                        'apparent_MD_timestamp': {
                                                    'date_time':False,
                                                    'location':12,
                                                    'data_bytes':4 
                                                    },
                                        'apparent_MD_value': {
                                                    'date_time':False,
                                                    'location':16,
                                                    'data_bytes':4  
                                                    }
                                        'real_energy_snap': {
                                                    'date_time':True,
                                                    'location':20,
                                                    'data_bytes':4
                                                    },
                                        'apparent_energy_snap': {
                                                    'date_time':True,
                                                    'location':24,
                                                    'data_bytes':4
                                                    },
                                        'real_energy_export_snap': {
                                                    'date_time':True,
                                                    'location':28,
                                                    'data_bytes':4
                                                    },
                                        'apparent_energy_export_snap': {
                                                    'date_time':False,
                                                    'location':32,
                                                    'data_bytes':4
                                                    },
                                        'system_power_factor': {
                                                    'date_time':False,
                                                    'location':36,
                                                    'data_bytes':4
                                                    },
                                        'total_billing_duration': {
                                                    'date_time':False,
                                                    'location':40,
                                                    'data_bytes':4
                                                    }
                                            }
                            
                                    }


                        


                     }
    return response_keys