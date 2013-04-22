#ifndef MESSAGE_H
#define MESSAGE_H

#ifdef __cplusplus
extern "C" {
#endif

struct message_s{
	char msg_type;
	short payload_len;

	char sender_addr[6];
	char src_addr[6];
	char dst_num;
	char dst_addr[60];

	int file_size;
	char file_hash[32];

	char payload[];
} __attribute__((__packed__));
typedef struct message_s message_t;

message_t* create_message(int type, int payload_length);
void destroy_message(message_t* msg);

void set_sender(message_t* msg, char* sender_ip, unsigned short sender_asid);
void set_src(message_t* msg, char* src_ip, unsigned short src_asid);
void set_dst(message_t* msg, char* dst_ip, unsigned short dst_asid);
void clear_dst(message_t* msg);

void set_fileinfo(message_t* msg, int size, char* hash);
void set_payload(message_t* msg, char* payload);

void ip_string_to_byte(char* src_str, char* dst_byte);
void ip_byte_to_string(char* src_byte, char* dst_str);

#ifdef __cplusplus
}
#endif

#endif
