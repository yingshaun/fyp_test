#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include "message.h"

message_t* create_message(int type, int payload_length){
	int size = sizeof(message_t) + payload_length;
	message_t* m = (message_t*) malloc(size);
	memset(m, 0, size);
	m->msg_type = (char) type;
	m->payload_len = htons((short) payload_length);
	return m;
}

void destroy_message(message_t* msg) {
	free(msg);
}

void set_sender(message_t* msg, char* sender_ip, unsigned short sender_asid) {
	ip_string_to_byte(sender_ip, msg->sender_addr);
	*((unsigned short*) (msg->sender_addr + 4)) = htons(sender_asid);
}

void set_src(message_t* msg, char* src_ip, unsigned short src_asid) {
	ip_string_to_byte(src_ip, msg->src_addr);
	*((unsigned short*) (msg->src_addr + 4)) = htons(src_asid);
}

void set_dst(message_t* msg, char* dst_ip, unsigned short dst_asid) {
	ip_string_to_byte(dst_ip, msg->dst_addr + msg->dst_num * 6);
	*((unsigned short*) (msg->dst_addr + msg->dst_num * 6 + 4)) = htons(dst_asid);
}

void clear_dst(message_t* msg) {
	msg->dst_num = 0;
}

void set_fileinfo(message_t* msg, int size, char* hash) {
	msg->file_size = htonl(size);
	memcpy(msg->file_hash, hash, 32);
}

void set_payload(message_t* msg, char* payload) {
	memcpy(msg->payload, payload, ntohs(msg->payload_len));
}

void ip_string_to_byte(char* src_str, char* dst_byte) {
	int i;
	int len = strlen(src_str);
	int val = 0;
	int parsed = 0;

	for (i = 0; i < len; i++) {
		if (src_str[i] != '.') {
			int digit = src_str[i] - '0';
			val = val * 10 + digit;
		}else{
			*(dst_byte + parsed++) = val;
			val = 0;
		}
	}
	*(dst_byte + parsed) = val;
}

void ip_byte_to_string(char* src_byte, char* dst_str) {
	int i;
	int pos = 0;

	for (i = 0; i < 4; i++) {
		int val = (unsigned char) src_byte[i];
		int div = 100;
		int started = 0;

		while (val >= 0) {
			int digi = val / div;
			if (digi || started) {
				started = 1;
				dst_str[pos++] = '0' + digi;
			}
			val -= digi * div;
			div /= 10;
			if (!div) {
				break;
			}
		}
		dst_str[pos++] = i == 3 ? 0 : '.';
	}
}
