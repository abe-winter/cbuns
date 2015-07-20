@import("../pkgfunc", pkgfunc);
#include <stdio.h>

int main(int argc, char* argv[]){
  printf("pkg1func %i\n", pkgfunc.func(1));
  printf("pkg1func %i\n", pkgfunc.src.func(1));
  return 0;
}
