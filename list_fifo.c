
#include "list_fifo.h"

list_fifo_t * list_fifo_init(){
  list_fifo_t * lst;
  lst = (list_fifo_t*) malloc(sizeof(list_fifo_t));
  lst->head = NULL;
  lst->tail = NULL;
  
  return lst;
}

void list_fifo_push(list_fifo_t * lst, void * data){

  /* new node */
  list_fifo_node_t * n = malloc(sizeof(list_fifo_node_t));
  n->data = data;
  n->next = NULL;

  /* add to end of list */
  if(lst->head == NULL){
    lst->head = n;
  }
  
  if(lst->tail)//if there is a node in the list
    lst->tail->next = n; //add this to end of list
  lst->tail = n; //redirect tail pointer

}

void * list_fifo_pop(list_fifo_t * lst){
  list_fifo_node_t * node;
  void * data;
  
  if(lst->head == NULL)return NULL;
  /* get node */
  node=lst->head; //save top node
  data = node->data; //save data

  /* adjust list */
  if(lst->tail == lst->head) lst->tail=NULL; //last node make tail null
  lst->head = lst->head->next; //point head to next node will be null if last node
  
  free(node);
  return data;
}
