#ifndef DIARY_KERNEL_H
#define DIARY_KERNEL_H

#include <stdint.h>

typedef struct {
    uint32_t text_offset;   // 文字在檔案中的位置
    uint32_t text_len;      // 文字長度
    uint32_t media_index;   // [預留] 媒體 ID (預設 0)
    uint32_t reserved;      // [預留]
    uint64_t created_at;    // 時間戳
    uint8_t  mood;          // 心情分數
    uint8_t  flags;         // 標記 (1=TEXT, 2=AUDIO)
    uint16_t link_id;       // 關聯 ID
    uint32_t padding;       // 補齊 32 bytes
} DiaryMarker;

// Function prototypes
int write_index(const char* filename, uint32_t day_index, DiaryMarker* marker);

#endif
