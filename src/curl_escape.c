#include <curl/curl.h>
#include <stdio.h>
int main(int argc, char ** argv) {
	puts(curl_escape(argv[1],0));
	return 0;
}
