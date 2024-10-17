from test import X, print_X_from_test

def change_X():
    global X
    X = 5
    print(f'In change_X, X is now {X}')
    print()
    print_X_from_test()

change_X()