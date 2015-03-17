#ifndef _LIST_FIFO_H
#define _LIST_FIFO_H


#ifdef __cplusplus
extern "C" {
#endif  /* __cplusplus */

#include <stdio.h>
#include <stdlib.h> 
#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct __attribute__((__packed__)) list_fifo_node{

  void * data;
  struct list_fifo_node * next;
  
} list_fifo_node_t;

typedef struct __attribute__((__packed__)){

  list_fifo_node_t * head; //pop - remove from head
  list_fifo_node_t * tail; //push - add to tail

} list_fifo_t;

list_fifo_t * list_fifo_init();
void list_fifo_push(list_fifo_t * lst, void * data);
void * list_fifo_pop(list_fifo_t * lst);

#ifdef __cplusplus
}      /* extern "C" */
#endif  /* __cplusplus */


#endif  /* ! _LIST_FIFO_H */
