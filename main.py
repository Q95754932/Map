import cv2
import os
import numpy as np
from PIL import Image


class CoordinateDrawer:
    """坐标点绘制器，用于在图像上绘制经纬度坐标点"""

    def __init__(self, folder_path, display_size=(1920, 1080)):
        """
        初始化坐标点绘制器
        :param folder_path: 包含图片和坐标文件的文件夹路径
        :param display_size: 显示图像的目标尺寸，默认(1920, 1080)
        """
        self.folder_path = os.path.normpath(folder_path)
        self.display_size = display_size
        self.image_path = None
        self.txt_path = None
        self.corner_points = None
        self.original_image = None
        self.lon_range = None
        self.lat_range = None
        self._initialize()

    def _initialize(self):
        """初始化：查找图片和坐标文件，读取角点信息"""
        # 查找png图片和txt文件
        for file in os.listdir(self.folder_path):
            if file.endswith(".png"):
                self.image_path = os.path.join(self.folder_path, file)
            elif file.endswith(".txt"):
                self.txt_path = os.path.join(self.folder_path, file)
        if not (self.image_path and self.txt_path):
            raise FileNotFoundError("未找到配对的png图片和txt文件")
        # 读取图像
        self.original_image = cv2.imread(self.image_path)
        if self.original_image is None:
            raise ValueError(f"无法读取图像: {self.image_path}")
        # 读取角点坐标
        self.corner_points = self._read_corner_points()
        # 设置经纬度范围
        self._set_coordinate_range()

    def _read_corner_points(self):
        """读取txt文件中的角点坐标"""
        points = []
        with open(self.txt_path, "r", encoding="utf-8") as f:
            for line in f:
                if "经纬度坐标" in line:
                    coords = line.split("：")[-1].strip().split(",")
                    points.append(list(map(float, coords)))
        if len(points) != 4:
            raise ValueError("需要正好4个角点坐标")
        return points

    def _set_coordinate_range(self):
        """设置经纬度范围"""
        left_bottom, left_top, right_top, right_bottom = self.corner_points
        self.lon_range = (left_top[0], right_bottom[0])
        self.lat_range = (left_bottom[1], left_top[1])

    def _convert_to_pixel(self, lon, lat):
        """将经纬度转换为像素坐标"""
        height, width = self.original_image.shape[:2]
        left_bottom, left_top, right_top, right_bottom = self.corner_points
        x = int((lon - left_top[0]) / (right_bottom[0] - left_top[0]) * width)
        y = int((lat - left_top[1]) / (right_bottom[1] - left_top[1]) * height)
        return x, y

    def _resize_with_padding(self, image):
        """等比例缩放图像并添加灰色填充"""
        target_width, target_height = self.display_size
        img_height, img_width = image.shape[:2]
        # 计算缩放比例
        scale = min(target_width / img_width, target_height / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        # 创建灰色背景
        display_img = np.ones((target_height, target_width, 3), dtype=np.uint8) * 128
        # 缩放原图
        resized_img = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        # 计算偏移量并粘贴图像
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        display_img[y_offset : y_offset + new_height, x_offset : x_offset + new_width] = resized_img
        return display_img

    def draw(self, coordinates, color=(0, 255, 0), size=5, show=True):
        """
        在图像上绘制坐标点
        :param coordinates: 经纬度坐标列表 [(lon1,lat1), ...]
        :param color: 点的颜色(BGR格式)，默认绿色
        :param size: 点的大小，默认5
        :param show: 是否显示图像，默认True
        :return: 原始大小的绘制结果图像
        """
        result_image = self.original_image.copy()
        for lon, lat in coordinates:
            x, y = self._convert_to_pixel(lon, lat)
            if 0 <= x < result_image.shape[1] and 0 <= y < result_image.shape[0]:
                cv2.circle(result_image, (x, y), size, color, -1)
        if show:
            display_img = self._resize_with_padding(result_image)
            rgb_display = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
            Image.fromarray(rgb_display).show()
        return result_image

    def get_coordinate_range(self):
        """获取经纬度范围"""
        return {"longitude": self.lon_range, "latitude": self.lat_range}


# 使用示例
if __name__ == "__main__":
    # 初始化绘制器
    drawer = CoordinateDrawer("map")

    # import random
    # # 获取坐标范围
    # coord_range = drawer.get_coordinate_range()
    # # 生成随机点
    # test_coordinates = [
    #     (
    #         round(random.uniform(coord_range["longitude"][0], coord_range["longitude"][1]), 9),
    #         round(random.uniform(coord_range["latitude"][0], coord_range["latitude"][1]), 9),
    #     )
    #     for _ in range(100)
    # ]

    test_coordinates = [
        (117.625616938, 36.000582576),
        (117.615423202, 36.005922854),
        (117.636689097, 35.995920897),
    ]

    # 绘制点位  颜色格式：BGR
    drawer.draw(test_coordinates, color=(0, 0, 255), size=5)
