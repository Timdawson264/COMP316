#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <tgmath.h>

//FAST CRC32
#include "nmmintrin.h"

//Hash map - google sparse hash
#include "libchash/libchash.h"

//external c with crc64
extern uint64_t crc64(uint64_t crc, const unsigned char *s, uint64_t l);

#define PUZZLE_SIZE  5

enum puzzle_move_e {
    NOMOVE  = 0,
    LEFT    = 1,
    RIGHT   = 2,
    UP      = 4,
    DOWN    = 8
};

enum puzzle_search {
    FROM_NONE  = 0, //used to test insert
    FROM_START  = 1, 
    FROM_FINAL  = 2,
};

/* defines a change in the puzzle */
typedef struct __attribute__((__packed__)){
  uint8_t direction;
  uint64_t  hash; //TODO not use this here put in seperate hash table 
} puzzle_node_t;

typedef struct __attribute__((__packed__)){
  uint8_t * contents;
  uint16_t size;
} puzzle_state_t;

/* define 4 way storage tree */
typedef struct __attribute__((__packed__)) tree_level{
    size_t hight; //hight of this level;
    
    struct tree_level * prevlevel; //nul at hight 0;
    puzzle_node_t * treelayer; //pointer to node array
    struct tree_level * nextlevel; //next level, null if unexpanded
} tree_level_t;

void print_puzzle_state(puzzle_state_t* state, FILE* out);
void print_puzzle_state_bi(puzzle_state_t* state, puzzle_state_t* state2 , FILE* out);


inline size_t num_nodes_on_level(size_t hight){
  return (( pow(4,hight+1) -1 ) / (4-1)) - ( pow(4,hight) -1 ) / (4-1) ;
}

inline size_t num_nodes_in_tree(size_t hight){
  return ( pow(4,hight+1) -1 ) / (4-1);
}

puzzle_state_t * puzzle_state_new(uint16_t size){
  size_t i;
  puzzle_state_t * new_state = malloc( sizeof(puzzle_state_t) + (size*size));
  new_state->contents = (uint8_t*) new_state+sizeof(puzzle_state_t);
  new_state->size = size;

  for(i=0;i<size*size;i++){
    new_state->contents[i] = i;
  }
  
  return new_state;
}

/* creates a new tree level pass prev is null for root level */
tree_level_t * tree_level_new(tree_level_t * prev){
  tree_level_t * lvl = malloc( sizeof(tree_level_t) );

  lvl->nextlevel = NULL;
  lvl->prevlevel = NULL;
  
  if(prev){
    lvl->prevlevel = prev;
    lvl->hight = prev->hight+1;
    prev->nextlevel = lvl;
  }else{/* root node */
    lvl->hight = 0;
    lvl->prevlevel = NULL;
  }

  lvl->treelayer =  malloc( num_nodes_on_level(lvl->hight) * sizeof(puzzle_node_t) );
  
  return lvl;
}



uint32_t tree_compare_hashs(tree_level_t * a, tree_level_t * b){
  size_t a_i,b_i;
  
  size_t a_len = num_nodes_on_level(a->hight);
  size_t b_len = num_nodes_on_level(b->hight);

  for(a_i=0;a_i<a_len;a_i++)
    for(b_i=0;b_i<b_len;b_i++)
      if(a->treelayer[a_i].hash == b->treelayer[b_i].hash && a->treelayer[a_i].hash!=0)
        return a->treelayer[a_i].hash;
  
  return 0;
}

uint8_t puzzle_state_move_hole(enum puzzle_move_e dir, puzzle_state_t * state){
  size_t i;
  size_t x,y;
  
  for(i=0;i<state->size*state->size;i++){
    if(state->contents[i] == 0) break;
  }

  x = i % state->size;//get x
  y = (i-x)/state->size;//get y

  //fprintf(stdout,"(X,Y): (%u,%u)\n",x,y);
  
  switch(dir){
    case DOWN:{
      //y+1
      if(y==state->size-1) return 0;
      state->contents[x+(y*state->size)] = state->contents[x+( (y+1) *state->size)];
      state->contents[x+( (y+1) *state->size)] = 0;
      break;
    }
    case UP:{
      //y-1
      if(y==0) return 0;
      state->contents[x+(y*state->size)] = state->contents[x+( (y-1) *state->size)];
      state->contents[x+( (y-1) *state->size)] = 0;
      break;
    }
    case LEFT:{
      //x-1
      if(x==0) return 0;
      state->contents[x+(y*state->size)] = state->contents[x-1 +( y*state->size )];
      state->contents[x-1 +( y*state->size )] = 0;
      break;
    }
    case RIGHT:{
      //x+1
      if(x==state->size-1) return 0;
      state->contents[x+(y*state->size)] = state->contents[x+1 +( y*state->size )];
      state->contents[x+1 +( y*state->size )] = 0;
      break;
    }
  }
  return 1; //move was valid
}

uint8_t puzzle_state_unmove_hole(enum puzzle_move_e dir, puzzle_state_t * state){
 switch(dir){
    case UP: return puzzle_state_move_hole(DOWN, state);
    case DOWN: return puzzle_state_move_hole(UP, state);
    case LEFT: return puzzle_state_move_hole(RIGHT, state);
    case RIGHT: return puzzle_state_move_hole(LEFT, state);
  }
}

uint64_t puzzle_state_hash(puzzle_state_t * state){
  size_t size = state->size*state->size;//bytes to hash
  size_t rem = size;
  size_t i;
  uint8_t * data = state->contents;
  uint64_t hash;
  
  return crc64(0,state->contents,size);

/*
  while( rem >= sizeof(uint64_t) ){
    uint64_t in = * data+(size-rem);
    hash = _mm_crc32_u64 (hash, in);
    rem -= sizeof(uint64_t);
  }
  
*/
/*
  
  while( size-count>=sizeof(uint32_t) ){
    uint32_t in = * (uint32_t*) &data[count];
    hash = _mm_crc32_u32 (hash, in);
    count+=sizeof(uint32_t);
  }
  
  while( size-count>=sizeof(uint16_t) ){
    uint16_t in = * (uint16_t*) &data[count];
    hash = _mm_crc32_u16 (hash, in);
    count+=sizeof(uint16_t);
  }
  */
  
  while( rem >= sizeof(uint8_t) ){
    uint8_t in = data[size-rem];
    hash = _mm_crc32_u8 (hash, in);
    rem--;
  }

/*
  for(i=0;i<size;i++)
    fprintf(stderr,"%2u ", state->contents[i]);
  fprintf(stderr,"%#x\n", hash);
*/
  return hash;
}

void puzzle_node_move_hash(enum puzzle_move_e dir, puzzle_state_t * state, puzzle_node_t* node){
  
  //Do move and calc crc
  
  if( puzzle_state_move_hole(dir, state) ){
    //valid move
    node->hash = puzzle_state_hash(state);
    node->direction=dir;
    puzzle_state_unmove_hole(dir, state);
  }else{
    //invalid move
    node->direction=NOMOVE;
    node->hash = 0;
  }
}



void puzzle_state_delete(puzzle_state_t* state){
  free(state->contents);
  free(state);
}

void print_puzzle_state_bi(puzzle_state_t* state, puzzle_state_t* state2 , FILE* out){
  int x,y;
  fprintf(out, "  hash: %#x \thash: %#x\n", puzzle_state_hash(state), puzzle_state_hash(state2) );
  for(y=0; y<state->size; y++){
    fputs("  ", out);
    for(x=0; x<state->size; x++){
      fprintf(out, "%2u,", state->contents[x+(y*state->size)] );
    }
    fputc('\t', out);
    for(x=0; x<state->size; x++){
      fprintf(out, "%2u,", state2->contents[x+(y*state->size)] );
    }
    fputc('\n', out);
  }

}

void print_puzzle_state(puzzle_state_t* state, FILE* out){
  int x,y;
  //fprintf(out, "\thash: %u\n", puzzle_state_hash(state) );
  for(y=0; y<state->size; y++){
    fputc('\t', out);
    for(x=0; x<state->size; x++){
      fprintf(out, "%2u,", state->contents[x+(y*state->size)] );
    }
    fputc('\n', out);
  }

}

void generate_puzzle_state(tree_level_t * lvl, size_t idx, puzzle_state_t * state, puzzle_state_t* root_state){
  //recurse upto root_state then gen backwards
  
  size_t p_node=abs(idx-1)/4;
  //if current node is at the root of the tree
  //fprintf(stderr, "gen_state- lvl: %p, idx: %lu, p_node: %lu\n", lvl,idx,p_node);
  if(lvl==NULL || lvl->treelayer[idx].direction==NOMOVE){
    memcpy(state->contents, root_state->contents, root_state->size*root_state->size);
    return;
  }else{
    generate_puzzle_state(lvl->prevlevel, p_node, state, root_state);
    puzzle_state_move_hole(lvl->treelayer[idx].direction, state);
  }
}

void expand_tree_level(tree_level_t * level, puzzle_state_t * root_state, puzzle_state_t * tmp_state){
  size_t i;
  HTItem* itm;
  
  tree_level_t * next_level = tree_level_new(level);//allocate next tree level to expand into
  size_t count = num_nodes_on_level(level->hight);//num nodes to expand
 
  for(i=0; i<count; i++){
    /* if this is an invalid move then all its children are invalid */
    
    if(level->prevlevel && level->treelayer[i].direction==NOMOVE){
      next_level->treelayer[(4*i)].direction=NOMOVE;
      next_level->treelayer[(4*i)+1].direction=NOMOVE;
      next_level->treelayer[(4*i)+2].direction=NOMOVE;
      next_level->treelayer[(4*i)+3].direction=NOMOVE;
      continue; //dont need anystate 
    }
    
    
    //generate current node state - tmp_state will have this nodes state.
    generate_puzzle_state(level, i, tmp_state, root_state);
    
    //generate children and hash, direction to move, current state, where to save new state_node
    puzzle_node_move_hash( UP, tmp_state, &next_level->treelayer[(4*i)] );
    puzzle_node_move_hash( DOWN, tmp_state, &next_level->treelayer[(4*i)+1] );
    puzzle_node_move_hash( LEFT, tmp_state, &next_level->treelayer[(4*i)+2] );
    puzzle_node_move_hash( RIGHT, tmp_state, &next_level->treelayer[(4*i)+3] );
  
  }
  

}

/* adds an entire tree level while checking for loops and solutions */
uint64_t puzzle_combine_tree_to_hash(tree_level_t * add_level, tree_level_t * other_level, struct HashTable* ht, enum puzzle_search search){
  size_t i,j,skiped,added, looped;
  size_t count = num_nodes_on_level(add_level->hight);//num nodes to proccess
  skiped=0; added=0; looped=0;
  HashSetDeltaGoalSize(ht, count);/* warns hash map of impending inserts */
  
  for(i=0; i<count; i++){
    if(add_level->treelayer[i].direction == NOMOVE){
       skiped++;
       //fprintf(stderr, "SkipState: %#x:%u\n",add_level->treelayer[i].hash, add_level->treelayer[i].direction);
       continue;//no move dont add to hashtable
    }
    
    HTItem * find = HashFind(ht, add_level->treelayer[i].hash);
    if(find && find->data==search){
      //printf("Loop Hash: %#x\n",add_level->treelayer[i].hash);
      add_level->treelayer[i].direction = NOMOVE; //node is a loop within the same search tree
      //fprintf(stderr, "LoopState: %#x:%u\n",add_level->treelayer[i].hash, find->data);
      looped++;
    }else if(find){
      //Find other node
      size_t other_count = num_nodes_on_level(add_level->hight);//num nodes to proccess
      puzzle_node_t* othernode;
      for(j=0;j<other_count;i++){
        if(other_level->treelayer[j].hash == add_level->treelayer[i].hash){
          othernode=&other_level->treelayer[j];
          break;
        }
      }
      if(memcmp(othernode->contents, add_level->treelayer[i].contents, 25, 2) )){
        fprintf(stderr, "SolutionState: %#x:%u\n",add_level->treelayer[i].hash, search);
        return add_level->treelayer[i].hash; //Solution node is from other search direction
      }
    }else{
      /* use state hash as key. and the search direction as data*/
      //fprintf(stderr, "AddState: %#x:%u\n",add_level->treelayer[i].hash, search);
      HTItem* itm = HashInsert(ht, add_level->treelayer[i].hash, search);
      added++;
    }
  }
  fprintf(stderr,"HashCheck - Skipped: %u, Looped: %u, Added: %u\n",skiped,looped,added);
  return 0;
}

void puzzle_solve_bi_search(puzzle_state_t * state_inital, puzzle_state_t * state_final,puzzle_state_t * state_tmp){
  size_t x;
  
  tree_level_t* inital_root = tree_level_new(NULL); //top down search
  tree_level_t* final_root = tree_level_new(NULL); //bottem up search

  inital_root->treelayer[0].direction=NOMOVE;
  inital_root->treelayer[0].hash = puzzle_state_hash(state_inital);

  final_root->treelayer[0].direction=NOMOVE;
  final_root->treelayer[0].hash = 0xbb1fb689;

  tree_level_t * tree_down = inital_root;
  tree_level_t * tree_up = final_root;

  /* key is 32bits or 4 bytes, 0: don't copy keys,
   *  Data will be a pointer to the state node - could be enum of witch state_node tree - ie loop or solution
   *  Key will a hash of the entire state
   * */
  struct HashTable* HT_all = AllocateHashTable(1, 0);
  HashSetDeltaGoalSize(HT_all, 10000000);
  
  //add inital state and goal state
  HashInsert(HT_all, inital_root->treelayer[0].hash, FROM_START);
  HashInsert(HT_all, final_root->treelayer[0].hash, FROM_FINAL);
  
  //expand and check hashes
  while(1){
    expand_tree_level(tree_down, state_inital, state_tmp);
    tree_down = tree_down->nextlevel;
    if(puzzle_combine_tree_to_hash(tree_down, tree_up, HT_all, FROM_START)){
      fprintf(stderr,"Solution At depth down: %u\n", tree_down->hight);
      break;
    }
          
    expand_tree_level(tree_up, state_final, state_tmp);
    tree_up = tree_up->nextlevel;
    if(puzzle_combine_tree_to_hash(tree_up, tree_down, HT_all, FROM_FINAL)){
      fprintf(stderr,"Solution At depth up: %u\n", tree_up->hight);
      break;
    }
    
    fprintf(stderr,"At depth: %u, entry count:%.2fM\n", tree_down->hight, (num_nodes_in_tree(tree_down->hight)*2.0f) / 1000000.0f);
    if(tree_down->hight == 13) break;
  }
 
  //Clean up from this search
  FreeHashTable(HT_all);

  /* free state change trees */
  tree_level_t * tmp;
  tree_down=inital_root;
  while(tree_down){
    tmp=tree_down->nextlevel;
    free(tree_down->treelayer);
    free(tree_down);
    tree_down=tmp;
  }
  tree_up = final_root;
  while(tree_up){
    tmp=tree_up->nextlevel;
    free(tree_up->treelayer);
    free(tree_up);
    tree_up=tmp;
  }
}

int main(int argc, char ** argv){
  int i;
  char puzzle_name[256];
   
  puzzle_state_t * state_inital = puzzle_state_new(PUZZLE_SIZE);
  puzzle_state_t * state_final  = puzzle_state_new(PUZZLE_SIZE);
  puzzle_state_t * state_tmp    = puzzle_state_new(PUZZLE_SIZE);
  //set final state

  char* filename = argv[1];
  FILE* puzzle_sets_f = fopen ( filename, "r" );


  int x;
  for(x=0;x<100;x++){
    fscanf(puzzle_sets_f, "\n%[^\n]",puzzle_name);
    for(i=0; i<PUZZLE_SIZE*PUZZLE_SIZE; i++){
      fscanf(puzzle_sets_f, "%hhu", &state_inital->contents[i]);
    }
    fprintf(stderr,"Trying to solve %s\n", puzzle_name);
    print_puzzle_state_bi(state_inital, state_final, stderr );
    puzzle_solve_bi_search(state_inital, state_final, state_tmp);
    fprintf(stderr,"End %s\n\n", puzzle_name);
  }  

  free(state_inital);
  free(state_final);
  free(state_tmp);
  
  fclose(puzzle_sets_f);
  
}
