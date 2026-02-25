#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "diary_kernel.h"

// Returns 0 on success, -1 on error, -2 if entry exists
int write_index(const char* filename, uint32_t day_index, DiaryMarker* marker) {
    FILE *fp = fopen(filename, "rb+");
    if (!fp) {
        // Try to create if not exists
        fp = fopen(filename, "wb+");
        if (!fp) return -1;
    }

    // Calculate offset: day_index * sizeof(DiaryMarker)
    long offset = (long)day_index * sizeof(DiaryMarker);
    
    // Check file size / expand file if needed
    fseek(fp, 0, SEEK_END);
    long file_size = ftell(fp);
    
    if (offset >= file_size) {
        // We are writing beyond current size, fill with zeros up to offset
        // But actually, we can just seek and write? 
        // Standard C allows fseek past EOF for writing, filling gap with random or zeros?
        // Safe way: if offset > file_size, we might need to pad.
        // But for rb+, fseek to huge offset works on most systems (sparse file or zero fill).
        // Let's rely on fseek.
    }

    // Check if entry exists
    DiaryMarker existing;
    memset(&existing, 0, sizeof(DiaryMarker));
    
    if (offset < file_size) {
        fseek(fp, offset, SEEK_SET);
        if (fread(&existing, sizeof(DiaryMarker), 1, fp) == 1) {
            if (existing.text_len > 0) {
                fclose(fp);
                return -2; // Preventing overwrite
            }
        }
    }

    // Write new marker
    fseek(fp, offset, SEEK_SET);
    if (fwrite(marker, sizeof(DiaryMarker), 1, fp) != 1) {
        fclose(fp);
        return -1;
    }

    fclose(fp);
    return 0;
}
