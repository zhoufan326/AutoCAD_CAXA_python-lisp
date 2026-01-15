from pyautocad import Autocad

# 在创建图形之前加载线型
def load_linetypes(acad):
    """加载常用线型"""
    linetypes_to_load = [
        "DASHED",    # 虚线
        "CENTER",    # 中心线
        "HIDDEN",    # 隐藏线
        "DASHDOT",   # 点划线
        "PHANTOM",   # 双点划线
        "DOT",       # 点线
        "DASHED2",   # 虚线2
        "CENTER2"    # 中心线2
    ]
    
    for linetype in linetypes_to_load:
        try:
            # 检查线型是否已存在
            exists = False
            try:
                # 尝试获取线型，如果能获取到，说明已存在
                existing_linetype = acad.doc.Linetypes.Item(linetype)
                exists = True
                print(f"线型 {linetype} 已存在，跳过加载")
            except:
                # 获取失败，说明不存在
                exists = False
            
            if not exists:
                acad.doc.Linetypes.Load(linetype, "acad.lin")
                print(f"已加载线型: {linetype}")
                
        except Exception as e:
            # 检查错误是否是"记录名重复"
            error_str = str(e)
            if "记录名重复" in error_str or "Duplicate record name" in error_str:
                print(f"线型 {linetype} 已存在，跳过加载")
                continue
                
            print(f"加载线型 {linetype} 失败: {e}")
            
            # 尝试其他线型文件
            try:
                acad.doc.Linetypes.Load(linetype, "acadiso.lin")
                print(f"已从acadiso.lin加载线型: {linetype}")
            except Exception as e2:
                error_str2 = str(e2)
                if "记录名重复" in error_str2 or "Duplicate record name" in error_str2:
                    print(f"线型 {linetype} 已存在，跳过加载")
                else:
                    print(f"从acadiso.lin加载线型 {linetype} 也失败: {e2}")


if __name__ == "__main__":
    # 在连接AutoCAD后调用
    acad = Autocad(create_if_not_exists=True)
    load_linetypes(acad)