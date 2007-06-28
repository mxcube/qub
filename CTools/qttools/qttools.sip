

%Import qt/qtmod.sip


%Module qttools 0

%Doc
<h1>Class qttools</h1>
<p>
This class is use to access to variable and fonction which is not wrap in qt module
</p>
%End

class qttools
{

%TypeHeaderCode
#include <qttools_qttools.h>
%End

public:
	static bool get_qt_resolve_symlinks();
	static void set_qt_resolve_symlinks(bool);
};

class QtXEmbedClient : QWidget
{
%TypeHeaderCode
#include <qtxembed.h>
%End

public:
    QtXEmbedClient(QWidget* = 0, const char * = 0);
    ~QtXEmbedClient();

    void embedInto(WId);
    WId containerWinId() const;

    enum Errors {
	Unknown = 0,
	Internal = 1,
	InvalidWindowID = 2
    };
    
signals:
    void embedded();
    void containerClosed();
    void error(int);
    
protected:
    bool eventFilter(QObject *, QEvent *);
    
    void setEmbedded();
};

class QtXEmbedContainer : QWidget
{
%TypeHeaderCode
#include <qtxembed.h>
%End
public:
    QtXEmbedContainer(QWidget* = 0,const char * = 0);
    ~QtXEmbedContainer();
        
    void embed(WId,bool = true);
    void discardClient();

    WId clientWinId() const;

    QSize minimumSizeHint() const;
    
    enum Errors {
	Unknown = 0,
	Internal = 1,
	InvalidWindowID = 2
    };

signals:
    void clientIsEmbedded();
    void clientClosed();
    void error(int);
    
protected:
    bool eventFilter(QObject *, QEvent *);
    void resizeEvent(QResizeEvent *);
    void showEvent(QShowEvent *);
    void hideEvent(QHideEvent *);
    
    bool isEmbedded() const;
    void moveInputToProxy();

    void acceptClient(WId);
    void rejectClient(WId);

    void checkGrab();
    
    WId topLevelParentWinId() const;

};
