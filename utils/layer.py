from pyautocad import Autocad

acad = Autocad(create_if_not_exists = True)
def set_layer(layer_name="轮廓线", create_if_missing=True):
    """优化的图层设置方法（对 COM 错误进行保护）"""
    try:
        doc = getattr(acad, 'doc', None)
        if doc is None:
            raise RuntimeError("未连接到 AutoCAD 文档")

        try:
            # 直接通过名称设置（性能最佳）
            doc.ActiveLayer = doc.Layers.Item(layer_name)
            print(f"当前图层已设置为: {layer_name}")
            return True
        except Exception:
            # 图层不存在或取值失败
            if create_if_missing:
                try:
                    new_layer = doc.Layers.Add(layer_name)
                    doc.ActiveLayer = new_layer
                    print(f"创建并设置图层: {layer_name}")
                    return True
                except Exception as e_add:
                    print(f"创建图层失败: {e_add}")
                    return False
            else:
                print(f"图层 '{layer_name}' 不存在")
                return False
    except Exception as e_outer:
        print(f"设置图层失败: {e_outer}")
        return False

if __name__ == "__main__":
# 使用示例
    # set_layer("轮廓线")  # 存在则设置，不存在则创建
    set_layer("虚线", create_if_missing=False)  # 只设置，不创建
    acad.doc.SendCommand("_QSAVE\n")
    del acad