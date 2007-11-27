import qt
import os.path

def loadIcon(iconName):
    """
    Try to load an icon from file and return the QPixmap object
    Normally, the directory is Qub/Icons/IconLibrary
    """
    icondir   = os.path.dirname(__file__)
    ICONS_DIR = os.path.join(icondir, 'IconsLibrary')
    filename  = os.path.join(ICONS_DIR, iconName)

    """
    In case of frozen applications, icon files may not be in
    Qub/Icons/IconsLibrary but in ./IconsLibrary.
    Therefore, we first check in ./IconsLibrary before stating that the
    file does not exist
    """
    if not os.path.exists(filename):
        icondir = "."
        ICONS_DIR = os.path.join(icondir, 'IconsLibrary')
        filename  = os.path.join(ICONS_DIR, iconName)

    if not os.path.exists(filename):
        for ext in ['png', 'xpm', 'gif', 'bmp']:
            f = '.'.join([filename, ext])
            if os.path.exists(f):
                filename = f
                break

    try:
        icon = qt.QPixmap(filename)
    except:
        return qt.QPixmap(os.path.join(ICONS_DIR, 'esrf_logo.png'))
    else:
        if icon.isNull():
            return qt.QPixmap(os.path.join(ICONS_DIR, 'esrf_logo.png'))
        else:
            return icon


def getIconPath(iconName):
    """
    Return path to an icon
    """
    icondir   = os.path.dirname(__file__)
    ICONS_DIR = os.path.join(icondir, 'IconsLibrary')
    filename  = os.path.join(ICONS_DIR, iconName)
    
    if not os.path.exists(filename):
        icondir = "."
        ICONS_DIR = os.path.join(icondir, 'IconsLibrary')
        filename  = os.path.join(ICONS_DIR, iconName)

    if not os.path.exists(filename):
        for ext in ['png', 'xpm', 'gif', 'bmp']:
            f = '.'.join([filename, ext])
            if os.path.exists(f):
                filename = f
                break
    
    if os.path.exists(filename):
        return filename
        

