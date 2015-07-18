@import("../pkgfunc", pkgfunc);
#include <stdio.h>

int main(int argc, char* argv[]){
  printf("pkg1func %i\n", pkgfunc.func());
  printf("pkg1func %i\n", pkgfunc.src.func());
  return 0;
}
