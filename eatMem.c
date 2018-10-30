#include <unistd.h>
#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>



void eatMem(int time,int block_num)
{
 int block = block_num;

 int i =0; int j = 0;
 int cell = 0.1 * 1024 * 1024;
 char * pMem[block];
 for(i = 0; i < block; i++)
 {        
  pMem[i] = (char*)malloc(cell); 
  if(NULL == pMem[i])        
   {            
    printf("Insufficient memory avalible ,Cell %d Failure\n", i);            
    break;        
  }
  
  memset(pMem[i], 0, cell);        
  printf("[%d]%d Bytes.\n", i, cell);
  
  fflush(stdout);
 }    
 
sleep(time);
 
 printf("Done! Start to release memory.\n");
 //释放内存    
 for(i = 0; i < block; i++)
 {
  printf("free[%d]\n", i);
  if(NULL != pMem[i])        
  {            
   free(pMem[i]);    
   pMem[i] = NULL;
  }
  
  fflush(stdout);
 }    
  
 printf("Operation successfully!\n");
 fflush(stdout);  
}

int main(int argc,char * args[])
{
   eatMem(atoi(args[1]),atoi(args[2]));
}