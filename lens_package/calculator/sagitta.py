import math

def chord_length(sagitta: float, radius: float) -> float:
    """
    根据矢高（sagitta）和半径计算弦长。

    参数:
        sagitta (float): 矢高，即圆心到弦的垂直距离。
        radius (float): 圆的半径。

    返回:
        float: 弦长。
    """
    if radius <= 0:
        raise ValueError("半径必须为正数")
    if sagitta < 0 or sagitta > radius:
        raise ValueError("矢高必须在 0 到半径之间")
    # 弦长 = 2 * sqrt(r^2 - (r - s)^2)
    return 2 * math.sqrt(radius ** 2 - (radius - sagitta) ** 2)
if __name__ == "__main__":
    # 测试示例
    sagitta = 0.296
    radius = 28.11
    print(chord_length(sagitta, radius))
