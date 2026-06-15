from utils.com_interface import Autocad
#使用sendcommand的方式删除
def delete_all_entities():
    """删除模型空间和图纸空间中的所有实体。"""
    acad = Autocad()
    # 删除模型空间对象（SendCommand 可能抛出 COM 错误）
    try:
        doc = getattr(acad, 'doc', None)
        if doc is None:
            raise RuntimeError("未连接到 AutoCAD 文档")
        doc.SendCommand("_ERASE _ALL\n\n")
        # 切换到图纸空间（布局）并删除对象
        doc.SendCommand("_PSPACE\n")  # 进入图纸空间
        doc.SendCommand("_ERASE _ALL\n\n")
        doc.SendCommand("_MSPACE\n")   # 切换回模型空间（可选）
        print("All entities in Model and Paper space have been deleted.")
    except Exception as e:
        print(f"删除实体失败（SendCommand）: {e}")

def purge_all_unused():
    """彻底清理所有未使用的图层、块、样式等。"""
    acad = pyautocad.Autocad()
    try:
        doc = getattr(acad, 'doc', None)
        if doc is None:
            raise RuntimeError("未连接到 AutoCAD 文档")
        # 运行两次PURGE以确保清理嵌套的未使用项
        doc.SendCommand("_-PURGE\n_A\n*\n_N\n")  # 第一轮清理
        doc.SendCommand("_-PURGE\n_A\n*\n_N\n")  # 第二轮清理
        print("All unused items have been purged.")
    except Exception as e:
        print(f"Purge 失败（SendCommand）: {e}")

# 使用示例
if __name__ == "__main__":
    delete_all_entities()
    # purge_all_unused()