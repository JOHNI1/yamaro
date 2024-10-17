# X = None

# def print_X_from_test():
#     global X
#     print(f'In print_X_from_tesQt, X is {X}')

# Y = {"a": 1, "b": 2}

# # for Y["x"] in range(3):
# #     print(Y["x"])

# # print(Y)

# Z = Y

# M = Z

# Z = {"c": 3, "d": 4}

# print(M)
# import os
# print(os.path.expanduser('~/yamaro/example.yaml'))


# T = dict(a=1, b=2, c=3, d=4)

# print(T["k"] is not None)

# if  (w := 1) or (w := 2) or (w := 6):
#     print('w: ', w)
#     print("done")


# e = [4, 5]

# for i in range(3):
#     print(i)
#     e.insert(i , 100)

# print(e)


# def b(aw):

#     aw('hi')

# def a(txt):
#     print(txt)

# b(a)    

# print(2/5)


# a = ''.split(',')
# print(a)
# import math

# print(math.pi)


# a= 1

# print(eval('a/2'))

sub_vars = dict()

sub_vars['xyz'] = '1 2 3'

sub_vars['xyzz'] = [1, 2, 3]


print(' '.join(str(float((sub_vars['xyz']).split()[i]) - sub_vars['xyzz'][i]) for i in range(3)))