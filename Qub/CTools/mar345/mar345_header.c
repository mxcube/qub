/*********************************************************************
 *
 * mar345_header.c
 * 
 * Author:  	Claudio Klein, X-Ray Research GmbH.
 * Version: 	1.5
 * Date:        06/09/1999
 *
 * History:
 * Version    Date    	Changes
 * ______________________________________________________________________
 *
 * 1.5	      06/09/99  Element gap extended (8 values: gaps 1-8)
 * 1.4        14/05/98  Element gap introduced 
 *
 *********************************************************************/

#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#ifndef __sgi
#include <stdlib.h>
#endif
#include <time.h>

/*
 * mar software include files
 */
#include "mar345_header.h"

/*
 * Definitions
 */
#define STRING		0
#define INTEGER		1
#define FLOAT		2

/*
 * External variables
 */
extern int  InputType(char *);
extern void WrongType(int type, char *key, char *string);
extern void RemoveBlanks(char *str);	

/*
 * Local functions
 */
MAR345_HEADER	Getmar345Header(FILE *);
MAR345_HEADER	Setmar345Header(void  );
int 		Putmar345Header(int   , MAR345_HEADER);

/******************************************************************
 * Function: Getmar345Header
 ******************************************************************/
MAR345_HEADER
Getmar345Header(FILE *fp)
{
MAR345_HEADER	h;
int 		i,j, ntok=0,fpos=0;
int		ngaps = 0;
char 		str[64], buf[128], *key, *token[20];
int		head[32];


	/*
	 * Set defaults
	 */

	h = Setmar345Header();

	if( fp == NULL ) return( h ); 

	fseek( fp, 0, SEEK_SET );

	if ( fread( head, sizeof(int), 32, fp ) < 32) {
		return( h );
	}

	/* First 32 longs contain: */
	h.byteorder 	= (int  )head[ 0];
	h.size 		= (short)head[ 1];
	h.high 		= (int  )head[ 2];
	h.format	= (char )head[ 3];
	h.mode		= (char )head[ 4];
	h.pixels	= (int  )head[ 5];
	h.pixel_length 	= (float)head[ 6];
	h.pixel_height 	= (float)head[ 7];
	h.wave      	= (float)head[ 9]/1000000.;
	h.dist    	= (float)head[ 8]/1000.;
	h.phibeg	= (float)head[10]/1000.;
	h.phiend	= (float)head[11]/1000.;
	h.omebeg	= (float)head[12]/1000.;
	h.omeend	= (float)head[13]/1000.;
	h.chi   	= (float)head[14]/1000.;
	h.theta 	= (float)head[15]/1000.;

	/* First ASCII line (bytes 128 to 192 contains: mar research */
	/* Ignore it...                                              */

	fpos = fseek( fp, 192, SEEK_SET );

	/*
	 * Read input lines
	 */

	while( fgets(buf,64,fp)!= NULL){

		/* Always add 64 bytes to current filemarker after 1 read */
		fpos += 64;
		fseek( fp, fpos, SEEK_SET );

		/* Keyword: END OF HEADER*/
		if(strstr(buf,"END OF HEADER") ) 
			break;
		else if ( strstr( buf, "SKIP" ) ) continue;

		if ( strlen(buf) < 2 ) continue;

		/* Scip comment lines */
		if( buf[0] == '#' || buf[0]=='!' ) continue;

		/* Tokenize input string */
		/* ntok  = number of items on input line - 1 (key) */
		ntok = -1;	

		for(i=0;i<64;i++) {
			/* Convert TAB to SPACE */
			if( buf[i] == '\t') buf[i] = ' ';
			if( buf[i] == '\f') buf[i] = ' '; 
			if( buf[i] == '\n') buf[i] = '\0'; 
			if( buf[i] == '\r') buf[i] = '\0'; 
			if( buf[i] == '\0') break;
		}

		for(i=0;i<(int)strlen(buf);i++) {
			if( buf[i] == ' ' ) continue;
			ntok++; 
			for (j=i;j<(int)strlen(buf);j++) 
				if( buf[j] == ' ') break;
			i=j;
		}
		if (strlen(buf) < 3 ) continue; 

		key = strtok( buf, " ");

		/* Convert keyword to uppercase */
		for ( i=0; i<(int)strlen(key); i++ )
			if ( isalnum( key[i] ) ) key[i] = toupper( key[i] );

		for(i=0;i<ntok;i++) {
			token[i] = strtok( NULL, " ");
			strcpy( str, token[i] );

			for ( j=0; j<(int)strlen( str ); j++ )
				if ( isalnum( str[j] ) && !strstr(key,"PROG") ) str[j] = toupper( str[j] );
			strcpy( token[i] , str );
			RemoveBlanks( token[i] );
		}

		/* Keyword: PROGRAM */
		if(!strncmp(key,"PROG",4) && ntok >= 2 ) {
			strcpy( h.program, token[0] );
			strcpy( h.version, token[2] );
		}

		/* Keyword: OFFSET */
		else if(!strncmp(key,"OFFS",4) && ntok >= 1 ) {
		    	for ( i=0; i<ntok; i++ ) {
			    if ( strstr( token[i], "ROF" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.roff = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "TOF" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.toff = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    /* Compatibility with previous versions for GAP entries: */
			    else if ( strstr( token[i], "GAP" ) ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.gap[1]  = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			    }
			}
		}
		/* Keyword: GAP */
		else if(!strncmp(key,"GAPS",4) && ntok >= 1 ) {
		    	for ( i=0; i<ntok; i++ ) {
			    	if ( InputType( token[i] ) == INTEGER ) {
					if ( ngaps < N_GAPS ) 
						h.gap[ngaps++]  = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			}
		}

		/* Keyword: ADC */
		else if(!strncmp(key,"ADC",3) && ntok >= 1 ) {
		    	for ( i=0; i<ntok; i++ ) {
			    if ( strstr( token[i], "A" ) && strlen( token[i] ) == 1 ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.adc_A = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			    }
			    else if ( strstr( token[i], "B" ) && strlen( token[i] ) == 1 ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.adc_B = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			    }
			    else if ( strstr( token[i], "ADD_A" ) ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.add_A = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			    }
			    else if ( strstr( token[i], "ADD_B" ) ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.add_B = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			    }
			}
		}

		/* Keyword: MULTIPLIER */
		else if(!strncmp(key,"MULT",4) && ntok >= 0 )
			if ( InputType( token[0] ) >= INTEGER ) 
				h.multiplier = atof( token[0] );
			else
				WrongType( FLOAT, key, token[0] );

		/* Keyword: GAIN */
		else if(!strncmp(key,"GAIN",4) && ntok >= 0 )
			if ( InputType( token[0] ) >= INTEGER ) 
				h.gain = atof( token[0] );
			else
				WrongType( FLOAT, key, token[0] );

		/* Keyword: COUNTS */
		else if(!strncmp(key,"COUN",4) && ntok >= 1 )
			for(i=0;i<ntok;i++) {
			    if ( strstr( token[i], "STA" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.dosebeg = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "END" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.doseend = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "MIN" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.dosemin = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "MAX" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.dosemax = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "AVE" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.doseavg = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "SIG" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.dosesig = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "NME" ) ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.dosen = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			    }
			}

		/* Keyword: MODE */
		else if( !strncmp(key,"MODE",4) && ntok >= 0 ) 
			if ( strstr( token[0], "TIME" ) )
				h.mode  = 1;
			else if ( strstr( token[0], "DOSE" ) )
				h.mode  = 0;
			else
				WrongType( STRING, key, token[0] );

		/* Keyword: DISTANCE */
		else if(!strncmp(key,"DIST",4) && ntok >= 0 )
			if ( InputType( token[0] ) >= INTEGER ) 
				h.dist = atof( token[0] );
			else
				WrongType( FLOAT, key, token[0] );

		/* Keyword: PIXELSIZE */
		else if(!strncmp(key,"PIXE",4) && ntok >= 0 ) {
			for(i=0;i<ntok;i++) {
			    if ( strstr( token[i], "LEN" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.pixel_length = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "HEI" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.pixel_height= atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			}
		}


		/* Keyword: SCANNER */
		else if(!strncmp(key,"SCAN",4) && ntok >= 0 )
			if ( InputType( token[0] ) == INTEGER ) 
				h.scanner = atoi( token[0] );
			else
				WrongType( INTEGER, key, token[0] );

		/* Keyword: HIGH */
		else if(!strncmp(key,"HIGH",4) && ntok >= 0 )
			if ( InputType( token[0] ) == INTEGER ) 
				h.high    = atoi( token[0] );
			else
				WrongType( INTEGER, key, token[0] );

		/* Keyword: DATE */
		else if(!strncmp(key,"DATE",4) && ntok >= 0 ) {
			for ( i=0; i<(int)strlen( buf ); i++ ) 
				if ( buf[i] == ' ' ) break;
			for ( j=i; j<(int)strlen( buf ); j++ ) 
				if ( buf[j] != ' ' ) break;
			strcpy( h.date, buf+j );
		}

		/* Keyword: REMARK */
		else if(!strncmp(key,"REMA",4) && ntok >= 0 ) {
			for ( i=0; i<(int)strlen( buf ); i++ ) 
				if ( buf[i] == ' ' ) break;
			for ( j=i; j<(int)strlen( buf ); j++ ) 
				if ( buf[j] != ' ' ) break;
			strcpy( h.remark, buf+j );
		}

		/* Keyword: FORMAT */
		else if(!strncmp(key,"FORM",4) && ntok >= 1 )  {
			if ( InputType( token[0] ) == INTEGER ) 
				h.size = atoi( token[0] );
			else
				WrongType( INTEGER, key, token[0] );
			for ( i=1; i<ntok; i++ ) {
				if ( strstr( token[i], "PCK" ) ) 
					h.format = 1;
				else if ( strstr( token[i], "IMA" ) ) 
					h.format = 0;
				else if ( strstr( token[i], "SPI" ) )
					h.format = 2;
				else {
					if ( InputType( token[i] ) == INTEGER ) 
						h.pixels = atoi( token[i] );
					else
						WrongType( INTEGER, key, token[i] );
				}
			}
		}

		/* Keyword: LAMBDA or WAVELENGTH */
		else if( (!strncmp(key,"LAMB",4) || !strncmp(key,"WAVE",4) ) && ntok >= 0 ) 
			if ( InputType( token[0] ) >= INTEGER ) 
				h.wave = atof( token[0] );
			else
				WrongType( FLOAT, key, token[0] );
		

		/* Keyword: MONOCHROMATOR */
		else if( !strncmp(key,"MONO",4) && ntok >=0 ) { 
		    for ( i=0; i<ntok; i++ ) {
			 if ( strstr( token[i], "POLA" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.polar = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			}
			else {
				strcat( h.filter, token[i] );
			}
		    }
		}


		/* Keyword: PHI */
		else if(!strncmp(key,"PHI",3) && ntok >= 1 )
			for(i=0;i<ntok;i++) {
			    if ( strstr( token[i], "STA" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.phibeg = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "END" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.phiend = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "OSC" ) ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.phiosc = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			    }
			}

		/* Keyword: OMEGA */
		else if(!strncmp(key,"OMEG",4) && ntok >= 1 )
			for(i=0;i<ntok;i++) {
			    if ( strstr( token[i], "STA" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.omebeg = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "END" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.omeend = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "OSC" ) ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.omeosc = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			    }
			}

		/* Keyword: TWOTHETA */
		else if( !strncmp(key,"TWOT",4) && ntok >= 0 ) 
			if ( InputType( token[0] ) >= INTEGER ) 
				h.theta = atof( token[0] );
			else
				WrongType( FLOAT, key, token[0] );

		/* Keyword: CHI */
		else if( !strncmp(key,"CHI",3) && ntok >= 0 ) 
			if ( InputType( token[0] ) >= INTEGER ) 
				h.chi   = atof( token[0] );
			else
				WrongType( FLOAT, key, token[0] );

		/* Keyword: RESOLUTION */
		else if( !strncmp(key,"RESO",4) && ntok >= 0 ) 
			if ( InputType( token[0] ) >= INTEGER ) 
				h.resol = atof( token[0] );
			else
				WrongType( FLOAT, key, token[0] );

		/* Keyword: TIME */
		else if( !strncmp(key,"TIME",4) && ntok >= 0 ) 
			if ( InputType( token[0] ) >= INTEGER ) 
				h.time  = atof( token[0] );
			else
				WrongType( FLOAT, key, token[0] );

		/* Keyword: CENTER */
		else if( !strncmp(key,"CENT",4) && ntok >= 1 ) {
			for(i=0;i<ntok;i++) {
			    if ( strstr( token[i], "X" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.xcen = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "Y" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.ycen = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			}
		}
		
		/* Keyword: COLLIMATOR, SLITS */
		else if( ( !strncmp(key,"COLL",4) || !strncmp(key,"SLIT",4) )&& ntok >= 1 ) {
			for(i=0;i<ntok;i++) {
			    if ( strstr( token[i], "WID" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.slitx= atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			    else if ( strstr( token[i], "HEI" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.slity = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			    }
			}
		}
		
		/* Keyword: GENERATOR */
		else if( !strncmp(key,"GENE",4) && ntok >= 0 ) {
		    for(i=0;i<ntok;i++) {
		    	if ( strstr( token[i], "MA" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.mA = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			}
		    	else if ( strstr( token[i], "KV" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.kV = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			}
			else
				strcat( h.source, token[i] );
		    }
		}

		/* Keyword: INTENSITY */
		else if( !strncmp(key,"INTE",4) && ntok >= 0 ) {
		    for(i=0;i<ntok;i++) {
		    	if ( strstr( token[i], "MIN" ) ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.valmin = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			}
		    	else if ( strstr( token[i], "MAX" ) ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.valmax = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			}
		    	else if ( strstr( token[i], "AVE" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.valavg = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			}
		    	else if ( strstr( token[i], "SIG" ) ) {
				i++;
			    	if ( InputType( token[i] ) >= INTEGER ) {
					h.valsig = atof( token[i] );
				}
			        else
					WrongType( FLOAT, key, token[i] );
			}
		    }
		}
		
		/* Keyword: HISTOGRAM */
		else if( !strncmp(key,"HIST",4) && ntok >= 0 ) {
		    for(i=0;i<ntok;i++) {
		    	if ( strstr( token[i], "STA" ) ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.histbeg = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			}
		    	else if ( strstr( token[i], "END" ) ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.histend = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			}
		    	else if ( strstr( token[i], "MAX" ) ) {
				i++;
			    	if ( InputType( token[i] ) == INTEGER ) {
					h.histmax = atoi( token[i] );
				}
			        else
					WrongType( INTEGER, key, token[i] );
			}
		    }
		}
		
	} /* End of while loop */

	/*
	 * End of input lines (while loop)
	 */

	return( h );

}

/******************************************************************
 * Function: Setmar345Header
 ******************************************************************/
MAR345_HEADER
Setmar345Header()
{
MAR345_HEADER 	h;
int		i;

	h.byteorder		= 1234;
	h.wave      		= 1.541789;
	h.polar    		= 0.0;
	h.pixel_length 		= 150.0;
	h.pixel_height 		= 150.0;
	h.scanner		= 1;
	h.format		= 1;
	h.high  		= 0;
	h.size			= 0;
	h.dist			= 70.0;
	h.multiplier		= 1.0;
	h.mode			= 1;
	h.time			= 0.0;
	h.dosebeg		= 0.0;
	h.doseend		= 0.0;
	h.dosemin		= 0.0;
	h.dosemax		= 0.0;
	h.doseavg		= 0.0;
	h.dosesig		= 0.0;
	h.dosen  		= 0;
	h.phibeg		= 0.0;
	h.phiend		= 0.0;
	h.omebeg		= 0.0;
	h.omeend		= 0.0;
	h.phiosc		= 0;
	h.omeosc		= 0;
	h.theta  		= 0.0;
	h.chi			= 0.0;
	h.gain			= 1.0;
	h.xcen			= 600.;
	h.ycen			= 600.;
	h.kV			= 40.0;
	h.mA			= 50.0;
	h.valmin		= 0;
	h.valmax		= 0;
	h.valavg		= 0.0;
	h.valsig		= 0.0;
	h.histbeg		= 0;
	h.histend		= 0;
	h.histmax		= 0;
	h.roff			= 0.0;
	h.toff			= 0.0;
	h.slitx 		= 0.3;
	h.slity 		= 0.3;
	h.pixels		= 0;
   	h.adc_A			= -1;
   	h.adc_B			= -1;
	h.add_A			= 0;
	h.add_B			= 0;

	h.date[0]		= '\0';
	h.remark[0]		= '\0';
	strcpy( h.source, "\0" );
	strcpy( h.filter, "\0" );

	for ( i=0; i<N_GAPS; i++ )
		h.gap[i]	= 0;

	return( h );
}
