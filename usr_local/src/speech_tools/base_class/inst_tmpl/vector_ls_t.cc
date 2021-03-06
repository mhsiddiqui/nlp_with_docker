 /************************************************************************/
 /*                                                                      */
 /*                Centre for Speech Technology Research                 */
 /*                     University of Edinburgh, UK                      */
 /*                       Copyright (c) 1996,1997                        */
 /*                        All Rights Reserved.                          */
 /*                                                                      */
 /*  Permission is hereby granted, free of charge, to use and distribute */
 /*  this software and its documentation without restriction, including  */
 /*  without limitation the rights to use, copy, modify, merge, publish, */
 /*  distribute, sublicense, and/or sell copies of this work, and to     */
 /*  permit persons to whom this work is furnished to do so, subject to  */
 /*  the following conditions:                                           */
 /*   1. The code must retain the above copyright notice, this list of   */
 /*      conditions and the following disclaimer.                        */
 /*   2. Any modifications must be clearly marked as such.               */
 /*   3. Original authors' names are not deleted.                        */
 /*   4. The authors' names are not used to endorse or promote products  */
 /*      derived from this software without specific prior written       */
 /*      permission.                                                     */
 /*                                                                      */
 /*  THE UNIVERSITY OF EDINBURGH AND THE CONTRIBUTORS TO THIS WORK       */
 /*  DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING     */
 /*  ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT  */
 /*  SHALL THE UNIVERSITY OF EDINBURGH NOR THE CONTRIBUTORS BE LIABLE    */
 /*  FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES   */
 /*  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN  */
 /*  AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,         */
 /*  ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF      */
 /*  THIS SOFTWARE.                                                      */
 /*                                                                      */
 /************************************************************************/
 /*                                                                      */
 /*                   Date: December 1997                                */
 /* -------------------------------------------------------------------- */
 /* Instantiate string vector.                                           */
 /*                                                                      */
 /************************************************************************/

#include "EST_types.h"
#include "EST_TVector.h"
#include "EST_TSimpleVector.h"

Declare_TVector(EST_StrList)

#if defined(INSTANTIATE_TEMPLATES)

#include "../base_class/EST_TSimpleVector.cc"
#include "../base_class/EST_TVector.cc"
#include "../base_class/EST_Tvectlist.cc"

Instantiate_TVector(EST_StrList)

#endif

int operator !=(const EST_StrList &l1, 
		const EST_StrList &l2)
{
    EST_Litem *p1, *p2;

    for (p1 = l1.head(), p2 = l2.head(); p1 && p2; p1 = p1->next(),p2 = p2->next())
	if (l1(p1) != l2(p2))
	    return false;

    if (p1 || p2)
	return false;

    return true;
}


