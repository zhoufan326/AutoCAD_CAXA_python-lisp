# fixture/__init__.py
# 初始化模块，用于便捷导入FixtureOperations类

from .fixture import FixtureOperations

__all__ = ['FixtureOperations']

"""
使用示例：

# 从fixture模块导入FixtureOperations
from fixture import FixtureOperations

# 方法1：自动创建AutoCAD连接
fixture = FixtureOperations()

# 方法2：使用现有的AutoCAD连接
# from utils.com_interface import Autocad
# acad = Autocad()
# fixture = FixtureOperations(acad=acad)

# 使用示例
params = {
    "type": "XSZJ_POM",
    "base": APoint(0, 0),
    "diameter": 10.8,
    "POM_thickness": 1.5,
    "Cu_thickness": 0.5,
    "POM_height": 10.0,
    "height": 1.1,
    "radius": -9.497
}

try:
    # 执行主函数
    fixture.main(params, type=params["type"], designer_name="周凡")
    
    # 保存图形
    saved_path = fixture.save_drawing(params)
    if saved_path:
        print(f"图形保存成功: {saved_path}")
    else:
        print("图形保存失败")
finally:
    # 清理资源
    fixture.acad = None
    print("操作完成")
"""
