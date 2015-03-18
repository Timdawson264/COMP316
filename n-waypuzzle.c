#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <tgmath.h>
#include <stddef.h>
#include <stdbool.h>
#include <time.h>

//chunk allocator
#include "challoc/challoc.h"

//FIFO
#include "list_fifo.h"

//Cuckoo hash table - 95% load factor
#include "Cuckoo-hash/src/cuckoo_hash.h"

#define PUZZLE_SIZE  5
#define PUZZLE_SIZE2 (PUZZLE_SIZE*PUZZLE_SIZE)

enum puzzle_move_e {
    MOVE_INVALID,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UP,
    MOVE_DOWN,
    
};

enum puzzle_search {
    FROM_NONE  = 0, //used to test insert
    FROM_INITAL  = 1, 
    FROM_GOAL  = 2,
};

/* Struct holds all board state and enough infomation to find perent state */
typedef struct __attribute__((__packed__)) puzzle_state{
  //perent state - can undo move and use do a HT key search
  uint8_t move : 4; //NIBBLE - move that generated this state
  uint8_t search : 4; //NIBBLE - the origin of the state - ie which side of the search
  uint8_t board[]; //the current array of the pieaces TODO:BitPack Board
} puzzle_state_t;

size_t num_states; //tracks the total number of states generated
size_t memusage; //tracks memory usage in bytes
ChunkAllocator * chunkalloc;

void* my_malloc(size_t size){
  void * ptr;
  ptr = malloc(size);
  if(!ptr) exit(2);//no memory
  memusage+=size;
  //fprintf(stderr,"malloc: %p\n", ptr);
  return ptr;
}

void my_free(void * ptr){
  free(ptr);
  //fprintf(stderr,"free: %p\n", ptr);
}


void print_puzzle_state(puzzle_state_t* state, FILE* out);
void print_puzzle_state_bi(puzzle_state_t* state, puzzle_state_t* state2 , FILE* out);




uint8_t puzzle_state_move_hole(enum puzzle_move_e dir, puzzle_state_t * state){
  size_t i;
  size_t x,y;
  
  for(i=0;i<PUZZLE_SIZE2;i++){
    if(state->board[i] == 0) break;
  }

  x = i % PUZZLE_SIZE;//get x
  y = (i-x)/PUZZLE_SIZE;//get y

  //fprintf(stdout,"(X,Y): (%u,%u)\n",x,y);
  
  switch(dir){
    case MOVE_DOWN:{
      //y+1
      if(y==PUZZLE_SIZE-1) return 0;
      state->board[x+(y*PUZZLE_SIZE)] = state->board[x+( (y+1) * PUZZLE_SIZE)];
      state->board[x+( (y+1) *PUZZLE_SIZE)] = 0;
      break;
    }
    case MOVE_UP:{
      //y-1
      if(y==0) return 0;
      state->board[x+(y*PUZZLE_SIZE)] = state->board[x+( (y-1) * PUZZLE_SIZE)];
      state->board[x+( (y-1) *PUZZLE_SIZE)] = 0;
      break;
    }
    case MOVE_LEFT:{
      //x-1
      if(x==0) return 0;
      state->board[x+(y*PUZZLE_SIZE)] = state->board[x-1 +( y * PUZZLE_SIZE )];
      state->board[x-1 +( y*PUZZLE_SIZE )] = 0;
      break;
    }
    case MOVE_RIGHT:{
      //x+1
      if(x==PUZZLE_SIZE-1) return 0;
      state->board[x+(y*PUZZLE_SIZE)] = state->board[x+1 +( y * PUZZLE_SIZE )];
      state->board[x+1 +( y*PUZZLE_SIZE )] = 0;
      break;
    }
  }
  return 1; //move was valid
}

uint8_t puzzle_state_unmove_hole(enum puzzle_move_e dir, puzzle_state_t * state){
 switch(dir){
    case MOVE_UP: return puzzle_state_move_hole(MOVE_DOWN, state);
    case MOVE_DOWN: return puzzle_state_move_hole(MOVE_UP, state);
    case MOVE_LEFT: return puzzle_state_move_hole(MOVE_RIGHT, state);
    case MOVE_RIGHT: return puzzle_state_move_hole(MOVE_LEFT, state);
  }
}


void puzzle_state_delete(puzzle_state_t * state){
  #ifdef CHUNK_MALLOC
    chfree(chunkalloc, state);
  #else
    free(state);
  #endif
}

puzzle_state_t * puzzle_state_new_blank(){
  size_t i;

  #ifdef CHUNK_MALLOC
    puzzle_state_t * new_state = challoc(chunkalloc);
    memusage += sizeof(puzzle_state_t) + PUZZLE_SIZE2;
  #else
    puzzle_state_t * new_state = my_malloc( sizeof(puzzle_state_t) + PUZZLE_SIZE2 );
  #endif

  for(i=0;i<PUZZLE_SIZE2;i++){
    new_state->board[i] = i;
  }

  new_state->move = MOVE_INVALID;
  num_states++;
  return new_state;
}

puzzle_state_t * puzzle_state_new_expand(puzzle_state_t * old_state, enum puzzle_move_e dir){
  puzzle_state_t * new_state;
  new_state = puzzle_state_new_blank();

  memcpy(new_state->board, old_state->board, PUZZLE_SIZE2); //Clone state
  new_state->search = old_state->search; //set nodes search direction
  
  if( puzzle_state_move_hole(dir, new_state) ){
    new_state->move=dir;
    return new_state;
  }else{
    puzzle_state_delete(new_state);
    return NULL;
  }
}

void print_puzzle_state_bi(puzzle_state_t* state, puzzle_state_t* state2 , FILE* out){
  int x,y;
  for(y=0; y<PUZZLE_SIZE; y++){
    fputs("  ", out);
    for(x=0; x<PUZZLE_SIZE; x++){
      fprintf(out, "%2u,", state->board[x+(y*PUZZLE_SIZE)] );
    }
    fputc('\t', out);
    for(x=0; x<PUZZLE_SIZE; x++){
      fprintf(out, "%2u,", state2->board[x+(y*PUZZLE_SIZE)] );
    }
    fputc('\n', out);
  }

}

void print_puzzle_state(puzzle_state_t* state, FILE* out){
  int x,y;
  //fprintf(out, "\thash: %u\n", puzzle_state_hash(state) );
  for(y=0; y<PUZZLE_SIZE; y++){
    fputc('\t', out);
    for(x=0; x<PUZZLE_SIZE; x++){
      fprintf(out, "%2u,", state->board[x+(y*PUZZLE_SIZE)] );
    }
    fputc('\n', out);
  }

}

int add_state_to_ht(struct cuckoo_hash * HT, puzzle_state_t * state){
  struct cuckoo_hash_item * itm;
  puzzle_state_t * found_state;
  
  /* use board as key, also use state as data so we can find all state info */
  itm = cuckoo_hash_insert(HT, state->board, PUZZLE_SIZE2, state);

  if(itm == NULL) return 1;//inserted
  if(itm == CUCKOO_HASH_FAILED){
    fprintf(stderr,"Hash Table out of memory %u\n", cuckoo_hash_count(HT) );
    exit(3); //No memory
  }
  
  found_state = itm->value;//get state with same key

  //Loop
  if(found_state->search == state->search){
    if(state->move == MOVE_INVALID) return 1;//Root Node needs to expand
    //free state and ignore
    puzzle_state_delete(state);
    return 0; //dont queue for expansion
  }else{
    //Solution
    return -1;
  }
  
}

void puzzle_expand_node(puzzle_state_t * state, list_fifo_t * lst){
  puzzle_state_t * tmp;
  
  //Generate new state that has moved
  tmp = puzzle_state_new_expand(state, MOVE_UP);
  if(tmp) list_fifo_push(lst, tmp);
  
  tmp = puzzle_state_new_expand(state, MOVE_DOWN);
  if(tmp) list_fifo_push(lst, tmp);
  
  tmp = puzzle_state_new_expand(state, MOVE_LEFT);
  if(tmp) list_fifo_push(lst, tmp);
  
  tmp = puzzle_state_new_expand(state, MOVE_RIGHT);
  if(tmp) list_fifo_push(lst, tmp);
  
}

size_t depth_of_solution(puzzle_state_t * state, struct cuckoo_hash * HT){
  size_t depth;
  puzzle_state_t * state_from_ht;
  puzzle_state_t * prev;
  struct cuckoo_hash_item * itm;
  
  /* Find the state still in the hash table, this state is the same as "state"*/
  itm = cuckoo_hash_lookup(HT, state->board, PUZZLE_SIZE2);
  state_from_ht = itm->value;
  
  depth=0;
  prev=state;

  while(prev && prev->move!=MOVE_INVALID){/* ie not root node */
    depth++;
    puzzle_state_unmove_hole(prev->move, prev);/* unmove to find perent node */
    itm = cuckoo_hash_lookup(HT, prev->board, PUZZLE_SIZE2);
    if(!itm) return 0;
    prev=itm->value;
  }

  prev=state_from_ht;
  while(prev && prev->move!=MOVE_INVALID){/* ie not root node */
    depth++;
    puzzle_state_unmove_hole(prev->move, prev);/* unmove to find perent node */
    itm = cuckoo_hash_lookup(HT, prev->board, PUZZLE_SIZE2);
    if(!itm) return 0;
    prev=itm->value;
  }

  return depth;
}

void puzzle_solve_bi_search(puzzle_state_t * state_inital, puzzle_state_t * state_goal, time_t start_time){
  int res;
  size_t depth;
  struct cuckoo_hash hash;
  puzzle_state_t * state_tmp;
  puzzle_state_t * state_in_ht;
  if( cuckoo_hash_init(&hash, 8) == false ) exit(1);

  list_fifo_t * expand_lst = list_fifo_init(); //nodes to be expanded

  state_inital->search = FROM_INITAL;
  state_goal->search = FROM_GOAL;
  
  add_state_to_ht(&hash, state_inital);//add solution so it can be found
  add_state_to_ht(&hash, state_goal);//add solution so it can be found
  
  list_fifo_push(expand_lst, state_inital);
  list_fifo_push(expand_lst, state_goal); //should add to a stack based search -- ie iter depth first

  //while less then 3 minutes
  while( difftime(time(NULL), start_time) < (60*3) ){
    //get next state to expand
    state_tmp = list_fifo_pop(expand_lst);
    //Check State
    res = add_state_to_ht(&hash, state_tmp);
    //time check after this op
    if( difftime(time(NULL), start_time) > (60*3) ) break;

    if(res == 0) continue; //dont expand this node as this node is not valid
    if(res == 1) puzzle_expand_node(state_tmp, expand_lst);
    
    if(res == -1){
      //Solution
      //state_tmp is here but the equivilant state is in hash table need to join states and count moves
      //fprintf(stderr, "Found Solution - num nodes: %u\n",cuckoo_hash_count(&hash));
      depth = depth_of_solution(state_tmp, &hash);
      fprintf(stderr,"Solved - generated %u states, Time: %.0f seconds, Depth of solution %u\n", num_states, difftime(time(NULL), start_time), depth );

      puzzle_state_delete(state_tmp);
      break;
    }
  }
  
  //Clean up
  while( (state_tmp = list_fifo_pop(expand_lst)) ) puzzle_state_delete(state_tmp); //empty list
  my_free(expand_lst);
  
  struct cuckoo_hash_item * itm;
  for(cuckoo_hash_each(itm, &hash)){
    puzzle_state_delete(itm->value);
    cuckoo_hash_remove(&hash, itm); //empty table
  }
  cuckoo_hash_destroy(&hash);

  //Delete all state chunks
  //chclear(chunkalloc);
}


int main(int argc, char ** argv){
  int i;
  char puzzle_name[256];
  time_t start_time, end_time;
  puzzle_state_t * state_inital;
  puzzle_state_t * state_final;

  char* filename = argv[1];
  FILE* puzzle_sets_f = fopen ( filename, "r" );

  //Setup chunk allocator
  #ifdef CHUNK_MALLOC
    #define num_chunks 10000000
    chunkalloc = chcreate(num_chunks, (sizeof(puzzle_state_t) + PUZZLE_SIZE2));
    fprintf(stderr,"sizeof chunk allocators: %uMb\n", ((sizeof(puzzle_state_t) + PUZZLE_SIZE2)*num_chunks)/(1024*1024) );
  #endif
  
  int x;
  for(x=0;x<100;x++){
    /* all memory is cleared after a puzzle */
    state_inital = puzzle_state_new_blank();
    state_final = puzzle_state_new_blank();
    
    //Parse Puzzle
    fscanf(puzzle_sets_f, "\n%[^\n]",puzzle_name);
    for(i=0; i<PUZZLE_SIZE*PUZZLE_SIZE; i++){
      fscanf(puzzle_sets_f, "%hhu", &state_inital->board[i]);
    }
    //Solve Puzzle
    fprintf(stderr,"\n%s\n", puzzle_name );
    print_puzzle_state(state_inital, stderr);
    memusage=0;
    num_states=0;
    start_time = time(NULL);
    puzzle_solve_bi_search(state_inital, state_final, start_time);
    end_time = time(NULL);
    
  }
  
  fclose(puzzle_sets_f);
  
}
