from pyautocad import Autocad
from pyautocad import APoint
acad = Autocad(create_if_not_exists = True)
acad.prompt("Hello! Autocad from pyautocad.")

def insert_block(insertionPnt):
    
    RetVal = acad.model.InsertBlock(insertionPnt, "Z:\\AutoCAD_AI\\Blocks\\A4图框.dwg", 1, 1, 1, 0 )
                # 外部文件名尽量与当前文件中的各块名称不同；
                # 插入后外部文件名将作为其在当前文件中的块名；
                # 外部文件的坐标原点为其作为块的定位夹点。
    return RetVal
    

def insert_XJMJM(insertionPnt2):
    
    RetVal2 = acad.model.InsertBlock(insertionPnt2, "Z:\\AutoCAD_AI\\Blocks\\下摆机精磨基模技术要求.dwg", 1, 1, 1, 0 )
                # 外部文件名尽量与当前文件中的各块名称不同；
                # 插入后外部文件名将作为其在当前文件中的块名；
                # 外部文件的坐标原点为其作为块的定位夹点。
    return RetVal2

def insert_Zhoufan(insertionPnt2):
    
    RetVal3 = acad.model.InsertBlock(insertionPnt2, "Z:\\AutoCAD_AI\\Blocks\\周凡绘图.dwg", 1, 1, 1, 0 )
                # 外部文件名尽量与当前文件中的各块名称不同；
                # 插入后外部文件名将作为其在当前文件中的块名；
                # 外部文件的坐标原点为其作为块的定位夹点。
    return RetVal3