/*************************************************************************/
/*                                                                       */
/*                Centre for Speech Technology Research                  */
/*                     University of Edinburgh, UK                       */
/*                      Copyright (c) 1995,1996                          */
/*                        All Rights Reserved.                           */
/*                                                                       */
/*  Permission is hereby granted, free of charge, to use and distribute  */
/*  this software and its documentation without restriction, including   */
/*  without limitation the rights to use, copy, modify, merge, publish,  */
/*  distribute, sublicense, and/or sell copies of this work, and to      */
/*  permit persons to whom this work is furnished to do so, subject to   */
/*  the following conditions:                                            */
/*   1. The code must retain the above copyright notice, this list of    */
/*      conditions and the following disclaimer.                         */
/*   2. Any modifications must be clearly marked as such.                */
/*   3. Original authors' names are not deleted.                         */
/*   4. The authors' names are not used to endorse or promote products   */
/*      derived from this software without specific prior written        */
/*      permission.                                                      */
/*                                                                       */
/*  THE UNIVERSITY OF EDINBURGH AND THE CONTRIBUTORS TO THIS WORK        */
/*  DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING      */
/*  ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT   */
/*  SHALL THE UNIVERSITY OF EDINBURGH NOR THE CONTRIBUTORS BE LIABLE     */
/*  FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES    */
/*  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN   */
/*  AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,          */
/*  ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF       */
/*  THIS SOFTWARE.                                                       */
/*                                                                       */
/*************************************************************************/
/*                    Author :  Simon King                               */
/*                    Date   :  November 1996                            */
/*-----------------------------------------------------------------------*/
/*           Lattice/Finite State Network i/o functions                  */
/*                                                                       */
/*=======================================================================*/

#include <fstream>
#include <cstdlib>
#include "EST_lattice.h"
#include "EST_types.h"
#include "EST_Token.h"
#include "EST_StringTrie.h"

bool save(Lattice &lattice, EST_String filename)
{
    ostream *outf;
    EST_Litem *n_ptr, *a_ptr;
    int acount=0,ncount=0;
    int i,from,to;
    Lattice::symbol_t *symbol;
    EST_String word;

    if (filename == "-")
	outf = &cout;
    else
	outf = new ofstream(filename);
    
    if (!(*outf))
    {
	cerr << "lattice save: can't open lattice output file \"" 
	    << filename << "\"" << endl;
	return false;
    }

    // count
    for (n_ptr = lattice.nodes.head(); n_ptr != 0; n_ptr = n_ptr->next()){
	ncount++;
	for (a_ptr = lattice.nodes(n_ptr)->arcs_out.head();
	     a_ptr != 0; a_ptr = a_ptr->next())
	    acount++;
    }

    // size line (duh!)
    *outf << "# " << "Generated by Edinburgh Speech Tools" << endl << "#" << endl;
    *outf << "# Header" << endl;
    *outf << "VERSION=1.1" << endl << "#" << endl;
    *outf << "# Size line" << endl;
    *outf << "N=" << ncount << " L=" << acount << endl;
    *outf << "#" << endl;


    // to do : for HTK name nodes, not arcs
    // since all arcs in have same label

    // nodes
    for(i=0;i<=1;i++){

	if(i==0)
	    *outf << "# Nodes" << endl;
	else
	    *outf << "# Arcs" << endl;

	ncount=0;
	acount=0;

	for (n_ptr = lattice.nodes.head(); n_ptr != 0; n_ptr = n_ptr->next()){
	    
	    from=lattice.node_index(lattice.nodes(n_ptr));
	    
	    if(i==0){
		*outf << "I=" << from << endl;
		
	    }else
		for (a_ptr = lattice.nodes(n_ptr)->arcs_out.head();
		     a_ptr != 0; a_ptr = a_ptr->next()){

		    to = lattice.node_index(lattice.nodes(n_ptr)->arcs_out(a_ptr)->to);
		    
		    symbol = lattice.alphabet_index_to_symbol(lattice.nodes(n_ptr)->arcs_out(a_ptr)->label);

		    if(lattice.nodes(n_ptr)->arcs_out(a_ptr)->label == lattice.e_move_symbol_index){
			*outf << "J=" << acount++ << " S=" << from << " E=" << to 
			      << " W=!NULL" << endl;

		    }else{
			*outf << "J=" << acount++ << " S=" << from << " E=" << to 
			      << " l=" << lattice.qmap_index_to_value(symbol->qmap_index)
			      << " W=" << lattice.nmap_index_to_name(symbol->nmap_index)
			      << endl;
		    }
		}
	}
    }
    
    return true;
}

bool
load(Lattice &lattice,EST_String filename)
{

    EST_String name, next_token, str;
    EST_TokenStream ts;
    EST_Token t;
    int i,j;
    // temporary storage
    struct arc_t{
	int start;
	int end;
	float logprob;
	EST_String word;
    };

    arc_t *temp_arcs = NULL;
    int arcindex=0;
    int nodeindex=0;

    // nodes can have labels too - but this is not yet supported
	
    

    if (((filename == "-") ? ts.open(cin) : ts.open(filename)) != 0)
    {
	cerr << "Can't open lattice input file " << filename << endl;
	return false;
    }

    // read file into a arrays, make alphabet, then make lattice

    // find 'size' line

    int numnodes=0;
    int numarcs=0;

    int narcs=-1;
    int nnodes=-1;
    int nodenum=-1;
    int arcnum=-1;
    int startnode=-1;
    int endnode=-1;
    float logprob = 0.0;
    EST_String word="";

    while(!ts.eof())
    {

	str = ts.get().string();

	if(!str.contains("="))
	    continue;

	EST_String left=str.before("=");
	EST_String right=str.after("=");

	if(left == "N")
	    nnodes=atoi(right);
	else if(left == "L")
	    narcs=atoi(right);
	else if(left == "I")
	    nodenum=atoi(right);
	else if(left == "J")
	    arcnum=atoi(right);	
	else if(left == "S")
	    startnode=atoi(right);
	else if(left == "E")
	    endnode=atoi(right);
	else if(left == "l")
	    logprob=atof(right);
	else if(left == "W")
	    word=right;


	if(ts.eoln()){

	    // do something

	    if( (narcs>0) && (nnodes>0) ){
		// it's the size line
		if(temp_arcs != NULL){
		    cerr << "Error in lattice file : 2 size lines found"
			 << " : line " << ts.linenum() << endl;
		    ts.close();
		    return false;
		}else{
		    numarcs=narcs;
		    numnodes=nnodes;
		    temp_arcs = new arc_t[numarcs];
		    cerr << "size : " << numnodes << " " << numarcs << endl;
		}
		
	    }else if(nodenum>=0){
	       		
		if(arcnum>0){
		    cerr << "Error in lattice file at line "
			 << ts.linenum() << endl;
		    ts.close();
		    return false;
		}

		if(nodenum>=numnodes){
		    cerr << "Error in lattice file at line "
			 << ts.linenum() 
			 << " : node index (" << nodenum << ") out of range"
			 << endl;
		    ts.close();
		    return false;
		}

		nodeindex++;

	    }else if(arcnum>=0){
		if(nodenum>0){
		    cerr << "Error in lattice file at line "
			 << ts.linenum() << endl;
		    ts.close();
		    return false;
		}
		
		if(arcnum>=numarcs){
		    cerr << "Error in lattice file at line "
			 << ts.linenum() 
			 << " : arc index (" << arcnum << ") out of range"
			 << endl;
		    ts.close();
		    return false;
		}

		if((startnode<0) || (startnode>=numnodes)){
		    cerr << "Error in lattice file at line " << ts.linenum()
			 << endl
			 << " arc starts at out of range node " 
			 << startnode << endl;
		    return false;
		}

		if((endnode<0) || (endnode>=numnodes)){
		    cerr << "Error in lattice file at line " << ts.linenum()
			 << endl
			 << " arc ends at out of range node " 
			 << endnode << endl;
		    return false;
		}

		// make arc
		temp_arcs[arcindex].start = startnode;
		temp_arcs[arcindex].end = endnode;
		temp_arcs[arcindex].logprob = logprob;
		temp_arcs[arcindex].word = word;
		arcindex++;
	       		
	    }

	    narcs=-1;
	    nnodes=-1;
	    nodenum=-1;
	    arcnum=-1;
	    startnode=-1;
	    endnode=-1;
	    logprob=-1;
	    word="";
	    
	}

    }

    if(arcindex != numarcs){
	cerr << "Error in lattice file at line "
	     << "found " << arcindex << " arcs, but expected " 
	     << numarcs << endl;
	return false;
    }

    if(nodeindex != numnodes){
	cerr << "Error in lattice file at line "
	     << "found " << nodeindex << " nodes, but expected " 
	     << numnodes << endl;
	return false;
    }


    // make nmap
    EST_StringTrie seen_before;
    EST_StrList list_nmap;
    
    for(i=0;i<numarcs;i++){

	if(seen_before.lookup(temp_arcs[i].word) != (void *)(1)){
	    seen_before.add(temp_arcs[i].word,(void *)(1));
	    list_nmap.append(temp_arcs[i].word);
	}
    }
    qsort(list_nmap);
    
    //cerr << "here is the list nmap" << list_nmap << endl;

    i=0;
    EST_Litem *l_ptr;
    bool flag;
    for(l_ptr=list_nmap.head();l_ptr != 0; l_ptr=l_ptr->next())
	i++;

    // transfer to array
    lattice.nmap.resize(i);
    i=0;
    for(l_ptr=list_nmap.head();l_ptr != 0; l_ptr=l_ptr->next())
	lattice.nmap[i++] = list_nmap(l_ptr);

    list_nmap.clear();
    cerr << "Built nmap with " << i << " entries" << endl;


    // make qmap
    // should be a separate fn

    EST_TList<float> list_qmap;

    float error_margin = 1.0e-02; // temporary hack

    for(i=0;i<numarcs;i++){
		
	    flag = false;
	    for(l_ptr=list_qmap.head();l_ptr != 0; l_ptr=l_ptr->next())
		if(fabs(list_qmap(l_ptr) - temp_arcs[i].logprob) <= error_margin){
		    flag = true;
		    break;
		}

	    if(!flag)
		list_qmap.append(temp_arcs[i].logprob);
	    
    }
    
    // special zero (within error_margin) entry, if not already there
    flag = false;
    for(l_ptr=list_qmap.head();l_ptr != 0; l_ptr=l_ptr->next())
	if(fabs(list_qmap(l_ptr)) <= error_margin){
	    flag = true;
	    break;
	}
    
    if(!flag)
	list_qmap.append(0);
    
    qsort(list_qmap);
    
    i=0;
    for(l_ptr=list_qmap.head();l_ptr != 0; l_ptr=l_ptr->next())
	i++;
    
    // transfer to array
    lattice.qmap.resize(i);
    i=0;
    for(l_ptr=list_qmap.head();l_ptr != 0; l_ptr=l_ptr->next())
	lattice.qmap[i++] = list_qmap(l_ptr);

    list_qmap.clear();
    cerr << "Built qmap with " << i << " entries" << endl;


    // make alphabet
   
    // temporary list
    bool **used; // index nmap,qmap
    int nl = lattice.nmap.n();
    int ql = lattice.qmap.n();
    used = new bool*[nl];
    for(i=0;i<nl;i++)
	used[i] = new bool[ql];

    for(i=0;i<nl;i++)
	for(j=0;j<ql;j++)
	    used[i][j] = false;

    // get all combinations of word and log probability actually used
    for(i=0;i<numarcs;i++){

	//cerr << "arc " << i << " " << temp_arcs[i].logprob
	//<< " " << temp_arcs[i].word << endl;

	used[lattice.nmap_name_to_index(temp_arcs[i].word)][lattice.qmap_value_to_index(temp_arcs[i].logprob)] = true;
    }

    int count = 0;
    for(i=0;i<nl;i++)
	for(j=0;j<ql;j++)
	    if(used[i][j])
		count++;

    lattice.alphabet.resize(count);
    count=0;
    Lattice::symbol_t *sym;
    // ordered this way so already sorted, first by q then by n
    for(j=0;j<ql;j++)
	for(i=0;i<nl;i++)
	    if(used[i][j]){
		sym = new Lattice::symbol_t;
		sym->nmap_index=i;
		sym->qmap_index=j;
		lattice.alphabet[count++] = *sym;

	    }

    cerr << "Alphabet has " << count << " symbols " << endl;

    // make lattice itself

    // nodes
    for(i=0;i<numnodes;i++){
	Lattice::Node *new_node;
	new_node = new Lattice::Node;
	lattice.nodes.append(new_node);

    }

    // arcs
    EST_Litem *n_ptr;
    for(j=0;j<numarcs;j++){
	
	// find from and to nodes by counting down node list

	// from node

	for (n_ptr =lattice. nodes.head(),count=0; 
	     count<temp_arcs[j].start;
	     n_ptr = n_ptr->next(),count++){

	    if(n_ptr == NULL){
		cerr << "Couldn't find 'from' node ";
		return false;
	    }
	}
	Lattice::Node *from_node = lattice.nodes(n_ptr);

	// double check
	if(from_node == NULL){
	    cerr << "Couldn't find from node, index " 
		 << temp_arcs[j].start << endl;
	    return false;
	}


	for (n_ptr = lattice.nodes.head(),count=0; 
	     count<temp_arcs[j].end;
	     n_ptr = n_ptr->next(),count++){

	    if(n_ptr == NULL){
		cerr << "Couldn't find 'to' node ";
		return false;
	    }
	}
	Lattice::Node *to_node = lattice.nodes(n_ptr);

	// double check
	if(to_node == NULL){
	    cerr << "Couldn't find to node, index " 
		 << temp_arcs[j].end << endl;
	    return false;
	}


	int word_index = lattice.nmap_name_to_index(temp_arcs[j].word);

	// get arc symbol
	int symbol = lattice.alphabet_index_lookup(word_index,
				       lattice.qmap_value_to_index(temp_arcs[j].logprob));
	if(symbol < 0){
	    cerr << "Couldn't lookup symbol in alphabet !" << endl;
	    return false;
	}
 	
	Lattice::Arc *new_arc = new Lattice::Arc;
	new_arc->label = symbol;
	new_arc->to = to_node;

	if(to_node->name.head() == NULL)
	    to_node->name.append(word_index); // only name of first arc in .. !

	from_node->arcs_out.append(new_arc);
	
    }

    // find final nodes
    for (n_ptr = lattice.nodes.head(),count=0; 
	 n_ptr!= NULL;
	 n_ptr = n_ptr->next()){

	if(lattice.nodes(n_ptr)->arcs_out.head() == NULL){
	    lattice.final_nodes.append(lattice.nodes(n_ptr));
	    count++;
	}
    }

    cerr << "found " << count << " final nodes" << endl;



    cerr << "Lattice loaded !" << endl;

    delete [] used;
    delete [] temp_arcs;

    return true;
}
