# # 调用函数创建剖面线（默认参数）
# create_hatch(acad)

# # 或使用自定义参数
# create_hatch(acad, internal_x=-3, internal_y=-8, pattern="ANSI31", scale=1.0, angle=0)


from pyautocad import Autocad
import time
acad = Autocad(create_if_not_exists=True) 
def create_hatch(acad, internal_x=-99, internal_y=1, pattern="ANSI31", scale=0.5, angle=0):
    """
    在已有图形上自动创建剖面线
    内部点默认(-99,1)，剖面线为ANSI31图案，比例0.5，角度0
    """
    try:
        print("正在创建剖面线...")

        # 第一步：创建边界
        print("执行BOUNDARY命令...")
        try:
            # 使用下划线前缀和空格避免对话框，回车确认
            doc = getattr(acad, 'doc', None)
            if doc is None:
                raise RuntimeError("未连接到 AutoCAD 文档")
            doc.SendCommand(f"_-BOUNDARY {internal_x},{internal_y} \n")
        except Exception as e_cmd:
            print(f"BOUNDARY 命令发送失败: {e_cmd}")
            return False

        # 等待边界创建完成
        print("等待边界创建...")
        time.sleep(2)

        # 第二步：创建剖面线
        print("执行HATCH命令...")
        try:
            cmd = f"_-HATCH P {pattern} {scale} {angle} S L \n\n"
            doc.SendCommand(cmd)
        except Exception as e_cmd:
            print(f"HATCH 命令发送失败: {e_cmd}")
            return False

        # 等待剖面线创建完成
        print("等待剖面线创建...")
        time.sleep(2.5)
        #我的电脑慢，多等一会儿
        print("剖面线创建完成")
        return True

    except Exception as e:
        print(f"剖面线创建失败: {e}")
        return False

# 使用示例
if __name__ == "__main__":
    # 连接到已打开的AutoCAD
    acad = Autocad(create_if_not_exists=True)
    
    # 创建剖面线
    create_hatch(acad)    
