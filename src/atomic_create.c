#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>

int main(int argc, char **argv) 
{
	int handle;
	if (argc!=2) {
		fprintf(stderr, "Usage: atomic_create <filename>");
		return 1;
	}

	if( handle = open(argv[1], O_RDWR | O_CREAT | O_EXCL, 0600) >=0) {
		close(handle);
		return 0;	
	} else {
		return 2;
	}	
}
