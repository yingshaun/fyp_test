#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "message.h"

int main() {
	int i, j;
	message_t* abc = create_message(1, 1042);
	printf("type: %hhd\n", abc->msg_type);
	printf("length: %hd\n", abc->payload_len);

	char input[255];
	while (1) {
		printf("ip string to byte (0 for exit): ");
		scanf("%s", input);
		if (!strcmp(input, "0")) {
			break;
		}else{
			char ret[4];
			char str[16];
			ip_string_to_byte(input, ret);
			for (i = 0; i < 4; i++) {
				printf("%dth digi: %hhu\n", i + 1, ret[i]);
			}
			ip_byte_to_string(ret, str);
			printf("in string: %s\n", str);
		}
	}
	return 0;
}
