import logging
import qt
import os
import os.path

class QubSvgImageSave :
    def __init__(self,image,canvas = None) :
        self.__items = []
        self.__image = image
        if canvas is not None :
            for item in canvas.allItems() :
                if item.isVisible() :
                    if hasattr(item,'setScrollView') : # remove standalone items
                        continue
                    newObject = item.__class__(item)
                    newObject.setCanvas(None)
                    self.__items.append(newObject)
                    
    def save(self,file_path) :
        old_path = os.getcwdu()
        path,filename = os.path.split(file_path)
        os.chdir(path)
        device = qt.QPicture()
        painter = qt.QPainter(device)
        if self.__image is not None :
            painter.drawImage(0,0,self.__image)
        for item in self.__items :
            item.draw(painter)
        painter.end()
        try:
            if not device.save(filename,'svg') :
                logging.getLogger().error("could not save the image file %s in SVG format",
                                          file_path)
            else:                       # HACK
                f = file(file_path,'r+')
                lines = ''
                for line in f:
                    if line[0:4] == '<svg' :
                        line = '<svg xmlns:xlink="http://www.w3.org/1999/xlink"' + line[4:]
                    lines += line
                f.seek(0,0)
                f.write(lines)
                f.close()
                
        except:
            import traceback
            traceback.print_exc()
