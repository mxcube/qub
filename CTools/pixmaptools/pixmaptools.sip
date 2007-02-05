

%Import qt/qtmod.sip


%Module pixmaptools 0

%Doc
<h1>Class IO</h1>
<p>
This class was copied from KPixmapIO and just rename IO
</p>
%End

class IO
{

%TypeHeaderCode
#include <pixmaptools_io.h>
%End

public:
    IO();
    ~IO();

    /**
     * Convert an image to a pixmap.
     * @param image The image to convert.
     * @return The pixmap containing the image.
     */
    QPixmap convertToPixmap(const QImage&);
    
    /**
     * Convert a pixmap to an image.
     * @param pixmap The pixmap to convert.
     * @return The image.
     */
    QImage convertToImage(const QPixmap&);

    /**
     * Bitblt an image onto a pixmap.
     * @param dst The destination pixmap.
     * @param dx Destination x offset.
     * @param dy Destination y offset.
     * @param src The image to load.
     */
    void putImage(QPixmap*,int,int,const QImage *);

    /**
     * This function is identical to the one above. It only differs in the
     * arguments it accepts.
     */
    void putImage(QPixmap*,const QPoint &,const QImage *);

    /**
     * Transfer (a part of) a pixmap to an image.
     * @param src The source pixmap.
     * @param sx Source x offset.
     * @param sy Source y offset.
     * @param sw Source width.
     * @param sh Source height.
     * @return The image.
     */
    QImage getImage(const QPixmap*,int,int,int,int);

    /**
     * This function is identical to the one above. It only differs in the
     * arguments it accepts.
     */
    QImage getImage(const QPixmap*,const QRect&);

    /**
     * Shared memory allocation policies.
     */
    enum ShmPolicies {
	ShmDontKeep,
	ShmKeepAndGrow
    };
    /**
     * Set the shared memory allocation policy. See the introduction for
     * IO for a discussion.
     * @param policy The alloction policy.
     */
    void setShmPolicy(int);

    /**
     * Pre-allocate shared memory. IO will be able to transfer images
     * up to this size without resizing.
     * @param size The size of the image in @em pixels.
     */
    void preAllocShm(int);
};

