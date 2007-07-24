#include <curl/curl.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char ** argv) {
	if(argc!=2) {
		return 1;
	} else {
		char * s;
		s = curl_unescape(argv[1],0);
		if (s==NULL) {
			return 2;
		} else {
			puts(s);
			curl_free(s);
			return 0;
		}
	}
}
