from xml.parsers.expat import model
from pyautocad import Autocad
from pyautocad import APoint

acad = Autocad(create_if_not_exists = True)
def insert_block( insertionPnt, block_name):
    
        model = getattr(acad, 'model', None)
        if model is None:
                raise RuntimeError("未连接到 AutoCAD  model")
      
        RetVal = model.InsertBlock(insertionPnt, block_name, 1, 1, 1, 0 )

   
        return RetVal