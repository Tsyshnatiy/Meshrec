import numpy as np
import math
import trimesh


class CylinderProjection:
    def __init__(self, path, res_height, res_width):
        self.mesh = trimesh.load_mesh(path)

        ps_pt1, ps_pt2, ps_dir_vect = self.__principal_section()
        ray_sources = self.__construct_projection_points(res_height, ps_pt1, ps_pt2)
        ray_dirs = self.__construct_ray_dirs(ps_dir_vect, res_width)

        def fill_by_array(n, arr):
            result = arr.copy()
            for idx in range(n - 1):
                result = np.vstack((result, arr))
            return result

        self.projection = np.empty((res_height, res_width))
        self.projection.fill(0)

        for i in range(res_height):
            point = ray_sources[i]
            ray_source = fill_by_array(res_width, ray_sources[i])
            locations, ind_ray = self.mesh.ray.intersects_location(ray_source, ray_dirs)

            for j in range(len(ind_ray)):
                loc = locations[j]
                intersected_ray_idx = ind_ray[j]
                intersection_point_dist = np.linalg.norm(point - loc)

                # We can take ray_sources[0] because all rays in the batch have same source
                if self.projection[i][intersected_ray_idx] < intersection_point_dist:
                    self.projection[i][intersected_ray_idx] = intersection_point_dist

    def __principal_section(self):
        box = self.mesh.bounding_box
        assert len(box.vertices) == 8 and box.volume != 0

        dir_vect = np.array([0, 0, 1])

        z1, z2 = box.bounds[0][2], box.bounds[1][2]
        x, y = box.center_mass[0], box.center_mass[1]
        pt1 = np.array([x, y, z1])
        pt2 = np.array([x, y, z2])

        return pt2, pt1, dir_vect

    def __construct_projection_points(self, proj_size, ps_pt1, ps_pt2):
        dist = np.linalg.norm(ps_pt1 - ps_pt2)
        step = dist / (proj_size - 1)

        ps_vect = (ps_pt2 - ps_pt1) / dist

        result = np.zeros((proj_size, 3))
        pt = np.copy(ps_pt1)
        for i in range(proj_size):
            result[i] = pt
            pt += step * ps_vect

        return result

    def __construct_ray_dirs(self, ps_vect, proj_width_size):
        def rotation_matrix(axis, theta):
            """
            Return the rotation matrix associated with counterclockwise rotation about
            the given axis by theta radians.
            """
            axis = np.asarray(axis)
            axis = axis / math.sqrt(np.dot(axis, axis))

            a = math.cos(theta/2.0)
            b, c, d = -axis * math.sin(theta / 2.0)
            aa, bb, cc, dd = a * a, b * b, c * c, d * d
            bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
            return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                             [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                             [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

        rad_step = 2 * np.pi / proj_width_size
        ray_dir_vect = np.array([1, 0, 0])

        result = np.zeros((proj_width_size, 3))
        for i in range(proj_width_size):
            result[i] = ray_dir_vect
            rot_mat = rotation_matrix(ps_vect, rad_step)
            ray_dir_vect = np.dot(rot_mat, ray_dir_vect)

        return result
