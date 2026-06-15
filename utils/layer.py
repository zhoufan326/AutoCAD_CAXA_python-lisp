# 直接创建 AutoCAD 实例
from utils.com_interface import Autocad
import time
from .retry_decorator import safe_acad_retry

def _ensure_acad_instance(acad):
    """确保AutoCAD实例有效，如果无效则尝试重新连接"""
    try:
        # 尝试访问ActiveDocument以验证连接
        doc = acad.doc
        if doc is None:
            raise RuntimeError("AutoCAD文档不可用")
        return True
    except Exception:
        # 连接失败，尝试重新创建实例
        try:
            time.sleep(0.5)  # 短暂延迟后重试
            # 尝试重新初始化现有实例
            acad.app = Autocad(create_if_not_exists=True).app
            time.sleep(0.5)  # 等待实例初始化
            # 再次验证连接
            doc = acad.doc
            return doc is not None
        except Exception:
            return False

@safe_acad_retry(max_retries=5, delay=1.0, name="设置图层")
def set_layer(layer_name="轮廓线", create_if_missing=True):
    """优化的图层设置方法（对 COM 错误进行保护）"""
    # 内部创建AutoCAD实例
    acad = Autocad(create_if_not_exists=True)
    time.sleep(0.3)  # 短暂延迟
    
    # 确保AutoCAD实例有效
    if not _ensure_acad_instance(acad):
        raise RuntimeError("未连接到 AutoCAD")
    
    doc = acad.doc

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

if __name__ == "__main__":
# 使用示例
    # set_layer("轮廓线")  # 存在则设置，不存在则创建
    set_layer("虚线", create_if_missing=False)  # 只设置，不创建
    acad.doc.SendCommand("_QSAVE\n")
    del acad

__version__ = "0.2.0"