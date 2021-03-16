import numpy as np
class detectionInfo(object):
    def __init__(self, line):
        self.name = line[0]

        self.truncation = float(line[1])
        self.occlusion = int(line[2])

        # local orientation = alpha + pi/2
        self.alpha = float(line[3])

        # in pixel coordinate
        self.xmin = float(line[4])
        self.ymin = float(line[5])
        self.xmax = float(line[6])
        self.ymax = float(line[7])

        # height, weigh, length in object coordinate, meter
        self.h = float(line[8])
        self.w = float(line[9])
        self.l = float(line[10])

        # x, y, z in camera coordinate, meter
        self.tx = float(line[11])
        self.ty = float(line[12])
        self.tz = float(line[13])

        # global orientation [-pi, pi]
        self.rot_global = float(line[14])

    def member_to_list(self):
        output_line = []
        for name, value in vars(self).items():
            output_line.append(value)
        return output_line

    def box3d_candidate(self, rot_local, soft_range):
        x_corners = [self.l, self.l, self.l, self.l, 0, 0, 0, 0]
        y_corners = [self.h, 0, self.h, 0, self.h, 0, self.h, 0]
        z_corners = [0, 0, self.w, self.w, self.w, self.w, 0, 0]

        x_corners = [i - self.l / 2 for i in x_corners]
        y_corners = [i - self.h for i in y_corners]
        z_corners = [i - self.w / 2 for i in z_corners]

        corners_3d = np.transpose(np.array([x_corners, y_corners, z_corners]))
        point1 = corners_3d[0, :]
        point2 = corners_3d[1, :]
        point3 = corners_3d[2, :]
        point4 = corners_3d[3, :]
        point5 = corners_3d[6, :]
        point6 = corners_3d[7, :]
        point7 = corners_3d[4, :]
        point8 = corners_3d[5, :]

        # set up projection relation based on local orientation
        xmin_candi = xmax_candi = ymin_candi = ymax_candi = 0

        if 0 < rot_local < np.pi / 2:
            xmin_candi = point8
            xmax_candi = point2
            ymin_candi = point2
            ymax_candi = point5

        if np.pi / 2 <= rot_local <= np.pi:
            xmin_candi = point6
            xmax_candi = point4
            ymin_candi = point4
            ymax_candi = point1

        if np.pi < rot_local <= 3 / 2 * np.pi:
            xmin_candi = point2
            xmax_candi = point8
            ymin_candi = point8
            ymax_candi = point1

        if 3 * np.pi / 2 <= rot_local <= 2 * np.pi:
            xmin_candi = point4
            xmax_candi = point6
            ymin_candi = point6
            ymax_candi = point5

        # soft constraint
        div = soft_range * np.pi / 180
        if 0 < rot_local < div or 2*np.pi-div < rot_local < 2*np.pi:
            xmin_candi = point8
            xmax_candi = point6
            ymin_candi = point6
            ymax_candi = point5

        if np.pi - div < rot_local < np.pi + div:
            xmin_candi = point2
            xmax_candi = point4
            ymin_candi = point8
            ymax_candi = point1

        return xmin_candi, xmax_candi, ymin_candi, ymax_candi, rot_global
