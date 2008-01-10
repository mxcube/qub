/***********************************************************************
 *
 * mar345: pck.c
 *
 * Copyright by:        Dr. Claudio Klein
 *                      X-ray Research GmbH, Hamburg
 *
 * Version:     1.0
 * Date:        16/01/1997
 *
 ***********************************************************************/

#include <stdio.h>

#define BYTE char
#define WORD short int
#define LONG int

#define PACKIDENTIFIER "\nCCP4 packed image, X: %04d, Y: %04d\n"

const LONG setbits[33] = {0x00000000L, 0x00000001L, 0x00000003L, 0x00000007L,
			  0x0000000FL, 0x0000001FL, 0x0000003FL, 0x0000007FL,
			  0x000000FFL, 0x000001FFL, 0x000003FFL, 0x000007FFL,
			  0x00000FFFL, 0x00001FFFL, 0x00003FFFL, 0x00007FFFL,
			  0x0000FFFFL, 0x0001FFFFL, 0x0003FFFFL, 0x0007FFFFL,
			  0x000FFFFFL, 0x001FFFFFL, 0x003FFFFFL, 0x007FFFFFL,
			  0x00FFFFFFL, 0x01FFFFFFL, 0x03FFFFFFL, 0x07FFFFFFL,
			  0x0FFFFFFFL, 0x1FFFFFFFL, 0x3FFFFFFFL, 0x7FFFFFFFL,
                          0xFFFFFFFFL};
#define shift_left(x, n)  (((x) & setbits[32 - (n)]) << (n))
#define shift_right(x, n) (((x) >> (n)) & setbits[32 - (n)])

/***************************************************************************
 * Function: unpack_word
 ***************************************************************************/
void unpack_word(FILE *packfile, int x, int y, WORD *img)
{
  int 		valids = 0, spillbits = 0, usedbits, total = x * y;
  LONG 		window = 0L, spill = 0, pixel = 0, nextint, bitnum, pixnum;
  static int 	bitdecode[8] = {0, 4, 5, 6, 7, 8, 16, 32};

  while (pixel < total) 
    {
      if (valids < 6) 
	{
	  if (spillbits > 0) 
	    {
	      window |= shift_left(spill, valids);
	      valids += spillbits;
	      spillbits = 0;
	    }
	  else
	    {
	      spill = (LONG) getc(packfile);
	      spillbits = 8;
	    }
	}
      else 
	{
	  pixnum = 1 << (window & setbits[3]);
	  window = shift_right(window, 3);
	  bitnum = bitdecode[window & setbits[3]];
	  window = shift_right(window, 3);
	  valids -= 6;
	  while ((pixnum > 0) && (pixel < total)) 
	    {
	      if (valids < bitnum) 
		{
		  if (spillbits > 0) 
		    {
		      window |= shift_left(spill, valids);
		      if ((32 - valids) > spillbits) 
			{
			  valids += spillbits;
			  spillbits = 0;
			}
		      else 
			{
			  usedbits = 32 - valids;
			  spill = shift_right(spill, usedbits);
			  spillbits -= usedbits;
			  valids = 32;
			}
		    }
		  else 
		    {
		      spill = (LONG) getc(packfile);
		      spillbits = 8;
		    }
		}
	      else 
		{
		  --pixnum;
		  if (bitnum == 0) 
		    nextint = 0;
		  else 
		    {
		      nextint = window & setbits[bitnum];
		      valids -= bitnum;
		      window = shift_right(window, bitnum);
		      if ((nextint & (1 << (bitnum - 1))) != 0)
			nextint |= ~setbits[bitnum];
		    }
		  if (pixel > x) 
		    {
		      img[pixel] = (WORD) (nextint +
					   (img[pixel-1] + img[pixel-x+1] +
					    img[pixel-x] + img[pixel-x-1] + 2) / 4);
		      ++pixel;
		    }
		  else if (pixel != 0) 
		    {
		      img[pixel] = (WORD) (img[pixel - 1] + nextint);
		      ++pixel;
		    }
		  else
		    img[pixel++] = (WORD) nextint;
		}
	    }
	}
    }
}



