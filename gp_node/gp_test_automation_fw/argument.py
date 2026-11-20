def test_var_kwargs(farg, **kwargs):
    print "formal arg:", farg

    for key in kwargs:
        print "%s: %s" % (key, kwargs[key])

test_var_kwargs(1, voltage=240,current=20)

# def test_var_args_call(arg1, arg2, arg3):
#     print "arg1:", arg1
#     print "arg2:", arg2
#     print "arg3:", arg3

# kwargs = {"arg3": 3, "arg2": "two"}
# test_var_args_call(1, **kwargs)

# def test_var_args_call(arg1, arg2, arg3):
#     print "arg1:", arg1
#     print "arg2:", arg2
#     print "arg3:", arg3

# args = ("two", 3)
# test_var_args_call(1, *args)