import os
import os.path
import re
import logging
import qt

class QubSvgImageSave :
    def __init__(self,image,canvasOrcanvasList = None,zoom = 1) :
        self.__items = []
        self.__image = image
        self.__zoom = zoom
        self.__path2ellipseExp = re.compile('^.*<path (.+?) d="M ([0-9.]+) ([0-9.]+) A ([0-9.]+) ([0-9.]+).*$')
        if canvasOrcanvasList is not None :
            if isinstance(canvasOrcanvasList,list) :
                itemsList = canvasOrcanvasList
            else:
                itemsList = canvasOrcanvasList.allItems()
            for item in itemsList :
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
        zoom = 1 / self.__zoom
        painter.setWorldMatrix(qt.QWMatrix(zoom,0,0,zoom,0,0))
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
                    else:
                        g = self.__path2ellipseExp.match(line)
                        if g:
                            line = '<ellipse %s cx="%f" cy="%s" rx="%s" ry="%s" />\n' % (g.group(1),float(g.group(2)) - float(g.group(4)),g.group(3),g.group(4),g.group(5))
                    lines += line
                f.seek(0,0)
                f.write(lines)
                f.close()
                
        except:
            import traceback
            traceback.print_exc()
