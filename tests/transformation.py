import numpy as np

def rotate_vector(vector, roll, pitch, yaw):
    # Create rotation matrices for roll, pitch, and yaw
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])
    
    Ry = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])
    
    # Combined rotation matrix
    R = Rz @ Ry @ Rx
    
    # Rotate the vector
    rotated_vector = R @ vector
    
    return rotated_vector

# Example usage
vector = np.array([0, 0, -0.5])  # Original vector (x, y, z)
roll, pitch, yaw = 0, 0, np.pi  # Rotation angles (r, p, y)
rotated_vector = rotate_vector(vector, roll, pitch, yaw)

print(list(rotated_vector))

print("Rotated vector:", rotated_vector)