@import pkg1func
#include <stdio.h>

int main(int argc, char* argv[]){
  printf("pkg1func %i\n", pkg1func.func());
  printf("pkg1func %i\n", pkg1func.src.func());
  return 0;
}
